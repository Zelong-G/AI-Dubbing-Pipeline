"""Deterministic QA checks; semantic judgement remains backend-optional."""
from __future__ import annotations

from dataclasses import dataclass

from ai_dubbing.common.models import Cue
from ai_dubbing.common.text import english_words, has_cjk


@dataclass(frozen=True)
class QAResult:
    ok: bool
    issues: tuple[str, ...]


def inspect_translation(cue: Cue, translation: str) -> QAResult:
    issues: list[str] = []
    words = english_words(translation)
    if not translation.strip():
        issues.append("empty translation")
    if has_cjk(translation):
        issues.append("contains untranslated CJK characters")
    if len(words) < 1:
        issues.append("contains no English words")
    if len(cue.text) < 10 and len(words) > 28:
        issues.append("unlikely length for a short source cue")
    return QAResult(ok=not issues, issues=tuple(issues))
