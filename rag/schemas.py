"""
RAG data model.

Three dataclasses used throughout Nodes 4.1–4.6:
  Section   — raw extracted section from a PDF book
  Chunk     — tokenised sub-section with metadata
  RetrievalResult — a scored Chunk returned by retrieve()
"""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Section:
    """A logical section parsed from a PDF book (Node 4.1 output)."""
    book_title: str          # short name: chous | marriotts | goldberger | ecgmadeeasy
    chapter: str
    title: str
    page_start: int
    page_end: int
    text: str                # concatenated plain text of the section


@dataclass
class ChunkMetadata:
    """Metadata attached to every Chunk."""
    chunk_id: str            # MD5[:8] of "book_title|section_title|chunk_index"
    book_title: str
    chapter: str
    section_title: str
    page_start: int
    page_end: int
    chunk_index: int         # 0-based position within parent section
    token_count: int


@dataclass
class Chunk:
    """A tokenised text unit ready for embedding (Node 4.2 output)."""
    text: str
    metadata: ChunkMetadata


@dataclass
class RetrievalResult:
    """A retrieved Chunk with its cosine similarity score (Node 4.4 output)."""
    chunk: Chunk
    score: float             # cosine similarity in [0, 1]
    rank: int                # 1-based rank in result list
