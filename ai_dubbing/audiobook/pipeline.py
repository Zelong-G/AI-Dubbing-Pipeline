"""A restart-friendly text-to-audiobook pipeline using public interfaces."""
from __future__ import annotations

from pathlib import Path

from ai_dubbing.audiobook.chapter_parser import Chapter, split_sentences
from ai_dubbing.audiobook.exporter import write_lrc
from ai_dubbing.common.models import Cue
from ai_dubbing.translation.service import TranslationService
from ai_dubbing.tts.base import TTSBackend
from ai_dubbing.tts.voice_assignment import assign_voice


def build_audiobook_chapter(
    chapter: Chapter,
    output_dir: Path,
    translator: TranslationService,
    tts: TTSBackend,
) -> dict[str, object]:
    """Translate, synthesize individual segments, and emit LRC timing metadata.

    Audio assembly is intentionally separate: model-specific segment audio can
    be joined with FFmpeg after review, while this stage remains resumable.
    """
    sentences = split_sentences(chapter.text)
    cues = [Cue(index + 1, float(index), float(index + 1), text) for index, text in enumerate(sentences)]
    records = translator.translate(
        cues, cache_path=output_dir / f"chapter_{chapter.index:04d}.translation.json"
    )
    starts: list[tuple[float, str]] = []
    cursor = 0.0
    failures: dict[int, tuple[str, ...]] = {}
    for record in records:
        if not record.qa.ok:
            failures[record.cue.index] = record.qa.issues
            continue
        output = output_dir / "segments" / f"chapter_{chapter.index:04d}_{record.cue.index:04d}.wav"
        result = tts.synthesize(
            record.english, output, speaker=assign_voice(record.cue.speaker)
        )
        starts.append((cursor, record.english))
        cursor += result.duration
    write_lrc(starts, output_dir / f"chapter_{chapter.index:04d}.lrc")
    return {"chapter": chapter.index, "segments": len(starts), "seconds": cursor, "failures": failures}
