"""Explicit placeholders for externally installed model-backed TTS adapters."""
from __future__ import annotations

from pathlib import Path

from ai_dubbing.common.models import TTSResult


class OptionalBackendUnavailable(RuntimeError):
    pass


class XTTSAdapter:
    """Integration boundary for XTTS; model loading is intentionally external."""

    name = "xtts"

    def synthesize(
        self, text: str, output_path: Path, *, reference_audio: Path | None = None,
        speaker: str | None = None, speed: float = 1.0,
    ) -> TTSResult:
        del text, output_path, reference_audio, speaker, speed
        raise OptionalBackendUnavailable(
            "Install and configure the optional XTTS integration in your environment."
        )


class ChatterboxAdapter:
    """Integration boundary for Chatterbox; model loading is intentionally external."""

    name = "chatterbox"

    def synthesize(
        self, text: str, output_path: Path, *, reference_audio: Path | None = None,
        speaker: str | None = None, speed: float = 1.0,
    ) -> TTSResult:
        del text, output_path, reference_audio, speaker, speed
        raise OptionalBackendUnavailable(
            "Install and configure the optional Chatterbox integration in your environment."
        )
