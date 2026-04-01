"""
Beat-by-beat ECG narrator.

Generates structured natural-language descriptions of each beat's morphology,
designed to be consumed by LLM agents the way a cardiology fellow presents
findings to an attending physician.

Instead of just "QRS=95ms, LBBB=false", the narrator produces:
  "Beat 1 (lead II): P-wave present, upright, 0.18 mV, duration 92ms.
   PR interval 162ms (normal). QRS narrow (88ms), R-wave 1.2 mV,
   small q-wave (12ms). ST segment isoelectric. T-wave upright, 0.4 mV."

This gives the LLM the morphological detail needed for pattern recognition
that threshold-based detectors miss (Wenckebach, subtle STEMI, WPW delta waves).
"""

from __future__ import annotations
import numpy as np
from typing import Optional
from pipeline.schemas import (
    PreprocessedECGRecord,
    FiducialTable,
    FeatureObject,
)

# FPT column indices
COL_PON, COL_PPEAK, COL_POFF = 0, 1, 2
COL_QRSON, COL_Q, COL_R, COL_S, COL_QRSOFF = 3, 4, 5, 6, 7
COL_L, COL_TON, COL_TPEAK, COL_TOFF = 8, 9, 10, 11
COL_CLASS = 12

# Beat class labels
BEAT_CLASS_LABELS = {0: "normal", 1: "PVC", 2: "PAC", -1: "unknown"}

# Normal ranges for narrative annotations
NORMAL_RANGES = {
    "pr_ms": (120, 200),
    "qrs_ms": (0, 120),
    "qt_ms": (350, 450),
    "p_dur_ms": (80, 120),
    "p_amp_mv": (0, 0.25),
    "hr_bpm": (60, 100),
}


def narrate_ecg(
    record: PreprocessedECGRecord,
    fiducials: FiducialTable,
    features: FeatureObject,
    max_beats: int = 8,
    leads_for_narrative: list[str] | None = None,
) -> str:
    """
    Generate a structured narrative of the ECG, beat by beat.

    Args:
        record: Preprocessed ECG record (for raw signal access)
        fiducials: FiducialTable with per-lead FPT arrays
        features: Extracted features (for global context)
        max_beats: Maximum beats to narrate (keeps token budget manageable)
        leads_for_narrative: Which leads to describe per beat.
            Default: ["II", "V1", "V5"] (rhythm + right + left heart)

    Returns:
        Multi-line narrative string suitable for LLM context.
        Typically 800-1500 tokens for 5-8 beats × 3 leads.
    """
    if leads_for_narrative is None:
        leads_for_narrative = ["II", "V1", "V5"]

    fs = record.fs
    s0 = record.safe_window_start_sample
    s1 = record.safe_window_end_sample
    morph = record.morphology_signal[:, s0:s1]
    lead_idx = {l: i for i, l in enumerate(record.lead_names)}

    fpt = fiducials.fpt
    ref_lead = _pick_ref_lead(fpt, leads_for_narrative)
    if ref_lead is None or ref_lead not in fpt or len(fpt[ref_lead]) == 0:
        return "No beats detected — narrative unavailable."

    n_beats = min(len(fpt[ref_lead]), max_beats)

    sections = []

    # 1. Global overview (2-3 lines)
    sections.append(_global_overview(features, n_beats))

    # 2. Beat-by-beat narrative
    rr_intervals = features.beat_summary.rr_intervals_ms or []

    for beat_i in range(n_beats):
        beat_lines = [f"\n--- Beat {beat_i + 1}/{n_beats} ---"]

        # RR interval to previous beat
        if beat_i > 0 and beat_i - 1 < len(rr_intervals):
            rr = rr_intervals[beat_i - 1]
            inst_hr = 60000 / rr if rr > 0 else None
            beat_lines.append(
                f"RR interval: {rr:.0f} ms"
                + (f" (instantaneous HR: {inst_hr:.0f} bpm)" if inst_hr else "")
            )

        # Beat class
        ref_fpt = fpt[ref_lead]
        if beat_i < len(ref_fpt):
            cls = int(ref_fpt[beat_i, COL_CLASS])
            cls_label = BEAT_CLASS_LABELS.get(cls, "unknown")
            if cls_label != "normal":
                beat_lines.append(f"Beat classification: {cls_label.upper()}")

        # Per-lead morphology
        for lead in leads_for_narrative:
            if lead not in fpt or beat_i >= len(fpt[lead]):
                continue
            if lead not in lead_idx:
                continue

            li = lead_idx[lead]
            sig = morph[li].astype(float)
            beat = fpt[lead][beat_i]

            desc = _describe_beat_lead(sig, beat, fs, lead)
            if desc:
                beat_lines.append(f"  [{lead}] {desc}")

        sections.append("\n".join(beat_lines))

    # 3. Rhythm pattern summary
    sections.append(_rhythm_pattern_summary(features, rr_intervals))

    # 4. Cross-lead comparison (key leads for territory)
    sections.append(_cross_lead_comparison(features))

    return "\n".join(sections)


def _global_overview(features: FeatureObject, n_beats: int) -> str:
    """One-paragraph global summary."""
    hr = features.heart_rate_ventricular_bpm
    rhythm = features.dominant_rhythm
    reg = "regular" if features.rhythm_regular else "irregular"
    qrs = features.qrs_duration_global_ms
    pr = features.pr_interval_ms

    lines = [
        f"ECG OVERVIEW: {n_beats} beats analyzed. "
        f"Rhythm: {rhythm} ({reg}). "
        f"Ventricular rate: {hr:.0f} bpm. " if hr else "Rate: unknown. ",
    ]
    if pr is not None:
        ann = _annotate("pr_ms", pr)
        lines.append(f"PR interval: {pr:.0f} ms{ann}. ")
    if qrs is not None:
        ann = _annotate("qrs_ms", qrs)
        lines.append(f"QRS duration: {qrs:.0f} ms{ann}. ")
    if features.qtc_bazett_ms is not None:
        lines.append(f"QTc(Bazett): {features.qtc_bazett_ms:.0f} ms. ")
    if features.qrs_axis_deg is not None:
        lines.append(f"QRS axis: {features.qrs_axis_deg:.0f}°.")

    return "".join(lines)


def _describe_beat_lead(
    sig: np.ndarray, beat: np.ndarray, fs: float, lead: str
) -> str:
    """Describe one beat in one lead as a cardiologist would."""
    parts = []

    p_on = int(beat[COL_PON])
    p_peak = int(beat[COL_PPEAK])
    p_off = int(beat[COL_POFF])
    qrs_on = int(beat[COL_QRSON])
    q_idx = int(beat[COL_Q])
    r_idx = int(beat[COL_R])
    s_idx = int(beat[COL_S])
    qrs_off = int(beat[COL_QRSOFF])
    l_idx = int(beat[COL_L])
    t_on = int(beat[COL_TON])
    t_peak = int(beat[COL_TPEAK])
    t_off = int(beat[COL_TOFF])

    N = len(sig)

    # --- P wave ---
    if p_peak > 0 and 0 <= p_peak < N:
        p_amp_uv = float(sig[p_peak])
        # Baseline reference
        if p_on > 0 and p_on < p_peak:
            baseline = float(np.mean(sig[max(0, p_on - 5):p_on])) if p_on > 5 else 0
        else:
            baseline = 0
        p_amp_mv = (p_amp_uv - baseline) / 1000.0
        polarity = "upright" if p_amp_mv > 0.02 else ("inverted" if p_amp_mv < -0.02 else "flat")

        p_desc = f"P-wave {polarity} ({p_amp_mv:+.2f} mV)"
        if p_on > 0 and p_off > 0 and p_off > p_on:
            p_dur = (p_off - p_on) / fs * 1000
            ann = _annotate("p_dur_ms", p_dur)
            p_desc += f", duration {p_dur:.0f}ms{ann}"
        parts.append(p_desc)
    else:
        parts.append("P-wave absent/undetected")

    # --- PR interval ---
    if p_on > 0 and qrs_on > 0 and qrs_on > p_on:
        pr_ms = (qrs_on - p_on) / fs * 1000
        ann = _annotate("pr_ms", pr_ms)
        parts.append(f"PR {pr_ms:.0f}ms{ann}")

    # --- QRS complex ---
    if qrs_on > 0 and qrs_off > 0 and qrs_off > qrs_on:
        qrs_ms = (qrs_off - qrs_on) / fs * 1000
        width = "narrow" if qrs_ms < 120 else "WIDE"
        qrs_desc = f"QRS {width} ({qrs_ms:.0f}ms)"

        # R amplitude
        if r_idx > 0 and 0 <= r_idx < N and qrs_on > 0:
            r_amp = abs(float(sig[r_idx]) - float(sig[qrs_on])) / 1000.0
            qrs_desc += f", R={r_amp:.2f}mV"

        # S amplitude
        if s_idx > 0 and 0 <= s_idx < N and qrs_on > 0:
            s_amp = abs(float(sig[s_idx]) - float(sig[qrs_on])) / 1000.0
            qrs_desc += f", S={s_amp:.2f}mV"

        # Q wave
        if q_idx > 0 and 0 <= q_idx < N and qrs_on > 0:
            q_amp = abs(float(sig[q_idx])) / 1000.0
            q_dur = (q_idx - qrs_on) / fs * 1000 if q_idx > qrs_on else 0
            if q_dur > 5:
                pathological = " (PATHOLOGICAL)" if q_dur > 40 else ""
                qrs_desc += f", q={q_amp:.2f}mV/{q_dur:.0f}ms{pathological}"

        # R/S morphology pattern
        if r_idx > 0 and s_idx > 0 and 0 <= r_idx < N and 0 <= s_idx < N:
            r_val = abs(float(sig[r_idx]))
            s_val = abs(float(sig[s_idx]))
            if lead in ("V1", "V2"):
                if r_val > s_val:
                    qrs_desc += " [R>S: consider RVH/posterior MI/RBBB]"
                elif s_val > 3 * r_val:
                    qrs_desc += " [deep S: normal or LVH]"
            elif lead in ("V5", "V6", "I"):
                if s_val > r_val:
                    qrs_desc += " [S>R: consider RBBB/RVH]"

        parts.append(qrs_desc)

    # --- ST segment ---
    if qrs_off > 0 and 0 <= qrs_off < N:
        # Isoelectric reference
        iso_start = max(0, (qrs_on if qrs_on > 0 else qrs_off) - 10)
        iso_seg = sig[iso_start:max(iso_start + 1, qrs_on if qrs_on > 0 else qrs_off)]
        isoelectric = float(np.mean(iso_seg)) if len(iso_seg) > 0 else 0

        # J-point
        j_mv = (float(sig[qrs_off]) - isoelectric) / 1000.0

        # ST at J+60ms
        j60 = qrs_off + int(0.06 * fs)
        if 0 <= j60 < N:
            st_mv = (float(sig[j60]) - isoelectric) / 1000.0
        else:
            st_mv = j_mv

        if st_mv > 0.1:
            parts.append(f"ST ELEVATED +{st_mv:.2f}mV")
        elif st_mv < -0.1:
            parts.append(f"ST DEPRESSED {st_mv:.2f}mV")
        else:
            parts.append("ST isoelectric")

        # ST morphology
        if t_on > 0 and t_on > qrs_off:
            st_seg = sig[qrs_off:t_on].astype(float)
            if len(st_seg) >= 3:
                slope = np.polyfit(np.arange(len(st_seg)), st_seg, 1)[0]
                if slope > 2:
                    parts[-1] += " (upsloping)"
                elif slope < -2:
                    parts[-1] += " (downsloping)"
                else:
                    parts[-1] += " (horizontal)"

    # --- T wave ---
    if t_peak > 0 and 0 <= t_peak < N:
        t_amp_mv = float(sig[t_peak]) / 1000.0
        if t_amp_mv > 0.1:
            t_desc = f"T-wave upright ({t_amp_mv:+.2f}mV)"
        elif t_amp_mv < -0.1:
            t_desc = f"T-wave INVERTED ({t_amp_mv:+.2f}mV)"
        else:
            t_desc = f"T-wave flat ({t_amp_mv:+.2f}mV)"

        # T/QRS ratio for hyperacute T detection
        if r_idx > 0 and 0 <= r_idx < N:
            r_amp = abs(float(sig[r_idx])) / 1000.0
            if r_amp > 0:
                ratio = abs(t_amp_mv) / r_amp
                if ratio > 0.75:
                    t_desc += f" [T/QRS={ratio:.2f} — HYPERACUTE?]"

        # QT interval
        if qrs_on > 0 and t_off > 0 and t_off > qrs_on:
            qt_ms = (t_off - qrs_on) / fs * 1000
            t_desc += f", QT={qt_ms:.0f}ms"

        parts.append(t_desc)

    return ". ".join(parts) + "." if parts else ""


def _rhythm_pattern_summary(features: FeatureObject, rr_intervals: list[float]) -> str:
    """Describe rhythm patterns across beats."""
    lines = ["\n--- Rhythm Analysis ---"]

    if not rr_intervals:
        lines.append("Insufficient beats for rhythm analysis.")
        return "\n".join(lines)

    rr = np.array(rr_intervals)
    rr_mean = rr.mean()
    rr_std = rr.std()
    rr_cv = rr_std / rr_mean if rr_mean > 0 else 0

    lines.append(f"RR intervals (ms): {', '.join(f'{v:.0f}' for v in rr[:10])}"
                 + ("..." if len(rr) > 10 else ""))
    lines.append(f"Mean RR: {rr_mean:.0f}ms, SD: {rr_std:.0f}ms, CV: {rr_cv:.3f}")

    # Irregularity assessment
    if rr_cv < 0.05:
        lines.append("Rhythm: REGULAR (CV < 0.05)")
    elif rr_cv < 0.10:
        lines.append("Rhythm: MILDLY IRREGULAR (CV 0.05-0.10)")
    elif rr_cv < 0.15:
        lines.append("Rhythm: IRREGULARLY IRREGULAR (CV > 0.10) — consider AFib")
    else:
        lines.append("Rhythm: GROSSLY IRREGULAR (CV > 0.15) — AFib likely")

    # Progressive PR prolongation (Wenckebach pattern)?
    if features.beat_summary.dropped_beat_context:
        lines.append(f"DROPPED BEAT: {features.beat_summary.dropped_beat_context}")

    # Beat pattern
    if features.beat_summary.beat_pattern:
        lines.append(f"Pattern: {features.beat_summary.beat_pattern}")

    # PVC/PAC burden
    counts = features.beat_summary.beat_class_counts
    total = sum(counts.values())
    pvcs = counts.get("pvc", 0)
    pacs = counts.get("pac", 0)
    if pvcs > 0:
        burden = pvcs / total * 100 if total > 0 else 0
        lines.append(f"PVC burden: {pvcs}/{total} beats ({burden:.1f}%)")
    if pacs > 0:
        burden = pacs / total * 100 if total > 0 else 0
        lines.append(f"PAC burden: {pacs}/{total} beats ({burden:.1f}%)")

    return "\n".join(lines)


def _cross_lead_comparison(features: FeatureObject) -> str:
    """Compare findings across leads for territorial assessment."""
    lines = ["\n--- Cross-Lead Comparison ---"]

    # ST elevation by territory
    ant_leads = ["V1", "V2", "V3", "V4"]
    inf_leads = ["II", "III", "aVF"]
    lat_leads = ["I", "aVL", "V5", "V6"]

    for territory, territory_leads, name in [
        (ant_leads, ant_leads, "Anterior (LAD)"),
        (inf_leads, inf_leads, "Inferior (RCA)"),
        (lat_leads, lat_leads, "Lateral (LCx)"),
    ]:
        elevations = []
        depressions = []
        for lead in territory_leads:
            e = features.st_elevation_mv.get(lead)
            d = features.st_depression_mv.get(lead)
            if e and e > 0.05:
                elevations.append(f"{lead}:+{e:.2f}")
            if d and d > 0.05:
                depressions.append(f"{lead}:-{d:.2f}")

        if elevations:
            lines.append(f"  {name} ST elevation: {', '.join(elevations)} mV")
        if depressions:
            lines.append(f"  {name} ST depression: {', '.join(depressions)} mV")

    # R-wave progression
    lines.append(f"  R-wave progression V1→V6: {features.r_progression}")

    # LVH voltage
    if features.lvh_criteria_met:
        lines.append(f"  LVH criteria met: {', '.join(features.lvh_criteria_met)}")

    return "\n".join(lines)


def _annotate(metric: str, value: float) -> str:
    """Add clinical annotation to a measurement."""
    ranges = NORMAL_RANGES.get(metric)
    if ranges is None:
        return ""
    lo, hi = ranges
    if value < lo:
        return " (SHORT)" if "pr" in metric or "qt" in metric else " (LOW)"
    if value > hi:
        return " (PROLONGED)" if "pr" in metric or "qt" in metric or "qrs" in metric else " (HIGH)"
    return " (normal)"


def _pick_ref_lead(fpt: dict, preferred: list[str]) -> str | None:
    """Pick reference lead from preferred list."""
    for lead in preferred:
        if lead in fpt and len(fpt[lead]) > 0:
            return lead
    for lead, arr in fpt.items():
        if len(arr) > 0:
            return lead
    return None
