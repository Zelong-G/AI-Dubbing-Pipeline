#!/usr/bin/env python3
"""Assign deterministic placeholder voices from speaker labels in a small CSV file."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ai_dubbing.tts.voice_assignment import assign_voices


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--speakers", type=Path, required=True, help="One speaker label per line.")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    labels = [line.strip() for line in args.speakers.read_text(encoding="utf-8").splitlines() if line.strip()]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(assign_voices(labels), indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
