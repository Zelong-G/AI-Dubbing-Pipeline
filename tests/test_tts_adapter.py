from pathlib import Path

from ai_dubbing.common.models import TTSResult
from ai_dubbing.tts.adapters import CallableTTSAdapter


def test_callable_tts_adapter_wraps_external_synthesizer(
    tmp_path: Path,
) -> None:
    def synthesize(text, output_path, **kwargs):
        del text, kwargs
        output_path.write_bytes(b"synthetic")
        return TTSResult(
            str(output_path),
            duration=1.25,
            sample_rate=16_000,
            backend="external-demo",
        )

    adapter = CallableTTSAdapter("external-demo", synthesize)
    output = tmp_path / "speech.wav"
    result = adapter.synthesize("Hello.", output)

    assert output.read_bytes() == b"synthetic"
    assert result.duration == 1.25
    assert adapter.name == "external-demo"
