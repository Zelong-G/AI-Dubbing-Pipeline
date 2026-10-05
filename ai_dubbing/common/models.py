"""Common, serializable representations shared by both workflows."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Cue:
    """One timed subtitle or utterance unit, measured in source seconds."""

    index: int
    start: float
    end: float
    text: str
    speaker: str | None = None

    def __post_init__(self) -> None:
        if self.index < 1:
            raise ValueError("Cue indices begin at one.")
        if self.end <= self.start:
            raise ValueError("A cue end time must be later than its start time.")
        if not self.text.strip():
            raise ValueError("A cue must contain text.")

    @property
    def duration(self) -> float:
        return self.end - self.start


@dataclass(frozen=True)
class SlowRegion:
    """A source-timeline interval that will play slower in the output video."""

    start: float
    end: float
    speed: float

    def __post_init__(self) -> None:
        if self.start < 0 or self.end <= self.start:
            raise ValueError("A slowdown region must have a positive interval.")
        if not 0 < self.speed <= 1:
            raise ValueError("A slowdown speed must be in (0, 1].")


@dataclass(frozen=True)
class TTSResult:
    path: str
    duration: float
    sample_rate: int = 24_000
    backend: str = "unknown"


@dataclass(frozen=True)
class FittedUtterance:
    cue: Cue
    generated_duration: float
    playback_speed: float
    video_speed: float
    output_start: float
    output_end: float
    warning: str | None = None


@dataclass
class RunSummary:
    completed: list[int] = field(default_factory=list)
    skipped: list[int] = field(default_factory=list)
    failed: dict[int, str] = field(default_factory=dict)
