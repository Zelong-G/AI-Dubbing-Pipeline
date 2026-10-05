import pytest

from ai_dubbing.common.models import Cue
from ai_dubbing.subtitles.alignment import map_timestamp, remap_cues
from ai_dubbing.video.timing import (
    FitPolicy,
    build_slow_regions,
    fit_utterance_duration,
)


def test_duration_fit_prefers_local_slowdown_before_acceleration() -> None:
    cue = Cue(1, 0.0, 2.0, "A test line.")
    decision = fit_utterance_duration(cue, 2.2, policy=FitPolicy())
    assert decision.tts_speed == 1.0
    assert decision.video_speed == pytest.approx(2.0 / 2.2)
    regions = build_slow_regions([decision])
    assert map_timestamp(2.0, regions) == pytest.approx(2.2)
    assert remap_cues([cue], regions)[0].end == pytest.approx(2.2)


def test_hard_limit_is_explicit() -> None:
    decision = fit_utterance_duration(Cue(1, 0, 1, "x"), 10.0)
    assert decision.video_speed == 0.4
    assert decision.warning is not None
