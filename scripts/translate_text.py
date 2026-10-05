#!/usr/bin/env python3
"""Translate supplied plain text into newline-separated English with the mock backend."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ai_dubbing.audiobook.chapter_parser import split_sentences
from ai_dubbing.common.models import Cue
from ai_dubbing.translation.service import TranslationService
from ai_dubbing.translation.translator import MockTranslator


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    sentences = split_sentences(args.input.read_text(encoding="utf-8-sig"))
    cues = [Cue(index + 1, index, index + 1, sentence) for index, sentence in enumerate(sentences)]
    records = TranslationService(MockTranslator()).translate(cues)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(record.english for record in records) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
