#!/usr/bin/env python3
"""Run the offline-safe audiobook preparation workflow on supplied text."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ai_dubbing.audiobook.chapter_parser import parse_chapters, read_text
from ai_dubbing.audiobook.pipeline import build_audiobook_chapter
from ai_dubbing.translation.service import TranslationService
from ai_dubbing.translation.translator import MockTranslator
from ai_dubbing.tts.mock import MockTTSBackend


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/audiobook"))
    parser.add_argument("--translator", choices=("mock",), default="mock")
    parser.add_argument("--tts", choices=("mock",), default="mock")
    args = parser.parse_args()
    chapters = parse_chapters(read_text(args.input))
    service, backend = TranslationService(MockTranslator()), MockTTSBackend()
    for chapter in chapters:
        result = build_audiobook_chapter(chapter, args.output_dir, service, backend)
        print(f"chapter {result['chapter']}: {result['segments']} segments, {result['seconds']:.2f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
