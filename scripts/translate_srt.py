#!/usr/bin/env python3
"""Translate an SRT file with an offline mock or a configured HTTP backend."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ai_dubbing.common.models import Cue
from ai_dubbing.subtitles.srt import parse_srt, write_srt
from ai_dubbing.translation.service import TranslationService
from ai_dubbing.translation.translator import MockTranslator, OpenAICompatibleTranslator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--translator", choices=("mock", "openai-compatible"), default="mock")
    parser.add_argument("--endpoint", help="OpenAI-compatible endpoint; required for that backend.")
    parser.add_argument("--model", default="local-model")
    parser.add_argument("--cache", type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.translator == "mock":
        backend = MockTranslator()
    else:
        if not args.endpoint:
            raise SystemExit("--endpoint is required for the openai-compatible backend.")
        backend = OpenAICompatibleTranslator.from_environment(args.endpoint, args.model)
    source = parse_srt(args.input)
    records = TranslationService(backend).translate(source, cache_path=args.cache)
    failed = [record for record in records if not record.qa.ok]
    if failed:
        details = "; ".join(f"{record.cue.index}: {', '.join(record.qa.issues)}" for record in failed)
        raise SystemExit(f"Translation QA failed: {details}")
    translated = [
        Cue(record.cue.index, record.cue.start, record.cue.end, record.english, record.cue.speaker)
        for record in records
    ]
    write_srt(translated, args.output)
    print(f"Translated {len(translated)} cues with {backend.name}: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
