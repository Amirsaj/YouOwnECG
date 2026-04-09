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


TERRITORY_GROUPS = {
    "SEPTAL":   ["V1", "V2"],
    "ANTERIOR": ["V3", "V4"],
    "LATERAL":  ["I", "aVL", "V5", "V6"],
    "INFERIOR": ["II", "III", "aVF"],
}


def narrate_ecg(
    record: PreprocessedECGRecord,
    fiducials: FiducialTable,
    features: FeatureObject,
    max_beats: int = 8,
    leads_for_narrative: list[str] | None = None,
) -> str:
    """
    Generate a structured narrative of the ECG, beat by beat, grouped by territory.

    All 12 leads are narrated by default, organized as:
      Beat N:
        SEPTAL (V1, V2): per-lead description
        ANTERIOR (V3, V4): per-lead description
        LATERAL (I, aVL, V5, V6): per-lead description
        INFERIOR (II, III, aVF): per-lead description

    Args:
        record: Preprocessed ECG record (for raw signal access)
        fiducials: FiducialTable with per-lead FPT arrays
        features: Extracted features (for global context)
        max_beats: Maximum beats to narrate
        leads_for_narrative: Override lead list (None = all 12 via territories)
    """
    fs = record.fs
    s0 = record.safe_window_start_sample
    morph = record.morphology_signal[:, s0:record.safe_window_end_sample]
    lead_idx = {l: i for i, l in enumerate(record.lead_names)}

    fpt = fiducials.fpt
    all_leads = record.lead_names if leads_for_narrative is None else leads_for_narrative
    ref_lead = _pick_ref_lead(fpt, ["II", "V1", "V5", "I"])
    if ref_lead is None or ref_lead not in fpt or len(fpt[ref_lead]) == 0:
        return "No beats detected — narrative unavailable."

    n_beats = min(len(fpt[ref_lead]), max_beats)

    # Global PR from features (cross-lead median, not per-lead)
    global_pr = features.pr_interval_ms

    sections = []

    # 1. Global overview
    sections.append(_global_overview(features, n_beats))

    # 2. Beat-by-beat narrative grouped by territory
    rr_intervals = features.beat_summary.rr_intervals_ms or []

    for beat_i in range(n_beats):
        beat_lines = [f"\n{'='*50}\nBeat {beat_i + 1}/{n_beats}"]

        # RR interval
        if beat_i > 0 and beat_i - 1 < len(rr_intervals):
            rr = rr_intervals[beat_i - 1]
            inst_hr = 60000 / rr if rr > 0 else None
            beat_lines.append(
                f"RR: {rr:.0f} ms"
                + (f" (HR: {inst_hr:.0f} bpm)" if inst_hr else "")
            )

        # Global PR for this beat (use median, not per-lead)
        if global_pr is not None:
            beat_lines.append(f"PR interval (global): {global_pr:.0f} ms")

        # Beat class
        ref_fpt = fpt[ref_lead]
        if beat_i < len(ref_fpt):
            cls = int(ref_fpt[beat_i, COL_CLASS])
            cls_label = BEAT_CLASS_LABELS.get(cls, "unknown")
            if cls_label != "normal":
                beat_lines.append(f"Beat classification: {cls_label.upper()}")

        # Per-territory, per-lead morphology
        for territory, territory_leads in TERRITORY_GROUPS.items():
            available = [l for l in territory_leads if l in lead_idx and l in fpt
                         and beat_i < len(fpt[l])]
            if not available:
                continue

            beat_lines.append(f"\n  {territory} ({', '.join(available)}):")
            for lead in available:
                li = lead_idx[lead]
                sig = morph[li].astype(float)
                beat = fpt[lead][beat_i]
                desc = _describe_beat_lead(sig, beat, fs, lead)
                bl_note = _baseline_note(sig, beat, fs)
                shape_note = _shape_codes(sig, beat, fs)
                if desc:
                    beat_lines.append(f"    {lead}: {desc}{bl_note}")
                    if shape_note:
                        beat_lines.append(f"      Shapes: {shape_note}")

        # Per-beat cross-territory summary
        beat_summary = _beat_territory_summary(features, beat_i, fpt, morph, lead_idx, fs)
        if beat_summary:
            beat_lines.append(f"\n  BEAT {beat_i + 1} SUMMARY:")
            beat_lines.append(f"    {beat_summary}")

        sections.append("\n".join(beat_lines))

    # 3. Rhythm pattern summary
    sections.append(_rhythm_pattern_summary(features, rr_intervals))

    # 4. Cross-lead comparison
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

        # QRS morphology pattern (replaces simple R/S comparison)
        if qrs_on > 0 and qrs_off > 0 and qrs_off > qrs_on:
            from pipeline.morphology import classify_qrs_pattern
            qrs_morph = classify_qrs_pattern(sig, qrs_on, qrs_off, fs)
            pattern = qrs_morph.get("pattern", "unknown")
            polarity = qrs_morph.get("net_polarity", "unknown")
            # Pattern code + descriptive expansion
            desc_parts = [f"Pattern: {pattern} ({polarity})"]
            pos_pks = qrs_morph.get("positive_peaks", [])
            neg_pks = qrs_morph.get("negative_peaks", [])
            n_pos = len(pos_pks)
            n_neg = len(neg_pks)
            if qrs_morph.get("r_prime_present"):
                desc_parts.append("secondary R' deflection present")
            else:
                desc_parts.append("no R'")
            if qrs_morph.get("notching"):
                desc_parts.append("notching present")
            else:
                desc_parts.append("no notching")
            slope_ratio = qrs_morph.get("delta_wave_slope_ratio")
            if slope_ratio is not None and slope_ratio < 0.15:
                desc_parts.append(f"initial upstroke slope ratio {slope_ratio:.2f}")
            else:
                desc_parts.append("no slurring")
            if qrs_morph.get("fragmented"):
                desc_parts.append(f"fragmented ({n_pos}+ deflections)")
            qrs_desc += ". " + ", ".join(desc_parts)

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

        # ST curvature (replaces simple slope description)
        if qrs_off > 0 and t_on > 0 and t_on > qrs_off:
            from pipeline.morphology import classify_st_curvature
            st_morph = classify_st_curvature(sig, qrs_off, t_on, t_peak if t_peak > 0 else t_on + 50, fs)
            curv = st_morph.get("curvature", "")
            a_coeff = st_morph.get("a_coefficient")
            if curv:
                if a_coeff is not None:
                    parts[-1] += f" ({curv}, curvature={a_coeff:.2f})"
                else:
                    parts[-1] += f" ({curv})"

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
                if ratio > 0.5:
                    t_desc += f", T/QRS ratio={ratio:.2f}"

        # QT interval
        if qrs_on > 0 and t_off > 0 and t_off > qrs_on:
            qt_ms = (t_off - qrs_on) / fs * 1000
            t_desc += f", QT={qt_ms:.0f}ms"

        # T-wave symmetry
        if t_on > 0 and t_peak > 0 and t_off > 0:
            from pipeline.morphology import classify_t_morphology
            t_morph_detail = classify_t_morphology(sig, t_on, t_peak, t_off, fs)
            sym = t_morph_detail.get("symmetry_index")
            label = t_morph_detail.get("morphology_label", "")
            if sym is not None:
                t_desc += f", symmetry={sym:.2f}"
            if t_morph_detail.get("notched"):
                t_desc += ", notched"
            if t_morph_detail.get("biphasic"):
                t_desc += f", biphasic ({label})"

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


def _shape_codes(sig: np.ndarray, beat: np.ndarray, fs: float) -> str:
    """Describe P/QRS/ST/T shapes by sampling N evenly-spaced points."""
    try:
        from pipeline.shape_descriptor import describe_shape, format_shape_for_narration
    except ImportError:
        return ""

    parts = []

    segments = [
        ("P",   int(beat[COL_PON]),    int(beat[COL_PPEAK]),  int(beat[COL_POFF])),
        ("QRS", int(beat[COL_QRSON]),  int(beat[COL_R]),      int(beat[COL_QRSOFF])),
        ("ST",  int(beat[COL_QRSOFF]), int(beat[COL_QRSOFF]), int(beat[COL_TON])),
        ("T",   int(beat[COL_TON]),    int(beat[COL_TPEAK]),  int(beat[COL_TOFF])),
    ]

    for seg_type, onset, peak, offset in segments:
        if onset < 0 or offset < 0 or offset <= onset:
            continue
        # For ST: peak is midpoint
        if seg_type == "ST":
            peak = (onset + offset) // 2
        desc = describe_shape(sig, onset, peak, offset, fs, seg_type, n_points=12)
        if desc:
            parts.append(format_shape_for_narration(desc))

    return "\n      ".join(parts) if parts else ""


def _baseline_note(sig: np.ndarray, beat: np.ndarray, fs: float) -> str:
    """Assess baseline quality for one beat in one lead."""
    qrs_on = int(beat[COL_QRSON])
    if qrs_on <= 0:
        return ""

    # Check 50ms before QRS onset for baseline stability
    bl_start = max(0, qrs_on - int(0.05 * fs))
    bl_seg = sig[bl_start:qrs_on]
    if len(bl_seg) < 5:
        return ""

    bl_std = float(np.std(bl_seg))
    bl_std_mv = bl_std / 1000.0

    if bl_std_mv > 0.15:
        return " | baseline: noisy/wandering"
    elif bl_std_mv > 0.05:
        return " | baseline: mildly unstable"
    return " | baseline: stable"


def _beat_territory_summary(
    features: FeatureObject, beat_i: int, fpt: dict,
    morph: np.ndarray, lead_idx: dict, fs: float
) -> str:
    """Summarize cross-territory observations for one beat. Purely observational."""
    parts = []

    # Collect ST values per territory for this beat
    st_notes = []
    for territory, leads in TERRITORY_GROUPS.items():
        elevations = []
        depressions = []
        for lead in leads:
            e = features.st_elevation_mv.get(lead)
            d = features.st_depression_mv.get(lead)
            if e and e > 0.05:
                elevations.append(f"{lead}:+{e:.2f}")
            if d and d > 0.05:
                depressions.append(f"{lead}:-{d:.2f}")
        if elevations:
            st_notes.append(f"ST elevation in {territory} ({', '.join(elevations)} mV)")
        if depressions:
            st_notes.append(f"ST depression in {territory} ({', '.join(depressions)} mV)")

    if st_notes:
        parts.append("; ".join(st_notes))
    else:
        parts.append("ST isoelectric across all territories")

    # QRS width note
    qrs = features.qrs_duration_global_ms
    if qrs and qrs >= 120:
        parts.append(f"QRS wide ({qrs:.0f} ms)")

    # T-wave inversion territories
    t_inv = []
    for territory, leads in TERRITORY_GROUPS.items():
        inv_leads = [l for l in leads if (features.t_amplitude_mv.get(l) or 0) < -0.1]
        if inv_leads:
            t_inv.append(f"{territory} ({', '.join(inv_leads)})")
    if t_inv:
        parts.append(f"T-wave inversion in {'; '.join(t_inv)}")

    # High-amplitude R-waves (voltage)
    high_r = []
    for lead in ["V5", "V6", "I", "aVL"]:
        r = features.r_amplitude_mv.get(lead)
        if r and r > 2.0:
            high_r.append(f"{lead}:{r:.1f}mV")
    for lead in ["V1", "V2"]:
        r = features.r_amplitude_mv.get(lead)
        if r and r > 1.0:
            high_r.append(f"{lead}:{r:.1f}mV")
    if high_r:
        parts.append(f"High R amplitude: {', '.join(high_r)}")

    # Deep S-waves
    deep_s = []
    for lead in ["V1", "V2"]:
        s = features.s_amplitude_mv.get(lead)
        if s and s > 2.0:
            deep_s.append(f"{lead}:{s:.1f}mV")
    if deep_s:
        parts.append(f"Deep S-wave: {', '.join(deep_s)}")

    # QTc note
    qtc = features.qtc_bazett_ms
    if qtc and qtc > 470:
        parts.append(f"QTc {qtc:.0f} ms")

    return ". ".join(parts) + "." if parts else ""


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

    # Voltage measurements (raw, no diagnostic label)
    if features.lvh_sokolow_lyon_mv:
        lines.append(f"  Sokolow-Lyon voltage: {features.lvh_sokolow_lyon_mv:.1f} mV")
    if features.lvh_cornell_mv:
        lines.append(f"  Cornell voltage: {features.lvh_cornell_mv:.1f} mV")

    return "\n".join(lines)


def _annotate(metric: str, value: float) -> str:
    """Add reference range + uncertainty note when outside normal."""
    ranges = NORMAL_RANGES.get(metric)
    if ranges is None:
        return ""
    lo, hi = ranges
    if value < lo:
        return f" [ref: {lo}-{hi}, fiducial accuracy may affect this measurement]"
    if value > hi:
        return f" [ref: {lo}-{hi}, fiducial accuracy may affect this measurement]"
    return f" [ref: {lo}-{hi}]"


def _pick_ref_lead(fpt: dict, preferred: list[str]) -> str | None:
    """Pick reference lead from preferred list."""
    for lead in preferred:
        if lead in fpt and len(fpt[lead]) > 0:
            return lead
    for lead, arr in fpt.items():
        if len(arr) > 0:
            return lead
    return None
