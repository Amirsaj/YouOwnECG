"""
Single-stage RAG diagnostic reasoning pipeline.

Architecture:
  Narration + pipeline measurements + disease criteria → Reasoner LLM → Diagnoses

The reasoner sees the full picture in one call: the ECG narration (from Gemma
vision and/or pipeline narrator), the computed features as measurements, and
the relevant disease criteria from the knowledge base. It reasons through
to diagnoses with evidence.

All prompts and settings live in rag_prompts.py.
"""

from __future__ import annotations
import json
import re
from pathlib import Path

from pipeline.rag_prompts import (
    REASONER_SYSTEM_PROMPT,
    REASONER_USER_TEMPLATE,
    NARRATION_TO_DISEASE_FILES,
    EXTRACTION_SETTINGS,
    SAFETY_NET_RULES,
)

DISEASE_KB_DIR = Path(__file__).resolve().parents[1] / "docs" / "architecture" / "nodes" / "diseases"

# Keep old name for backward compat with dashboard imports
OBSERVATION_TO_DISEASE_FILES = NARRATION_TO_DISEASE_FILES


# ---------------------------------------------------------------------------
# Disease file selection — scans narration text + features for keywords
# ---------------------------------------------------------------------------

def select_disease_files_from_narration(narrative: str) -> list[str]:
    """Scan narration text for keywords and return matching disease files."""
    files = set()
    lower = narrative.lower()

    for keyword, disease_files in NARRATION_TO_DISEASE_FILES.items():
        if keyword in lower:
            files.update(disease_files)

    # Always include normal reference
    files.add("normal_ecg_reference.md")
    return sorted(files)


def _safety_net_files(narrative: str, features) -> set[str]:
    """
    Force-load disease files based on pipeline features.

    Features are computed from the signal (ground truth), not from LLM
    interpretation. This catches things the narration keyword scan may miss.
    """
    extra = set()
    lower = narrative.lower()

    for rule in SAFETY_NET_RULES:
        trigger = rule.get("trigger", "")
        rule_files = rule.get("files", [])

        if trigger in ("features", "both") and features is not None:
            field = rule.get("feature_field")
            conditions = rule.get("conditions")
            requires_lvh = rule.get("requires_lvh", False)

            if field and hasattr(features, field):
                val = getattr(features, field)
                check_leads = rule.get("check_leads")
                values = rule.get("values")

                if check_leads and isinstance(val, dict):
                    if any(val.get(l) for l in check_leads):
                        extra.update(rule_files)
                elif values and val in values:
                    extra.update(rule_files)

            if conditions:
                for cond in conditions:
                    f = cond.get("field")
                    if f and hasattr(features, f):
                        fval = getattr(features, f)
                        if fval is not None:
                            op = cond.get("op", ">=")
                            threshold = cond.get("value", 0)
                            if op == ">=" and fval >= threshold:
                                extra.update(rule_files)
                            elif op == ">" and fval > threshold:
                                extra.update(rule_files)

            if requires_lvh:
                lvh_met = getattr(features, "lvh_criteria_met", [])
                if lvh_met:
                    dep_leads = rule.get("st_depression_leads", [])
                    dep_thresh = rule.get("st_depression_threshold_mv", 0.05)
                    st_dep = getattr(features, "st_depression_mv", {})
                    if any((st_dep.get(l) or 0) > dep_thresh for l in dep_leads):
                        extra.update(rule_files)

        if trigger in ("narration", "both"):
            patterns = rule.get("narration_patterns", [])
            if patterns and any(p in lower for p in patterns):
                extra.update(rule_files)

    return extra


# ---------------------------------------------------------------------------
# Disease context loading
# ---------------------------------------------------------------------------

def load_disease_context(filenames: list[str], max_chars: int = None) -> str:
    """Load disease KB files, extract relevant sections, fit within budget."""
    if max_chars is None:
        max_chars = EXTRACTION_SETTINGS["max_total_chars"]
    per_file = EXTRACTION_SETTINGS["max_per_file_chars"]

    sections = []
    total_chars = 0

    for fname in filenames:
        fpath = DISEASE_KB_DIR / fname
        if not fpath.exists():
            continue
        content = fpath.read_text()
        truncated = _extract_key_sections(content, max_chars=per_file)
        if total_chars + len(truncated) > max_chars:
            break
        sections.append(f"=== {fname.replace('.md', '').upper()} ===\n{truncated}")
        total_chars += len(truncated)

    return "\n\n".join(sections)


def _extract_key_sections(content: str, max_chars: int = None) -> str:
    """Extract diagnostically relevant sections from a disease KB file."""
    if max_chars is None:
        max_chars = EXTRACTION_SETTINGS["max_per_file_chars"]
    relevant_headers = EXTRACTION_SETTINGS["relevant_headers"]

    lines = content.split("\n")
    relevant_sections = []
    current_section = []
    in_relevant = False

    for line in lines:
        if line.startswith("#"):
            if current_section and in_relevant:
                relevant_sections.extend(current_section)
            current_section = [line]
            in_relevant = any(kw in line.lower() for kw in relevant_headers)
        else:
            current_section.append(line)

    if current_section and in_relevant:
        relevant_sections.extend(current_section)

    if not relevant_sections:
        return content[:max_chars]

    result = "\n".join(relevant_sections)
    return result[:max_chars]


# ---------------------------------------------------------------------------
# Build pipeline measurements summary from features object
# ---------------------------------------------------------------------------

def _build_measurements_block(features) -> str:
    """Extract key computed measurements from the features object.

    v2 (2026-05-15) — adds explicit clinical-finding callouts beneath every
    threshold-crossing raw measurement. Reasoners were reading raw HR/QTc/PR
    numbers and estimating "normal" in their narratives; the v2 callouts
    anchor each threshold-crossing finding to a clear `→ FINDING` line.
    """
    if features is None:
        return "No pipeline measurements available."

    lines = []

    # Rate & rhythm
    hr = getattr(features, "heart_rate_ventricular_bpm", None)
    if hr is not None:
        lines.append("Heart rate: %.1f bpm" % hr)
        if hr < 60:
            lines.append("  → BRADYCARDIA (HR < 60 bpm) — commit sinus_bradycardia if rhythm is sinus")
        elif hr > 100:
            lines.append("  → TACHYCARDIA (HR > 100 bpm) — commit sinus_tachycardia if rhythm is sinus")
    rhythm = getattr(features, "dominant_rhythm", None)
    rhythm_reg = getattr(features, "rhythm_regular", True)
    if rhythm:
        reg = "regular" if rhythm_reg else "irregular"
        lines.append("Rhythm: %s (%s)" % (rhythm, reg))
    # v2 callout: rhythm-irregularity-based AFib pattern.
    # Use truthiness (`not rhythm_reg`) so this fires whether the field is False,
    # None, or 0 — same convention as the "Rhythm:" line above.
    # Use SDNN (RR-interval standard deviation) as a quantitative pattern strength
    # signal; SDNN > 100 ms strongly suggests AFib (normal sinus rhythm SDNN ≤ 50 ms).
    sdnn = getattr(features, "sdnn_ms", None)
    sdnn_str = (" SDNN=%.0fms" % sdnn) if sdnn is not None else ""
    if rhythm and not rhythm_reg:
        rhythm_s = str(rhythm).lower()
        if "afib" in rhythm_s:
            lines.append("  → AFIB CONFIRMED by signal pipeline%s — commit atrial_fibrillation" % sdnn_str)
        elif "sinus" in rhythm_s:
            # Contradiction: true sinus is regular; "sinus (irregular)" reliably indicates
            # AFib that the rhythm-classifier mis-labelled (audit confirmed 8/12 patients).
            lines.append("  → IRREGULAR RHYTHM despite 'sinus' label%s — likely AFib; commit atrial_fibrillation (the rhythm-irregularity contradicts pure sinus rhythm)" % sdnn_str)
        else:
            lines.append("  → IRREGULAR RHYTHM%s — consider atrial_fibrillation if P-waves are absent or vary across beats" % sdnn_str)

    # Intervals
    pr = getattr(features, "pr_interval_ms", None)
    if pr is not None:
        lines.append("PR interval: %.0f ms" % pr)
        if pr >= 200:
            lines.append("  → 1°AV BLOCK (PR ≥ 200 ms) — commit first_degree_avb")
        elif pr >= 180:
            lines.append("  → BORDERLINE 1°AVB (PR 180–199 ms) — consider first_degree_avb if PTB-XL/SNOMED labels suggest")
    qrs = getattr(features, "qrs_duration_global_ms", None)
    if qrs is not None:
        wide_tag = " (WIDE)" if qrs >= 120 else ""
        lines.append("QRS duration: %.0f ms%s" % (qrs, wide_tag))
        if 110 <= qrs < 120:
            lines.append("  → BORDERLINE WIDE QRS (110–119 ms) — consider incomplete BBB / IVCD")
    qtc = getattr(features, "qtc_bazett_ms", None)
    if qtc is not None:
        lines.append("QTc (Bazett): %.0f ms" % qtc)
        if qtc > 460:
            lines.append("  → LONG QT (QTc > 460 ms) — commit long_qt_interval")
        elif qtc >= 440:
            lines.append("  → BORDERLINE LONG QT (QTc 440–460 ms)")

    # P-wave
    p_dur = getattr(features, "p_duration_ms", None)
    if p_dur is not None:
        lines.append("P-wave duration: %.0f ms%s" % (p_dur, " (PROLONGED >=120)" if p_dur >= 120 else ""))
    ptf = getattr(features, "p_terminal_force_v1_mv_s", None)
    if ptf is not None:
        lines.append("P-terminal force V1: %.3f mV*s%s" % (ptf, " (>=0.04 = LAE)" if ptf >= 0.04 else ""))

    # Axes
    qrs_axis_for_rule = None
    for name, field in [("QRS axis", "qrs_axis_deg"), ("P axis", "p_axis_deg"), ("T axis", "t_axis_deg")]:
        val = getattr(features, field, None)
        if val is not None:
            lines.append("%s: %.0f degrees" % (name, val))
            if field == "qrs_axis_deg":
                qrs_axis_for_rule = val
                # Axis-based callouts
                if val > 90:
                    lines.append("  → RIGHT AXIS DEVIATION (QRS axis > +90°)")
                elif val < -30:
                    lines.append("  → LEFT AXIS DEVIATION (QRS axis < -30°) — consider LAFB / inferior MI / LVH")

    # Algorithm flags
    flags = []
    for flag in ["lbbb", "rbbb", "lafb", "lpfb", "wpw_pattern"]:
        if getattr(features, flag, False):
            flags.append(flag.upper())
    if flags:
        lines.append("Algorithm conduction flags: %s" % ", ".join(flags))
        # v2 callouts — each conduction-flag MUST be committed even if others co-exist.
        if "LAFB" in flags:
            qrs_axis = getattr(features, "qrs_axis_deg", None)
            ax_str = (" (axis = %.0f°)" % qrs_axis) if qrs_axis is not None else ""
            lines.append("  → LAFB%s — commit left_anterior_fascicular_block (co-exists with LBBB/RBBB/AVB)" % ax_str)
        if "RBBB" in flags:
            lines.append("  → RBBB — commit right_bundle_branch_block")
        if "LBBB" in flags:
            lines.append("  → LBBB — commit left_bundle_branch_block")
        if "LPFB" in flags:
            lines.append("  → LPFB — commit left_posterior_fascicular_block")
        if "WPW_PATTERN" in flags:
            lines.append("  → WPW pattern — commit wpw")
    # v2: IRBBB derived flag (signal sets RBBB only at QRS>=120; partial RBBB
    # cases at 110-119 ms with rSR' aren't currently flagged).
    qrs_val = getattr(features, "qrs_duration_global_ms", None)
    if (qrs_val is not None and 110 <= qrs_val < 120
            and "RBBB" not in flags and "LBBB" not in flags):
        # rSR' pattern hint via R/S amplitudes in V1
        r_amp_v1 = (getattr(features, "r_amplitude_mv", {}) or {}).get("V1")
        s_amp_v1 = (getattr(features, "s_amplitude_mv", {}) or {}).get("V1")
        if r_amp_v1 is not None and s_amp_v1 is not None and r_amp_v1 > 0.1:
            lines.append("  → POSSIBLE INCOMPLETE RBBB (QRS %.0f ms, V1 R=%.2f S=%.2f) — consider incomplete_rbbb"
                         % (qrs_val, r_amp_v1, s_amp_v1))

    # LVH
    lvh = getattr(features, "lvh_criteria_met", [])
    if lvh:
        lines.append("LVH criteria met: %s" % ", ".join(lvh))
        lines.append("  → LVH — commit left_ventricular_hypertrophy (any single LVH criterion is sufficient; do NOT require multi-criterion agreement)")
    sokolow = getattr(features, "lvh_sokolow_lyon_mv", None)
    if sokolow is not None:
        crit = " (>=3.5 = LVH)" if sokolow >= 3.5 else ""
        lines.append("Sokolow-Lyon: %.2f mV%s" % (sokolow, crit))
        if sokolow >= 3.5 and not lvh:
            lines.append("  → LVH (Sokolow-Lyon ≥ 3.5 mV) — commit left_ventricular_hypertrophy")
    cornell = getattr(features, "lvh_cornell_mv", None)
    if cornell is not None:
        lines.append("Cornell voltage: %.2f mV" % cornell)
        if cornell > 2.8 and not lvh:
            lines.append("  → LVH (Cornell > 2.8 mV) — commit left_ventricular_hypertrophy")

    # Pathological Q-waves
    path_q = getattr(features, "pathological_q_wave", {})
    q_leads = [l for l, v in path_q.items() if v]
    if q_leads:
        lines.append("PATHOLOGICAL Q-WAVES (from signal): %s" % ", ".join(q_leads))

    # R-wave progression
    r_prog = getattr(features, "r_progression", None)
    if r_prog and r_prog != "normal":
        lines.append("R-wave progression: %s" % r_prog.upper())

    # Per-lead ST elevation/depression
    st_elev = getattr(features, "st_elevation_mv", {}) or {}
    elev_leads = {l: v for l, v in st_elev.items() if v is not None and v > 0.05}
    if elev_leads:
        lines.append("ST elevation: %s" % ", ".join("%s=%.2fmV" % (l, v) for l, v in sorted(elev_leads.items())))
        # v2 territory rollups — STEMI commit rule: ≥0.1 mV in ≥2 leads of a territory
        # (≥0.2 mV in V2/V3 per ESC/AHA), and acute STEMI does NOT require Q-waves.
        inferior = ["II", "III", "aVF"]
        anterior = ["V1", "V2", "V3", "V4"]
        lateral = ["I", "aVL", "V5", "V6"]
        def _territory_hit(leads, lead_thr):
            hits = [(l, elev_leads[l]) for l in leads if l in elev_leads and elev_leads[l] >= lead_thr.get(l, 0.10)]
            return hits
        for name, terr in [("INFERIOR", inferior), ("LATERAL", lateral)]:
            hits = _territory_hit(terr, {l: 0.10 for l in terr})
            if len(hits) >= 2:
                lines.append("  → %s ST ELEVATION (%s) — commit %s_stemi (acute STEMI does NOT require Q-waves)"
                             % (name, ", ".join("%s=%.2fmV" % (l, v) for l, v in hits), name.lower()))
        ant_thr = {"V1": 0.10, "V2": 0.20, "V3": 0.20, "V4": 0.10}
        ant_hits = _territory_hit(anterior, ant_thr)
        if len(ant_hits) >= 2:
            lines.append("  → ANTERIOR ST ELEVATION (%s) — commit anterior_stemi (acute STEMI does NOT require Q-waves)"
                         % ", ".join("%s=%.2fmV" % (l, v) for l, v in ant_hits))

    st_dep = getattr(features, "st_depression_mv", {}) or {}
    dep_leads = {l: v for l, v in st_dep.items() if v is not None and v > 0.05}
    if dep_leads:
        lines.append("ST depression: %s" % ", ".join("%s=%.2fmV" % (l, v) for l, v in sorted(dep_leads.items())))
        # v2 — multi-lead ST depression callout. If ≥2 leads with ≥0.05 mV depression
        # AND no LBBB context, this is ischemia/strain (dual-interpret in LBBB context).
        if len(dep_leads) >= 2:
            has_lbbb = "LBBB" in flags
            note = " (in LBBB context — dual-interpret: secondary OR primary ischemia/strain)" if has_lbbb else ""
            lines.append("  → MULTI-LEAD ST DEPRESSION%s — consider ischemia / strain" % note)

    # Per-lead R and S amplitudes (for voltage criteria)
    r_amp = getattr(features, "r_amplitude_mv", {})
    s_amp = getattr(features, "s_amplitude_mv", {})
    voltage_leads = []
    for lead in ["V1", "V2", "V3", "V4", "V5", "V6", "I", "aVL"]:
        r = r_amp.get(lead)
        s = s_amp.get(lead)
        if r is not None or s is not None:
            parts = []
            if r is not None:
                parts.append("R=%.2f" % r)
            if s is not None:
                parts.append("S=%.2f" % s)
            voltage_leads.append("%s(%s)" % (lead, ",".join(parts)))
    if voltage_leads:
        lines.append("Amplitudes (mV): %s" % " | ".join(voltage_leads))
        # v2 RVH derived rule. Classical RVH criteria: tall R in V1 with R/S > 1
        # AND deep S in V5/V6 (R/S in V5 or V6 < 1) AND right axis deviation (>+90°).
        r_v1 = (r_amp or {}).get("V1")
        s_v1 = (s_amp or {}).get("V1")
        r_v5 = (r_amp or {}).get("V5")
        s_v5 = (s_amp or {}).get("V5")
        r_v6 = (r_amp or {}).get("V6")
        s_v6 = (s_amp or {}).get("V6")
        if r_v1 is not None and s_v1 is not None and r_v1 > 0 and s_v1 > 0:
            v1_rs = r_v1 / s_v1
            tall_r_v1 = v1_rs > 1.0
            deep_s_lateral = False
            if r_v5 is not None and s_v5 is not None and s_v5 > 0 and (r_v5 / max(s_v5, 0.01)) < 1.0:
                deep_s_lateral = True
            if r_v6 is not None and s_v6 is not None and s_v6 > 0 and (r_v6 / max(s_v6, 0.01)) < 1.0:
                deep_s_lateral = True
            rad = qrs_axis_for_rule is not None and qrs_axis_for_rule > 90
            if tall_r_v1 and (deep_s_lateral or rad):
                lines.append("  → RVH PATTERN (V1 R/S=%.1f >1, %s) — commit right_ventricular_hypertrophy"
                             % (v1_rs, "right axis" if rad else "deep S in lateral"))
        # v2 LOW VOLTAGE derived rule. Limb-lead low voltage = all 6 limb leads < 0.5 mV
        # (QRS p-p). Precordial low voltage = all 6 precordial leads < 1.0 mV.
        def _qrs_pp(lead):
            r = (r_amp or {}).get(lead)
            s = (s_amp or {}).get(lead)
            if r is None and s is None:
                return None
            return (r or 0.0) + (s or 0.0)
        limb_pp = {l: _qrs_pp(l) for l in ("I", "II", "III", "aVR", "aVL", "aVF")}
        prec_pp = {l: _qrs_pp(l) for l in ("V1", "V2", "V3", "V4", "V5", "V6")}
        limb_known = {k: v for k, v in limb_pp.items() if v is not None}
        prec_known = {k: v for k, v in prec_pp.items() if v is not None}
        limb_low = bool(limb_known) and all(v < 0.5 for v in limb_known.values())
        prec_low = bool(prec_known) and all(v < 1.0 for v in prec_known.values())
        if limb_low and prec_low:
            lines.append("  → LOW VOLTAGE (limb AND precordial leads all sub-threshold) — commit low_voltage")
        elif limb_low:
            lines.append("  → LIMB-LEAD LOW VOLTAGE (all limb QRS p-p < 0.5 mV) — commit low_voltage")
        elif prec_low and len(prec_known) >= 4:
            lines.append("  → PRECORDIAL LOW VOLTAGE (all precordial QRS p-p < 1.0 mV) — commit low_voltage")

    # Q-wave durations
    q_dur = getattr(features, "q_duration_ms", {})
    q_amp_dict = getattr(features, "q_amplitude_mv", {})
    q_details = []
    for lead in ["V1", "V2", "V3", "V4", "I", "aVL", "II", "III", "aVF"]:
        qd = q_dur.get(lead)
        qa = q_amp_dict.get(lead)
        if qd is not None and qd > 10:
            q_details.append("%s: q=%sms%s" % (lead, round(qd), "/%.2fmV" % qa if qa else ""))
    if q_details:
        lines.append("Q-wave details: %s" % " | ".join(q_details))

    # Beat summary — PVC, PAC, ectopics
    beat_sum = getattr(features, "beat_summary", None)
    if beat_sum is not None:
        counts = getattr(beat_sum, "beat_class_counts", {})
        if counts:
            lines.append("Beat classes: %s" % ", ".join("%s=%d" % (k, v) for k, v in counts.items() if v > 0))
        pvc_count = counts.get("pvc", 0)
        pac_count = counts.get("pac", 0)
        if pvc_count > 0:
            lines.append("PVC BEATS DETECTED: %d" % pvc_count)
        if pac_count > 0:
            lines.append("PAC BEATS DETECTED: %d" % pac_count)
        pattern = getattr(beat_sum, "beat_pattern", None)
        if pattern:
            lines.append("Beat pattern: %s" % pattern)

    return "\n".join(lines) if lines else "No measurements available."


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

async def run_two_stage_diagnosis(
    narrative: str,
    features,
    rag_store=None,
    call_agent_fn=None,
) -> dict:
    """
    Run the single-stage RAG diagnostic pipeline.

    Despite the legacy name (kept for backward compatibility with dashboard.py),
    this is now a single LLM call: narration + measurements + disease criteria → diagnoses.
    """
    from agents.deepseek import call_agent, extract_json
    _call = call_agent_fn or call_agent

    ecg_id = features.ecg_id if hasattr(features, "ecg_id") else "unknown"

    # 1. Select disease files from narration keywords
    narration_files = select_disease_files_from_narration(narrative)

    # 2. Add safety-net files from features
    safety_files = _safety_net_files(narrative, features)
    all_files = sorted(set(narration_files) | safety_files)

    # 3. Load disease context
    disease_context = load_disease_context(all_files)

    # 4. Build measurements block from features
    measurements = _build_measurements_block(features)

    # 5. Build prompt
    user_prompt = REASONER_USER_TEMPLATE.format(
        narrative=narrative,
        measurements=measurements,
        disease_context=disease_context,
    )

    # 6. Call LLM
    raw = await _call(
        system_prompt=REASONER_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        agent_name="ECG_REASONER",
        ecg_id=ecg_id,
    )

    content = raw.get("content", "")
    result = extract_json(content)
    if result is None:
        result = {"error": "Failed to parse output", "raw": content[:1000]}

    # Format for backward compat with dashboard
    return {
        "stage1_observations": result.get("diagnoses", []),
        "stage2_validated": result,
        "disease_files_consulted": all_files,
        "measurements_provided": measurements,
        "rag_evidence_used": bool(disease_context),
        "cost": {
            "stage1_tokens": raw.get("usage", {}),
            "stage2_tokens": {},
            "stage1_latency": raw.get("latency_sec", 0),
            "stage2_latency": 0,
        },
    }


# ---------------------------------------------------------------------------
# Legacy helpers kept for dashboard backward compatibility
# ---------------------------------------------------------------------------

def build_stage1_prompt(narrative, rag_evidence=""):
    """Legacy wrapper."""
    return REASONER_SYSTEM_PROMPT, REASONER_USER_TEMPLATE.format(
        narrative=narrative, measurements="", disease_context=rag_evidence,
    )

def build_stage2_prompt(observations, disease_context):
    """Legacy wrapper — unused in single-stage."""
    return REASONER_SYSTEM_PROMPT, json.dumps(observations)

def select_disease_files(observations):
    """Legacy wrapper."""
    return select_disease_files_from_narration(json.dumps(observations) if isinstance(observations, dict) else str(observations))

# Expose for external use
_narration_based_disease_files = _safety_net_files
