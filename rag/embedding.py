"""
Node 4.3 — Embedding & Vector Store.

Uses sentence-transformers/all-MiniLM-L6-v2 (384-dim) to embed chunks into a
FAISS IndexFlatIP matrix (inner product on L2-normalised vectors = cosine
similarity).

Checkpointing: after every BATCH_SIZE chunks the embeddings and metadata are
appended to a JSONL file so ingestion can resume on failure.

Entry point: EmbeddingStore class
"""

from __future__ import annotations
import json
import os
from dataclasses import asdict
from pathlib import Path
from typing import Optional

import numpy as np

from rag.schemas import Chunk, ChunkMetadata

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM = 384
BATCH_SIZE = 50

# Module-level lazy model cache
_model = None


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


class EmbeddingStore:
    """
    FAISS-backed vector store for ECG textbook chunks.

    Usage:
        store = EmbeddingStore("data/rag/faiss.index", "data/rag/chunks_meta.json")
        store.ingest_all_books(pdf_dir, checkpoint_path="data/rag/chunks.jsonl")
        store.save()

        # Later:
        store = EmbeddingStore.load("data/rag/faiss.index", "data/rag/chunks_meta.json")
        results = store.search(query_vec, top_k=5)
    """

    def __init__(self, index_path: str, meta_path: str):
        self.index_path = Path(index_path)
        self.meta_path = Path(meta_path)
        self._index = None          # faiss.IndexFlatIP — lazy init
        self._meta: list[dict] = [] # parallel list to FAISS rows

    # ------------------------------------------------------------------
    # Ingestion
    # ------------------------------------------------------------------

    def ingest_all_books(self, pdf_dir: str | Path, checkpoint_path: str | Path) -> None:
        """
        Ingest 4 ECG textbooks from pdf_dir.

        Book short names must match filenames (case-insensitive prefix match):
          chous, marriotts, goldberger, ecgmadeeasy
        Chunks are embedded in batches of BATCH_SIZE with JSONL checkpointing.
        Existing checkpoint entries are skipped (resume support).
        """
        from rag.ingestion import extract_book
        from rag.chunking import chunk_all_sections

        checkpoint_path = Path(checkpoint_path)
        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)

        already_done: set[str] = set()
        if checkpoint_path.exists():
            with open(checkpoint_path) as f:
                for line in f:
                    try:
                        rec = json.loads(line)
                        already_done.add(rec["metadata"]["chunk_id"])
                    except (json.JSONDecodeError, KeyError):
                        pass
            print(f"Resuming: {len(already_done)} chunks already embedded")

        book_map = _find_books(pdf_dir)
        all_pending: list[Chunk] = []

        for book_short, pdf_path in sorted(book_map.items()):
            print(f"Extracting {book_short} from {pdf_path.name} ...")
            sections = extract_book(pdf_path, book_short)
            chunks = chunk_all_sections(sections)
            new_chunks = [c for c in chunks if c.metadata.chunk_id not in already_done]
            print(f"  {len(chunks)} chunks total, {len(new_chunks)} new")
            all_pending.extend(new_chunks)

        print(f"Embedding {len(all_pending)} chunks ...")
        self._embed_and_store(all_pending, checkpoint_path)

    def _embed_and_store(self, chunks: list[Chunk], checkpoint_path: Path) -> None:
        """Embed chunks in batches, appending to checkpoint and FAISS index."""
        import faiss

        if self._index is None:
            self._index = faiss.IndexFlatIP(EMBEDDING_DIM)

        with open(checkpoint_path, "a") as ckpt:
            for i in range(0, len(chunks), BATCH_SIZE):
                batch = chunks[i: i + BATCH_SIZE]
                texts = [c.text for c in batch]

                vecs = self._embed_with_retry(texts)
                if vecs is None:
                    print(f"  Batch {i // BATCH_SIZE} failed after retries — skipping")
                    continue

                self._index.add(vecs)
                for j, chunk in enumerate(batch):
                    meta = asdict(chunk.metadata)
                    self._meta.append(meta)
                    ckpt.write(json.dumps({"text": chunk.text, "metadata": meta}) + "\n")

                print(f"  Embedded {min(i + BATCH_SIZE, len(chunks))}/{len(chunks)} chunks")

    def _embed_with_retry(self, texts: list[str]) -> Optional[np.ndarray]:
        """Embed texts using local sentence-transformers model."""
        try:
            model = _get_model()
            vecs = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
            return np.array(vecs, dtype=np.float32)
        except Exception as exc:
            print(f"  Embedding failed: {exc}")
            return None

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self) -> None:
        """Write FAISS index and metadata to disk."""
        import faiss

        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self._index, str(self.index_path))
        with open(self.meta_path, "w") as f:
            json.dump(self._meta, f)
        print(f"Saved {len(self._meta)} vectors to {self.index_path}")

    @classmethod
    def load(cls, index_path: str, meta_path: str) -> "EmbeddingStore":
        """Load a previously saved store from disk."""
        import faiss

        store = cls(index_path, meta_path)
        store._index = faiss.read_index(str(index_path))
        with open(meta_path) as f:
            store._meta = json.load(f)
        return store

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(self, query_vec: np.ndarray, top_k: int) -> list[tuple[int, float]]:
        """
        Return list of (row_index, score) for top_k nearest neighbours.
        query_vec must be L2-normalised and shape (1, EMBEDDING_DIM).
        """
        if self._index is None or self._index.ntotal == 0:
            return []
        k = min(top_k, self._index.ntotal)
        scores, indices = self._index.search(query_vec, k)
        return [(int(idx), float(score)) for idx, score in zip(indices[0], scores[0]) if idx >= 0]

    def get_meta(self, row_index: int) -> Optional[dict]:
        if 0 <= row_index < len(self._meta):
            return self._meta[row_index]
        return None

    def get_text(self, row_index: int, checkpoint_path: str | Path) -> Optional[str]:
        """Retrieve chunk text from the JSONL checkpoint by row index."""
        checkpoint_path = Path(checkpoint_path)
        if not checkpoint_path.exists():
            return None
        with open(checkpoint_path) as f:
            for i, line in enumerate(f):
                if i == row_index:
                    try:
                        return json.loads(line)["text"]
                    except (json.JSONDecodeError, KeyError):
                        return None
        return None


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _find_books(pdf_dir: str | Path) -> dict[str, Path]:
    """Match PDF files to book short names by filename prefix heuristics."""
    pdf_dir = Path(pdf_dir)
    name_map = {
        "chous": None,
        "marriotts": None,
        "goldberger": None,
        "ecgmadeeasy": None,
    }
    keywords = {
        "chous": ["chou"],
        "marriotts": ["marriott"],
        "goldberger": ["goldberger"],
        "ecgmadeeasy": ["ecg_made", "ecgmade", "easy", "fourth"],
    }
    for pdf in sorted(pdf_dir.glob("*.pdf")):
        lower = pdf.name.lower()
        for short, kws in keywords.items():
            if any(k in lower for k in kws):
                name_map[short] = pdf
                break

    missing = [k for k, v in name_map.items() if v is None]
    if missing:
        print(f"Warning: could not find PDFs for: {missing}")
    return {k: v for k, v in name_map.items() if v is not None}


def embed_query(text: str) -> np.ndarray:
    """Embed a single query string. Returns L2-normalised (1, EMBEDDING_DIM) array."""
    model = _get_model()
    vec = model.encode([text], normalize_embeddings=True, show_progress_bar=False)
    return np.array(vec, dtype=np.float32)
