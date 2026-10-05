# Architecture

The project separates content processing, model boundaries, temporal planning, and media export so that the core orchestration can be tested without a network connection, GPU, speech model, or media asset.

## Shared representation

Both workflows use a common Cue representation with index, start/end times, text, and an optional speaker label. SRT files already provide timestamps. Text chapters are converted into ordered cue-like units so translation, QA, and voice-label handling can reuse the same interfaces. Speaker labels are preserved when supplied; the public text parser does not claim automatic character attribution.

## Translation

TranslationService is backend-agnostic. It validates unique cue IDs, batches by count and character budget, provides bounded previous context, normalizes responses, runs deterministic structural QA, and writes only QA-valid translations to an atomic cache.

The cache records an input fingerprint and backend name, so stale progress is ignored after a material input or backend change.

## Speech boundary

TTSBackend is the synthesis contract used by the audiobook workflow. MockTTSBackend writes deterministic tone-based WAV files for offline tests. CallableTTSAdapter can wrap an externally managed synthesizer without making this repository responsible for model loading, weights, or model-specific licensing.

Video timing planning is deliberately decoupled from synthesis through SpeechDurationEstimator. The included HeuristicDurationEstimator makes the planner deterministic and model-free; a deployment can replace it with measured durations or a learned estimator.

## Temporal alignment

The timing policy:
1. uses the cue plus safe silence before the next cue;
2. keeps natural speech speed when possible;
3. allows bounded local video slowdown;
4. increases TTS speed only when the soft slowdown limit would be exceeded;
5. emits an explicit warning when the hard fitting limit is still violated.

The resulting SlowRegion objects define one source-to-output timeline. The same map_timestamp function is reused for dialogue placement and subtitle remapping.

## Export boundary

Planning and export are separate. FFmpeg helpers only operate on existing user-provided local files and prepared audio. Parsing, translation, duration planning, subtitle remapping, and command construction can all be tested without invoking FFmpeg.
