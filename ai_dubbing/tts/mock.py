"""Offline deterministic TTS used for tests, CI, and pipeline demonstrations."""
from __future__ import annotations

import math
import wave
from pathlib import Path

from ai_dubbing.common.models import TTSResult
from ai_dubbing.common.text import english_words


class MockTTSBackend:
    """Writes a quiet tone whose duration follows a transparent speech heuristic."""

    name = "mock"

    def __init__(self, *, words_per_second: float = 2.5, sample_rate: int = 16_000) -> None:
        self.words_per_second = words_per_second
        self.sample_rate = sample_rate

    def estimate_duration(self, text: str, *, speed: float = 1.0) -> float:
        if speed <= 0:
            raise ValueError("Speed must be positive.")
        words = max(1, len(english_words(text)))
        punctuation_pause = 0.10 * sum(text.count(mark) for mark in ".,!?;")
        return max(0.20, (words / self.words_per_second + punctuation_pause) / speed)

    def synthesize(
        self,
        text: str,
        output_path: Path,
        *,
        reference_audio: Path | None = None,
        speaker: str | None = None,
        speed: float = 1.0,
    ) -> TTSResult:
        del reference_audio, speaker
        duration = self.estimate_duration(text, speed=speed)
        sample_count = max(1, round(duration * self.sample_rate))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with wave.open(str(output_path), "wb") as output:
            output.setnchannels(1)
            output.setsampwidth(2)
            output.setframerate(self.sample_rate)
            frames = bytearray()
            for sample in range(sample_count):
                amplitude = int(350 * math.sin(2 * math.pi * 220 * sample / self.sample_rate))
                frames.extend(amplitude.to_bytes(2, byteorder="little", signed=True))
            output.writeframes(bytes(frames))
        return TTSResult(str(output_path), duration, self.sample_rate, self.name)
