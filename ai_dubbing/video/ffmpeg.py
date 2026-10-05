"""FFmpeg integration for user-provided local media only."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from ai_dubbing.video.audio_mix import audio_mix_filter


def find_ffmpeg() -> str | None:
    return shutil.which("ffmpeg")


def build_mux_command(
    video_path: Path,
    dub_audio_path: Path,
    output_path: Path,
    *,
    original_volume: float = 0.18,
) -> list[str]:
    """Return a safe local-file mux command; callers decide when to execute it."""
    return [
        "ffmpeg", "-y", "-i", str(video_path), "-i", str(dub_audio_path),
        "-filter_complex", audio_mix_filter(original_volume=original_volume),
        "-map", "0:v:0", "-map", "[mix]", "-c:v", "copy", "-c:a", "aac", str(output_path),
    ]


def mux_local_media(video_path: Path, dub_audio_path: Path, output_path: Path) -> None:
    if not video_path.is_file() or not dub_audio_path.is_file():
        raise FileNotFoundError("Video and dub audio must be existing local files.")
    if find_ffmpeg() is None:
        raise RuntimeError("FFmpeg was not found on PATH.")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(build_mux_command(video_path, dub_audio_path, output_path), check=True)
