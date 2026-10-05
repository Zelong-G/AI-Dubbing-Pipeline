"""Conservative normalization after a backend response."""
from __future__ import annotations

import re

from ai_dubbing.common.text import compact_whitespace


def normalize_translation(value: str) -> str:
    value = compact_whitespace(value.replace("“", '"').replace("”", '"'))
    value = re.sub(r"\s+([,.!?;:])", r"\1", value)
    return value.strip("` ")
