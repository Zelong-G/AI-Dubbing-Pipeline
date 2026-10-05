"""End-to-end planning for subtitle-driven dubbing of local video files."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ai_dubbing.common.models import Cue, FittedUtterance, SlowRegion
from ai_dubbing.subtitles.cleanup import clean_cues
from ai_dubbing.subtitles.grouping import build_groups, conservative_join_decisions
from ai_dubbing.translation.service import TranslationRecord, TranslationService
from ai_dubbing.tts.mock import MockTTSBackend
from ai_dubbing.tts.voice_assignment import assign_voice
from ai_dubbing.video.timing import FitPolicy, FitDecision, build_slow_regions, finalize_plan, fit_utterance_duration


@dataclass(frozen=True)
class VideoDubPlan:
    translations: list[TranslationRecord]
    decisions: list[FitDecision]
    fitted: list[FittedUtterance]
    slow_regions: list[SlowRegion]
    group_count: int


def plan_video_dub(
    cues: list[Cue],
    translator: TranslationService,
    tts: MockTTSBackend,
    *,
    policy: FitPolicy = FitPolicy(),
    cache_path: Path | None = None,
) -> VideoDubPlan:
    """Create a deterministic plan without reading or changing a video file."""
    cleaned = clean_cues(cues)
    groups = build_groups(cleaned, conservative_join_decisions(cleaned))
    utterances = [
        Cue(group.index, group.start, group.end, group.text)
        for group in groups
    ]
    records = translator.translate(utterances, cache_path=cache_path)
    decisions: list[FitDecision] = []
    for position, record in enumerate(records):
        if not record.qa.ok:
            continue
        next_cue = records[position + 1].cue if position + 1 < len(records) else None
        duration = tts.estimate_duration(record.english, speed=policy.base_tts_speed)
        decisions.append(
            fit_utterance_duration(record.cue, duration, next_cue=next_cue, policy=policy)
        )
        assign_voice(record.cue.speaker)
    regions = build_slow_regions(decisions)
    return VideoDubPlan(records, decisions, finalize_plan(decisions, regions), regions, len(groups))
