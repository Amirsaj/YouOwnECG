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
    if not f.lbbb:
        return None
    qrs = f.qrs_duration_global_ms or 0
    return _make(
        "lbbb", "HIGH",
        f"Left bundle branch block detected (QRS {_fmt(f.qrs_duration_global_ms)} ms).",
        f"QRS {_fmt(f.qrs_duration_global_ms)} ms. QS/rS pattern in V1, "
        f"broad notched R in V5/V6. ST-T discordance expected.",
        {"qrs_duration_global_ms": f.qrs_duration_global_ms, "lbbb": True},
    )


def _detect_rbbb(f: FeatureObject) -> Optional[DiagnosticFinding]:
    if not f.rbbb:
        return None
    return _make(
        "rbbb", "HIGH",
        f"Right bundle branch block detected (QRS {_fmt(f.qrs_duration_global_ms)} ms).",
        f"QRS {_fmt(f.qrs_duration_global_ms)} ms. RSR' in V1/V2, wide S in I and V6.",
        {"qrs_duration_global_ms": f.qrs_duration_global_ms, "rbbb": True},
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
    conf = "HIGH" if len(elev_leads) >= 3 and max_st > 0.2 else "MODERATE"
    return _make(
        "anterior_stemi", conf,
        f"Anterior ST elevation in {', '.join(elev_leads)}.",
        f"ST elevation in {', '.join(elev_leads)} (max {max_st:.2f} mV). "
        f"Anterior territory (LAD). Reciprocal depression: {', '.join(inf_dep) or 'none'}.",
        {"st_elevation_mv": {l: f.st_elevation_mv.get(l) for l in elev_leads}},
    )


def _detect_inferior_stemi(f: FeatureObject) -> Optional[DiagnosticFinding]:
    if f.lbbb or f.rbbb:
        return None
    inferior = ["II", "III", "aVF"]
    elev_leads = [l for l in inferior if (f.st_elevation_mv.get(l) or 0) > 0.1]
    if len(elev_leads) < 2:
        return None
    max_st = max(f.st_elevation_mv.get(l) or 0 for l in elev_leads)
    lat_dep = [l for l in ("I", "aVL") if (f.st_depression_mv.get(l) or 0) > 0.05]
    conf = "HIGH" if len(elev_leads) >= 2 and max_st > 0.15 else "MODERATE"
    return _make(
        "inferior_stemi", conf,
        f"Inferior ST elevation in {', '.join(elev_leads)}.",
        f"ST elevation in {', '.join(elev_leads)} (max {max_st:.2f} mV). "
        f"Inferior territory (RCA/LCx). Reciprocal: {', '.join(lat_dep) or 'none'}.",
        {"st_elevation_mv": {l: f.st_elevation_mv.get(l) for l in elev_leads}},
    )


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
    # Deep symmetric T inversion in V2-V3 without significant ST elevation
    inv_leads = [l for l in ("V2", "V3", "V4")
                 if f.t_morphology.get(l) == "inverted" and f.symmetric_t_inversion.get(l, False)]
    if len(inv_leads) < 2:
        return None
    # Must NOT have significant ST elevation
    if any((f.st_elevation_mv.get(l) or 0) > 0.1 for l in inv_leads):
        return None
    return _make(
        "wellens", "MODERATE",
        f"Wellens pattern — deep T inversion in {', '.join(inv_leads)}.",
        f"Deep symmetric T-wave inversion in {', '.join(inv_leads)} without ST elevation. "
        f"Pattern suggests critical LAD stenosis.",
        {"t_morphology": {l: "inverted" for l in inv_leads}, "symmetric_t_inversion": {l: True for l in inv_leads}},
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
    if not f.brugada_type1_pattern:
        return None
    return _make(
        "brugada_type1", "MODERATE",
        "Brugada Type 1 pattern in V1-V2.",
        "Coved ST elevation with T-wave inversion in V1-V2. "
        "Risk of sudden cardiac death — EP consultation needed.",
        {"brugada_type1_pattern": True},
    )


def _detect_pericarditis(f: FeatureObject) -> Optional[DiagnosticFinding]:
    if not f.pericarditis_pattern:
        return None
    elev, _ = _st_leads(f, 0.05)
    return _make(
        "pericarditis", "MODERATE",
        f"Diffuse ST elevation — pericarditis pattern.",
        f"Diffuse concave ST elevation in {', '.join(elev[:6])}. "
        f"Pattern consistent with pericarditis.",
        {"pericarditis_pattern": True},
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
    """Approximate 2nd degree AVB: dropped beats (long pause) with P waves present."""
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
    """Complete AVB: P waves present but AV dissociation (atrial rate >> ventricular rate)."""
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
    """Modified Sgarbossa criteria for STEMI in setting of LBBB."""
    if not f.lbbb:
        return None
    score = 0
    details = []
    for lead in ["V1", "V2", "V3", "V4", "V5", "V6", "I", "II", "III", "aVL", "aVF"]:
        elev = f.st_elevation_mv.get(lead) or 0
        if elev >= 0.1:
            r = f.r_amplitude_mv.get(lead) or 0
            s = f.s_amplitude_mv.get(lead) or 0
            qrs_positive = r > s
            if qrs_positive and elev >= 0.1:
                score += 5
                details.append(f"Concordant ST elevation in {lead} ({elev:.2f} mV)")
                break
    for lead in ["V1", "V2", "V3"]:
        dep = f.st_depression_mv.get(lead) or 0
        if dep >= 0.1:
            r = f.r_amplitude_mv.get(lead) or 0
            s = f.s_amplitude_mv.get(lead) or 0
            qrs_negative = s > r
            if qrs_negative and dep >= 0.1:
                score += 3
                details.append(f"Concordant ST depression in {lead} ({dep:.2f} mV)")
                break
    if score < 3:
        return None
    conf = "HIGH" if score >= 5 else "MODERATE"
    return _make(
        "sgarbossa_stemi", conf,
        f"STEMI in LBBB (Sgarbossa score {score}).",
        f"Modified Sgarbossa criteria met (score {score}/8). " + ". ".join(details) + ".",
        {"sgarbossa_score": score, "lbbb": True},
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
