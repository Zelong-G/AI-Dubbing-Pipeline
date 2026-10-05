"""Experimental clustering interface, intentionally separate from core dubbing."""
from __future__ import annotations

from typing import Protocol


class SpeakerClusterer(Protocol):
    def cluster(self, embeddings: list[list[float]]) -> list[int]:
        """Return one experimental cluster label per embedding."""
