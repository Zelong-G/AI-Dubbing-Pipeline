# Third-party components

This repository vendors no third-party source code, model weights, datasets, reference audio, or media assets. The core test suite and offline planning demos use only the Python standard library.

Optional integrations may use independently installed software:

| Component | Purpose | Bundled? |
| --- | --- | --- |
| FFmpeg | Local audio mixing, muxing, and media export | No |
| RapidOCR | Optional subtitle OCR from user-provided local frames | No |
| PyTorch / speech frameworks | Model-specific TTS implementations connected through the TTSBackend contract | No |
| XTTS, Chatterbox, or other TTS models | Examples of externally managed synthesis backends | No |

The repository provides a generic CallableTTSAdapter; it does **not** claim to ship a ready-to-run wrapper for any particular model family. Model loading, weights, device placement, reference-audio policy, and model-specific licenses remain deployment-owned.

Before using an optional integration, verify the license and model terms for the exact version installed. Users are responsible for ensuring they have rights to their local media, text, reference audio, and generated outputs.
