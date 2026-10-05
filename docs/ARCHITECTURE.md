# Architecture

Both workflows operate on a small common representation: `Cue(index, start, end, text, speaker)`. Text chapters convert sentences into cues with synthetic order timestamps; SRT inputs already carry source timestamps. This reduces translation, voice assignment, and QA to the same interfaces.

`TranslationService` is backend-agnostic. It batches by count and character budget, gives each batch bounded previous context, normalizes the result, runs deterministic checks, and saves valid rows atomically. The cache contains an input fingerprint and backend name, so it cannot be reused after a material input change or backend switch.

The TTS protocol takes text, an output path, a speaker label, optional reference audio, and requested speed. Its result reports a measured duration. The mock implementation gives CI a real file-writing implementation without a speech model. Model-backed adapters are optional integration boundaries.

Temporal alignment lives in `video/timing.py`. Each cue produces a fit decision with its generated duration, selected TTS speed, local video speed, and any hard-limit warning. These become non-overlapping `SlowRegion` objects. The single mapping function is then reused to plan audio placement and finalize subtitle timestamps.

Export is separated from planning. The core can fully test parsing, planning, and command construction without a GPU, model, media file, or FFmpeg. When available, FFmpeg performs reviewed local-file assembly and muxing.
