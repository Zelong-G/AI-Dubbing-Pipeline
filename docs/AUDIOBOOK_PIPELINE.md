# Audiobook workflow

1. chapter_parser reads UTF-8-compatible plain text and recognizes common Chinese and English chapter headings. If no heading is found, the input is treated as one chapter.
2. A chapter is split into sentence-sized translation units.
3. TranslationService batches those units with bounded prior context, deterministic structural QA, and restart-safe caching.
4. If speaker labels are supplied by an upstream application, voice_assignment maps them to stable voice labels. The basic public chapter parser does not claim automatic character attribution.
5. A TTSBackend emits per-segment audio. The offline mock writes deterministic tones; an external model can be connected through the same protocol.
6. LRC timestamps are derived from the durations returned by the synthesis backend.
7. Media assembly is intentionally separate so generated segments can be reviewed before FFmpeg concatenation/export.

The README command exercises the full public path through translation, mock synthesis, and LRC generation without a GPU or network connection.
