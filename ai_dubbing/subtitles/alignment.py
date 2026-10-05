"""Readable English subtitle segmentation and deterministic timeline remapping."""
from __future__ import annotations

import math
import re

from ai_dubbing.common.models import Cue, SlowRegion


def map_timestamp(source_seconds: float, regions: list[SlowRegion]) -> float:
    """Map a source time onto a timeline containing local slowdowns."""
    result = source_seconds
    for region in sorted(regions, key=lambda value: value.start):
        if source_seconds <= region.start:
            break
        covered = min(source_seconds, region.end) - region.start
        if covered > 0:
            result += covered * (1 / region.speed - 1)
    return result


def remap_cues(cues: list[Cue], regions: list[SlowRegion]) -> list[Cue]:
    remapped: list[Cue] = []
    for cue in cues:
        start, end = map_timestamp(cue.start, regions), map_timestamp(cue.end, regions)
        remapped.append(Cue(cue.index, start, max(end, start + 0.05), cue.text, cue.speaker))
    return remapped


def split_for_display(text: str, count: int) -> list[str]:
    words = text.split()
    if count <= 1 or len(words) <= 1:
        return [text.strip()]
    count = min(count, len(words))
    width = math.ceil(len(words) / count)
    return [" ".join(words[start : start + width]) for start in range(0, len(words), width)]


def wrap_two_lines(text: str, maximum: int = 38) -> str:
    if len(text) <= maximum:
        return text
    words = text.split()
    candidates = []
    for position in range(1, len(words)):
        left, right = " ".join(words[:position]), " ".join(words[position:])
        if len(left) <= maximum and len(right) <= maximum:
            candidates.append((abs(len(left) - len(right)), left, right))
    return text if not candidates else min(candidates)[1] + "\n" + min(candidates)[2]


def resegment_group(group: CueGroupLike, english: str) -> list[Cue]:
    """Spread readable English pieces over a grouped source interval."""
    source_count = len(group.source_indices)
    desired = min(source_count, max(1, math.ceil(len(english) / 42)))
    pieces = split_for_display(english, desired)
    weights = [max(1, len(re.findall(r"[A-Za-z]+", piece))) for piece in pieces]
    total = sum(weights)
    cursor = group.start
    output: list[Cue] = []
    for index, (piece, weight) in enumerate(zip(pieces, weights), start=1):
        end = group.end if index == len(pieces) else cursor + group.duration * weight / total
        output.append(Cue(index, cursor, max(end, cursor + 0.05), wrap_two_lines(piece)))
        cursor = end
    return output


class CueGroupLike:
    """Structural type kept tiny to avoid coupling display logic to grouping."""

    source_indices: tuple[int, ...]
    start: float
    end: float

    @property
    def duration(self) -> float:  # pragma: no cover - interface declaration
        raise NotImplementedError
