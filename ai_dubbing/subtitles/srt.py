"""Small, permissive SRT reader/writer with strict output invariants."""
from __future__ import annotations

import html
import re
from pathlib import Path

from ai_dubbing.common.models import Cue
from ai_dubbing.common.text import compact_whitespace

_TIMING = re.compile(
    r"^\s*(\d{2}:\d{2}:\d{2}[,.]\d{3})\s*-->\s*"
    r"(\d{2}:\d{2}:\d{2}[,.]\d{3})(?:\s+.*)?$"
)


def parse_timestamp(value: str) -> float:
    normalized = value.strip().replace(",", ".")
    hours, minutes, second_fraction = normalized.split(":")
    seconds, milliseconds = second_fraction.split(".")
    return (
        int(hours) * 3600
        + int(minutes) * 60
        + int(seconds)
        + int(milliseconds) / 1000
    )


def format_timestamp(seconds: float) -> str:
    milliseconds = max(0, round(seconds * 1000))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    whole_seconds, millis = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{whole_seconds:02d},{millis:03d}"


def parse_srt(path: Path) -> list[Cue]:
    raw = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    cues: list[Cue] = []
    for block in re.split(r"\n{2,}", raw.strip()):
        lines = [line.rstrip() for line in block.split("\n")]
        timing_position = next((i for i, line in enumerate(lines[:3]) if "-->" in line), None)
        if timing_position is None:
            continue
        match = _TIMING.match(lines[timing_position])
        if match is None:
            continue
        try:
            index = int(lines[0].strip()) if timing_position else len(cues) + 1
        except ValueError:
            index = len(cues) + 1
        text = compact_whitespace(
            re.sub(r"<[^>]+>", "", html.unescape(" ".join(lines[timing_position + 1 :])))
        )
        if not text:
            continue
        start, end = parse_timestamp(match.group(1)), parse_timestamp(match.group(2))
        if end <= start:
            continue
        cues.append(Cue(index=index, start=start, end=end, text=text))
    if not cues:
        raise ValueError(f"No valid SRT cues found in {path.name}.")
    return cues


def write_srt(cues: list[Cue], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    blocks = []
    for output_index, cue in enumerate(cues, start=1):
        blocks.append(
            f"{output_index}\n{format_timestamp(cue.start)} --> {format_timestamp(cue.end)}\n{cue.text}"
        )
    path.write_text("\n\n".join(blocks) + "\n", encoding="utf-8")
