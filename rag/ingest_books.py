"""
CLI entry point for book ingestion.

Usage:
    python -m rag.ingest_books --books-dir <path> --output-dir data/rag [--resume]

Estimated runtime: ~45 min on CPU (OpenAI embedding API, 4 books, ~8000 chunks).
Requires OPENAI_API_KEY environment variable.
"""

from __future__ import annotations
import argparse
import os
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest ECG textbooks into FAISS vector store")
    parser.add_argument("--books-dir", required=True, help="Directory containing the 4 PDF books")
    parser.add_argument("--output-dir", default="data/rag", help="Output directory for FAISS index and metadata")
    parser.add_argument("--resume", action="store_true", help="Resume from existing checkpoint")
    args = parser.parse_args()

    books_dir = Path(args.books_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    index_path = output_dir / "faiss.index"
    meta_path = output_dir / "chunks_meta.json"
    checkpoint_path = output_dir / "chunks.jsonl"

    from rag.embedding import EmbeddingStore

    if index_path.exists() and not args.resume:
        print("Index already exists. Use --resume to add new chunks or delete data/rag/ to rebuild.")
        sys.exit(0)

    if index_path.exists() and args.resume:
        print("Loading existing index for resume...")
        store = EmbeddingStore.load(str(index_path), str(meta_path))
    else:
        store = EmbeddingStore(str(index_path), str(meta_path))

    store.ingest_all_books(books_dir, checkpoint_path)
    store.save()

    print(f"\nIngestion complete.")
    print(f"  Index: {index_path} ({store._index.ntotal} vectors)")
    print(f"  Metadata: {meta_path} ({len(store._meta)} entries)")
    print(f"  Checkpoint: {checkpoint_path}")


if __name__ == "__main__":
    main()
