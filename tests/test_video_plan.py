import pytest

from ai_dubbing.common.models import Cue
from ai_dubbing.translation.service import TranslationService
from ai_dubbing.translation.translator import MockTranslator
from ai_dubbing.tts.duration import HeuristicDurationEstimator
from ai_dubbing.video.pipeline import plan_video_dub
from ai_dubbing.video.timing import FitPolicy, fit_utterance_duration


def test_planner_uses_duration_interface_and_returns_voice_labels() -> None:
    cues = [
        Cue(1, 0.0, 1.0, "我们到了吗？", "speaker-a"),
        Cue(2, 1.5, 2.5, "应该快了。", "speaker-b"),
    ]
    plan = plan_video_dub(
        cues,
        TranslationService(MockTranslator()),
        HeuristicDurationEstimator(words_per_second=3.0),
    )
    assert len(plan.fitted) == 2
    assert set(plan.voice_labels) == {1, 2}
    assert plan.voice_labels[1] != ""


def test_fitting_can_use_safe_silence_before_next_cue() -> None:
    current = Cue(1, 0.0, 1.0, "A line.")
    following = Cue(2, 2.0, 3.0, "Another line.")
    decision = fit_utterance_duration(
        current,
        1.5,
        next_cue=following,
        policy=FitPolicy(speech_gap=0.08),
    )
    assert decision.video_speed == 1.0
    assert decision.usable_end == pytest.approx(1.92)
