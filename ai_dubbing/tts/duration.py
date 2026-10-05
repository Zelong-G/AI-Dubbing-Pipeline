"""Speech-duration estimation contracts used by the video planner."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from ai_dubbing.common.text import english_words


class SpeechDurationEstimator(Protocol):
    """Estimate spoken duration without requiring a synthesis model."""

    name: str

    def estimate_duration(self, text: str, *, speed: float = 1.0) -> float:
        """Return an estimated duration in seconds."""


@dataclass(frozen=True)
class HeuristicDurationEstimator:
    """Transparent offline estimate based on word rate and punctuation pauses."""

    words_per_second: float = 2.5
    punctuation_pause_seconds: float = 0.10
    name: str = "heuristic"

    def __post_init__(self) -> None:
        if self.words_per_second <= 0:
            raise ValueError("words_per_second must be positive.")
        if self.punctuation_pause_seconds < 0:
            raise ValueError("punctuation_pause_seconds cannot be negative.")

    def estimate_duration(self, text: str, *, speed: float = 1.0) -> float:
        if speed <= 0:
            raise ValueError("speed must be positive.")
        words = max(1, len(english_words(text)))
        punctuation = sum(text.count(mark) for mark in ".,!?;")
        base = words / self.words_per_second
        base += self.punctuation_pause_seconds * punctuation
        return max(0.20, base / speed)
