"""
IEC-004 — SDA-4 Implementation Contract: RAG Knowledge Base

Issuer: EPM
Recipient: SDA-4 Implementation Lead
Date: 2026-03-29
Status: OPEN
Prerequisite gates: SDA-4 Nodes 4.1–4.6 ALL GATE PASSED ✓
"""

# IEC-004: SDA-4 RAG Knowledge Base — Implementation Contract

## Scope

Build the complete offline-first RAG pipeline that ingests 4 ECG textbooks into a
FAISS vector store and exposes a `retrieve(query, top_k, book_filter)` interface
used by SDA-2 agents to ground their outputs.

Books path: /Users/amirsadjadtaleban/Documents/NewECG_Agentic/ecg-platform/books/

## Directory Layout

```
rag/
├── __init__.py
├── schemas.py          # Chunk, ChunkMetadata, RetrievalResult dataclasses
├── ingestion.py        # Node 4.1 — PDF → Section list
├── chunking.py         # Node 4.2 — Section → Chunk list
├── embedding.py        # Node 4.3 — Chunk → FAISS index
├── retrieval.py        # Node 4.4 — query → RetrievalResult list
├── safety.py           # Node 4.5 — hallucination + grounding check
├── attribution.py      # Node 4.6 — Citation parsing + rag_invoked flag
└── ingest_books.py     # CLI entry point: python -m rag.ingest_books
```

Data artefacts (gitignored):
```
data/rag/
├── chunks.jsonl        # All chunks with metadata (checkpoint)
└── faiss.index         # FAISS IndexFlatIP matrix
data/rag/chunks_meta.json  # Parallel metadata list for FAISS rows
```

## Module Contracts

### rag/schemas.py
```python
@dataclass
class ChunkMetadata:
    chunk_id: str           # MD5[:8] of (book_short + section_title + chunk_index)
    book_title: str         # Short name: "chous" | "marriotts" | "goldberger" | "ecgmadeeasy"
    chapter: str
    section_title: str
    page_start: int
    page_end: int
    chunk_index: int        # 0-based within section
    token_count: int

@dataclass
class Chunk:
    text: str
    metadata: ChunkMetadata

@dataclass
class RetrievalResult:
    chunk: Chunk
    score: float            # cosine similarity [0, 1]
    rank: int
```

### rag/ingestion.py — Node 4.1
- `extract_book(pdf_path, book_short) -> list[Section]`
- `Section` = `{title, chapter, page_start, page_end, text}`
- PyMuPDF `fitz.open()` → iterate pages, detect heading by font size > body threshold
- Body threshold: median font size on page; heading = font_size ≥ 1.2× median
- Minimum section size: 200 characters (merge short sections into previous)
- Figure blocks (image xrefs): attach caption text to preceding section's text

### rag/chunking.py — Node 4.2
- `chunk_section(section, max_tokens=600, min_tokens=300) -> list[Chunk]`
- Tokenise with `tiktoken.get_encoding("cl100k_base")`
- Split by sentence boundaries (`.`, `!`, `?` followed by space + capital)
- Tail chunk: if last chunk < `min_tokens` → merge with previous (guard: merged must be ≤ 800 tokens)
- `chunk_id` = `hashlib.md5(f"{book_short}|{section_title}|{chunk_index}".encode()).hexdigest()[:8]`

### rag/embedding.py — Node 4.3
- `EmbeddingStore` class
  - `__init__(index_path, meta_path)` — load existing or create new
  - `ingest_all_books(pdf_dir, checkpoint_path)` — process 4 books, JSONL checkpoint per batch of 50 chunks
  - `embed_chunks(chunks) -> np.ndarray` — batch openai `text-embedding-3-small` (1536-dim), normalise L2
  - `save()` / `load()` — FAISS `write_index` / `read_index`
- Retry: up to 3 attempts with exponential backoff (2s, 4s, 8s) per batch
- CLIP: lazy-loaded only when figure chunks are present; released after batch

### rag/retrieval.py — Node 4.4
- `retrieve(query, store, top_k=5, book_filter=None, similarity_threshold=0.35) -> list[RetrievalResult]`
- Embed query with same `text-embedding-3-small`, L2-normalise
- FAISS `index.search(q_vec, top_k * 3)` → raw distances
- Filter by `score >= similarity_threshold`
- If `book_filter` provided: filter metadata by `book_title`
- Adjacent deduplication: if consecutive results share `chunk_id` prefix → keep higher score
- Context expansion: if top result score ≥ 0.70 and `chunk_index > 0` → also fetch `chunk_index - 1` from same section (via metadata scan)
- Return at most `top_k` results sorted by score descending

### rag/safety.py — Node 4.5
- `GroundingCheck` dataclass: `passed: bool, failed_claims: list[str], warning: str | None`
- `check_grounding(agent_text, retrieved_chunks, signal_features) -> GroundingCheck`
  - Keyword overlap ≥ 0.35 required: `len(claim_words & chunk_words) / len(claim_words)`
  - Numeric contradiction: extract `(value, unit)` pairs from agent text; flag if not within ±15% of signal feature value
  - Out-of-scope patterns (MVP flag-only, not truncation):
    `["diagnos", "definit", "rule out", "confirm", "prescri", "treat", "medic"]`
  - STAT confidence floor: STAT conditions must carry confidence ≥ "LOW" (strip INSUFFICIENT_EVIDENCE STAT claims)

### rag/attribution.py — Node 4.6
- `Citation` dataclass: `book_title, chapter, page, figure_ref, quote_snippet`
- `InvalidCitation` dataclass: `raw_ref, reason`
- `parse_agent_citations(agent_text, retrieved_chunks) -> tuple[list[Citation], list[InvalidCitation]]`
  - Agent cites as `[REF:N]` where N is 1-based index into `retrieved_chunks`
  - Out-of-range N → `InvalidCitation(raw_ref=f"[REF:{N}]", reason="index_out_of_range")`
  - `rag_invoked: bool` = `len(retrieved_chunks) > 0`
- `NO_CITATION_TEXT = "No textbook source retrieved for this finding."`

## Ingestion CLI (rag/ingest_books.py)

```
python -m rag.ingest_books \
    --books-dir /Users/amirsadjadtaleban/Documents/NewECG_Agentic/ecg-platform/books \
    --output-dir data/rag \
    [--resume]   # skip books already in checkpoint
```

Estimated runtime: ~45min on CPU (openai embedding API, 4 books, ~8000 chunks).

## Integration with SDA-2 Agents

In `agents/context_builder.py`, each `build_*_context()` function accepts an optional
`rag_store: EmbeddingStore | None`. When provided:

```python
query = f"{finding_type} ECG criteria"
results = retrieve(query, rag_store, top_k=3)
rag_block = format_rag_block(results)   # "--- Textbook Evidence ---\n[REF:1] ..."
```

This rag_block is appended to the agent's user message before sending to DeepSeek.

## Done Criteria (VTs)

| VT | Test |
|----|------|
| VT-4.1 | `extract_book(goldberger_pdf, "goldberger")` → ≥ 50 sections, each ≥ 200 chars |
| VT-4.2 | Section with 1200 tokens → split into 2–3 chunks, no chunk > 800 tokens |
| VT-4.3 | `ingest_all_books()` on Goldberger only → FAISS index with correct row count |
| VT-4.4 | `retrieve("STEMI ST elevation criteria", store, top_k=5)` → all results score ≥ 0.35 |
| VT-4.5 | Numeric contradiction: agent says "HR=120" but signal shows HR=65 → flagged |
| VT-4.6 | Agent text with `[REF:99]` on 5-result set → `InvalidCitation` returned |

## Critical Constraints (from SDA-4 RRC reviews)

- Node 4.1: Figure size filter — skip images < 100×80 px
- Node 4.1: KMeans column split only when page has ≥ 2 text columns (data-driven, not hardcoded)
- Node 4.2: Tail merge guard — merged chunk must stay ≤ 800 tokens
- Node 4.3: CLIP lazy load; release after each batch (GPU/MPS memory)
- Node 4.4: FAISS raw matrix (no `reconstruct()` call — IndexFlatIP doesn't support it)
- Node 4.4: `SIMILARITY_THRESHOLD=0.35` is a placeholder — validate empirically post-ingest
- Node 4.5: Out-of-scope patterns: flag only, do NOT truncate output at MVP
- Node 4.6: `rag_invoked` bool distinguishes searched vs not-searched paths
