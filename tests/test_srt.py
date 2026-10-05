from pathlib import Path

from ai_dubbing.subtitles.srt import format_timestamp, parse_srt, parse_timestamp, write_srt


def test_srt_round_trip(tmp_path: Path) -> None:
    source = tmp_path / "input.srt"
    source.write_text(
        "1\n00:00:01,000 --> 00:00:02.500\nHello <i>there</i>\n\n"
        "2\n00:00:03,000 --> 00:00:04,000\nSecond line\n",
        encoding="utf-8",
    )
    cues = parse_srt(source)
    assert [(cue.index, cue.text) for cue in cues] == [(1, "Hello there"), (2, "Second line")]
    assert parse_timestamp("00:00:02,500") == 2.5
    assert format_timestamp(2.5) == "00:00:02,500"
    target = tmp_path / "roundtrip.srt"
    write_srt(cues, target)
    assert [cue.text for cue in parse_srt(target)] == ["Hello there", "Second line"]
