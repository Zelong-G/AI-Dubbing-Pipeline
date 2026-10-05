from ai_dubbing.common.models import Cue
from ai_dubbing.subtitles.grouping import build_groups, conservative_join_decisions


def test_conservative_grouping_joins_only_clear_continuation() -> None:
    cues = [
        Cue(1, 0.0, 1.0, "这是一个，"),
        Cue(2, 1.1, 2.0, "连续的句子。"),
        Cue(3, 2.1, 3.0, "这是另一个问题？"),
    ]
    groups = build_groups(cues, conservative_join_decisions(cues))
    assert [group.source_indices for group in groups] == [(1, 2), (3,)]
    assert groups[0].text == "这是一个， 连续的句子。"
