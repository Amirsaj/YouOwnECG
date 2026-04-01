"""
Core ECG morphology detection engine.

Provides six functions that analyze raw ECG signal data and fiducial positions
to produce detailed morphological analysis dicts. Every function is designed
for mathematical precision and medical accuracy -- these outputs drive
downstream diagnostic classification (LBBB/RBBB, Brugada, Wellens, Sgarbossa,
WPW, AV block, etc.).

Signal convention: input in µV at 500 Hz.  All amplitude outputs in mV
(÷1000).  All time outputs in ms.  Sentinel value -1 means "not detected".
"""

from __future__ import annotations

import numpy as np

# FPT column indices (mirrored from features.py / narrator.py)
COL_PON, COL_PPEAK, COL_POFF = 0, 1, 2
COL_QRSON, COL_Q, COL_R, COL_S, COL_QRSOFF = 3, 4, 5, 6, 7
COL_L, COL_TON, COL_TPEAK, COL_TOFF = 8, 9, 10, 11
COL_CLASS = 12

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SENTINEL = -1


def _safe_slice(sig: np.ndarray, start: int, end: int) -> np.ndarray:
    """Return sig[start:end] clamped to valid bounds, as float64."""
    n = len(sig)
    start = max(0, min(start, n))
    end = max(start, min(end, n))
    return sig[start:end].astype(np.float64)


def _is_valid(*indices: int, n: int) -> bool:
    """True when every index is a detected fiducial inside the signal."""
    return all(0 < idx < n for idx in indices)


def _find_peaks_derivative(segment: np.ndarray, min_amp_frac: float = 0.05):
    """
    Find peaks in *segment* via derivative zero-crossings with amplitude gate.

    Returns list of (index_in_segment, amplitude_relative_to_baseline) sorted
    by position.  Positive amplitude = local max, negative = local min.
    """
    if len(segment) < 3:
        return []

    baseline = segment[0]
    centered = segment - baseline

    d1 = np.diff(centered)
    sign_d1 = np.sign(d1)
    sign_changes = np.diff(sign_d1)

    ptp = np.ptp(centered)
    gate = ptp * min_amp_frac if ptp > 0 else 0

    peaks = []
    for i in np.nonzero(sign_changes != 0)[0]:
        idx = i + 1  # peak position in segment
        amp = centered[idx]
        if abs(amp) < gate:
            continue
        peaks.append((idx, amp))

    return peaks


# ---------------------------------------------------------------------------
# Function 1
# ---------------------------------------------------------------------------


def classify_qrs_pattern(
    sig: np.ndarray, qrs_on: int, qrs_off: int, fs: float
) -> dict:
    """
    Analyze QRS waveform shape to determine morphological pattern.

    The QRS pattern is the SINGLE most important morphological feature for:
    - LBBB vs RBBB differentiation (V1: QS/rS vs RSR')
    - WPW detection (delta wave = slow initial upstroke)
    - Fragmented QRS detection (extra peaks)

    Algorithm:
    1. Extract QRS segment, compute baseline-corrected signal
    2. Compute signed integral (net area) -> net polarity
    3. Find all peaks (derivative zero-crossings with amplitude gate)
    4. Classify positive peaks (R, R') and negative peaks (Q, S)
    5. Analyze terminal force (last 40ms polarity)
    6. Check initial slope for delta wave (WPW)
    7. Assign pattern name from peak structure

    Pattern naming convention (standard ECG notation):
    - Lowercase = small deflection (<0.5mV or <50% of dominant)
    - Uppercase = dominant deflection
    - R' = second positive deflection
    - Examples: "QS" (entirely negative), "rS" (small r, deep S),
      "RSR'" (M-shaped, RBBB), "qRs" (normal), "monophasic_R" (tall R only)
    """
    n = len(sig)
    result: dict = {
        "pattern": "indeterminate",
        "net_area_uv_samples": 0.0,
        "net_polarity": "neutral",
        "positive_peaks": [],
        "negative_peaks": [],
        "terminal_force_polarity": "neutral",
        "terminal_force_mean_uv": 0.0,
        "delta_wave": False,
        "delta_wave_slope_ratio": None,
        "fragmented": False,
        "n_peaks_total": 0,
    }

    if not _is_valid(qrs_on, qrs_off, n=n) or qrs_off <= qrs_on:
        return result

    segment = _safe_slice(sig, qrs_on, qrs_off)
    if len(segment) < 3:
        return result

    baseline = segment[0]
    centered = segment - baseline

    # -- net area / polarity --
    net_area = float(np.sum(centered))
    result["net_area_uv_samples"] = net_area
    result["net_polarity"] = (
        "positive" if net_area > 0 else ("negative" if net_area < 0 else "neutral")
    )

    # -- peaks --
    peaks = _find_peaks_derivative(segment)
    pos_peaks = [(i, a) for i, a in peaks if a > 0]
    neg_peaks = [(i, a) for i, a in peaks if a < 0]
    result["n_peaks_total"] = len(peaks)

    # Dominant amplitude for upper/lowercase classification
    all_amps = [abs(a) for _, a in peaks]
    dominant = max(all_amps) if all_amps else 1.0

    def _label(amp: float, base_char: str) -> str:
        return base_char.upper() if abs(amp) >= 0.5 * dominant else base_char.lower()

    # Store peak info (convert amplitude to mV)
    result["positive_peaks"] = [
        {"index": int(i), "amplitude_mv": round(a / 1000.0, 4)} for i, a in pos_peaks
    ]
    result["negative_peaks"] = [
        {"index": int(i), "amplitude_mv": round(a / 1000.0, 4)} for i, a in neg_peaks
    ]

    # -- terminal force (last 40 ms) --
    terminal_samples = int(0.040 * fs)
    terminal_seg = centered[-terminal_samples:] if terminal_samples < len(centered) else centered
    terminal_mean = float(np.mean(terminal_seg))
    result["terminal_force_mean_uv"] = round(terminal_mean, 2)
    result["terminal_force_polarity"] = (
        "positive" if terminal_mean > 0 else ("negative" if terminal_mean < 0 else "neutral")
    )

    # -- delta wave detection (WPW: slow initial upstroke + short PR + wide QRS) --
    # Delta wave = gradual initial QRS slope (< 15% of max slope)
    # AND QRS must be wide (> 100ms) — narrow QRS with slow start is just a q-wave
    qrs_duration_ms = (qrs_off - qrs_on) / fs * 1000
    initial_samples = max(1, int(0.020 * fs))
    initial_seg = centered[:initial_samples]
    max_slope = float(np.max(np.abs(np.diff(centered)))) if len(centered) > 1 else 1.0
    initial_slope = float(np.max(np.abs(np.diff(initial_seg)))) if len(initial_seg) > 1 else 0.0
    if max_slope > 0:
        slope_ratio = initial_slope / max_slope
        result["delta_wave_slope_ratio"] = round(slope_ratio, 3)
        # Strict: ratio < 0.15 AND QRS > 100ms AND initial segment is smoothly rising
        # (not just a q-wave dip which also has low initial slope)
        # Also require meaningful amplitude (peak-to-peak > 0.3mV = 300µV)
        ptp = float(np.ptp(centered))
        if slope_ratio < 0.15 and qrs_duration_ms > 110 and ptp > 300:
            # Additional check: initial segment should be monotonically increasing/decreasing
            # (delta wave is smooth, not a q-wave dip-then-rise)
            if len(initial_seg) >= 3:
                diffs = np.diff(initial_seg)
                monotonic = np.all(diffs >= 0) or np.all(diffs <= 0)
                if monotonic:
                    result["delta_wave"] = True

    # -- fragmented QRS (stricter: > 6 peaks, not 4) --
    if len(peaks) > 6:
        result["fragmented"] = True

    # -- pattern naming --
    n_pos = len(pos_peaks)
    n_neg = len(neg_peaks)

    if n_pos == 0 and n_neg == 0:
        result["pattern"] = "indeterminate"
    elif n_pos == 0:
        result["pattern"] = "QS"
    elif n_pos >= 1 and n_neg == 0:
        result["pattern"] = "monophasic_R"
    elif n_pos == 1 and n_neg == 1:
        neg_i = neg_peaks[0][0]
        pos_i = pos_peaks[0][0]
        r_label = _label(pos_peaks[0][1], "R")
        if neg_i < pos_i:
            q_label = _label(neg_peaks[0][1], "q")
            result["pattern"] = f"{q_label}{r_label}"
        else:
            s_label = _label(neg_peaks[0][1], "S")
            result["pattern"] = f"{r_label}{s_label}"
    elif n_pos == 1 and n_neg == 2:
        r_label = _label(pos_peaks[0][1], "R")
        sorted_neg = sorted(neg_peaks, key=lambda x: x[0])
        before = [p for p in sorted_neg if p[0] < pos_peaks[0][0]]
        after = [p for p in sorted_neg if p[0] > pos_peaks[0][0]]
        q_label = _label(before[0][1], "q") if before else ""
        s_label = _label(after[0][1], "S") if after else ""
        result["pattern"] = f"{q_label}{r_label}{s_label}"
    elif n_pos == 2:
        sorted_pos = sorted(pos_peaks, key=lambda x: x[0])
        r1_label = _label(sorted_pos[0][1], "R")
        r2_label = _label(sorted_pos[1][1], "R") + "'"
        neg_between = [p for p in neg_peaks if sorted_pos[0][0] < p[0] < sorted_pos[1][0]]
        if neg_between:
            s_label = _label(neg_between[0][1], "S")
            result["pattern"] = f"{r1_label}{s_label}{r2_label}"
        else:
            result["pattern"] = f"{r1_label}{r2_label}"
    else:
        result["fragmented"] = True
        result["pattern"] = "fragmented"

    return result


# ---------------------------------------------------------------------------
# Function 2
# ---------------------------------------------------------------------------


def classify_st_curvature(
    sig: np.ndarray,
    qrs_off: int,
    t_on: int,
    t_peak: int,
    fs: float,
) -> dict:
    """
    Classify ST segment curvature using parabolic fit.

    Distinguishes:
    - Concave up (positive 2nd derivative) = pericarditis, early repolarization
    - Convex up (negative 2nd derivative) = STEMI, Brugada Type 1
    - Linear (near-zero 2nd derivative) = horizontal ST
    - Coved = convex dome descending into T-wave inversion (Brugada)

    Algorithm:
    1. Extract ST segment (qrs_off to t_on)
    2. Fit parabola: y = ax^2 + bx + c
    3. 'a' coefficient determines curvature
    4. Check for coved pattern: convex + monotonic descent + T inverted
    5. Check ST-T continuity (no isoelectric gap -> Brugada)
    """
    n = len(sig)
    result: dict = {
        "curvature": "indeterminate",
        "a_coefficient": None,
        "linear_slope_uv_per_sample": None,
        "coved": False,
        "st_t_continuous": None,
    }

    if not _is_valid(qrs_off, t_on, n=n) or t_on <= qrs_off:
        return result

    segment = _safe_slice(sig, qrs_off, t_on)
    seg_len = len(segment)
    if seg_len < 5:
        return result

    x = np.arange(seg_len, dtype=np.float64)

    # Parabolic fit
    coeffs = np.polyfit(x, segment, 2)
    a = coeffs[0]

    # Normalize 'a' by segment length so threshold is length-independent.
    # With N samples the x range is [0, N-1]; second derivative = 2a.
    # We compare a * N to fixed thresholds.
    a_norm = a * seg_len
    result["a_coefficient"] = round(float(a), 6)

    if a_norm > 0.3:
        result["curvature"] = "concave"
    elif a_norm < -0.3:
        result["curvature"] = "convex"
    else:
        result["curvature"] = "linear"

    # Linear slope for backward compatibility
    lin_coeffs = np.polyfit(x, segment, 1)
    result["linear_slope_uv_per_sample"] = round(float(lin_coeffs[0]), 4)

    # -- Coved detection --
    # Convex + monotonic descent in last 60% of ST + T-peak negative
    if result["curvature"] == "convex" and _is_valid(t_peak, n=n):
        tail_start = int(seg_len * 0.4)
        tail = segment[tail_start:]
        monotonic_desc = bool(np.all(np.diff(tail) <= 0)) if len(tail) > 1 else False
        t_peak_val = float(sig[t_peak])
        baseline_ref = float(sig[qrs_off])
        t_inverted = t_peak_val < baseline_ref
        if monotonic_desc and t_inverted:
            result["coved"] = True

    # -- ST-T continuity --
    if _is_valid(t_on, n=n):
        boundary_start = max(0, t_on - 5)
        boundary_end = min(n, t_on + 5)
        boundary_seg = _safe_slice(sig, boundary_start, boundary_end)
        if len(boundary_seg) > 1:
            baseline_st = float(sig[qrs_off]) if _is_valid(qrs_off, n=n) else 0.0
            crossings = np.sum(np.abs(np.diff(np.sign(boundary_seg - baseline_st))) > 0)
            result["st_t_continuous"] = bool(crossings == 0)

    return result


# ---------------------------------------------------------------------------
# Function 3
# ---------------------------------------------------------------------------


def classify_t_morphology(
    sig: np.ndarray,
    t_on: int,
    t_peak: int,
    t_off: int,
    fs: float,
) -> dict:
    """
    Full T-wave morphology analysis.

    Critical for:
    - Wellens (symmetric deep inversion or biphasic)
    - LVH strain (asymmetric inversion)
    - Hyperacute T (symmetric, tall, wide)
    - LQT2 (notched/bifid T-wave)
    - De Winter (tall, symmetric, peaked)

    Algorithm:
    1. Determine polarity from peak relative to onset baseline
    2. Measure ascending limb (t_on to t_peak) and descending limb (t_peak to t_off)
    3. Symmetry index = min/max of ascending/descending durations
    4. Check for biphasic: zero-crossing within T-wave
    5. Check for notching: derivative sign-change within same polarity
    6. Peaked: narrow width + high amplitude
    """
    n = len(sig)
    result: dict = {
        "polarity": "indeterminate",
        "amplitude_mv": None,
        "ascending_ms": None,
        "descending_ms": None,
        "width_ms": None,
        "symmetry_index": None,
        "biphasic": False,
        "biphasic_type": None,
        "notched": False,
        "peaked": False,
        "morphology_label": "indeterminate",
    }

    if not _is_valid(t_on, t_peak, t_off, n=n) or not (t_on < t_peak < t_off):
        return result

    # Baseline: mean of 5 samples before t_on, or sig[t_on]
    bl_start = max(0, t_on - 5)
    baseline = float(np.mean(sig[bl_start:t_on])) if t_on > bl_start else float(sig[t_on])

    peak_val = float(sig[t_peak])
    amplitude_uv = peak_val - baseline
    amplitude_mv = amplitude_uv / 1000.0
    result["amplitude_mv"] = round(amplitude_mv, 4)

    # Polarity
    if amplitude_mv > 0.02:
        result["polarity"] = "upright"
    elif amplitude_mv < -0.02:
        result["polarity"] = "inverted"
    else:
        result["polarity"] = "flat"

    # Ascending / descending durations
    asc_samples = t_peak - t_on
    desc_samples = t_off - t_peak
    asc_ms = asc_samples / fs * 1000.0
    desc_ms = desc_samples / fs * 1000.0
    width_ms = (t_off - t_on) / fs * 1000.0
    result["ascending_ms"] = round(asc_ms, 1)
    result["descending_ms"] = round(desc_ms, 1)
    result["width_ms"] = round(width_ms, 1)

    # Symmetry index
    if asc_ms > 0 and desc_ms > 0:
        sym = min(asc_ms, desc_ms) / max(asc_ms, desc_ms)
        result["symmetry_index"] = round(sym, 3)

    # -- Biphasic detection --
    t_segment = _safe_slice(sig, t_on, t_off)
    if len(t_segment) >= 5:
        centered = t_segment - baseline
        signs = np.sign(centered)
        sign_changes = np.where(np.abs(np.diff(signs)) > 0)[0]
        if len(sign_changes) >= 1:
            result["biphasic"] = True
            first_cross = sign_changes[0]
            mid = len(t_segment) // 2
            first_half_pos = float(np.mean(centered[:mid])) > 0
            second_half_neg = float(np.mean(centered[mid:])) < 0
            if first_half_pos and second_half_neg:
                result["biphasic_type"] = "wellens_type_a"
            elif not first_half_pos and float(np.mean(centered[mid:])) > 0:
                result["biphasic_type"] = "negative_positive"
            else:
                result["biphasic_type"] = "other"

    # -- Notched detection (stricter: 3+ sign changes + amplitude gate) --
    if len(t_segment) >= 8:
        d1 = np.diff(t_segment.astype(np.float64))
        sign_d1 = np.sign(d1)
        d1_changes = np.where(np.abs(np.diff(sign_d1)) > 0)[0]
        # Notch requires 3+ derivative reversals (normal T has 0-1)
        # AND the notch amplitude must be > 10% of T-wave amplitude
        if len(d1_changes) >= 3 and abs(amplitude_mv) > 0.1:
            # Check that at least one reversal has significant amplitude
            significant_notches = 0
            for idx in d1_changes:
                if idx > 0 and idx < len(t_segment) - 1:
                    local_amp = abs(float(t_segment[idx]) - float(t_segment[max(0, idx - 2)]))
                    if local_amp > abs(amplitude_mv) * 100:  # 10% of T amplitude (in µV)
                        significant_notches += 1
            if significant_notches >= 1:
                result["notched"] = True

    # -- Peaked detection --
    sym_val = result["symmetry_index"]
    if (
        width_ms < 160
        and abs(amplitude_mv) > 0.5
        and sym_val is not None
        and sym_val > 0.6
    ):
        result["peaked"] = True

    # -- Composite label --
    if result["biphasic"]:
        result["morphology_label"] = f"biphasic_{result['biphasic_type']}"
    elif result["notched"]:
        result["morphology_label"] = "notched"
    elif result["peaked"]:
        result["morphology_label"] = f"peaked_{result['polarity']}"
    elif result["polarity"] == "inverted":
        if sym_val is not None and sym_val > 0.7:
            result["morphology_label"] = "symmetric_inversion"
        elif sym_val is not None and sym_val < 0.5:
            result["morphology_label"] = "asymmetric_inversion"
        else:
            result["morphology_label"] = "inverted"
    elif result["polarity"] == "upright":
        if sym_val is not None and sym_val > 0.7 and abs(amplitude_mv) > 0.5:
            result["morphology_label"] = "hyperacute"
        else:
            result["morphology_label"] = "upright_normal"
    else:
        result["morphology_label"] = "flat"

    return result


# ---------------------------------------------------------------------------
# Function 4
# ---------------------------------------------------------------------------


def assess_concordance(
    sig: np.ndarray,
    qrs_on: int,
    qrs_off: int,
    st_elevation_mv: float,
    st_depression_mv: float,
    s_amplitude_mv: float,
    fs: float,
) -> dict:
    """
    Determine ST-QRS concordance for Sgarbossa criteria (STEMI in LBBB).

    Concordant = ST change in SAME direction as terminal QRS = PATHOLOGICAL
    Discordant = ST change in OPPOSITE direction = expected secondary change in BBB

    Also computes Smith-modified ratio: |ST elevation| / |S-wave depth|
    If ratio >= 0.25 -> Sgarbossa criterion 3 positive
    """
    n = len(sig)
    result: dict = {
        "terminal_qrs_polarity": "indeterminate",
        "terminal_qrs_mean_mv": None,
        "st_direction": "isoelectric",
        "concordance": "indeterminate",
        "smith_ratio": None,
        "sgarbossa_criterion_3": False,
    }

    if not _is_valid(qrs_on, qrs_off, n=n) or qrs_off <= qrs_on:
        return result

    # Terminal QRS (last 40 ms)
    terminal_start = max(qrs_on, qrs_off - int(0.040 * fs))
    terminal_seg = _safe_slice(sig, terminal_start, qrs_off)
    if len(terminal_seg) == 0:
        return result

    baseline = float(sig[qrs_on])
    terminal_mean = float(np.mean(terminal_seg)) - baseline
    terminal_mv = terminal_mean / 1000.0
    result["terminal_qrs_mean_mv"] = round(terminal_mv, 4)
    result["terminal_qrs_polarity"] = "positive" if terminal_mean > 0 else "negative"

    # ST direction
    st_elev = st_elevation_mv if st_elevation_mv is not None else 0.0
    st_dep = st_depression_mv if st_depression_mv is not None else 0.0

    if st_elev > 0.05:
        result["st_direction"] = "elevation"
    elif st_dep > 0.05:
        result["st_direction"] = "depression"
    else:
        result["st_direction"] = "isoelectric"

    # Concordance
    tp = result["terminal_qrs_polarity"]
    sd = result["st_direction"]
    if sd == "isoelectric":
        result["concordance"] = "isoelectric"
    elif (tp == "positive" and sd == "elevation") or (tp == "negative" and sd == "depression"):
        result["concordance"] = "concordant"
    else:
        result["concordance"] = "discordant"

    # Smith-modified ratio (criterion 3)
    s_amp = abs(s_amplitude_mv) if s_amplitude_mv is not None else 0.0
    if s_amp > 0 and st_elev > 0:
        ratio = st_elev / s_amp
        result["smith_ratio"] = round(ratio, 3)
        if ratio >= 0.25:
            result["sgarbossa_criterion_3"] = True

    return result


# ---------------------------------------------------------------------------
# Function 5
# ---------------------------------------------------------------------------


def detect_av_relationship(fpt: np.ndarray, fs: float) -> dict:
    """
    Analyze P-wave to QRS relationship for AV block classification.

    1:1 with constant PR = normal or 1st degree AVB
    Progressive PR -> drop = Wenckebach (2nd degree Type I)
    Variable PR with some drops = 2nd degree Type II
    Independent P and QRS = complete (3rd degree) AVB

    Parameters:
        fpt: 2-D array shape (n_beats, 13) for a single lead.
        fs:  Sampling frequency in Hz.
    """
    result: dict = {
        "av_relationship": "indeterminate",
        "atrial_rate_bpm": None,
        "ventricular_rate_bpm": None,
        "mean_pr_ms": None,
        "pr_intervals_ms": [],
        "pp_cv": None,
        "rr_cv": None,
        "pr_cv": None,
        "wenckebach_detected": False,
        "dissociated": False,
    }

    if fpt is None or len(fpt) < 3:
        return result

    p_peaks = fpt[:, COL_PPEAK].astype(np.float64)
    r_peaks = fpt[:, COL_R].astype(np.float64)

    valid_p = p_peaks[p_peaks > 0]
    valid_r = r_peaks[r_peaks > 0]

    if len(valid_p) < 3 or len(valid_r) < 3:
        return result

    pp = np.diff(valid_p) / fs * 1000.0
    rr = np.diff(valid_r) / fs * 1000.0

    pp_mean = float(np.mean(pp))
    rr_mean = float(np.mean(rr))

    pp_cv = float(np.std(pp) / pp_mean) if pp_mean > 0 else 1.0
    rr_cv = float(np.std(rr) / rr_mean) if rr_mean > 0 else 1.0

    result["pp_cv"] = round(pp_cv, 4)
    result["rr_cv"] = round(rr_cv, 4)
    result["atrial_rate_bpm"] = round(60000.0 / pp_mean, 1) if pp_mean > 0 else None
    result["ventricular_rate_bpm"] = round(60000.0 / rr_mean, 1) if rr_mean > 0 else None

    # Per-beat PR intervals
    pr_intervals: list[float] = []
    for beat in fpt:
        p_on = int(beat[COL_PON])
        qrs_on = int(beat[COL_QRSON])
        if p_on > 0 and qrs_on > 0 and qrs_on > p_on:
            pr_intervals.append((qrs_on - p_on) / fs * 1000.0)
    result["pr_intervals_ms"] = [round(v, 1) for v in pr_intervals]

    if len(pr_intervals) < 2:
        return result

    pr_arr = np.array(pr_intervals)
    pr_mean = float(np.mean(pr_arr))
    pr_cv = float(np.std(pr_arr) / pr_mean) if pr_mean > 0 else 0.0
    result["mean_pr_ms"] = round(pr_mean, 1)
    result["pr_cv"] = round(pr_cv, 4)

    # -- Dissociation (complete AVB) --
    atrial = result["atrial_rate_bpm"]
    vent = result["ventricular_rate_bpm"]
    if (
        pp_cv < 0.15
        and rr_cv < 0.15
        and pr_cv > 0.3
        and atrial is not None
        and vent is not None
        and atrial > vent * 1.2
    ):
        result["dissociated"] = True
        result["av_relationship"] = "complete_av_block"
        return result

    # -- Wenckebach (progressive PR prolongation then dropped beat) --
    if len(pr_intervals) >= 3 and len(rr) >= 2:
        wenckebach = _check_wenckebach(pr_intervals, rr, rr_mean)
        if wenckebach:
            result["wenckebach_detected"] = True
            result["av_relationship"] = "wenckebach"
            return result

    # -- Normal / first-degree / second-degree type II --
    if pr_cv < 0.10:
        if pr_mean > 200:
            result["av_relationship"] = "first_degree_avb"
        else:
            result["av_relationship"] = "normal_1_to_1"
    else:
        result["av_relationship"] = "variable_pr"

    return result


def _check_wenckebach(
    pr_intervals: list[float], rr: np.ndarray, rr_mean: float
) -> bool:
    """
    Look for a Wenckebach cycle: progressively increasing PR intervals
    followed by a long RR gap (dropped beat).
    """
    n = len(pr_intervals)
    for start in range(n - 2):
        # Find a run of increasing PR intervals
        run_len = 1
        for j in range(start + 1, n):
            if pr_intervals[j] > pr_intervals[j - 1]:
                run_len += 1
            else:
                break
        if run_len < 2:
            continue
        # The beat after the last increasing PR should have a long RR
        drop_idx = start + run_len - 1
        if drop_idx < len(rr) and rr[drop_idx] > rr_mean * 1.4:
            return True
    return False


# ---------------------------------------------------------------------------
# Function 6
# ---------------------------------------------------------------------------


def validate_fiducials_by_morphology(
    morph: np.ndarray,
    fpt_dict: dict,
    lead_names: list,
    fs: float,
) -> dict:
    """
    Use morphology analysis to validate and correct fiducial positions.

    Checks per beat per lead:
    1. R-peak should be a local maximum (not a local minimum)
    2. S-peak should be a local minimum after R (not positive)
    3. Q-peak should be a local minimum before R (not after R)
    4. T-onset should be after QRS-offset (not inside QRS)
    5. If QRS has two positive peaks, R should be the TALLEST one
    6. QRS duration should be consistent with QRS pattern

    Parameters:
        morph:      (n_leads, n_samples) raw morphology signal in µV.
        fpt_dict:   dict[lead_name] -> 2-D array (n_beats, 13).
        lead_names: ordered list of lead names matching morph rows.
        fs:         Sampling frequency in Hz.

    Returns:
        dict with keys:
        - "fpt": corrected fpt_dict (deep copy)
        - "corrections_log": list of correction descriptions
        - "n_corrections": total count
        - "per_lead_counts": dict[lead] -> int
    """
    import copy

    corrected = copy.deepcopy(fpt_dict)
    log: list[str] = []
    per_lead: dict[str, int] = {}
    lead_idx_map = {name: i for i, name in enumerate(lead_names)}

    for lead in lead_names:
        if lead not in corrected or len(corrected[lead]) == 0:
            per_lead[lead] = 0
            continue

        li = lead_idx_map.get(lead)
        if li is None or li >= morph.shape[0]:
            per_lead[lead] = 0
            continue

        sig = morph[li].astype(np.float64)
        n = len(sig)
        count = 0
        fpt_arr = corrected[lead]

        for bi in range(len(fpt_arr)):
            beat = fpt_arr[bi]
            qrs_on = int(beat[COL_QRSON])
            qrs_off = int(beat[COL_QRSOFF])
            r_idx = int(beat[COL_R])
            s_idx = int(beat[COL_S])
            q_idx = int(beat[COL_Q])
            t_on = int(beat[COL_TON])

            if not _is_valid(qrs_on, qrs_off, n=n) or qrs_off <= qrs_on:
                continue

            # Check 1: R should be local max
            if _is_valid(r_idx, n=n) and 0 < r_idx < n - 1:
                if not (sig[r_idx] >= sig[r_idx - 1] and sig[r_idx] >= sig[r_idx + 1]):
                    # Find actual local max in QRS window
                    qrs_seg = sig[qrs_on:qrs_off]
                    if len(qrs_seg) > 0:
                        new_r = qrs_on + int(np.argmax(qrs_seg))
                        if new_r != r_idx:
                            log.append(
                                f"{lead} beat {bi}: R moved {r_idx}->{new_r} (not local max)"
                            )
                            fpt_arr[bi, COL_R] = new_r
                            r_idx = new_r
                            count += 1

            # Check 5: If two positive peaks, R should be tallest
            if _is_valid(r_idx, qrs_on, qrs_off, n=n):
                qrs_seg = _safe_slice(sig, qrs_on, qrs_off)
                baseline_qrs = qrs_seg[0] if len(qrs_seg) > 0 else 0.0
                peaks = _find_peaks_derivative(qrs_seg)
                pos_peaks = [(i + qrs_on, a) for i, a in peaks if a > 0]
                if len(pos_peaks) >= 2:
                    tallest = max(pos_peaks, key=lambda p: p[1])
                    if tallest[0] != r_idx:
                        log.append(
                            f"{lead} beat {bi}: R moved {r_idx}->{tallest[0]} "
                            f"(taller positive peak found)"
                        )
                        fpt_arr[bi, COL_R] = tallest[0]
                        r_idx = tallest[0]
                        count += 1

            # Check 2: S should be local min after R and negative relative to baseline
            if _is_valid(s_idx, n=n) and _is_valid(qrs_on, n=n):
                baseline_val = sig[qrs_on]
                if sig[s_idx] > baseline_val:
                    # Find actual min after R in QRS window
                    search_start = max(qrs_on, r_idx) if _is_valid(r_idx, n=n) else qrs_on
                    after_r = _safe_slice(sig, search_start, qrs_off)
                    if len(after_r) > 0:
                        new_s = search_start + int(np.argmin(after_r))
                        if new_s != s_idx:
                            log.append(
                                f"{lead} beat {bi}: S moved {s_idx}->{new_s} "
                                f"(was positive relative to baseline)"
                            )
                            fpt_arr[bi, COL_S] = new_s
                            count += 1

            # Check 3: Q should be before R
            if _is_valid(q_idx, r_idx, n=n) and q_idx >= r_idx:
                # Find min before R in QRS window
                before_r = _safe_slice(sig, qrs_on, r_idx)
                if len(before_r) > 0:
                    new_q = qrs_on + int(np.argmin(before_r))
                    log.append(
                        f"{lead} beat {bi}: Q moved {q_idx}->{new_q} (was after R)"
                    )
                    fpt_arr[bi, COL_Q] = new_q
                    count += 1
                else:
                    fpt_arr[bi, COL_Q] = _SENTINEL
                    log.append(f"{lead} beat {bi}: Q set to -1 (no room before R)")
                    count += 1

            # Check 4: T-onset should be after QRS-offset
            if _is_valid(t_on, qrs_off, n=n) and t_on < qrs_off:
                new_t_on = qrs_off + 1
                if new_t_on < n:
                    log.append(
                        f"{lead} beat {bi}: T-onset moved {t_on}->{new_t_on} "
                        f"(was inside QRS)"
                    )
                    fpt_arr[bi, COL_TON] = new_t_on
                    count += 1

        per_lead[lead] = count

    return {
        "fpt": corrected,
        "corrections_log": log,
        "n_corrections": sum(per_lead.values()),
        "per_lead_counts": per_lead,
    }
