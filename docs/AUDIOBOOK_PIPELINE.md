# Audiobook workflow

1. `chapter_parser` reads UTF-8-compatible plain text and recognizes common Chinese and English chapter headings. If no heading is detected, it safely treats the input as one chapter.
2. A chapter is split into sentence-sized translation units. The translation service batches those units while preserving a bounded context window.
3. Structural QA rejects empty output, residual CJK text, and implausibly long output for very short source units. Successful rows are restart-safe.
4. `voice_assignment` maps speakers to stable labels. A real backend may map those labels to its own voices or reference-audio policy.
5. The backend emits per-segment audio. LRC starts are derived from actual returned segment durations.
6. Optional FFmpeg assembly can concatenate reviewed local segments into an MP3. No generated audio is tracked by the repository.

The mock command in the README exercises stages 1–5. It writes intentionally simple tone segments and LRC metadata so no speech model is needed.
