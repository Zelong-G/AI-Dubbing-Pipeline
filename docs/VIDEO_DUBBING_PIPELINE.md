# Video dubbing workflow

The input boundary is intentionally narrow: a user-provided local video and an SRT file. `RapidOCRAdapter` is an optional interface for producing text from local frame images when an SRT does not yet exist.

1. The SRT reader accepts common comma and period timestamp variants, removes display markup, and keeps original cue timing.
2. Cleanup removes trivial artifacts. Conservative grouping joins only a short gap after a continuation mark; it avoids accidental cross-speaker merges.
3. Translation is batched, checked, and cached by input fingerprint.
4. TTS duration is compared with the usable cue window, bounded by the next cue. The policy first accepts natural speech, then local slowdown, then a capped TTS speed increase. A hard-limit warning signals that a human should review the cue.
5. Every slowdown interval becomes a `SlowRegion`. `map_timestamp` maps source cue boundaries to final video time; `finalize_subtitles` uses that same map.
6. FFmpeg helpers build an original-audio bed plus dubbed-dialogue mix and mux it into an existing local video. A full media run requires an installed FFmpeg binary and prepared dialogue audio.

The dry-run CLI performs stages 1–5 and prints all fitting decisions without opening the supplied video path or invoking FFmpeg.
