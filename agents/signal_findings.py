"""
Signal-only finding generator.

Produces DiagnosticFindings from FeatureObject using deterministic rules,
without any LLM calls. Used when DEEPSEEK_API_KEY is not set.

Each rule mirrors the criteria from the disease knowledge base (Node 2.7)
and the frontend disease-config.ts criteria checks.
"""

from __future__ import annotations
from typing import Optional

from agents.schemas import DiagnosticFinding, StatAlert, STAT_CONDITIONS
from pipeline.schemas import FeatureObject


def generate_signal_findings(features: FeatureObject) -> list[DiagnosticFinding]:
    """Generate all detectable findings from signal features alone."""
    findings: list[DiagnosticFinding] = []

    for detector in _DETECTORS:
        result = detector(features)
        if result is not None:
            findings.append(result)

    # Clinical suppression rules (post-detection)
    finding_types = {f.finding_type for f in findings}

    # WPW pre-excitation can explain LBBB-pattern wide QRS — suppress LBBB.
    # RBBB is confirmed by independent amplitude criteria (RSR' in V1) and is kept.
    if "wpw_pattern" in finding_types:
        findings = [f for f in findings if f.finding_type != "lbbb"]

    # WPW inflates voltages — suppress LVH
    if "wpw_pattern" in finding_types:
        findings = [f for f in findings if f.finding_type != "lvh"]

    # WPW delta waves produce pseudo-ST elevation in precordial leads that mimics
    # anterior STEMI — suppress STEMI findings when WPW is confirmed.
    # Exception: lateral_stemi is kept because accessory pathway location matters clinically.
    if "wpw_pattern" in finding_types:
        findings = [f for f in findings if f.finding_type not in ("anterior_stemi", "sgarbossa_stemi")]

    # LBBB inflates QTc — already handled in detector, but safety check
    # (no additional suppression needed here)

    return findings


def generate_stat_alerts(findings: list[DiagnosticFinding]) -> list[StatAlert]:
    """Generate StatAlert entries for any STAT-condition findings."""
    alerts = []
    for f in findings:
        if f.stat_alert_fires:
            alerts.append(StatAlert(
                finding_type=f.finding_type,
                confidence=f.confidence,
                message=f.clinical_summary,
            ))
    return alerts


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make(
    finding_type: str,
    confidence: str,
    summary: str,
    detail: str,
    key_values: dict,
    source: str = "SIGNAL",
) -> DiagnosticFinding:
    return DiagnosticFinding(
        finding_type=finding_type,
        confidence=confidence,
        clinical_summary=summary,
        technical_detail=detail,
        key_feature_values=key_values,
        citations=[],
        rag_invoked=False,
        stat_alert_fires=finding_type in STAT_CONDITIONS,
        agent_source=source,
        reasoning_text=None,
    )


def _st_leads(feat: FeatureObject, threshold: float = 0.1) -> tuple[list[str], list[str]]:
    """Return (elevation_leads, depression_leads) above threshold (mV)."""
    elev = [l for l, v in feat.st_elevation_mv.items() if v is not None and v > threshold]
    dep = [l for l, v in feat.st_depression_mv.items() if v is not None and v > threshold]
    return elev, dep


def _fmt(v: Optional[float], precision: int = 0) -> str:
    if v is None:
        return "N/A"
    return f"{v:.{precision}f}" if precision > 0 else str(round(v))


# ---------------------------------------------------------------------------
# Detectors — each returns a DiagnosticFinding or None
# ---------------------------------------------------------------------------

def _detect_lbbb(f: FeatureObject) -> Optional[DiagnosticFinding]:
    qrs = f.qrs_duration_global_ms or 0
    v1_pat = f.qrs_pattern.get("V1", "unknown")
    v5_pat = f.qrs_pattern.get("V5", "unknown")
    v6_pat = f.qrs_pattern.get("V6", "unknown")
    # Primary: feature-level flag (already incorporates morphology cross-checks)
    # Fallback: V1=QS + V5/V6=monophasic_R + QRS>=120ms (strict LBBB criteria)
    morph_lbbb = (v1_pat == "QS" and qrs >= 120
                  and (v5_pat == "monophasic_R" or v6_pat == "monophasic_R"))
    if not f.lbbb and not morph_lbbb:
        return None
    v1_desc = f"V1={v1_pat}" if v1_pat != "unknown" else "V1 net negative"
    return _make(
        "lbbb", "HIGH",
        f"Left bundle branch block detected (QRS {_fmt(f.qrs_duration_global_ms)} ms).",
        f"QRS {_fmt(f.qrs_duration_global_ms)} ms. {v1_desc}, "
        f"V5={v5_pat}, V6={v6_pat}. ST-T discordance expected.",
        {"qrs_duration_global_ms": f.qrs_duration_global_ms, "lbbb": True,
         "v1_pattern": v1_pat, "v5_pattern": v5_pat},
    )


def _detect_rbbb(f: FeatureObject) -> Optional[DiagnosticFinding]:
    qrs = f.qrs_duration_global_ms or 0
    v1_pat = f.qrs_pattern.get("V1", "unknown")
    # Primary: feature-level flag; Fallback: RSR' pattern in V1 with wide QRS
    morph_rbbb = v1_pat == "RSR'" and qrs >= 110
    if not f.rbbb and not morph_rbbb:
        return None
    v1_desc = f"V1={v1_pat}" if v1_pat != "unknown" else "RSR' in V1"
    return _make(
        "rbbb", "HIGH",
        f"Right bundle branch block detected (QRS {_fmt(f.qrs_duration_global_ms)} ms).",
        f"QRS {_fmt(f.qrs_duration_global_ms)} ms. {v1_desc}, wide S in I and V6.",
        {"qrs_duration_global_ms": f.qrs_duration_global_ms, "rbbb": True,
         "v1_pattern": v1_pat},
    )


def _detect_wpw(f: FeatureObject) -> Optional[DiagnosticFinding]:
    if not f.wpw_pattern:
        return None
    return _make(
        "wpw_pattern", "HIGH",
        f"WPW pre-excitation pattern (PR {_fmt(f.pr_interval_ms)} ms).",
        f"Short PR {_fmt(f.pr_interval_ms)} ms, QRS {_fmt(f.qrs_duration_global_ms)} ms. "
        f"Delta wave present — ventricular pre-excitation.",
        {"pr_interval_ms": f.pr_interval_ms, "qrs_duration_global_ms": f.qrs_duration_global_ms, "wpw_pattern": True},
    )


def _detect_afib(f: FeatureObject) -> Optional[DiagnosticFinding]:
    if f.dominant_rhythm != "afib":
        return None
    hr = f.heart_rate_ventricular_bpm
    rate_class = "RVR" if hr and hr > 100 else "controlled" if hr and hr >= 60 else "slow"
    return _make(
        "afib", "HIGH",
        f"Atrial fibrillation detected ({rate_class}, {_fmt(hr)} bpm).",
        f"Irregularly irregular RR intervals. P waves absent. "
        f"Ventricular rate {_fmt(hr)} bpm ({rate_class}). "
        f"QRS {_fmt(f.qrs_duration_global_ms)} ms.",
        {"dominant_rhythm": "afib", "heart_rate_ventricular_bpm": hr, "rhythm_regular": False},
    )


def _detect_first_degree_avb(f: FeatureObject) -> Optional[DiagnosticFinding]:
    pr = f.pr_interval_ms
    if pr is None or pr <= 200:
        return None
    return _make(
        "first_degree_avb", "HIGH",
        f"First-degree AV block (PR {_fmt(pr)} ms).",
        f"PR interval {_fmt(pr)} ms (> 200 ms). All P waves conducted (1:1).",
        {"pr_interval_ms": pr},
    )


def _detect_lafb(f: FeatureObject) -> Optional[DiagnosticFinding]:
    if not f.lafb:
        return None
    return _make(
        "lafb", "MODERATE",
        f"Left anterior fascicular block (axis {_fmt(f.qrs_axis_deg)}\u00b0).",
        f"QRS axis {_fmt(f.qrs_axis_deg)}\u00b0 (< -45\u00b0). LAFB criteria met.",
        {"qrs_axis_deg": f.qrs_axis_deg, "lafb": True},
    )


def _detect_anterior_stemi(f: FeatureObject) -> Optional[DiagnosticFinding]:
    # LBBB/RBBB produce expected ST changes — skip standard STEMI detection
    if f.lbbb or f.rbbb:
        return None
    precordial = ["V1", "V2", "V3", "V4"]
    elev_leads = [l for l in precordial if (f.st_elevation_mv.get(l) or 0) > 0.1]
    if len(elev_leads) < 2:
        return None
    max_st = max(f.st_elevation_mv.get(l) or 0 for l in elev_leads)
    _, dep_leads = _st_leads(f)
    inf_dep = [l for l in dep_leads if l in ("II", "III", "aVF")]
    # ST curvature: convex = true STEMI (higher confidence), concave = may be benign
    convex_leads = [l for l in elev_leads if f.st_curvature.get(l) == "convex"]
    concave_leads = [l for l in elev_leads if f.st_curvature.get(l) == "concave"]
    if len(elev_leads) >= 3 and max_st > 0.2:
        conf = "HIGH"
    elif convex_leads:
        conf = "HIGH"
    elif concave_leads and not convex_leads:
        conf = "LOW"  # concave ST = likely benign (early repol / pericarditis)
    else:
        conf = "MODERATE"
    curvature_str = ", ".join(f"{l}={f.st_curvature.get(l, '?')}" for l in elev_leads)
    return _make(
        "anterior_stemi", conf,
        f"Anterior ST elevation in {', '.join(elev_leads)}.",
        f"ST elevation in {', '.join(elev_leads)} (max {max_st:.2f} mV). "
        f"ST curvature: {curvature_str}. "
        f"Anterior territory (LAD). Reciprocal depression: {', '.join(inf_dep) or 'none'}.",
        {"st_elevation_mv": {l: f.st_elevation_mv.get(l) for l in elev_leads},
         "st_curvature": {l: f.st_curvature.get(l) for l in elev_leads}},
    )


def _detect_inferior_stemi(f: FeatureObject) -> Optional[DiagnosticFinding]:
    if f.lbbb or f.rbbb:
        return None
    inferior = ["II", "III", "aVF"]
    elev_leads = [l for l in inferior if (f.st_elevation_mv.get(l) or 0) > 0.1]
    lat_dep = [l for l in ("I", "aVL") if (f.st_depression_mv.get(l) or 0) > 0.05]

    # Amplitude-based path
    if len(elev_leads) >= 2:
        max_st = max(f.st_elevation_mv.get(l) or 0 for l in elev_leads)
        convex_leads = [l for l in elev_leads if f.st_curvature.get(l) == "convex"]
        if len(elev_leads) >= 2 and max_st > 0.15:
            conf = "HIGH"
        elif convex_leads:
            conf = "HIGH"
        else:
            conf = "MODERATE"
        curvature_str = ", ".join(f"{l}={f.st_curvature.get(l, '?')}" for l in elev_leads)
        return _make(
            "inferior_stemi", conf,
            f"Inferior ST elevation in {', '.join(elev_leads)}.",
            f"ST elevation in {', '.join(elev_leads)} (max {max_st:.2f} mV). "
            f"ST curvature: {curvature_str}. "
            f"Inferior territory (RCA/LCx). Reciprocal: {', '.join(lat_dep) or 'none'}.",
            {"st_elevation_mv": {l: f.st_elevation_mv.get(l) for l in elev_leads},
             "st_curvature": {l: f.st_curvature.get(l) for l in elev_leads}},
        )

    # Shape-based path: convex ST curvature + QS pattern in inferior leads
    # Detects acute/recent STEMI when absolute ST amplitude is small (wander, early, RCA occlusion).
    # Specificity guards:
    #   - QS in III alone is a normal variant (vertical heart, respiratory) — require aVF OR II+III
    #   - Convex curvature in III alone can occur normally — require II or aVF involvement
    convex_inf = [l for l in inferior if f.st_curvature.get(l) == "convex"]
    qs_inf = [l for l in inferior if f.qrs_pattern.get(l) == "QS"]
    # Must have aVF involvement in QS OR QS in both II and III
    avf_qs = "aVF" in qs_inf
    multi_qs = len(qs_inf) >= 2
    # Must have convex curvature in II or aVF (not just III)
    convex_key = any(l in convex_inf for l in ("II", "aVF"))
    if (avf_qs or multi_qs) and convex_key and len(convex_inf) >= 1 and len(qs_inf) >= 1:
        all_shape_leads = sorted(set(convex_inf + qs_inf))
        max_st_any = max((f.st_elevation_mv.get(l) or 0) for l in inferior)
        # Require reciprocal depression in I/aVL for HIGH confidence
        conf = "HIGH" if lat_dep else "MODERATE"
        return _make(
            "inferior_stemi", conf,
            f"Inferior STEMI pattern — shape evidence in {', '.join(all_shape_leads)}.",
            f"Convex ST curvature in {', '.join(convex_inf)} + QS pattern in {', '.join(qs_inf)}. "
            f"ST amplitude {max_st_any:.2f} mV (may be underestimated due to wander). "
            f"Reciprocal: {', '.join(lat_dep) or 'none'}. "
            f"Shape evidence indicates inferior STEMI (RCA territory) — correlate clinically.",
            {"st_curvature_convex": convex_inf, "qs_pattern": qs_inf,
             "st_elevation_mv": {l: f.st_elevation_mv.get(l) for l in inferior}},
        )

    return None


def _detect_lateral_stemi(f: FeatureObject) -> Optional[DiagnosticFinding]:
    if f.lbbb or f.rbbb:
        return None
    lateral = ["I", "aVL", "V5", "V6"]
    # Primary: ≥2 leads at 0.1 mV; fallback: ≥1 lead at 0.05 mV (fiducials often miss aVL/I)
    elev_leads = [l for l in lateral if (f.st_elevation_mv.get(l) or 0) > 0.1]
    if len(elev_leads) < 2:
        elev_leads = [l for l in lateral if (f.st_elevation_mv.get(l) or 0) > 0.05]
    if len(elev_leads) < 1:
        return None
    max_st = max(f.st_elevation_mv.get(l) or 0 for l in elev_leads)
    return _make(
        "lateral_stemi", "MODERATE",
        f"Lateral ST elevation in {', '.join(elev_leads)}.",
        f"ST elevation in {', '.join(elev_leads)} (max {max_st:.2f} mV). "
        f"Lateral territory (LCx).",
        {"st_elevation_mv": {l: f.st_elevation_mv.get(l) for l in elev_leads}},
    )


def _detect_wellens(f: FeatureObject) -> Optional[DiagnosticFinding]:
    # Type B (more common): deep symmetric T inversion in V2-V3
    # Type A: biphasic T (initial up, terminal down) in V2-V3
    type_b_leads = []
    type_a_leads = []
    for l in ("V2", "V3", "V4"):
        t_morph = f.t_morphology.get(l, "")
        sym_idx = f.t_symmetry_index.get(l)
        det_morph = f.t_detailed_morphology.get(l, "")
        # Type B: deep symmetric inversion (symmetry > 0.6 OR legacy symmetric flag)
        if t_morph == "inverted":
            is_symmetric = (sym_idx is not None and sym_idx > 0.6) or f.symmetric_t_inversion.get(l, False)
            if is_symmetric:
                type_b_leads.append(l)
        # Type A: biphasic T-wave (positive-then-negative)
        if det_morph in ("biphasic_pos_neg", "biphasic"):
            type_a_leads.append(l)

    wellens_type = None
    leads_involved = []
    if len(type_b_leads) >= 2:
        wellens_type = "B"
        leads_involved = type_b_leads
    elif len(type_a_leads) >= 1:
        wellens_type = "A"
        leads_involved = type_a_leads

    if wellens_type is None:
        return None
    # Must NOT have significant ST elevation
    if any((f.st_elevation_mv.get(l) or 0) > 0.1 for l in leads_involved):
        return None
    sym_vals = {l: f.t_symmetry_index.get(l) for l in leads_involved}
    return _make(
        "wellens", "MODERATE",
        f"Wellens Type {wellens_type} — {'deep symmetric T inversion' if wellens_type == 'B' else 'biphasic T'} in {', '.join(leads_involved)}.",
        f"Wellens Type {wellens_type} in {', '.join(leads_involved)}. "
        f"{'Symmetry indices: ' + ', '.join(f'{l}={v:.2f}' for l, v in sym_vals.items() if v is not None) + '. ' if any(v is not None for v in sym_vals.values()) else ''}"
        f"Critical LAD stenosis pattern.",
        {"wellens_type": wellens_type, "leads": leads_involved, "t_symmetry": sym_vals},
    )


def _detect_de_winter(f: FeatureObject) -> Optional[DiagnosticFinding]:
    if not f.de_winter_pattern:
        return None
    return _make(
        "de_winter", "MODERATE",
        "de Winter T-wave pattern — STEMI equivalent.",
        "Upsloping ST depression with tall symmetric T waves in precordial leads. "
        "ST elevation in aVR. Proximal LAD occlusion pattern.",
        {"de_winter_pattern": True},
    )


def _detect_brugada(f: FeatureObject) -> Optional[DiagnosticFinding]:
    # Feature-level flag OR coved ST curvature in V1/V2 with ST elevation
    coved_leads = [l for l in ("V1", "V2")
                   if f.st_curvature.get(l) == "coved"
                   and (f.st_elevation_mv.get(l) or 0) >= 0.2]
    if not f.brugada_type1_pattern and not coved_leads:
        return None
    curvature_detail = ", ".join(f"{l}={f.st_curvature.get(l, '?')}" for l in ("V1", "V2"))
    return _make(
        "brugada_type1", "MODERATE",
        "Brugada Type 1 pattern in V1-V2.",
        f"Coved ST elevation with T-wave inversion in V1-V2. "
        f"ST curvature: {curvature_detail}. "
        f"Risk of sudden cardiac death — EP consultation needed.",
        {"brugada_type1_pattern": True, "st_curvature_v1": f.st_curvature.get("V1"),
         "st_curvature_v2": f.st_curvature.get("V2")},
    )


def _detect_pericarditis(f: FeatureObject) -> Optional[DiagnosticFinding]:
    # Feature-level flag OR morphology: concave ST in >=4 leads + PR depression
    concave_leads = [l for l in f.st_curvature
                     if f.st_curvature[l] == "concave"
                     and (f.st_elevation_mv.get(l) or 0) > 0.05]
    pr_dep_leads = [l for l in f.pr_depression_mv
                    if (f.pr_depression_mv[l] or 0) > 0.05]
    morph_pericarditis = len(concave_leads) >= 4
    if not f.pericarditis_pattern and not morph_pericarditis:
        return None
    elev, _ = _st_leads(f, 0.05)
    detail = f"Diffuse concave ST elevation in {', '.join(elev[:6]) or ', '.join(concave_leads[:6])}."
    if pr_dep_leads:
        detail += f" PR depression in {', '.join(pr_dep_leads[:4])}."
    detail += " Pattern consistent with pericarditis."
    conf = "HIGH" if morph_pericarditis and pr_dep_leads else "MODERATE"
    return _make(
        "pericarditis", conf,
        "Diffuse ST elevation — pericarditis pattern.",
        detail,
        {"pericarditis_pattern": True, "concave_st_leads": concave_leads[:6],
         "pr_depression_leads": pr_dep_leads[:4]},
    )


def _detect_lvh(f: FeatureObject) -> Optional[DiagnosticFinding]:
    if not f.lvh_criteria_met:
        return None
    criteria_str = ", ".join(f.lvh_criteria_met)
    re = f.lvh_romhilt_estes_score
    conf = "HIGH" if re is not None and re >= 5 else "MODERATE"
    return _make(
        "lvh", conf,
        f"LVH — {criteria_str}.",
        f"LVH criteria met: {criteria_str}. "
        f"Sokolow-Lyon: {_fmt(f.lvh_sokolow_lyon_mv, 2)} mV. "
        f"Romhilt-Estes: {_fmt(f.lvh_romhilt_estes_score)}/5.",
        {"lvh_criteria_met": f.lvh_criteria_met, "lvh_sokolow_lyon_mv": f.lvh_sokolow_lyon_mv},
    )


def _detect_long_qt(f: FeatureObject) -> Optional[DiagnosticFinding]:
    qtc = f.qtc_bazett_ms
    if qtc is None:
        return None
    # QTc unreliable with very wide QRS (> 140ms) — severe BBB inflates QT too much
    qrs = f.qrs_duration_global_ms or 0
    if qrs > 140:
        return None
    # Threshold: 470ms (between borderline 460 and definite 480)
    if qtc <= 470:
        return None
    risk = "high TdP risk" if qtc > 500 else "prolonged"
    conf = "HIGH" if qtc > 500 else "MODERATE"
    return _make(
        "long_qt", conf,
        f"Long QT — QTc {_fmt(qtc)} ms ({risk}).",
        f"QTc {_fmt(qtc)} ms (Bazett). "
        f"Fridericia: {_fmt(f.qtc_fridericia_ms)} ms. {risk.capitalize()}.",
        {"qtc_bazett_ms": qtc},
    )


def _detect_low_voltage(f: FeatureObject) -> Optional[DiagnosticFinding]:
    if not f.low_voltage_limb and not f.low_voltage_precordial:
        return None
    where = []
    if f.low_voltage_limb:
        where.append("limb")
    if f.low_voltage_precordial:
        where.append("precordial")
    return _make(
        "low_voltage", "LOW",
        f"Low voltage in {' and '.join(where)} leads.",
        f"Low voltage: {', '.join(where)}. Consider pericardial effusion, "
        f"obesity, COPD, or infiltrative disease.",
        {"low_voltage_limb": f.low_voltage_limb, "low_voltage_precordial": f.low_voltage_precordial},
    )


def _detect_sinus_bradycardia(f: FeatureObject) -> Optional[DiagnosticFinding]:
    hr = f.heart_rate_ventricular_bpm
    if hr is None or hr >= 60:
        return None
    if f.dominant_rhythm not in ("sinus", "brady_unknown"):
        return None
    conf = "HIGH" if hr < 50 else "MODERATE"
    return _make(
        "sinus_bradycardia", conf,
        f"Sinus bradycardia ({_fmt(hr)} bpm).",
        f"Heart rate {_fmt(hr)} bpm. P waves present, regular rhythm. "
        f"PR interval {_fmt(f.pr_interval_ms)} ms.",
        {"heart_rate_ventricular_bpm": hr, "dominant_rhythm": f.dominant_rhythm},
    )


def _detect_sinus_tachycardia(f: FeatureObject) -> Optional[DiagnosticFinding]:
    hr = f.heart_rate_ventricular_bpm
    if hr is None or hr <= 100:
        return None
    if f.dominant_rhythm not in ("sinus", "tachy_unknown"):
        return None
    conf = "HIGH" if hr > 120 else "MODERATE"
    return _make(
        "sinus_tachycardia", conf,
        f"Sinus tachycardia ({_fmt(hr)} bpm).",
        f"Heart rate {_fmt(hr)} bpm. P waves present before each QRS.",
        {"heart_rate_ventricular_bpm": hr, "dominant_rhythm": f.dominant_rhythm},
    )


def _detect_rvh(f: FeatureObject) -> Optional[DiagnosticFinding]:
    if not f.rvh_criteria_met:
        return None
    criteria_str = ", ".join(f.rvh_criteria_met)
    conf = "HIGH" if len(f.rvh_criteria_met) >= 2 else "MODERATE"
    return _make(
        "rvh", conf,
        f"Right ventricular hypertrophy — {criteria_str}.",
        f"RVH criteria: {criteria_str}. QRS axis {_fmt(f.qrs_axis_deg)}°.",
        {"rvh_criteria_met": f.rvh_criteria_met, "qrs_axis_deg": f.qrs_axis_deg},
    )


def _detect_lae(f: FeatureObject) -> Optional[DiagnosticFinding]:
    ptf = f.p_terminal_force_v1_mv_s
    p_dur = f.p_duration_ms
    lae = False
    details = []
    if ptf is not None and ptf > 0.04:
        lae = True
        details.append(f"P terminal force V1 = {ptf:.3f} mV·s (> 0.04)")
    if p_dur is not None and p_dur > 120:
        lae = True
        details.append(f"P duration = {_fmt(p_dur)} ms (> 120)")
    if not lae:
        return None
    return _make(
        "lae", "MODERATE",
        "Left atrial enlargement suggested.",
        ". ".join(details) + ".",
        {"p_terminal_force_v1_mv_s": ptf, "p_duration_ms": p_dur},
    )


def _detect_rae(f: FeatureObject) -> Optional[DiagnosticFinding]:
    p_amp = f.p_amplitude_mv
    if p_amp is None or p_amp <= 0.25:
        return None
    return _make(
        "rae", "MODERATE",
        f"Right atrial enlargement — peaked P wave ({p_amp:.2f} mV).",
        f"P-wave amplitude {p_amp:.2f} mV in lead II (> 0.25 mV). P-pulmonale pattern.",
        {"p_amplitude_mv": p_amp},
    )


def _detect_second_degree_avb(f: FeatureObject) -> Optional[DiagnosticFinding]:
    """2nd degree AVB: Wenckebach (progressive PR) or dropped beats."""
    # Primary: morphology-based Wenckebach detection
    if f.av_relationship == "wenckebach":
        return _make(
            "second_degree_avb", "MODERATE",
            "Second-degree AV block (Mobitz Type I / Wenckebach).",
            f"Progressive PR prolongation with dropped QRS detected. "
            f"AV relationship: Wenckebach pattern.",
            {"av_relationship": "wenckebach"},
        )
    # Fallback: dropped beat heuristic
    bs = f.beat_summary
    if bs.dropped_beat_context is None:
        return None
    if not f.p_wave_present:
        return None
    if f.av_ratio is not None and f.av_ratio > 0.95:
        return None
    return _make(
        "second_degree_avb", "LOW",
        "Possible second-degree AV block — dropped beat detected.",
        f"Dropped beat detected: {bs.dropped_beat_context}. "
        f"P waves present. AV ratio {_fmt(f.av_ratio, 2) if f.av_ratio else 'N/A'}.",
        {"dropped_beat_context": bs.dropped_beat_context, "av_ratio": f.av_ratio},
    )


def _detect_complete_avb(f: FeatureObject) -> Optional[DiagnosticFinding]:
    """Complete AVB: P waves present but AV dissociation (atrial rate >> ventricular rate).
    Uses av_relationship from morphology engine as primary signal."""
    # Primary: morphology-based AV relationship
    if f.av_relationship == "dissociated":
        hr_a = f.heart_rate_atrial_bpm
        hr_v = f.heart_rate_ventricular_bpm
        return _make(
            "complete_avb", "HIGH",
            f"Complete AV block — ventricular rate {_fmt(hr_v)} bpm.",
            f"AV dissociation detected. Atrial rate {_fmt(hr_a)} bpm, "
            f"ventricular rate {_fmt(hr_v)} bpm. P-waves march independently of QRS. "
            f"Complete heart block. STAT — pacing may be needed.",
            {"heart_rate_atrial_bpm": hr_a, "heart_rate_ventricular_bpm": hr_v,
             "av_relationship": "dissociated"},
        )
    # Fallback: rate-based heuristic
    if not f.p_wave_present:
        return None
    hr_a = f.heart_rate_atrial_bpm
    hr_v = f.heart_rate_ventricular_bpm
    if hr_a is None or hr_v is None:
        return None
    if hr_v >= hr_a * 0.7:
        return None
    if hr_v > 50:
        return None
    return _make(
        "complete_avb", "HIGH",
        f"Complete AV block — ventricular rate {_fmt(hr_v)} bpm.",
        f"AV dissociation: atrial rate {_fmt(hr_a)} bpm, ventricular rate {_fmt(hr_v)} bpm. "
        f"Complete heart block. STAT — pacing may be needed.",
        {"heart_rate_atrial_bpm": hr_a, "heart_rate_ventricular_bpm": hr_v},
    )


def _detect_posterior_stemi(f: FeatureObject) -> Optional[DiagnosticFinding]:
    if f.lbbb or f.rbbb:
        return None
    rv1 = f.r_amplitude_mv.get("V1") or 0
    sv1 = f.s_amplitude_mv.get("V1") or 0
    rv2 = f.r_amplitude_mv.get("V2") or 0
    sv2 = f.s_amplitude_mv.get("V2") or 0
    tall_r_v1 = rv1 > sv1 and rv1 > 0.1
    tall_r_v2 = rv2 > sv2 and rv2 > 0.1
    dep_v1 = (f.st_depression_mv.get("V1") or 0) > 0.05
    dep_v2 = (f.st_depression_mv.get("V2") or 0) > 0.05
    dep_v3 = (f.st_depression_mv.get("V3") or 0) > 0.05
    n_dep = sum([dep_v1, dep_v2, dep_v3])
    if not (tall_r_v1 or tall_r_v2) or n_dep < 2:
        return None
    return _make(
        "posterior_stemi", "MODERATE",
        "Possible posterior STEMI — tall R in V1-V2 with ST depression.",
        f"Tall R in V1 ({rv1:.2f} mV) and/or V2 ({rv2:.2f} mV). "
        f"ST depression in {n_dep} anterior leads. "
        f"Consider posterior leads (V7-V9).",
        {"r_amplitude_v1": rv1, "r_amplitude_v2": rv2},
    )


def _detect_sgarbossa_stemi(f: FeatureObject) -> Optional[DiagnosticFinding]:
    """Modified Sgarbossa criteria for STEMI in setting of LBBB.
    Uses concordance_analysis from morphology engine for primary detection."""
    # Must have confirmed LBBB: feature flag + wide QRS (≥120ms)
    # QRS pattern fallback alone is too permissive (LVH/other conditions can give QS in V1).
    # WPW is already screened out at the generate_signal_findings level (f.lbbb suppressed).
    qrs = f.qrs_duration_global_ms or 0
    if not f.lbbb or qrs < 120:
        return None
    score = 0
    details = []
    all_leads = ["V1", "V2", "V3", "V4", "V5", "V6", "I", "II", "III", "aVL", "aVF"]

    # Criterion 1: Concordant ST elevation >= 1mm in any lead (5 pts)
    for lead in all_leads:
        elev = f.st_elevation_mv.get(lead) or 0
        conc = f.concordance_analysis.get(lead, "unknown")
        if elev >= 0.1 and conc == "concordant":
            score += 5
            details.append(f"Concordant ST elevation {lead} ({elev:.2f} mV)")
            break

    # Criterion 2: Concordant ST depression >= 1mm in V1-V3 (3 pts)
    for lead in ["V1", "V2", "V3"]:
        dep = f.st_depression_mv.get(lead) or 0
        conc = f.concordance_analysis.get(lead, "unknown")
        if dep >= 0.1 and conc == "concordant":
            score += 3
            details.append(f"Concordant ST depression {lead} ({dep:.2f} mV)")
            break

    # Criterion 3 (Smith-modified): Excessive discordant ST elevation — ST/S ratio > 0.25
    # In LBBB, discordant ST elevation is expected (ST opposite QRS). Criterion 3 detects
    # when the discordant elevation is disproportionately large relative to the S-wave depth.
    # For QS-pattern leads: use q_amplitude as the reference (no R, so S = depth of QRS trough)
    if score < 3:
        for lead in all_leads:
            elev = f.st_elevation_mv.get(lead) or 0
            if elev < 0.05:
                continue
            pat = f.qrs_pattern.get(lead, "")
            r = f.r_amplitude_mv.get(lead) or 0
            s = f.s_amplitude_mv.get(lead) or 0
            q = f.q_amplitude_mv.get(lead) or 0
            # Net discordant deflection: for QS leads use q; for rS/RS use s
            net_deflection = q if pat in ("QS", "rS") else s
            if net_deflection < 0.01:
                continue
            ratio = elev / net_deflection
            if ratio >= 0.25:
                score += 3
                details.append(f"Excessive discordant ST elevation {lead} (ST={elev:.2f}mV, ratio={ratio:.2f})")
                break

    if score < 3:
        return None
    conf = "HIGH" if score >= 5 else "MODERATE"
    return _make(
        "sgarbossa_stemi", conf,
        f"STEMI in LBBB (Sgarbossa score {score}).",
        f"Modified Sgarbossa criteria met (score {score}/8). " + ". ".join(details) + ".",
        {"sgarbossa_score": score, "lbbb": True, "concordance_used": True},
    )


def _detect_inferior_mi_established(f: FeatureObject) -> Optional[DiagnosticFinding]:
    """
    Detect established (subacute/old) inferior MI from Q-wave and R-wave amplitude pattern.

    Triggers on QS morphology or R < Q in ≥2 contiguous inferior leads, WITHOUT
    requiring ST elevation. Left axis deviation provides supporting evidence (loss
    of inferior depolarization forces pulls the axis leftward).

    Catches cases _detect_inferior_stemi misses when ST has already normalized.
    Does NOT fire if active ST elevation is present in inferior leads (let _detect_inferior_stemi
    handle that case). Does NOT fire with LBBB/RBBB (secondary QS patterns expected).
    """
    if f.lbbb or f.rbbb:
        return None

    # Skip if active ST elevation OR shape-based STEMI evidence present — acute detector takes priority
    inferior = ["II", "III", "aVF"]
    if any((f.st_elevation_mv.get(l) or 0) > 0.1 for l in inferior):
        return None
    # Skip if shape-based inferior STEMI fired (uses same criteria as _detect_inferior_stemi)
    convex_inf = [l for l in inferior if f.st_curvature.get(l) == "convex"]
    qs_inf = [l for l in inferior if f.qrs_pattern.get(l) == "QS"]
    avf_qs = "aVF" in qs_inf
    multi_qs = len(qs_inf) >= 2
    convex_key = any(l in convex_inf for l in ("II", "aVF"))
    if (avf_qs or multi_qs) and convex_key and len(convex_inf) >= 1 and len(qs_inf) >= 1:
        return None

    qs_leads = []
    path_q_leads = []
    for lead in inferior:
        pat = f.qrs_pattern.get(lead, "") if f.qrs_pattern else ""
        r = f.r_amplitude_mv.get(lead) or 0
        q = f.q_amplitude_mv.get(lead) or 0
        path_q = f.pathological_q_wave.get(lead, False) if f.pathological_q_wave else False

        # QS pattern: explicit tag OR R so small it's essentially absent relative to Q
        is_qs = pat == "QS" or (r < 0.15 and q > r)
        if is_qs:
            qs_leads.append(lead)
        if path_q:
            path_q_leads.append(lead)

    # Primary: ≥2 inferior leads with QS/near-QS pattern
    # Fallback: ≥2 inferior leads with pathological Q waves — but ONLY with supporting
    # evidence (axis < -30° or small absolute R) to avoid false positives in normal ECGs
    # where Q/R ratio is borderline but R amplitude is still tall.
    axis = f.qrs_axis_deg
    lad = axis is not None and axis < -30

    if len(qs_leads) >= 2:
        matching_leads = qs_leads
        pattern_desc = "QS/near-QS pattern"
    elif len(path_q_leads) >= 2:
        # Require corroborating evidence for the fallback path
        small_r = all((f.r_amplitude_mv.get(l) or 1.0) < 0.3 for l in path_q_leads)
        if not lad and not small_r:
            return None
        matching_leads = path_q_leads
        pattern_desc = "pathological Q waves"
    else:
        return None

    r_vals = {l: f.r_amplitude_mv.get(l) for l in matching_leads if f.r_amplitude_mv.get(l) is not None}
    q_vals = {l: f.q_amplitude_mv.get(l) for l in matching_leads if f.q_amplitude_mv.get(l) is not None}

    if len(matching_leads) >= 3 and lad:
        conf = "HIGH"
    elif len(matching_leads) >= 2 and (lad or len(path_q_leads) >= 2):
        conf = "MODERATE"
    else:
        conf = "LOW"

    r_str = " | ".join(f"{l}:R={v:.2f}mV" for l, v in r_vals.items())
    q_str = " | ".join(f"{l}:Q={v:.2f}mV" for l, v in q_vals.items()) if q_vals else ""
    axis_str = f" Axis {axis:.0f}° (left axis deviation — supports loss of inferior forces)." if lad else (f" Axis {axis:.0f}°." if axis is not None else "")

    return _make(
        "inferior_mi_established",
        conf,
        f"Established inferior MI pattern — {pattern_desc} in {', '.join(matching_leads)}.",
        f"{pattern_desc.capitalize()} in {', '.join(matching_leads)}. "
        f"{r_str}. {q_str}.{axis_str} "
        f"Consistent with completed/subacute inferior MI — ST elevation may have normalized. "
        f"Correlate with symptoms and serial ECG for acuity.",
        {
            "qs_leads": qs_leads,
            "pathological_q_leads": path_q_leads,
            "r_amplitude_mv": {l: f.r_amplitude_mv.get(l) for l in matching_leads},
            "qrs_axis_deg": axis,
        },
    )


def _detect_pathological_q_waves(f: FeatureObject) -> Optional[DiagnosticFinding]:
    """Detect pathological Q waves across leads."""
    path_leads = []
    for lead in ["I", "II", "III", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"]:
        if hasattr(f, 'pathological_q_wave') and f.pathological_q_wave.get(lead, False):
            path_leads.append(lead)
        else:
            qd = f.q_duration_ms.get(lead)
            qa = f.q_amplitude_mv.get(lead)
            ra = f.r_amplitude_mv.get(lead)
            dur_path = qd is not None and qd > 40
            depth_path = qa is not None and ra is not None and ra > 0 and qa / ra > 0.25
            if dur_path or depth_path:
                path_leads.append(lead)
    if len(path_leads) < 2:
        return None
    return _make(
        "pathological_q_waves", "MODERATE",
        f"Pathological Q waves in {', '.join(path_leads[:4])}.",
        f"Pathological Q waves detected in {', '.join(path_leads)}. "
        f"May indicate prior myocardial infarction.",
        {"pathological_q_leads": path_leads},
    )


# Ordered list of detectors — run top to bottom
_DETECTORS = [
    # STAT conditions first
    _detect_anterior_stemi,
    _detect_inferior_stemi,
    _detect_inferior_mi_established,
    _detect_lateral_stemi,
    _detect_wellens,
    _detect_de_winter,
    _detect_brugada,
    _detect_complete_avb,
    _detect_sgarbossa_stemi,
    _detect_posterior_stemi,
    # Conduction
    _detect_lbbb,
    _detect_rbbb,
    _detect_wpw,
    _detect_afib,
    _detect_first_degree_avb,
    _detect_second_degree_avb,
    _detect_lafb,
    # Rate
    _detect_sinus_bradycardia,
    _detect_sinus_tachycardia,
    # Structural / morphology
    _detect_lvh,
    _detect_rvh,
    _detect_lae,
    _detect_rae,
    _detect_long_qt,
    _detect_pericarditis,
    _detect_low_voltage,
    _detect_pathological_q_waves,
]
