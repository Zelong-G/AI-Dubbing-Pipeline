"""Stable, explainable voice labels without embedding any voice assets."""
from __future__ import annotations

from hashlib import sha256


def assign_voice(speaker: str | None, *, available_voices: tuple[str, ...] = ("voice_a", "voice_b", "voice_c")) -> str:
    if not available_voices:
        raise ValueError("At least one voice label is required.")
    identity = (speaker or "narrator").strip().lower()
    digest = int.from_bytes(sha256(identity.encode("utf-8")).digest()[:4], "big")
    return available_voices[digest % len(available_voices)]


def assign_voices(speakers: list[str | None]) -> dict[str, str]:
    unique = sorted({speaker or "narrator" for speaker in speakers})
    return {speaker: assign_voice(speaker) for speaker in unique}
