"""Interface for optional local speaker-embedding implementations."""
from __future__ import annotations

from pathlib import Path
from typing import Protocol


class SpeakerEmbedder(Protocol):
    def embed(self, audio_path: Path) -> list[float]:
        """Produce an embedding from user-supplied local audio."""
