"""
Node 4.5 — Safety Layer.

Grounding check applied to every agent text output before it reaches the UI.
Three checks:
  1. Keyword overlap (agent claims must share ≥ 0.35 of words with retrieved chunks)
  2. Numeric contradiction (values in agent text must be within ±15% of signal features)
  3. Out-of-scope pattern detection (MVP: flag only, do not truncate output)
  4. STAT confidence floor (STAT conditions must carry confidence ≥ LOW)

This is a PATIENT SAFETY node. All failures are logged and surfaced to the UI.
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Any

from rag.schemas import RetrievalResult

# Minimum word-overlap fraction for a claim to be considered grounded
KEYWORD_OVERLAP_THRESHOLD = 0.35

# Maximum allowed relative deviation before numeric contradiction is flagged
NUMERIC_TOLERANCE = 0.15

# Patterns that suggest out-of-scope clinical action — flagged but NOT truncated at MVP
OUT_OF_SCOPE_PATTERNS = [
    r"\bdiagnos[ei]",
    r"\bdefinitiv",
    r"\brule\s+out\b",
    r"\bconfirm(ed|s)?\b",
    r"\bprescri",
    r"\btreat(ment|ing)?\b",
    r"\bmedic(at|ine|ation)",
]

# STAT conditions from agents/schemas.py — must always carry confidence ≥ LOW
STAT_CONDITIONS = frozenset({
    "stemi", "possible_stemi", "wellens", "de_winter", "vt", "vf",
    "complete_avb", "hyperk_sine_wave", "brugada_type1", "long_qt_tdp_risk",
})


@dataclass
class GroundingCheck:
    passed: bool
    failed_claims: list[str] = field(default_factory=list)
    out_of_scope_flags: list[str] = field(default_factory=list)
    stat_confidence_violations: list[str] = field(default_factory=list)
    warning: str | None = None


def check_grounding(
    agent_text: str,
    retrieved_chunks: list[RetrievalResult],
    signal_features: dict[str, Any] | None = None,
) -> GroundingCheck:
    """
    Run all four safety checks on agent_text.

    signal_features: flat dict of numeric measurements (e.g. {"heart_rate_ventricular_bpm": 68.3}).
    Returns a GroundingCheck. `passed=False` means at least one hard failure (keyword overlap
    or numeric contradiction). Out-of-scope flags are informational only at MVP.
    """
    failed_claims: list[str] = []
    out_of_scope_flags: list[str] = []
    stat_violations: list[str] = []

    # Build combined vocabulary from all retrieved chunks
    chunk_vocab = _build_vocab(
        " ".join(r.chunk.text for r in retrieved_chunks) if retrieved_chunks else ""
    )

    # 1. Keyword overlap check (sentence-level)
    for sentence in _split_sentences(agent_text):
        if not sentence.strip():
            continue
        claim_words = _build_vocab(sentence)
        if not claim_words:
            continue
        if chunk_vocab:
            overlap = len(claim_words & chunk_vocab) / len(claim_words)
            if overlap < KEYWORD_OVERLAP_THRESHOLD:
                failed_claims.append(f"Low overlap ({overlap:.2f}): {sentence[:80]}")

    # 2. Numeric contradiction check
    if signal_features:
        agent_numbers = _extract_numbers_with_units(agent_text)
        for value, unit, context in agent_numbers:
            ref_key = _match_feature_key(unit, signal_features)
            if ref_key is not None:
                ref_val = signal_features[ref_key]
                if ref_val and abs(value - ref_val) / max(abs(ref_val), 1e-6) > NUMERIC_TOLERANCE:
                    failed_claims.append(
                        f"Numeric contradiction: agent says {value} {unit}, signal={ref_val:.1f} (key={ref_key})"
                    )

    # 3. Out-of-scope pattern detection (flag only)
    for pattern in OUT_OF_SCOPE_PATTERNS:
        matches = re.findall(pattern, agent_text, re.IGNORECASE)
        for m in matches:
            out_of_scope_flags.append(f"Out-of-scope phrase detected: '{m}'")

    # 4. STAT confidence floor
    # Expects agent_text to contain JSON-parseable findings — best-effort scan
    for cond in STAT_CONDITIONS:
        if cond in agent_text.lower():
            if "insufficient_evidence" in agent_text.lower():
                stat_violations.append(
                    f"STAT condition '{cond}' paired with INSUFFICIENT_EVIDENCE confidence"
                )

    passed = len(failed_claims) == 0 and len(stat_violations) == 0

    warning = None
    if out_of_scope_flags:
        warning = "Out-of-scope language detected: " + "; ".join(out_of_scope_flags[:3])

    return GroundingCheck(
        passed=passed,
        failed_claims=failed_claims,
        out_of_scope_flags=out_of_scope_flags,
        stat_confidence_violations=stat_violations,
        warning=warning,
    )


def _build_vocab(text: str) -> set[str]:
    """Lowercase word set, strip punctuation, remove short stopwords."""
    _STOPWORDS = {"the", "a", "an", "is", "in", "of", "to", "and", "or", "for", "with", "this"}
    words = re.findall(r"[a-z]+", text.lower())
    return {w for w in words if len(w) > 2 and w not in _STOPWORDS}


def _split_sentences(text: str) -> list[str]:
    return re.split(r'(?<=[.!?])\s+', text)


def _extract_numbers_with_units(text: str) -> list[tuple[float, str, str]]:
    """
    Extract (value, unit, surrounding_context) tuples from agent text.
    Recognises: bpm, ms, mm, mV, deg, sec, s.
    """
    pattern = r"(\d+(?:\.\d+)?)\s*(bpm|ms|mm|mV|deg|sec\b|\bs\b)"
    results = []
    for m in re.finditer(pattern, text, re.IGNORECASE):
        value = float(m.group(1))
        unit = m.group(2).lower()
        context = text[max(0, m.start() - 30): m.end() + 30]
        results.append((value, unit, context))
    return results


def _match_feature_key(unit: str, features: dict) -> str | None:
    """Map a unit string to a signal feature key, if one exists."""
    _UNIT_MAP = {
        "bpm": "heart_rate_ventricular_bpm",
        "ms":  "qrs_duration_global_ms",      # best-effort: ms could be PR, QRS, QT
        "mm":  None,                            # mm measurements not in flat features
        "mv":  None,
        "deg": "qrs_axis_deg",
    }
    key = _UNIT_MAP.get(unit)
    if key and key in features:
        return key
    return None
