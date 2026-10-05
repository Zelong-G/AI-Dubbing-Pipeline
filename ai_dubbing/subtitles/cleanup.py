"""Safe subtitle cleanup before translation."""
from __future__ import annotations

import re

from ai_dubbing.common.models import Cue
from ai_dubbing.common.text import compact_whitespace


def clean_cues(cues: list[Cue]) -> list[Cue]:
    cleaned: list[Cue] = []
    for cue in cues:
        text = re.sub(r"[♪♬]+", "", cue.text)
        text = compact_whitespace(text)
        if text:
            cleaned.append(Cue(cue.index, cue.start, cue.end, text, cue.speaker))
    return cleaned
