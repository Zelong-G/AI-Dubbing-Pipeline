"""Small adapter for externally managed TTS implementations."""
from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from ai_dubbing.common.models import TTSResult

SynthesisCallable = Callable[..., TTSResult]


class CallableTTSAdapter:
    """Expose an external synthesis callable through the public TTS contract."""

    def __init__(self, name: str, synthesize_fn: SynthesisCallable) -> None:
        if not name.strip():
            raise ValueError("A backend name is required.")
        self.name = name.strip()
        self._synthesize_fn = synthesize_fn

    def synthesize(
        self,
        text: str,
        output_path: Path,
        *,
        reference_audio: Path | None = None,
        speaker: str | None = None,
        speed: float = 1.0,
    ) -> TTSResult:
        result = self._synthesize_fn(
            text,
            output_path,
            reference_audio=reference_audio,
            speaker=speaker,
            speed=speed,
        )
        if not isinstance(result, TTSResult):
            raise TypeError("The wrapped synthesizer must return TTSResult.")
        return result
