"""Chapter parsing for plain text supplied by the user."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


_CHAPTER = re.compile(
    r"(?im)^\s*(?:chapter\s+\d+\b.*|第\s*[0-9一二三四五六七八九十百千万两〇零]+\s*[章节回卷篇].*)$"
)


@dataclass(frozen=True)
class Chapter:
    index: int
    title: str
    text: str


def read_text(path: Path) -> str:
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return raw.decode(encoding).replace("\r\n", "\n").replace("\r", "\n")
        except UnicodeDecodeError:
            continue
    raise UnicodeError("Text must use UTF-8 or a compatible Chinese text encoding.")


def parse_chapters(text: str) -> list[Chapter]:
    headings = list(_CHAPTER.finditer(text))
    if not headings:
        clean = text.strip()
        return [Chapter(1, "Chapter 1", clean)] if clean else []
    chapters: list[Chapter] = []
    for number, match in enumerate(headings, start=1):
        end = headings[number].start() if number < len(headings) else len(text)
        body = text[match.end() : end].strip()
        chapters.append(Chapter(number, match.group().strip(), body))
    return chapters


def split_sentences(text: str) -> list[str]:
    pieces = re.split(r"(?<=[。！？.!?])\s*", text.strip())
    return [piece.strip() for piece in pieces if piece.strip()]
