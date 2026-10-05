"""Optional local OCR adapter for frames extracted from user-provided media."""
from __future__ import annotations

from pathlib import Path
from typing import Protocol


class SubtitleOCR(Protocol):
    def detect(self, image_path: Path) -> str:
        """Return detected subtitle text from one local image."""


class RapidOCRAdapter:
    """Lazy adapter: optional OCR packages and models are never imported by CI."""

    def detect(self, image_path: Path) -> str:
        try:
            from rapidocr import RapidOCR
        except ImportError as error:  # pragma: no cover - optional dependency
            raise RuntimeError("Install the OCR extra to use RapidOCRAdapter.") from error
        engine = RapidOCR()
        result, _ = engine(str(image_path))
        return " ".join(str(row[1]) for row in result or [])
