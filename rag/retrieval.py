"""
Node 4.4 — Retrieval Pipeline.

retrieve() takes a natural-language query and returns the top-k most relevant
Chunks from the FAISS store, with adjacent deduplication and context expansion.

The SIMILARITY_THRESHOLD (default 0.35) is a placeholder — validate empirically
after full book ingestion by sampling known ECG criteria queries.
"""

from __future__ import annotations
from typing import Optional

import numpy as np

from rag.schemas import Chunk, ChunkMetadata, RetrievalResult

SIMILARITY_THRESHOLD = 0.35   # empirical placeholder — validate post-ingest
CONTEXT_EXPANSION_THRESHOLD = 0.70  # fetch preceding chunk if top result ≥ this score


def retrieve(
    query: str,
    store,                          # EmbeddingStore
    top_k: int = 5,
    book_filter: Optional[str] = None,
    similarity_threshold: float = SIMILARITY_THRESHOLD,
    checkpoint_path: str = "data/rag/chunks.jsonl",
) -> list[RetrievalResult]:
    """
    Retrieve top-k Chunks most relevant to query.

    Steps:
      1. Embed query with text-embedding-3-small (L2-normalised)
      2. FAISS inner-product search (top_k * 3 candidates)
      3. Filter by similarity_threshold
      4. Filter by book_filter if provided
      5. Adjacent deduplication (same chunk_id prefix → keep higher score)
      6. Context expansion: if top result ≥ 0.70, also fetch chunk_index - 1
      7. Return at most top_k results sorted by score descending
    """
    from rag.embedding import embed_query

    q_vec = embed_query(query)
    raw_hits = store.search(q_vec, top_k * 3)

    candidates: list[tuple[int, float, dict]] = []
    for row_idx, score in raw_hits:
        if score < similarity_threshold:
            continue
        meta = store.get_meta(row_idx)
        if meta is None:
            continue
        if book_filter and meta.get("book_title") != book_filter:
            continue
        candidates.append((row_idx, score, meta))

    candidates = _deduplicate_adjacent(candidates)

    if candidates and candidates[0][1] >= CONTEXT_EXPANSION_THRESHOLD:
        candidates = _expand_context(candidates, store)

    results: list[RetrievalResult] = []
    for rank, (row_idx, score, meta) in enumerate(candidates[:top_k], start=1):
        text = store.get_text(row_idx, checkpoint_path) or ""
        chunk = _meta_to_chunk(text, meta)
        results.append(RetrievalResult(chunk=chunk, score=score, rank=rank))

    return results


def _deduplicate_adjacent(
    candidates: list[tuple[int, float, dict]],
) -> list[tuple[int, float, dict]]:
    """
    Remove duplicates where two results share the same chunk_id.
    Keep the one with the higher score.
    """
    seen: dict[str, tuple[int, float, dict]] = {}
    for row_idx, score, meta in candidates:
        cid = meta.get("chunk_id", "")
        if cid not in seen or score > seen[cid][1]:
            seen[cid] = (row_idx, score, meta)
    # Restore original score-descending order
    return sorted(seen.values(), key=lambda t: t[1], reverse=True)


def _expand_context(
    candidates: list[tuple[int, float, dict]],
    store,
) -> list[tuple[int, float, dict]]:
    """
    If the top result is very confident (≥ CONTEXT_EXPANSION_THRESHOLD) and its
    chunk_index > 0, attempt to find and prepend the preceding chunk from the same
    section. Uses linear metadata scan (IndexFlatIP does not support reconstruct()).
    """
    top_meta = candidates[0][2]
    if top_meta.get("chunk_index", 0) == 0:
        return candidates

    # Scan store metadata for the preceding chunk
    prev_chunk_index = top_meta["chunk_index"] - 1
    for row_idx, meta in enumerate(store._meta):
        if (
            meta.get("book_title") == top_meta["book_title"]
            and meta.get("section_title") == top_meta["section_title"]
            and meta.get("chunk_index") == prev_chunk_index
        ):
            # Insert at position 0 with a synthetic score slightly below the top
            preceding_score = candidates[0][1] * 0.95
            candidates.insert(0, (row_idx, preceding_score, meta))
            break

    return candidates


def _meta_to_chunk(text: str, meta: dict) -> Chunk:
    return Chunk(
        text=text,
        metadata=ChunkMetadata(
            chunk_id=meta.get("chunk_id", ""),
            book_title=meta.get("book_title", ""),
            chapter=meta.get("chapter", ""),
            section_title=meta.get("section_title", ""),
            page_start=meta.get("page_start", 0),
            page_end=meta.get("page_end", 0),
            chunk_index=meta.get("chunk_index", 0),
            token_count=meta.get("token_count", 0),
        ),
    )


def format_rag_block(results: list[RetrievalResult]) -> str:
    """
    Format retrieved results as a prompt-ready text block.
    Agent cites as [N] (1-based).
    """
    if not results:
        return ""
    lines = ["--- Textbook Evidence ---"]
    for r in results:
        m = r.chunk.metadata
        header = f"[{r.rank}] {m.book_title.upper()} | {m.chapter} | p.{m.page_start}"
        lines.append(f"{header}\n{r.chunk.text}")
    return "\n\n".join(lines)
