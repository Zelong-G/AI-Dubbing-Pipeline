"""TTS contracts, duration planning, and offline-safe adapters."""

from ai_dubbing.tts.adapters import CallableTTSAdapter
from ai_dubbing.tts.base import TTSBackend
from ai_dubbing.tts.duration import (
    HeuristicDurationEstimator,
    SpeechDurationEstimator,
)
from ai_dubbing.tts.mock import MockTTSBackend

__all__ = [
    "CallableTTSAdapter",
    "HeuristicDurationEstimator",
    "MockTTSBackend",
    "SpeechDurationEstimator",
    "TTSBackend",
]
