"""Finalize English subtitles after local timeline adjustment."""
from __future__ import annotations

from pathlib import Path

from ai_dubbing.common.models import Cue, SlowRegion
from ai_dubbing.subtitles.alignment import remap_cues
from ai_dubbing.subtitles.srt import write_srt


def finalize_subtitles(cues: list[Cue], regions: list[SlowRegion], output_path: Path) -> list[Cue]:
    remapped = remap_cues(cues, regions)
    write_srt(remapped, output_path)
    return remapped
