from pathlib import Path

from ai_dubbing.common.models import Cue
from ai_dubbing.translation.service import TranslationService
from ai_dubbing.translation.translator import MockTranslator


def test_mock_translation_passes_qa_and_resumes_from_cache(tmp_path: Path) -> None:
    cues = [Cue(1, 0, 1, "我们到了吗？"), Cue(2, 1, 2, "应该快了。")]
    cache = tmp_path / "progress.json"
    first = TranslationService(MockTranslator(), batch_items=1).translate(cues, cache_path=cache)
    second = TranslationService(MockTranslator(), batch_items=1).translate(cues, cache_path=cache)
    assert all(record.qa.ok for record in first)
    assert [record.english for record in first] == ["Are we there?", "We should be close."]
    assert all(record.cached for record in second)
