"""Build predictable FFmpeg audio-mix filters without invoking external tools."""
from __future__ import annotations


def audio_mix_filter(
    *,
    original_volume: float = 0.18,
    dub_volume: float = 1.0,
    fade_seconds: float = 0.03,
) -> str:
    if original_volume < 0 or dub_volume < 0 or fade_seconds < 0:
        raise ValueError("Mix levels and fade duration cannot be negative.")
    return (
        f"[0:a]volume={original_volume},afade=t=in:st=0:d={fade_seconds}[bed];"
        f"[1:a]volume={dub_volume},afade=t=in:st=0:d={fade_seconds}[dub];"
        "[bed][dub]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.95[mix]"
    )
