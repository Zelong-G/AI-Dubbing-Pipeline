#!/usr/bin/env python3
"""Plan temporally aligned dubbing for a local video and subtitle file."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ai_dubbing.subtitles.srt import parse_srt
from ai_dubbing.translation.service import TranslationService
from ai_dubbing.translation.translator import MockTranslator
from ai_dubbing.tts.duration import HeuristicDurationEstimator
from ai_dubbing.video.ffmpeg import build_mux_command, mux_local_media
from ai_dubbing.video.pipeline import plan_video_dub


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="User-supplied local video path.",
    )
    parser.add_argument("--srt", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--cache", type=Path)
    parser.add_argument(
        "--words-per-second",
        type=float,
        default=2.5,
        help="Offline speech-duration estimate used for planning.",
    )
    parser.add_argument(
        "--dub-audio",
        type=Path,
        help="Prepared dialogue WAV for an FFmpeg mux run.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("outputs/dubbed_video.mp4"),
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    cues = parse_srt(args.srt)
    estimator = HeuristicDurationEstimator(
        words_per_second=args.words_per_second
    )
    plan = plan_video_dub(
        cues,
        TranslationService(MockTranslator()),
        estimator,
        cache_path=args.cache,
    )

    print(f"translation: {len(plan.translations)} cue(s)")
    print(f"cue grouping: {plan.group_count} group(s)")
    for item in plan.fitted:
        adjustment = (
            f"TTS {item.playback_speed:.2f}x; "
            f"video {item.video_speed:.2f}x"
        )
        voice = plan.voice_labels.get(item.cue.index, "unassigned")
        print(
            f"cue {item.cue.index}: voice={voice}; "
            f"predicted {item.generated_duration:.2f}s; {adjustment}"
        )
        if item.warning:
            print(f"  warning: {item.warning}")
    print(f"timeline: {len(plan.slow_regions)} local slow region(s)")

    if args.dry_run:
        print("dry run complete; no media tool was invoked")
        return 0

    if args.dub_audio is None:
        raise SystemExit(
            "--dub-audio is required to mux a non-dry-run output."
        )
    command = build_mux_command(args.input, args.dub_audio, args.output)
    print("FFmpeg command:", " ".join(command))
    mux_local_media(args.input, args.dub_audio, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
