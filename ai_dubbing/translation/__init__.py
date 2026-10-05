"""Translation backends, prompt construction, normalization, and QA."""

from ai_dubbing.translation.service import TranslationService
from ai_dubbing.translation.translator import MockTranslator, TranslationBackend

__all__ = ["MockTranslator", "TranslationBackend", "TranslationService"]
