"""
Node 4.1 — Book Ingestion Pipeline.

Extracts logical sections from ECG textbook PDFs using PyMuPDF.
Each section is defined by heading detection (font size ≥ 1.2× median body font).
Figures are represented by their caption text appended to the preceding section.

Entry point: extract_book(pdf_path, book_title) -> list[Section]
"""

from __future__ import annotations
import statistics
from pathlib import Path
from typing import Optional

import fitz  # PyMuPDF

from rag.schemas import Section

# Minimum section text length (chars). Sections below this are merged into previous.
MIN_SECTION_CHARS = 200

# Multiplier above median font size to classify a span as a heading.
HEADING_FONT_RATIO = 1.2

# Minimum figure image dimensions to include (px). Smaller images are decorative.
MIN_FIGURE_WIDTH = 100
MIN_FIGURE_HEIGHT = 80


def extract_book(pdf_path: str | Path, book_title: str) -> list[Section]:
    """
    Extract all logical sections from a PDF ECG textbook.

    Sections are detected by heading spans (font size ≥ 1.2× median page body font).
    Figure captions are appended to the text of the section where the figure appears.
    Short sections (< MIN_SECTION_CHARS) are merged into the preceding section.

    Returns list of Section ordered by page.
    """
    doc = fitz.open(str(pdf_path))
    raw_sections = _extract_raw_sections(doc, book_title)
    sections = _merge_short_sections(raw_sections)
    doc.close()
    return sections


def _extract_raw_sections(doc: fitz.Document, book_title: str) -> list[Section]:
    """Iterate pages, detect headings, accumulate section text blocks."""
    sections: list[Section] = []
    current: Optional[dict] = None

    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]

        body_font_sizes = _collect_body_font_sizes(blocks)
        if not body_font_sizes:
            continue
        median_size = statistics.median(body_font_sizes)
        heading_threshold = median_size * HEADING_FONT_RATIO

        # Detect KMeans column split only when page has ≥ 2 text columns
        column_x_boundaries = _detect_columns(blocks)

        for block in blocks:
            if block["type"] == 1:  # image block
                caption = _extract_figure_caption(block, page, page_num)
                if caption and current is not None:
                    current["text"] += f"\n[Figure caption: {caption}]"
                continue

            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span["text"].strip()
                    if not text:
                        continue

                    font_size = span["size"]
                    is_heading = (
                        font_size >= heading_threshold
                        and len(text) < 200
                        and len(text) > 3           # exclude bullet chars, single symbols
                        and text[0].isalnum()       # must start with letter or digit
                    )

                    if is_heading:
                        if current is not None:
                            sections.append(_finalise_section(current, page_num - 1, book_title))
                        current = {
                            "chapter": _infer_chapter(sections, text),
                            "title": text,
                            "page_start": page_num,
                            "text": "",
                        }
                    else:
                        if current is None:
                            current = {
                                "chapter": "Preface",
                                "title": "Introduction",
                                "page_start": page_num,
                                "text": "",
                            }
                        current["text"] += " " + text

    if current is not None:
        sections.append(_finalise_section(current, len(doc), book_title))

    return sections


def _collect_body_font_sizes(blocks: list) -> list[float]:
    """Collect all span font sizes from text blocks (type 0)."""
    sizes = []
    for block in blocks:
        if block["type"] != 0:
            continue
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                if span["text"].strip():
                    sizes.append(span["size"])
    return sizes


def _detect_columns(blocks: list) -> list[float]:
    """
    Return x-midpoints of detected text columns if page has ≥ 2 columns.
    Uses basic clustering of block x-origins; returns [] for single-column pages.
    """
    x_origins = [b["bbox"][0] for b in blocks if b["type"] == 0]
    if len(x_origins) < 6:
        return []

    # Sort and find the largest gap — if gap > 80px, assume two-column layout
    x_sorted = sorted(set(round(x, -1) for x in x_origins))  # round to 10px buckets
    if len(x_sorted) < 2:
        return []

    gaps = [(x_sorted[i + 1] - x_sorted[i], x_sorted[i]) for i in range(len(x_sorted) - 1)]
    max_gap, gap_start = max(gaps, key=lambda t: t[0])
    if max_gap > 80:
        return [gap_start, gap_start + max_gap]
    return []


def _extract_figure_caption(block: dict, page: fitz.Page, page_num: int) -> Optional[str]:
    """
    For an image block, extract caption text from the region immediately below the image.
    Returns None if image is below minimum size or no caption found.
    """
    x0, y0, x1, y1 = block["bbox"]
    width = x1 - x0
    height = y1 - y0
    if width < MIN_FIGURE_WIDTH or height < MIN_FIGURE_HEIGHT:
        return None

    # Look for text in a 30px strip below the image
    caption_rect = fitz.Rect(x0, y1, x1, y1 + 30)
    caption_text = page.get_text("text", clip=caption_rect).strip()
    return caption_text if caption_text else None


def _infer_chapter(existing_sections: list[Section], heading_text: str) -> str:
    """
    Infer chapter name from heading text or inherit from previous section.
    Simple heuristic: headings starting with "Chapter" or a digit set the chapter.
    """
    if heading_text.lower().startswith("chapter") or (heading_text and heading_text[0].isdigit()):
        return heading_text
    if existing_sections:
        return existing_sections[-1].chapter
    return "Unknown"


def _finalise_section(current: dict, page_end: int, book_title: str) -> Section:
    return Section(
        book_title=book_title,
        chapter=current["chapter"],
        title=current["title"],
        page_start=current["page_start"],
        page_end=page_end,
        text=current["text"].strip(),
    )


def _dedup_empty_sections(sections: list[Section]) -> list[Section]:
    """
    Disambiguate sections that share (title, page_start, page_end).
    Empty duplicates (< 10 chars) are dropped; non-empty duplicates have a
    numeric suffix appended to their title to ensure unique chunk IDs.
    """
    from collections import Counter
    key_count: Counter = Counter()
    result = []
    for sec in sections:
        key = (sec.title, sec.page_start, sec.page_end)
        key_count[key] += 1
        if key_count[key] > 1 and len(sec.text) < 10:
            continue
        if key_count[key] > 1:
            # Append ordinal to title so chunk_id hash differs
            sec = Section(
                book_title=sec.book_title,
                chapter=sec.chapter,
                title=f"{sec.title} ({key_count[key]})",
                page_start=sec.page_start,
                page_end=sec.page_end,
                text=sec.text,
            )
        result.append(sec)
    return result


def _merge_short_sections(sections: list[Section]) -> list[Section]:
    """Merge sections shorter than MIN_SECTION_CHARS into the preceding section."""
    sections = _dedup_empty_sections(sections)
    if not sections:
        return sections

    merged: list[Section] = [sections[0]]
    for sec in sections[1:]:
        if len(sec.text) < MIN_SECTION_CHARS and merged:
            prev = merged[-1]
            merged[-1] = Section(
                book_title=prev.book_title,
                chapter=prev.chapter,
                title=prev.title,
                page_start=prev.page_start,
                page_end=sec.page_end,
                text=prev.text + "\n" + sec.text,
            )
        else:
            merged.append(sec)
    return merged
