"""Duration fitting and source-to-output timeline construction."""
from __future__ import annotations

from dataclasses import dataclass

from ai_dubbing.common.models import Cue, FittedUtterance, SlowRegion
from ai_dubbing.subtitles.alignment import map_timestamp


@dataclass(frozen=True)
class FitPolicy:
    base_tts_speed: float = 1.0
    max_tts_speed: float = 1.25
    soft_min_video_speed: float = 0.80
    hard_min_video_speed: float = 0.40
    speech_gap: float = 0.08

    def __post_init__(self) -> None:
        if not 0 < self.hard_min_video_speed <= self.soft_min_video_speed <= 1:
            raise ValueError("Video speed limits must satisfy 0 < hard <= soft <= 1.")
        if not 0 < self.base_tts_speed <= self.max_tts_speed:
            raise ValueError("TTS speed limits must be positive and ordered.")


@dataclass(frozen=True)
class FitDecision:
    cue: Cue
    generated_duration: float
    tts_speed: float
    video_speed: float
    usable_end: float
    warning: str | None = None


def usable_window(cue: Cue, next_cue: Cue | None, *, policy: FitPolicy) -> float:
    boundary = cue.end
    if next_cue is not None:
        boundary = min(boundary, next_cue.start - policy.speech_gap)
    return max(0.05, boundary - cue.start)


def fit_utterance_duration(
    cue: Cue,
    generated_duration: float,
    *,
    next_cue: Cue | None = None,
    policy: FitPolicy = FitPolicy(),
) -> FitDecision:
    """Prefer natural speech, then mild local slowdown, then controlled TTS speed-up.

    ``generated_duration`` is the duration at ``base_tts_speed``. A caller may
    synthesize at the selected speed and rerun this function with its measured
    duration if a model has non-linear speed behavior.
    """
    if generated_duration <= 0:
        raise ValueError("Generated duration must be positive.")
    window = usable_window(cue, next_cue, policy=policy)
    speed = policy.base_tts_speed
    effective_duration = generated_duration
    required_video_speed = min(1.0, window / effective_duration)
    warning = None
    if required_video_speed < policy.soft_min_video_speed:
        required_tts_speed = policy.base_tts_speed * effective_duration / (
            window / policy.soft_min_video_speed
        )
        speed = min(policy.max_tts_speed, max(policy.base_tts_speed, required_tts_speed))
        effective_duration = generated_duration * policy.base_tts_speed / speed
        required_video_speed = min(1.0, window / effective_duration)
    video_speed = required_video_speed
    if video_speed < policy.hard_min_video_speed:
        video_speed = policy.hard_min_video_speed
        warning = "speech exceeds the hard fitting limit and must be clipped or reviewed"
    return FitDecision(cue, generated_duration, speed, video_speed, cue.start + window, warning)


def build_slow_regions(decisions: list[FitDecision]) -> list[SlowRegion]:
    """Build non-overlapping local video-slowdown regions from cue decisions."""
    regions = [
        SlowRegion(decision.cue.start, decision.usable_end, decision.video_speed)
        for decision in decisions
        if decision.video_speed < 0.999 and decision.usable_end > decision.cue.start
    ]
    regions.sort(key=lambda region: (region.start, region.end))
    for previous, current in zip(regions, regions[1:]):
        if current.start < previous.end - 1e-6:
            raise ValueError("Overlapping slowdown regions require a prior grouping decision.")
    return regions


def finalize_plan(decisions: list[FitDecision], regions: list[SlowRegion]) -> list[FittedUtterance]:
    output: list[FittedUtterance] = []
    for decision in decisions:
        output_start = map_timestamp(decision.cue.start, regions)
        output_end = map_timestamp(decision.usable_end, regions)
        output.append(
            FittedUtterance(
                cue=decision.cue,
                generated_duration=decision.generated_duration,
                playback_speed=decision.tts_speed,
                video_speed=decision.video_speed,
                output_start=output_start,
                output_end=output_end,
                warning=decision.warning,
            )
        )
    return output
