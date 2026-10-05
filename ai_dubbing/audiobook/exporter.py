"""Minimal LRC export based on measured or predicted segment starts."""
from __future__ import annotations

from pathlib import Path


def write_lrc(rows: list[tuple[float, str]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for start, text in rows:
        minutes, seconds = divmod(max(0.0, start), 60)
        lines.append(f"[{int(minutes):02d}:{seconds:05.2f}]{text}")
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_ffmpeg_assembly_command(segment_paths: list[Path], output_path: Path) -> list[str]:
    """Return an FFmpeg concat command for reviewed local segment files.

    The caller writes the concat manifest and executes the command only after
    selecting its own installed FFmpeg binary.
    """
    manifest = output_path.with_suffix(".concat.txt")
    manifest_rows = "\n".join(f"file '{path.as_posix()}'" for path in segment_paths)
    manifest.write_text(manifest_rows + "\n", encoding="utf-8")
    return [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(manifest),
        "-c:a", "libmp3lame", str(output_path),
    ]
