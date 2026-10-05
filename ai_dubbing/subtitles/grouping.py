"""Conservative grouping of split subtitle cues into TTS utterances."""
from __future__ import annotations

from dataclasses import dataclass

from ai_dubbing.common.models import Cue


@dataclass(frozen=True)
class CueGroup:
    index: int
    source_indices: tuple[int, ...]
    start: float
    end: float
    text: str

    @property
    def duration(self) -> float:
        return self.end - self.start


def conservative_join_decisions(cues: list[Cue], *, max_gap: float = 0.18) -> dict[int, bool]:
    """Join only clear continuations; uncertain boundaries remain separate.

    A model-based boundary classifier can provide this same mapping in a richer
    deployment. The default keeps an auditable deterministic policy.
    """
    decisions: dict[int, bool] = {}
    terminal = ("。", "！", "？", "!", "?", ".")
    continuation = ("，", "、", ",", ":", "：", "-", "…")
    for left, right in zip(cues, cues[1:]):
        gap = max(0.0, right.start - left.end)
        decisions[left.index] = gap <= max_gap and left.text.rstrip().endswith(continuation)
        if left.text.rstrip().endswith(terminal):
            decisions[left.index] = False
    return decisions


def build_groups(
    cues: list[Cue],
    joins: dict[int, bool],
    *,
    max_cues: int = 3,
    max_seconds: float = 5.0,
) -> list[CueGroup]:
    if not cues:
        return []
    groups: list[list[Cue]] = []
    current = [cues[0]]
    for left, right in zip(cues, cues[1:]):
        proposed_seconds = right.end - current[0].start
        may_join = joins.get(left.index, False)
        if may_join and len(current) < max_cues and proposed_seconds <= max_seconds:
            current.append(right)
        else:
            groups.append(current)
            current = [right]
    groups.append(current)
    return [
        CueGroup(
            index=index,
            source_indices=tuple(cue.index for cue in group),
            start=group[0].start,
            end=group[-1].end,
            text=" ".join(cue.text for cue in group),
        )
        for index, group in enumerate(groups, start=1)
    ]
