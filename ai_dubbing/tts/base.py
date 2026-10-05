"""A narrow TTS contract shared by audiobook and video workflows."""
from __future__ import annotations

from pathlib import Path
from typing import Protocol

from ai_dubbing.common.models import TTSResult


class TTSBackend(Protocol):
    name: str

    def synthesize(
        self,
        text: str,
        output_path: Path,
        *,
        reference_audio: Path | None = None,
        speaker: str | None = None,
        speed: float = 1.0,
    ) -> TTSResult:
        """Write speech to ``output_path`` and return measured metadata."""
