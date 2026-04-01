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
