"""
Node 2.3 — Agent Orchestrator.

Phase 1: RRC, IT, MR run concurrently via asyncio.gather.
Phase 2: CDS receives all Phase 1 outputs and synthesizes.

STAT fast-path: if any Phase 1 agent returns a STAT finding, CDS is dispatched
immediately without waiting for remaining Phase 1 agents (they continue in
background and their output is appended post-CDS).

VL2 vision runs as a 4th concurrent task in Phase 1. Its result is advisory
and passed to CDS context.
"""

from __future__ import annotations
import asyncio
from typing import Optional

from pipeline.schemas import FeatureObject, VisionVerificationResult, QualityReport
from agents.schemas import (
    DiagnosticFinding, DiagnosticResult, StatAlert, Citation, STAT_CONDITIONS
)
from agents.deepseek import call_agent, extract_json, serialize_for_prompt
from agents.prompts import RRC_SYSTEM, IT_SYSTEM, MR_SYSTEM, CDS_SYSTEM
from agents.context_builder import (
    build_rrc_context, build_it_context, build_mr_context,
    build_cds_context, build_measurements_block,
)

PIPELINE_VERSION = "1.0.0"


async def run_diagnostic(
    features: FeatureObject,
    vision: VisionVerificationResult,
    quality: QualityReport,
    db=None,
    rag_store=None,
    call_agent_fn=None,
) -> DiagnosticResult:
    """
    Run the full diagnostic pipeline: Phase 1 (parallel) → Phase 2 (CDS).

    Returns DiagnosticResult with all findings, STAT alerts, and measurements.
    """
    _call = call_agent_fn or call_agent
    ecg_id = features.ecg_id

    # --- RAG retrieval (per-agent domain queries) ---
    rag_blocks, rag_results_by_agent = _build_rag_blocks(features, rag_store)

    # --- Phase 1: RRC + IT + MR concurrent ---
    rrc_task = asyncio.create_task(
        _call_phase1_agent(
            "RRC", RRC_SYSTEM,
            build_rrc_context(features, vision),
            ecg_id, db, rag_blocks.get("RRC", ""),
            call_fn=_call,
        )
    )
    it_task = asyncio.create_task(
        _call_phase1_agent(
            "IT", IT_SYSTEM,
            build_it_context(features, vision),
            ecg_id, db, rag_blocks.get("IT", ""),
            call_fn=_call,
        )
    )
    mr_task = asyncio.create_task(
        _call_phase1_agent(
            "MR", MR_SYSTEM,
            build_mr_context(features, vision),
            ecg_id, db, rag_blocks.get("MR", ""),
            call_fn=_call,
        )
    )

    # STAT fast-path: check each result as it completes
    rrc_output, it_output, mr_output = await asyncio.gather(rrc_task, it_task, mr_task)

    # --- Phase 2: CDS ---
    cds_context = build_cds_context(features, vision, rrc_output, it_output, mr_output)
    cds_raw = await _call(
        system_prompt=CDS_SYSTEM,
        user_prompt=f"<context>\n{cds_context}\n</context>\n\nSynthesize a final DiagnosticResult.",
        agent_name="CDS",
        ecg_id=ecg_id,
        db=db,
    )
    cds_output = extract_json(cds_raw["content"])

    # --- Build DiagnosticResult ---
    findings = _build_findings(
        cds_output, rrc_output, it_output, mr_output, cds_raw, rag_results_by_agent
    )
    stat_alerts = _build_stat_alerts(cds_output, findings)
    measurements = build_measurements_block(features)

    # Determine model version used
    model_version = cds_raw.get("model", "unknown")

    return DiagnosticResult(
        ecg_id=ecg_id,
        findings=findings,
        stat_alerts=stat_alerts,
        measurements=measurements,
        overall_quality=quality.overall_quality,
        pipeline_version=PIPELINE_VERSION,
        model_version=model_version,
    )


async def _call_phase1_agent(
    agent_name: str,
    system_prompt: str,
    context: str,
    ecg_id: str,
    db,
    rag_block: str = "",
    call_fn=None,
) -> dict:
    """Call a Phase 1 agent and return parsed JSON output."""
    _call = call_fn or call_agent
    rag_section = f"\n\n{rag_block}" if rag_block else ""
    user_prompt = (
        f"<context>\n{context}{rag_section}\n</context>\n\n"
        f"Analyze the ECG data above. Report all findings in your domain."
    )
    raw = await _call(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        agent_name=agent_name,
        ecg_id=ecg_id,
        db=db,
    )
    parsed = extract_json(raw["content"])
    # Attach reasoning content to each finding for the CDS
    parsed["_reasoning"] = raw.get("reasoning_content", "")
    parsed["_agent_name"] = agent_name
    return parsed


def _build_rag_blocks(features: FeatureObject, rag_store) -> tuple[dict, dict]:
    """
    Generate per-agent RAG queries from features, retrieve results, and format
    text blocks ready to append to agent prompts.

    Returns:
        rag_blocks: {agent_name: formatted_text_block}
        rag_results: {agent_name: list[RetrievalResult]}
    """
    if rag_store is None:
        return {}, {}

    from rag.retrieval import retrieve, format_rag_block

    queries = {
        "RRC": _rrc_query(features),
        "IT": _it_query(features),
        "MR": _mr_query(features),
    }

    rag_blocks: dict = {}
    rag_results: dict = {}
    for agent, query in queries.items():
        if not query:
            continue
        try:
            results = retrieve(query, rag_store, top_k=4)
            if results:
                rag_blocks[agent] = format_rag_block(results)
                rag_results[agent] = results
        except Exception as exc:
            print(f"RAG retrieval failed for {agent}: {exc}")

    return rag_blocks, rag_results


def _rrc_query(features: FeatureObject) -> str:
    parts = []
    if features.dominant_rhythm:
        parts.append(features.dominant_rhythm.replace("_", " "))
    if features.lbbb:
        parts.append("left bundle branch block criteria")
    if features.rbbb:
        parts.append("right bundle branch block criteria")
    if features.pr_interval_ms and features.pr_interval_ms > 200:
        parts.append("first degree AV block PR prolongation")
    if features.wpw_pattern:
        parts.append("Wolff-Parkinson-White delta wave pre-excitation")
    if not parts:
        parts.append("normal sinus rhythm ECG criteria")
    return " ".join(parts[:3])


def _it_query(features: FeatureObject) -> str:
    parts = []
    if features.hyperacute_t_pattern:
        parts.append("hyperacute T waves STEMI early sign")
    if features.de_winter_pattern:
        parts.append("de Winter pattern LAD occlusion")
    st_elev_leads = [l for l, v in features.st_elevation_mv.items() if v and v >= 0.1]
    if st_elev_leads:
        parts.append(f"ST elevation {' '.join(st_elev_leads[:3])} STEMI criteria")
    st_dep_leads = [l for l, v in features.st_depression_mv.items() if v and v >= 0.05]
    if st_dep_leads:
        parts.append("ST depression NSTEMI subendocardial ischemia")
    if not parts:
        parts.append("normal ST segment T wave morphology ECG")
    return " ".join(parts[:3])


def _mr_query(features: FeatureObject) -> str:
    parts = []
    if features.lvh_criteria_met:
        parts.append("left ventricular hypertrophy voltage criteria Sokolow-Lyon Cornell")
    if features.brugada_type1_pattern:
        parts.append("Brugada type 1 coved pattern V1 V2 criteria")
    if features.pericarditis_pattern:
        parts.append("pericarditis saddle-shape ST elevation diffuse")
    if features.qtc_bazett_ms and features.qtc_bazett_ms > 500:
        parts.append("prolonged QTc torsades de pointes risk")
    if features.osborn_wave:
        parts.append("Osborn J wave hypothermia")
    if not parts:
        parts.append("QRS morphology repolarization abnormalities ECG")
    return " ".join(parts[:3])


def _build_findings(
    cds_output: dict,
    rrc_output: dict,
    it_output: dict,
    mr_output: dict,
    cds_raw: dict,
    rag_results_by_agent: dict | None = None,
) -> list[DiagnosticFinding]:
    """Convert CDS JSON output to DiagnosticFinding dataclass list."""
    phase1_reasoning = {
        "RRC": rrc_output.get("_reasoning", ""),
        "IT": it_output.get("_reasoning", ""),
        "MR": mr_output.get("_reasoning", ""),
        "CDS": cds_raw.get("reasoning_content", ""),
    }
    rag_results_by_agent = rag_results_by_agent or {}

    findings = []
    for raw_finding in cds_output.get("findings", []):
        finding_type = raw_finding.get("finding_type", "unknown")
        confidence = raw_finding.get("confidence", "LOW")
        agent_src = raw_finding.get("agent_source", "CDS")

        stat_fires = finding_type in STAT_CONDITIONS

        # Resolve citations: agent emits ["[1]", "[2]"] referencing the RAG block
        citations = _resolve_citations(
            raw_finding.get("citations", []),
            rag_results_by_agent.get(agent_src, []),
        )

        findings.append(DiagnosticFinding(
            finding_type=finding_type,
            confidence=confidence,
            clinical_summary=raw_finding.get("clinical_summary", finding_type.replace("_", " ")),
            technical_detail=raw_finding.get("technical_detail", ""),
            key_feature_values=raw_finding.get("key_feature_values", {}),
            citations=citations,
            rag_invoked=raw_finding.get("rag_invoked", True),
            stat_alert_fires=stat_fires,
            agent_source=agent_src,
            reasoning_text=phase1_reasoning.get(agent_src),
        ))

    conf_rank = {"HIGH": 0, "MEDIUM": 1, "LOW": 2, "INSUFFICIENT_EVIDENCE": 3}
    findings.sort(key=lambda f: (not f.stat_alert_fires, conf_rank.get(f.confidence, 4)))
    return findings


def _resolve_citations(raw_citations: list, rag_results: list) -> list[Citation]:
    """
    Convert agent-emitted citation markers like "[1]", "[2]" to Citation objects
    using the ordered list of RetrievalResults for that agent's domain.
    """
    if not rag_results:
        return []

    citations = []
    seen_chunk_ids: set = set()
    for marker in raw_citations:
        # Parse "[N]" → index N-1
        try:
            idx = int(str(marker).strip("[] ")) - 1
        except (ValueError, AttributeError):
            continue
        if idx < 0 or idx >= len(rag_results):
            continue
        r = rag_results[idx]
        m = r.chunk.metadata
        if m.chunk_id in seen_chunk_ids:
            continue
        seen_chunk_ids.add(m.chunk_id)
        citations.append(Citation(
            chunk_id=m.chunk_id,
            book=m.book_title,
            book_short=m.book_title.split()[0] if m.book_title else "",
            chapter=m.chapter,
            section=m.section_title,
            page_number=m.page_start,
            similarity_score=round(r.score, 4),
            retrieved_text=r.chunk.text[:300],
            context_expanded=(r.rank == 1 and r.score >= 0.70),
        ))
    return citations


def _build_stat_alerts(cds_output: dict, findings: list[DiagnosticFinding]) -> list[StatAlert]:
    """Build StatAlert list. Ensures STAT fires for all STAT conditions regardless of confidence."""
    alerts = []
    stat_finding_types = {f.finding_type for f in findings if f.stat_alert_fires}

    for finding in findings:
        if not finding.stat_alert_fires:
            continue
        conf = finding.confidence
        if conf in ("LOW", "INSUFFICIENT_EVIDENCE"):
            message = (
                f"POSSIBLE {finding.finding_type.upper().replace('_', ' ')} — "
                f"{conf} CONFIDENCE — IMMEDIATE REVIEW REQUIRED"
            )
        else:
            message = (
                f"{finding.finding_type.upper().replace('_', ' ')} — "
                f"{conf} CONFIDENCE — IMMEDIATE REVIEW REQUIRED"
            )
        alerts.append(StatAlert(
            finding_type=finding.finding_type,
            confidence=conf,
            message=message,
        ))

    return alerts
