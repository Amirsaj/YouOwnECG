"""
Node 4.2 — Chunking Strategy.

Splits extracted Sections into Chunks of 300–600 tokens using sentence-boundary
splitting. Tail chunks below MIN_TOKENS are merged into the previous chunk provided
the merged size stays ≤ MAX_TOKENS.

Entry point: chunk_section(section) -> list[Chunk]
             chunk_all_sections(sections) -> list[Chunk]
"""

from __future__ import annotations
import hashlib
import re

import tiktoken

from rag.schemas import Section, Chunk, ChunkMetadata

MAX_TOKENS = 600
MIN_TOKENS = 300
MERGE_GUARD_TOKENS = 800   # merged chunk must not exceed this

_ENC = tiktoken.get_encoding("cl100k_base")

# Sentence boundary pattern: ., !, ? followed by whitespace + capital letter
_SENTENCE_RE = re.compile(r'(?<=[.!?])\s+(?=[A-Z])')


def chunk_section(section: Section) -> list[Chunk]:
    """
    Split a Section into Chunks of MAX_TOKENS tokens.

    Splits at sentence boundaries. Tail chunk < MIN_TOKENS is merged into
    the previous chunk unless that would exceed MERGE_GUARD_TOKENS.
    """
    sentences = _SENTENCE_RE.split(section.text)
    chunks: list[Chunk] = []
    current_sentences: list[str] = []
    current_tokens = 0

    for sent in sentences:
        sent_tokens = len(_ENC.encode(sent))
        if current_tokens + sent_tokens > MAX_TOKENS and current_sentences:
            chunks.append(_make_chunk(section, current_sentences, len(chunks)))
            current_sentences = [sent]
            current_tokens = sent_tokens
        else:
            current_sentences.append(sent)
            current_tokens += sent_tokens

    if current_sentences:
        tail_text = " ".join(current_sentences)
        tail_tokens = len(_ENC.encode(tail_text))

        if chunks and tail_tokens < MIN_TOKENS:
            prev = chunks[-1]
            merged_text = prev.text + " " + tail_text
            merged_tokens = len(_ENC.encode(merged_text))
            if merged_tokens <= MERGE_GUARD_TOKENS:
                # Replace last chunk with merged version
                chunks[-1] = _rebuild_chunk(section, merged_text, prev.metadata.chunk_index, merged_tokens)
            else:
                chunks.append(_make_chunk(section, current_sentences, len(chunks)))
        else:
            chunks.append(_make_chunk(section, current_sentences, len(chunks)))

    return chunks


def chunk_all_sections(sections: list[Section]) -> list[Chunk]:
    """Chunk every section and return the combined flat list."""
    result: list[Chunk] = []
    for section in sections:
        result.extend(chunk_section(section))
    return result


def _make_chunk(section: Section, sentences: list[str], index: int) -> Chunk:
    text = " ".join(sentences).strip()
    token_count = len(_ENC.encode(text))
    chunk_id = _make_chunk_id(section.book_title, section.title, section.page_start, section.page_end, index)
    return Chunk(
        text=text,
        metadata=ChunkMetadata(
            chunk_id=chunk_id,
            book_title=section.book_title,
            chapter=section.chapter,
            section_title=section.title,
            page_start=section.page_start,
            page_end=section.page_end,
            chunk_index=index,
            token_count=token_count,
        ),
    )


def _rebuild_chunk(section: Section, text: str, index: int, token_count: int) -> Chunk:
    chunk_id = _make_chunk_id(section.book_title, section.title, section.page_start, section.page_end, index)
    return Chunk(
        text=text.strip(),
        metadata=ChunkMetadata(
            chunk_id=chunk_id,
            book_title=section.book_title,
            chapter=section.chapter,
            section_title=section.title,
            page_start=section.page_start,
            page_end=section.page_end,
            chunk_index=index,
            token_count=token_count,
        ),
    )


def _make_chunk_id(book_title: str, section_title: str, page_start: int, page_end: int, chunk_index: int) -> str:
    raw = f"{book_title}|{section_title}|{page_start}|{page_end}|{chunk_index}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]
