"""Planning pipeline for subtitle-driven dubbing of local video files."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ai_dubbing.common.models import Cue, FittedUtterance, SlowRegion
from ai_dubbing.subtitles.cleanup import clean_cues
from ai_dubbing.subtitles.grouping import (
    build_groups,
    conservative_join_decisions,
)
from ai_dubbing.translation.service import (
    TranslationRecord,
    TranslationService,
)
from ai_dubbing.tts.duration import SpeechDurationEstimator
from ai_dubbing.tts.voice_assignment import assign_voice
from ai_dubbing.video.timing import (
    FitDecision,
    FitPolicy,
    build_slow_regions,
    finalize_plan,
    fit_utterance_duration,
)


@dataclass(frozen=True)
class VideoDubPlan:
    translations: list[TranslationRecord]
    decisions: list[FitDecision]
    fitted: list[FittedUtterance]
    slow_regions: list[SlowRegion]
    voice_labels: dict[int, str]
    group_count: int


def plan_video_dub(
    cues: list[Cue],
    translator: TranslationService,
    duration_estimator: SpeechDurationEstimator,
    *,
    policy: FitPolicy | None = None,
    cache_path: Path | None = None,
) -> VideoDubPlan:
    """Create a deterministic timing plan without opening the video file."""
    policy = policy or FitPolicy()
    cleaned = clean_cues(cues)
    groups = build_groups(
        cleaned,
        conservative_join_decisions(cleaned),
    )
    utterances = [
        Cue(group.index, group.start, group.end, group.text)
        for group in groups
    ]
    records = translator.translate(utterances, cache_path=cache_path)

    decisions: list[FitDecision] = []
    voice_labels: dict[int, str] = {}
    for position, record in enumerate(records):
        if not record.qa.ok:
            continue
        next_cue = (
            records[position + 1].cue
            if position + 1 < len(records)
            else None
        )
        duration = duration_estimator.estimate_duration(
            record.english,
            speed=policy.base_tts_speed,
        )
        decisions.append(
            fit_utterance_duration(
                record.cue,
                duration,
                next_cue=next_cue,
                policy=policy,
            )
        )
        voice_labels[record.cue.index] = assign_voice(record.cue.speaker)

    regions = build_slow_regions(decisions)
    return VideoDubPlan(
        records,
        decisions,
        finalize_plan(decisions, regions),
        regions,
        voice_labels,
        len(groups),
    )
