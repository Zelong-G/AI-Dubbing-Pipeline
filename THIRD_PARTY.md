# Third-party components

The repository contains no vendored third-party source code, model weights, or
media assets. The core test suite uses only the Python standard library.

Optional integrations may use the following independently installed projects:

- FFmpeg for audio mixing, subtitle rendering, and video export.
- PyTorch and a compatible speech stack for model-backed synthesis.
- RapidOCR for local subtitle detection.
- XTTS or Chatterbox for optional TTS adapters.

These components are not bundled. Before using an integration, review the
license, model terms, and version-specific requirements published by its
upstream provider. Users are responsible for ensuring they have rights to
their local media, reference audio, and generated outputs.
