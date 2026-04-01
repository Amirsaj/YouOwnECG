"""
Agent input/output schemas for SDA-2.

DiagnosticFinding carries both clinical_summary (≤15 words, plain English)
and technical_detail (clinical terminology + values) in a single agent pass.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


STAT_CONDITIONS = frozenset({
    "stemi", "possible_stemi", "wellens", "de_winter",
    "anterior_stemi", "inferior_stemi", "lateral_stemi",
    "vt", "vf", "complete_avb", "hyperk_sine_wave",
    "brugada_type1", "long_qt", "sgarbossa_stemi",
})

CONFIDENCE_LEVELS = ("HIGH", "MEDIUM", "LOW", "INSUFFICIENT_EVIDENCE")


@dataclass
class Citation:
    chunk_id: str
    book: str
    book_short: str
    chapter: str
    section: str
    page_number: int
    similarity_score: float
    retrieved_text: str
    context_expanded: bool = False


@dataclass
class DiagnosticFinding:
    finding_type: str               # e.g. "possible_stemi", "afib", "lbbb"
    confidence: str                 # HIGH | MEDIUM | LOW | INSUFFICIENT_EVIDENCE
    clinical_summary: str           # ≤ 15 words, plain language
    technical_detail: str           # full clinical terminology with values
    key_feature_values: dict        # subset of FeatureObject fields that drove this finding
    citations: list[Citation]       # textbook evidence; empty list if none
    rag_invoked: bool               # False for pure signal measurements
    stat_alert_fires: bool          # True if finding_type in STAT_CONDITIONS (any confidence)
    agent_source: str               # "RRC" | "IT" | "MR" | "CDS"
    reasoning_text: Optional[str]   # verbatim agent chain-of-thought


@dataclass
class StatAlert:
    finding_type: str
    confidence: str
    message: str                    # includes confidence qualifier if LOW/INSUFFICIENT


@dataclass
class DiagnosticResult:
    ecg_id: str
    findings: list[DiagnosticFinding]
    stat_alerts: list[StatAlert]
    measurements: dict              # deterministic signal measurements (HR, PR, QRS, QTc, axis)
    overall_quality: str            # from QualityReport
    pipeline_version: str
    model_version: str              # DeepSeek model ID used
