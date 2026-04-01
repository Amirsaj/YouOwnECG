"""
Node 4.6 — Source Attribution System.

Parses [REF:N] citation markers from agent output text and maps them to
structured Citation objects backed by RetrievalResult metadata.

Out-of-range indices produce InvalidCitation records (never silently dropped).
The `rag_invoked` flag distinguishes searched vs not-searched code paths.
"""

from __future__ import annotations
import re
from dataclasses import dataclass

from rag.schemas import RetrievalResult

NO_CITATION_TEXT = "No textbook source retrieved for this finding."


@dataclass
class Citation:
    """A structured textbook citation mapped from a [REF:N] marker."""
    ref_index: int           # 1-based N from the agent output
    book_title: str
    chapter: str
    page_start: int
    page_end: int
    section_title: str
    quote_snippet: str | None   # First 120 chars of the chunk text


@dataclass
class InvalidCitation:
    """A [REF:N] marker that could not be resolved."""
    raw_ref: str             # e.g. "[REF:99]"
    reason: str              # "index_out_of_range" | "malformed"


def parse_agent_citations(
    agent_text: str,
    retrieved_chunks: list[RetrievalResult],
) -> tuple[list[Citation], list[InvalidCitation]]:
    """
    Extract all [REF:N] markers from agent_text and resolve them against
    retrieved_chunks (1-based indexing into the list).

    Returns:
        valid:   list of Citation for every resolved [REF:N]
        invalid: list of InvalidCitation for every unresolvable [REF:N]
    """
    refs = re.findall(r"\[REF:(\d+)\]", agent_text)
    valid: list[Citation] = []
    invalid: list[InvalidCitation] = []

    for ref_str in refs:
        n = int(ref_str)
        if n < 1 or n > len(retrieved_chunks):
            invalid.append(InvalidCitation(
                raw_ref=f"[REF:{n}]",
                reason="index_out_of_range",
            ))
            continue

        result = retrieved_chunks[n - 1]
        meta = result.chunk.metadata
        snippet = result.chunk.text[:120].strip() or None

        valid.append(Citation(
            ref_index=n,
            book_title=meta.book_title,
            chapter=meta.chapter,
            page_start=meta.page_start,
            page_end=meta.page_end,
            section_title=meta.section_title,
            quote_snippet=snippet,
        ))

    return valid, invalid


def rag_invoked(retrieved_chunks: list[RetrievalResult]) -> bool:
    """True when retrieval was performed and returned at least one result."""
    return len(retrieved_chunks) > 0


def format_citation_footnotes(citations: list[Citation]) -> str:
    """
    Render a compact footnote block for display alongside a finding.

    Example:
      [1] GOLDBERGER | Chapter 5 | p.42–44 — ST Elevation Criteria
    """
    if not citations:
        return NO_CITATION_TEXT
    lines = []
    for c in citations:
        page_range = f"p.{c.page_start}" if c.page_start == c.page_end else f"p.{c.page_start}–{c.page_end}"
        lines.append(
            f"[{c.ref_index}] {c.book_title.upper()} | {c.chapter} | {page_range} — {c.section_title}"
        )
    return "\n".join(lines)
