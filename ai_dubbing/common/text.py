"""Text cleanup deliberately kept independent of any language model."""
from __future__ import annotations

import re


def compact_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def has_cjk(value: str) -> bool:
    return bool(re.search(r"[\u3400-\u4dbf\u4e00-\u9fff]", value))


def english_words(value: str) -> list[str]:
    return re.findall(r"[A-Za-z]+(?:['’][A-Za-z]+)?", value)


def sentence_boundaries(value: str) -> list[str]:
    pieces = re.split(r"(?<=[.!?])\s+", compact_whitespace(value))
    return [piece for piece in pieces if piece]
