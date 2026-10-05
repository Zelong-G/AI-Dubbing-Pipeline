"""TTS contracts and offline-safe backends."""

from ai_dubbing.tts.base import TTSBackend
from ai_dubbing.tts.mock import MockTTSBackend

__all__ = ["MockTTSBackend", "TTSBackend"]
