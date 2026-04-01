"""
Node 1.4 — Fiducial Detection.

Wraps the ecgdeli mastermind delineator to produce a FiducialTable with
13-column FPT arrays (one per lead). Applies condition-based corrections
(AFib zeroing, irregular rhythm P/T suppression) before returning.
"""

from __future__ import annotations
import numpy as np
from pipeline.schemas import PreprocessedECGRecord, QualityReport, FiducialTable

# FPT column indices
COL_PON, COL_PPEAK, COL_POFF = 0, 1, 2
COL_QRSON, COL_Q, COL_R, COL_S, COL_QRSOFF = 3, 4, 5, 6, 7
COL_L, COL_TON, COL_TPEAK, COL_TOFF = 8, 9, 10, 11
COL_CLASS = 12


def detect_fiducials(
    record: PreprocessedECGRecord,
    quality: QualityReport,
) -> FiducialTable:
    """
    Run ecgdeli full annotation pipeline on all usable leads.

    Uses annotate_ecg_multi which expects signal shape (N, n_leads).
    Operates on the safe analysis window of preprocessed_signal.
    Applies condition corrections before returning the FiducialTable.
    total_recording_beats is computed from a full-recording beat count
    (separate from n_beats which covers the safe window only).
    """
    from ecgdeli.annotate import annotate_ecg_multi

    fs = record.fs
    safe_start = record.safe_window_start_sample
    safe_end = record.safe_window_end_sample

    # Full-recording R-peak count (for total_recording_beats)
    total_recording_beats = _count_full_recording_beats(record, quality)

    # Build multi-lead signal for the safe window: shape (N_samples, n_leads)
    # Include all leads (ecgdeli handles quality internally via multi-lead consensus)
    safe_signal_multi = record.preprocessed_signal[:, safe_start:safe_end].T.astype(float)
    # safe_signal_multi shape: (N_safe, n_leads)

    fpt_dict: dict[str, np.ndarray] = {}

    try:
        # annotate_ecg_multi returns (consensus_fpt, per_lead_fpt_list)
        # consensus_fpt shape: (n_beats, 13) — R-peak consensus only
        # per_lead_fpt_list: list of 12 arrays, each (n_beats, 13) — full PQRST per lead
        result = annotate_ecg_multi(
            safe_signal_multi,
            samplerate=fs,
            lead_names=record.lead_names,
            use_mastermind=True,
        )
        if isinstance(result, (tuple, list)) and len(result) == 2:
            _, per_lead_fpts = result
        else:
            per_lead_fpts = None

        for idx, lead in enumerate(record.lead_names):
            if lead in quality.unusable_leads:
                fpt_dict[lead] = np.full((0, 13), -1, dtype=np.int32)
            elif per_lead_fpts is not None and idx < len(per_lead_fpts):
                fpt_arr = np.asarray(per_lead_fpts[idx], dtype=np.int32)
                # ecgdeli uses 0 for undetected; convert to -1 for all non-R columns
                # R column (5) = 0 is valid (first sample); others: 0 means absent
                fpt_clean = fpt_arr.copy()
                for col in [COL_PON, COL_PPEAK, COL_POFF, COL_QRSON, COL_Q,
                             COL_S, COL_QRSOFF, COL_L, COL_TON, COL_TPEAK, COL_TOFF]:
                    fpt_clean[:, col] = np.where(fpt_arr[:, col] == 0, -1, fpt_arr[:, col])
                fpt_dict[lead] = fpt_clean
            else:
                fpt_dict[lead] = np.full((0, 13), -1, dtype=np.int32)
    except Exception:
        # Fallback: all leads get empty FPT
        for lead in record.lead_names:
            fpt_dict[lead] = np.full((0, 13), -1, dtype=np.int32)

    # Remove beats whose R-peak lands within the edge margin (100 ms) of the
    # safe window boundaries.  These partial beats corrupt RR interval CV and
    # should not be used for rhythm or fiducial analysis.
    edge_margin_samples = int(0.200 * fs)   # 200 ms — exclude partial beats near window edges
    safe_len = safe_end - safe_start
    for lead in list(fpt_dict.keys()):
        fpt = fpt_dict[lead]
        if len(fpt) == 0:
            continue
        r = fpt[:, COL_R]
        keep = (r < 0) | ((r >= edge_margin_samples) & (r <= safe_len - edge_margin_samples))
        fpt_dict[lead] = fpt[keep]

    # Refine fiducials using derivative analysis + multi-lead consensus
    morph_safe = record.morphology_signal[:, safe_start:safe_end]
    fpt_dict = refine_fiducials(fpt_dict, morph_safe, record.lead_names, fs)

    # Validate fiducials using morphology analysis
    from pipeline.morphology import validate_fiducials_by_morphology
    morph_validation = validate_fiducials_by_morphology(
        morph_safe, fpt_dict, record.lead_names, fs
    )
    fpt_dict = morph_validation["fpt"]

    # n_beats: use lead II if available, else first non-empty lead
    n_beats = _count_beats_in_fpt(fpt_dict)

    # Compute per-fiducial confidence scores
    fid_conf = _compute_fiducial_confidence(fpt_dict, fs)

    return FiducialTable(
        ecg_id=record.ecg_id,
        fpt=fpt_dict,
        n_beats=n_beats,
        total_recording_beats=total_recording_beats,
        fs=fs,
        safe_window_start_sample=safe_start,
        safe_window_end_sample=safe_end,
        condition_corrections_applied=False,
        fiducial_confidence=fid_conf,
    )



def _compute_fiducial_confidence(
    fpt_dict: dict[str, np.ndarray],
    fs: float,
) -> dict[str, float]:
    """
    Compute per-fiducial-type confidence scores (0.0–1.0).

    Combines two factors:
    1. Detection rate: fraction of beats (across all leads) where the fiducial was detected.
    2. Timing consistency: inverse of normalized beat-to-beat variance (lower variance = higher confidence).

    Score = 0.6 * detection_rate + 0.4 * consistency_score, clamped to [0, 1].
    """
    fiducial_names = {
        COL_PON: "pon", COL_PPEAK: "ppeak", COL_POFF: "poff",
        COL_QRSON: "qrson", COL_Q: "q", COL_R: "r", COL_S: "s", COL_QRSOFF: "qrsoff",
        COL_TON: "ton", COL_TPEAK: "tpeak", COL_TOFF: "toff",
    }
    # Maximum acceptable std dev (ms) for each fiducial type — used for normalization
    max_std_ms = {
        "pon": 30, "ppeak": 25, "poff": 30,
        "qrson": 15, "q": 20, "r": 10, "s": 20, "qrsoff": 15,
        "ton": 30, "tpeak": 25, "toff": 35,
    }

    confidence = {}
    for col, name in fiducial_names.items():
        total_beats = 0
        detected = 0
        all_positions = []

        for lead, fpt in fpt_dict.items():
            if len(fpt) == 0:
                continue
            vals = fpt[:, col]
            total_beats += len(vals)
            valid = vals[vals >= 0]
            detected += len(valid)
            if len(valid) >= 2:
                all_positions.extend(valid.tolist())

        if total_beats == 0:
            confidence[name] = 0.0
            continue

        det_rate = detected / total_beats

        # Consistency: compute relative std dev across all detections
        if len(all_positions) >= 3:
            positions = np.array(all_positions, dtype=float)
            # Normalize by subtracting per-beat R-peak reference to get relative timing
            std_ms = float(np.std(positions)) / fs * 1000
            norm_std = max_std_ms.get(name, 25)
            consistency = max(0.0, 1.0 - std_ms / norm_std)
        else:
            consistency = 0.5  # not enough data — neutral

        score = 0.6 * det_rate + 0.4 * consistency
        confidence[name] = round(min(1.0, max(0.0, score)), 3)

    return confidence


def refine_fiducials(
    fpt_dict: dict[str, np.ndarray],
    morph: np.ndarray,
    lead_names: list[str],
    fs: float,
    max_shift_ms: float = 15.0,
) -> dict[str, np.ndarray]:
    """
    Post-process FPT arrays using derivative-based refinement and multi-lead consensus.

    For each detected fiducial, refines the position using signal derivatives:
    - P-wave onset: find latest zero-crossing of 1st derivative before P-peak
    - P-wave offset: find earliest zero-crossing of 1st derivative after P-peak
    - QRS onset: find point of maximum negative slope before Q/R
    - QRS offset: find point where derivative returns to near-zero after S
    - T-wave onset: find inflection point (2nd derivative zero-crossing) before T-peak
    - T-wave offset: find where 1st derivative returns to near-zero after T-peak

    Multi-lead consensus: for ambiguous fiducials (confidence < 0.5 based on
    derivative sharpness), use the median position across leads.

    max_shift_ms: maximum allowed correction in milliseconds (prevents wild shifts)
    """
    max_shift_samples = int(max_shift_ms / 1000 * fs)
    refined = {}

    lead_idx = {l: i for i, l in enumerate(lead_names)}

    for lead in lead_names:
        if lead not in fpt_dict or len(fpt_dict[lead]) == 0:
            refined[lead] = fpt_dict.get(lead, np.empty((0, 13), dtype=np.int32))
            continue

        li = lead_idx.get(lead)
        if li is None or li >= morph.shape[0]:
            refined[lead] = fpt_dict[lead].copy()
            continue

        sig = morph[li].astype(float)
        fpt = fpt_dict[lead].copy()

        for beat_idx in range(len(fpt)):
            beat = fpt[beat_idx]

            # P-wave onset/offset: NOT refined (low-amplitude waves are too noisy
            # for derivative-based refinement — tested and confirmed worse on 3 patients)

            # Refine QRS onset (col 3)
            qrs_on = int(beat[COL_QRSON])
            r_idx = int(beat[COL_R])
            if qrs_on > 0 and r_idx > 0:
                new_qrson = _refine_qrs_onset(sig, qrs_on, r_idx, max_shift_samples, fs)
                if new_qrson is not None:
                    fpt[beat_idx, COL_QRSON] = new_qrson

            # Refine QRS offset (col 7)
            qrs_off = int(beat[COL_QRSOFF])
            s_idx = int(beat[COL_S])
            if qrs_off > 0 and (s_idx > 0 or r_idx > 0):
                ref_point = s_idx if s_idx > 0 else r_idx
                new_qrsoff = _refine_qrs_offset(sig, ref_point, qrs_off, max_shift_samples, fs)
                if new_qrsoff is not None:
                    fpt[beat_idx, COL_QRSOFF] = new_qrsoff

            # Refine T-wave onset (col 9)
            t_peak = int(beat[COL_TPEAK])
            t_on = int(beat[COL_TON])
            if t_peak > 0 and t_on > 0:
                new_ton = _refine_wave_onset(sig, t_on, t_peak, max_shift_samples)
                if new_ton is not None:
                    fpt[beat_idx, COL_TON] = new_ton

            # Refine T-wave offset (col 11)
            t_off = int(beat[COL_TOFF])
            if t_peak > 0 and t_off > 0:
                new_toff = _refine_twave_offset(sig, t_peak, t_off, max_shift_samples, fs)
                if new_toff is not None:
                    fpt[beat_idx, COL_TOFF] = new_toff

        refined[lead] = fpt

    # Multi-lead consensus for R-peak (most reliable anchor)
    refined = _apply_multilead_consensus(refined, lead_names, COL_R, max_shift_samples)

    return refined


def _refine_wave_onset(sig: np.ndarray, current: int, peak: int, max_shift: int) -> int | None:
    """Refine wave onset using 1st derivative zero-crossing before peak."""
    if current <= 0 or peak <= 0 or peak <= current:
        return None

    search_start = max(0, current - max_shift)
    search_end = min(peak, current + max_shift)

    if search_end - search_start < 3:
        return None

    segment = sig[search_start:search_end]
    deriv = np.diff(segment)

    zero_crossings = np.where(np.diff(np.sign(deriv)))[0]

    if len(zero_crossings) == 0:
        return None

    best = zero_crossings[-1]
    new_pos = search_start + best

    if abs(new_pos - current) <= max_shift:
        return int(new_pos)
    return None


def _refine_wave_offset(sig: np.ndarray, peak: int, current: int, max_shift: int) -> int | None:
    """Refine wave offset using 1st derivative zero-crossing after peak."""
    if peak <= 0 or current <= 0 or current <= peak:
        return None

    search_start = max(peak, current - max_shift)
    search_end = min(len(sig) - 1, current + max_shift)

    if search_end - search_start < 3:
        return None

    segment = sig[search_start:search_end]
    deriv = np.diff(segment)

    zero_crossings = np.where(np.diff(np.sign(deriv)))[0]

    if len(zero_crossings) == 0:
        return None

    best = zero_crossings[0]
    new_pos = search_start + best

    if abs(new_pos - current) <= max_shift:
        return int(new_pos)
    return None


def _refine_qrs_onset(sig: np.ndarray, current: int, r_peak: int, max_shift: int, fs: float) -> int | None:
    """Refine QRS onset: find maximum absolute slope point before R-peak."""
    if current <= 0 or r_peak <= 0 or r_peak <= current:
        return None

    search_start = max(0, current - max_shift)
    search_end = min(r_peak, current + max_shift)

    if search_end - search_start < 3:
        return None

    segment = sig[search_start:search_end]
    deriv = np.abs(np.diff(segment))

    threshold = 0.1 * np.max(deriv) if np.max(deriv) > 0 else 0
    above_thresh = np.where(deriv > threshold)[0]

    if len(above_thresh) == 0:
        return None

    new_pos = search_start + above_thresh[0]

    if abs(new_pos - current) <= max_shift:
        return int(new_pos)
    return None


def _refine_qrs_offset(sig: np.ndarray, s_peak: int, current: int, max_shift: int, fs: float) -> int | None:
    """Refine QRS offset: find where slope returns to near-zero after S-wave."""
    if s_peak <= 0 or current <= 0 or current <= s_peak:
        return None

    search_start = max(s_peak, current - max_shift)
    search_end = min(len(sig) - 1, current + max_shift)

    if search_end - search_start < 3:
        return None

    segment = sig[search_start:search_end]
    deriv = np.abs(np.diff(segment))

    if np.max(deriv) == 0:
        return None

    threshold = 0.1 * np.max(deriv)
    below_thresh = np.where(deriv < threshold)[0]

    if len(below_thresh) == 0:
        return None

    new_pos = search_start + below_thresh[0]

    if abs(new_pos - current) <= max_shift:
        return int(new_pos)
    return None


def _refine_twave_offset(sig: np.ndarray, t_peak: int, current: int, max_shift: int, fs: float) -> int | None:
    """Refine T-wave offset using tangent method: steepest descent tangent intersects baseline."""
    if t_peak <= 0 or current <= 0 or current <= t_peak:
        return None

    search_start = max(t_peak + int(0.020 * fs), current - max_shift)
    search_end = min(len(sig) - 1, current + max_shift)

    if search_end - search_start < 5:
        return None

    segment = sig[search_start:search_end]
    deriv = np.diff(segment)

    min_deriv_idx = np.argmin(deriv)

    if abs(deriv[min_deriv_idx]) < 0.5:
        return None

    baseline = np.mean(segment[-5:]) if len(segment) >= 5 else segment[-1]

    y0 = segment[min_deriv_idx]
    slope = deriv[min_deriv_idx]

    if abs(slope) < 0.01:
        return None

    dx = (baseline - y0) / slope
    new_pos = search_start + min_deriv_idx + int(dx)

    new_pos = max(search_start, min(search_end, new_pos))

    if abs(new_pos - current) <= max_shift:
        return int(new_pos)
    return None


def _apply_multilead_consensus(
    fpt_dict: dict[str, np.ndarray],
    lead_names: list[str],
    col: int,
    max_shift: int,
) -> dict[str, np.ndarray]:
    """For a given fiducial column, use median across leads to correct outliers."""
    n_beats_per_lead = {l: len(fpt_dict[l]) for l in lead_names if l in fpt_dict and len(fpt_dict[l]) > 0}

    if not n_beats_per_lead:
        return fpt_dict

    common_n = max(n_beats_per_lead.values(), key=lambda x: list(n_beats_per_lead.values()).count(x))

    for beat_idx in range(common_n):
        positions = []
        for lead in lead_names:
            if lead not in fpt_dict or beat_idx >= len(fpt_dict[lead]):
                continue
            val = int(fpt_dict[lead][beat_idx, col])
            if val > 0:
                positions.append(val)

        if len(positions) < 3:
            continue

        median_pos = int(np.median(positions))

        for lead in lead_names:
            if lead not in fpt_dict or beat_idx >= len(fpt_dict[lead]):
                continue
            val = int(fpt_dict[lead][beat_idx, col])
            if val > 0 and abs(val - median_pos) > max_shift:
                fpt_dict[lead][beat_idx, col] = median_pos

    return fpt_dict


def _get_reference_lead(fpt_dict: dict[str, np.ndarray]) -> str | None:
    """Return lead II if available and non-empty, else first non-empty lead."""
    if "II" in fpt_dict and len(fpt_dict["II"]) > 0:
        return "II"
    for lead, fpt in fpt_dict.items():
        if len(fpt) > 0:
            return lead
    return None


def _count_beats_in_fpt(fpt_dict: dict[str, np.ndarray]) -> int:
    ref = _get_reference_lead(fpt_dict)
    if ref is None:
        return 0
    fpt = fpt_dict[ref]
    valid_r = fpt[:, COL_R][fpt[:, COL_R] >= 0]
    return len(valid_r)


def _count_full_recording_beats(
    record: PreprocessedECGRecord,
    quality: QualityReport,
) -> int:
    """
    Estimate total beats in the full recording (including edge regions)
    using the bootstrap R-peaks from quality assessment.
    """
    # Use lead II bootstrap if available
    ref_lead = None
    for candidate in ["II", "V1", "aVF"]:
        if candidate in quality._bootstrap_r_peaks and len(quality._bootstrap_r_peaks[candidate]) > 0:
            ref_lead = candidate
            break

    if ref_lead is None:
        # Fall back to any lead
        for lead, peaks in quality._bootstrap_r_peaks.items():
            if len(peaks) > 0:
                ref_lead = lead
                break

    if ref_lead is None:
        return 0

    return int(len(quality._bootstrap_r_peaks[ref_lead]))
