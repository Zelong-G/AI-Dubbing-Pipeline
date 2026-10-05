# Video dubbing workflow

The input boundary is intentionally narrow: a user-provided local video and an SRT file. RapidOCRAdapter is optional for detecting text from user-provided local frame images when an SRT does not already exist.

1. The SRT reader accepts common comma and period timestamp variants, removes display markup, and keeps source timing.
2. Cleanup removes trivial artifacts. Conservative grouping joins only clear continuation boundaries; uncertain boundaries remain separate.
3. Translation is batched, structurally checked, and restart-safe through an input fingerprint.
4. Stable voice labels are assigned when speaker labels are available. Automatic speaker recognition is outside the core public pipeline.
5. SpeechDurationEstimator predicts or supplies spoken duration independently of any specific TTS model. The included heuristic is deterministic and offline.
6. Duration fitting may use safe silence before the next cue, then bounded local slowdown, then capped TTS acceleration. A hard-limit warning marks unresolved cases for review.
7. Slowdown intervals become SlowRegion objects. The same source-to-output mapping is used for planned dialogue placement and final subtitle timestamps.
8. FFmpeg helpers can mix a prepared dialogue track with the original audio and mux it into an existing local video.

The dry-run CLI performs stages 1–7 without opening the supplied video path or invoking FFmpeg. The repository deliberately does not bundle a model-specific speech checkpoint or claim that installing a named TTS package alone provides a complete integration.
