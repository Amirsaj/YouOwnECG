"""
Two-stage RAG diagnostic reasoning pipeline.

Stage 1 — Observation Extraction:
  Narrator output + textbook RAG → LLM reasoner → structured clinical observations
  ("What am I seeing on this ECG?")

Stage 2 — Disease Matching:
  Observations + disease knowledge base (.md files) → validate findings against criteria
  ("What disease does this match? Do the criteria actually hold?")

This architecture mirrors how cardiology departments work:
  Fellow describes the ECG (narrator) → attending interprets with textbook knowledge (Stage 1)
  → compares against diagnostic criteria for each condition (Stage 2)
"""

from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Optional

# Disease KB directory
DISEASE_KB_DIR = Path(__file__).resolve().parents[1] / "docs" / "architecture" / "nodes" / "diseases"

# Observation categories that Stage 1 should extract
OBSERVATION_SCHEMA = {
    "rhythm": {
        "description": "Rhythm analysis",
        "fields": ["type", "regularity", "p_wave_status", "av_relationship", "rate_bpm"]
    },
    "conduction": {
        "description": "Conduction system assessment",
        "fields": ["pr_interval_status", "qrs_width_status", "bundle_branch_pattern", "axis_deviation"]
    },
    "ischemia": {
        "description": "Ischemia/injury assessment",
        "fields": ["st_changes", "territory", "reciprocal_changes", "t_wave_changes", "q_waves"]
    },
    "morphology": {
        "description": "Structural/morphological findings",
        "fields": ["voltage_criteria", "strain_pattern", "chamber_enlargement", "special_patterns"]
    },
    "repolarization": {
        "description": "Repolarization abnormalities",
        "fields": ["qtc_status", "t_wave_abnormalities", "u_waves"]
    },
}

# Maps observation keywords → disease KB files to load
OBSERVATION_TO_DISEASE_FILES = {
    "afib": ["atrial_fibrillation.md"],
    "aflutter": ["atrial_flutter.md"],
    "irregular": ["atrial_fibrillation.md", "sinus_arrhythmia.md"],
    "absent_p": ["atrial_fibrillation.md", "junctional_rhythm.md"],
    "prolonged_pr": ["first_degree_av_block.md"],
    "dropped_beat": ["second_degree_av_block_type1.md", "second_degree_av_block_type2.md"],
    "av_dissociation": ["complete_av_block.md"],
    "wide_qrs": ["lbbb.md", "rbbb.md", "wpw.md", "ventricular_tachycardia.md"],
    "lbbb_pattern": ["lbbb.md", "sgarbossa_criteria.md"],
    "rbbb_pattern": ["rbbb.md"],
    "left_axis": ["lafb.md"],
    "right_axis": ["rvh.md", "lpfb.md"],
    "st_elevation": ["stemi_anterior.md", "stemi_inferior.md", "stemi_lateral.md",
                     "pericarditis.md", "early_repolarization.md", "brugada_type1.md"],
    "st_depression": ["nstemi.md", "subendocardial_ischemia.md"],
    "t_inversion": ["wellens_syndrome.md", "t_wave_inversion_patterns.md", "strain_pattern.md"],
    "hyperacute_t": ["stemi_anterior.md", "stemi_equivalent_patterns.md"],
    "tall_voltage": ["lvh.md", "voltage_criteria_reference.md"],
    "low_voltage": ["low_voltage.md", "pericardial_effusion.md"],
    "short_pr": ["wpw.md"],
    "long_qt": ["long_qt.md", "long_qt_tdp.md"],
    "bradycardia": ["sinus_bradycardia.md", "sick_sinus_syndrome.md"],
    "tachycardia": ["sinus_tachycardia.md", "svt.md", "ventricular_tachycardia.md"],
    "pvc": ["pvc.md"],
    "pathological_q": ["old_mi_anterior.md", "old_mi_inferior.md", "old_mi_lateral.md"],
}


def build_stage1_prompt(narrative: str, rag_evidence: str) -> tuple[str, str]:
    """
    Build the Stage 1 prompt: extract clinical observations from the narrative.

    Returns (system_prompt, user_prompt).
    """
    system_prompt = """You are a senior cardiology fellow performing a systematic ECG interpretation.

You will receive:
1. A beat-by-beat ECG narrative describing morphological features across multiple leads
2. Relevant textbook evidence from ECG reference books

Your task: Extract structured clinical observations. Think step by step through the ECG systematically.

SYSTEMATIC APPROACH (follow this order):
1. RATE: Calculate ventricular rate. Bradycardia (<60)? Tachycardia (>100)?
2. RHYTHM: Regular or irregular? Is there a pattern to irregularity? P-waves present? P:QRS ratio?
3. P-WAVES: Morphology (upright/inverted/absent/bifid/peaked)? Duration? Consistent across beats?
4. PR INTERVAL: Normal (120-200ms)? Prolonged? Short? Progressive lengthening (Wenckebach)?
5. QRS: Narrow (<120ms) or wide? If wide: LBBB pattern? RBBB pattern? Delta wave (WPW)?
6. ST SEGMENT: Elevation? Depression? Which leads? Territorial pattern? Reciprocal changes?
7. T-WAVES: Normal? Inverted? Hyperacute? Symmetric vs asymmetric inversion?
8. QT INTERVAL: QTc prolonged? Which formula?
9. OVERALL: Synthesize — what are the key findings?

OUTPUT FORMAT — respond with JSON:
{
    "reasoning": "step-by-step analysis following the systematic approach above",
    "observations": {
        "rhythm": {
            "type": "sinus|afib|aflutter|junctional|paced|ventricular|unknown",
            "regularity": "regular|irregular|irregularly_irregular",
            "p_wave_status": "present_normal|absent|inverted|bifid|peaked|variable",
            "av_relationship": "1:1|variable|dissociated|wenckebach|2:1_block",
            "rate_bpm": 75,
            "rate_category": "normal|bradycardia|tachycardia"
        },
        "conduction": {
            "pr_interval_status": "normal|prolonged|short|progressive_prolongation|absent",
            "pr_interval_ms": 160,
            "qrs_width_status": "narrow|borderline|wide",
            "qrs_duration_ms": 95,
            "bundle_branch_pattern": "none|lbbb|rbbb|ivcd|wpw_delta",
            "axis_deviation": "normal|left|right|extreme_right|indeterminate"
        },
        "ischemia": {
            "st_elevation_leads": ["V1", "V2"],
            "st_elevation_max_mv": 0.2,
            "st_depression_leads": [],
            "st_morphology": "concave_up|convex|horizontal|downsloping",
            "territory": "anterior_LAD|inferior_RCA|lateral_LCx|diffuse|none",
            "reciprocal_changes": true,
            "t_wave_changes": "normal|hyperacute|inverted|biphasic",
            "pathological_q_waves": []
        },
        "morphology": {
            "voltage_criteria": "normal|high_voltage_lvh|low_voltage",
            "lvh_pattern": "none|voltage_only|with_strain",
            "rvh_pattern": "none|suspected|definite",
            "chamber_enlargement": "none|lae|rae|biatrial",
            "special_patterns": []
        },
        "repolarization": {
            "qtc_status": "normal|borderline|prolonged|critically_prolonged",
            "qtc_bazett_ms": 420,
            "t_wave_abnormalities": [],
            "u_waves": false
        },
        "key_findings": ["list of the most clinically significant findings"],
        "urgency": "STAT|urgent|routine|normal"
    }
}

CRITICAL RULES:
- Base your analysis ONLY on the narrative data provided — never invent measurements
- If a finding is ambiguous, state the uncertainty
- Always check for reciprocal changes when ST elevation is present
- Consider rate-related changes (tachycardia can cause ST/T changes)
- Flag STAT findings immediately: STEMI, complete heart block, VT/VF, Brugada Type 1
"""

    user_prompt = f"""Analyze this ECG systematically:

<ecg_narrative>
{narrative}
</ecg_narrative>

<textbook_evidence>
{rag_evidence}
</textbook_evidence>

Extract your clinical observations following the systematic approach. Respond with JSON."""

    return system_prompt, user_prompt


def build_stage2_prompt(observations: dict, disease_context: str) -> tuple[str, str]:
    """
    Build the Stage 2 prompt: validate findings against disease criteria.

    Returns (system_prompt, user_prompt).
    """
    system_prompt = """You are a cardiology attending physician reviewing a fellow's ECG interpretation.

You will receive:
1. The fellow's structured observations from the ECG
2. Diagnostic criteria from the clinical knowledge base for relevant conditions

Your task: Validate each observation against the formal diagnostic criteria. For each potential condition:
- Does the ECG meet ALL required criteria?
- Are any criteria partially met (suggestive but not diagnostic)?
- Are there findings that CONTRADICT this diagnosis?
- What is your confidence level?

OUTPUT FORMAT — respond with JSON:
{
    "reasoning": "your attending-level reasoning, addressing each potential condition",
    "validated_findings": [
        {
            "condition": "condition name (e.g., atrial_fibrillation)",
            "criteria_met": ["list of specific criteria that ARE met"],
            "criteria_not_met": ["list of criteria that are NOT met or cannot be assessed"],
            "contradicting_evidence": ["any findings that argue against this diagnosis"],
            "confidence": "HIGH|MODERATE|LOW|INSUFFICIENT",
            "clinical_summary": "one-sentence clinical interpretation (max 15 words)",
            "action_required": "STAT|urgent|routine|none"
        }
    ],
    "differential_diagnosis": ["ordered list of conditions to consider"],
    "overall_interpretation": "2-3 sentence summary of the ECG"
}

VALIDATION RULES:
- A condition requires ALL its mandatory criteria to be met for HIGH confidence
- If only some criteria are met, confidence is MODERATE or LOW
- Contradicting evidence should LOWER confidence or EXCLUDE the diagnosis
- STAT conditions (STEMI, complete AVB, VT, Brugada Type 1) must be flagged even at LOW confidence
- Apply clinical suppression rules:
  * WPW → suppress LBBB, LVH
  * LBBB → use Sgarbossa for STEMI, suppress QTc
  * AFib → suppress P-wave findings
  * BBB → expected ST-T discordance is NOT ischemia
"""

    user_prompt = f"""Review the fellow's ECG observations and validate against diagnostic criteria:

<fellow_observations>
{json.dumps(observations, indent=2)}
</fellow_observations>

<diagnostic_criteria>
{disease_context}
</diagnostic_criteria>

Validate each finding. Respond with JSON."""

    return system_prompt, user_prompt


def select_disease_files(observations: dict) -> list[str]:
    """
    Based on Stage 1 observations, select which disease KB files are relevant.
    Returns list of filenames to load.
    """
    files = set()

    obs = observations if isinstance(observations, dict) else {}

    # Rhythm
    rhythm = obs.get("rhythm", {})
    rhythm_type = rhythm.get("type", "")
    if rhythm_type == "afib":
        files.update(OBSERVATION_TO_DISEASE_FILES.get("afib", []))
    elif rhythm_type == "aflutter":
        files.update(OBSERVATION_TO_DISEASE_FILES.get("aflutter", []))
    if rhythm.get("regularity") == "irregularly_irregular":
        files.update(OBSERVATION_TO_DISEASE_FILES.get("irregular", []))
    if rhythm.get("p_wave_status") == "absent":
        files.update(OBSERVATION_TO_DISEASE_FILES.get("absent_p", []))
    rate_cat = rhythm.get("rate_category", "")
    if rate_cat == "bradycardia":
        files.update(OBSERVATION_TO_DISEASE_FILES.get("bradycardia", []))
    elif rate_cat == "tachycardia":
        files.update(OBSERVATION_TO_DISEASE_FILES.get("tachycardia", []))

    # Conduction
    cond = obs.get("conduction", {})
    pr_status = cond.get("pr_interval_status", "")
    if pr_status == "prolonged":
        files.update(OBSERVATION_TO_DISEASE_FILES.get("prolonged_pr", []))
    elif pr_status == "short":
        files.update(OBSERVATION_TO_DISEASE_FILES.get("short_pr", []))
    elif pr_status == "progressive_prolongation":
        files.update(OBSERVATION_TO_DISEASE_FILES.get("dropped_beat", []))
    qrs_status = cond.get("qrs_width_status", "")
    if qrs_status == "wide":
        files.update(OBSERVATION_TO_DISEASE_FILES.get("wide_qrs", []))
    bbb = cond.get("bundle_branch_pattern", "")
    if "lbbb" in bbb:
        files.update(OBSERVATION_TO_DISEASE_FILES.get("lbbb_pattern", []))
    if "rbbb" in bbb:
        files.update(OBSERVATION_TO_DISEASE_FILES.get("rbbb_pattern", []))
    axis = cond.get("axis_deviation", "")
    if axis == "left":
        files.update(OBSERVATION_TO_DISEASE_FILES.get("left_axis", []))
    elif axis == "right":
        files.update(OBSERVATION_TO_DISEASE_FILES.get("right_axis", []))

    # Ischemia
    isch = obs.get("ischemia", {})
    if isch.get("st_elevation_leads"):
        files.update(OBSERVATION_TO_DISEASE_FILES.get("st_elevation", []))
    if isch.get("st_depression_leads"):
        files.update(OBSERVATION_TO_DISEASE_FILES.get("st_depression", []))
    t_changes = isch.get("t_wave_changes", "")
    if "inverted" in str(t_changes):
        files.update(OBSERVATION_TO_DISEASE_FILES.get("t_inversion", []))
    if "hyperacute" in str(t_changes):
        files.update(OBSERVATION_TO_DISEASE_FILES.get("hyperacute_t", []))
    if isch.get("pathological_q_waves"):
        files.update(OBSERVATION_TO_DISEASE_FILES.get("pathological_q", []))

    # Morphology
    morph = obs.get("morphology", {})
    voltage = morph.get("voltage_criteria", "")
    if "high" in voltage or "lvh" in str(morph.get("lvh_pattern", "")):
        files.update(OBSERVATION_TO_DISEASE_FILES.get("tall_voltage", []))
    if "low" in voltage:
        files.update(OBSERVATION_TO_DISEASE_FILES.get("low_voltage", []))

    # Repolarization
    repol = obs.get("repolarization", {})
    if repol.get("qtc_status") in ("prolonged", "critically_prolonged"):
        files.update(OBSERVATION_TO_DISEASE_FILES.get("long_qt", []))

    # Always include normal reference for context
    files.add("normal_ecg_reference.md")

    return sorted(files)


def load_disease_context(filenames: list[str], max_chars: int = 8000) -> str:
    """Load disease KB files and truncate to fit token budget."""
    sections = []
    total_chars = 0

    for fname in filenames:
        fpath = DISEASE_KB_DIR / fname
        if not fpath.exists():
            continue
        content = fpath.read_text()
        # Extract key sections (criteria + lead-by-lead + key discriminators)
        # Truncate each file to ~2000 chars to stay within budget
        truncated = _extract_key_sections(content, max_chars=2000)
        if total_chars + len(truncated) > max_chars:
            break
        sections.append(f"=== {fname.replace('.md', '').upper()} ===\n{truncated}")
        total_chars += len(truncated)

    return "\n\n".join(sections)


def _extract_key_sections(content: str, max_chars: int = 2000) -> str:
    """Extract the most diagnostic-relevant sections from a disease KB file."""
    lines = content.split("\n")
    relevant_sections = []
    current_section = []
    in_relevant = False

    # Keywords indicating diagnostically relevant sections
    relevant_headers = [
        "diagnostic criteria", "criteria", "lead-by-lead",
        "key discriminator", "mandatory", "required",
        "distinguishing", "differential", "clinical significance",
        "ecg presentation", "hallmark", "pathognomonic",
    ]

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

    # If no relevant sections found, take the first max_chars
    if not relevant_sections:
        return content[:max_chars]

    result = "\n".join(relevant_sections)
    return result[:max_chars]


async def run_two_stage_diagnosis(
    narrative: str,
    features,
    rag_store=None,
    call_agent_fn=None,
) -> dict:
    """
    Run the two-stage RAG diagnostic pipeline.

    Stage 1: Narrative + textbook RAG → extract observations
    Stage 2: Observations + disease KB → validate findings

    Returns dict with stage1_observations, stage2_validated, cost info.
    """
    from agents.deepseek import call_agent, extract_json
    _call = call_agent_fn or call_agent

    ecg_id = features.ecg_id if hasattr(features, 'ecg_id') else "unknown"

    # --- Stage 1: Get textbook evidence via RAG ---
    rag_evidence = ""
    if rag_store is not None:
        try:
            from rag.embedding import embed_query
            from rag.retrieval import retrieve, format_rag_block
            # Query based on narrative key terms
            query = _build_rag_query_from_narrative(narrative)
            results = retrieve(query, rag_store, top_k=4)
            rag_evidence = format_rag_block(results)
        except Exception:
            pass

    # --- Stage 1: Extract observations ---
    s1_system, s1_user = build_stage1_prompt(narrative, rag_evidence)
    s1_raw = await _call(
        system_prompt=s1_system,
        user_prompt=s1_user,
        agent_name="STAGE1_OBSERVER",
        ecg_id=ecg_id,
    )

    s1_content = s1_raw.get("content", "")
    observations = extract_json(s1_content)
    if observations is None:
        observations = {"error": "Failed to parse Stage 1 output", "raw": s1_content[:500]}

    # Extract the observations sub-dict
    obs_data = observations.get("observations", observations)

    # --- Stage 2: Select disease files based on observations ---
    disease_files = select_disease_files(obs_data)
    disease_context = load_disease_context(disease_files)

    # --- Stage 2: Validate against disease criteria ---
    s2_system, s2_user = build_stage2_prompt(obs_data, disease_context)
    s2_raw = await _call(
        system_prompt=s2_system,
        user_prompt=s2_user,
        agent_name="STAGE2_VALIDATOR",
        ecg_id=ecg_id,
    )

    s2_content = s2_raw.get("content", "")
    validated = extract_json(s2_content)
    if validated is None:
        validated = {"error": "Failed to parse Stage 2 output", "raw": s2_content[:500]}

    return {
        "stage1_observations": obs_data,
        "stage1_reasoning": observations.get("reasoning", ""),
        "stage2_validated": validated,
        "disease_files_consulted": disease_files,
        "rag_evidence_used": bool(rag_evidence),
        "cost": {
            "stage1_tokens": s1_raw.get("usage", {}),
            "stage2_tokens": s2_raw.get("usage", {}),
            "stage1_latency": s1_raw.get("latency_sec", 0),
            "stage2_latency": s2_raw.get("latency_sec", 0),
        },
    }


def _build_rag_query_from_narrative(narrative: str) -> str:
    """Extract key clinical terms from narrative for RAG query."""
    # Look for clinically significant keywords
    keywords = []
    lower = narrative.lower()

    if "st elevated" in lower or "st elevation" in lower:
        keywords.append("ST elevation STEMI criteria")
    if "st depressed" in lower or "st depression" in lower:
        keywords.append("ST depression ischemia")
    if "p-wave absent" in lower:
        keywords.append("absent P waves atrial fibrillation")
    if "wide" in lower and "qrs" in lower:
        keywords.append("wide QRS bundle branch block")
    if "inverted" in lower and "t-wave" in lower:
        keywords.append("T wave inversion differential diagnosis")
    if "hyperacute" in lower:
        keywords.append("hyperacute T waves acute MI")
    if "irregular" in lower:
        keywords.append("irregular rhythm differential")
    if "prolonged" in lower and "pr" in lower:
        keywords.append("prolonged PR interval AV block")
    if "prolonged" in lower and "qt" in lower:
        keywords.append("prolonged QT interval")

    if not keywords:
        keywords.append("ECG interpretation systematic approach")

    return " ".join(keywords[:3])
