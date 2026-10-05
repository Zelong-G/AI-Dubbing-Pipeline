"""Batching, cache validation, QA, and resumable translation orchestration."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from ai_dubbing.common.io import atomic_json_dump, content_digest, read_json
from ai_dubbing.common.models import Cue
from ai_dubbing.translation.normalization import normalize_translation
from ai_dubbing.translation.qa import QAResult, inspect_translation
from ai_dubbing.translation.translator import TranslationBackend


@dataclass(frozen=True)
class TranslationRecord:
    cue: Cue
    english: str
    qa: QAResult
    cached: bool = False


def make_batches(cues: list[Cue], max_items: int, max_characters: int) -> list[list[Cue]]:
    if max_items < 1 or max_characters < 1:
        raise ValueError("Batch limits must be positive.")
    batches: list[list[Cue]] = []
    current: list[Cue] = []
    characters = 0
    for cue in cues:
        size = len(cue.text)
        if current and (len(current) >= max_items or characters + size > max_characters):
            batches.append(current)
            current, characters = [], 0
        current.append(cue)
        characters += size
    if current:
        batches.append(current)
    return batches


class TranslationService:
    """Translate independently addressable units and persist valid progress."""

    schema_version = 1

    def __init__(
        self,
        backend: TranslationBackend,
        *,
        batch_items: int = 12,
        batch_characters: int = 2_400,
        context_size: int = 2,
    ) -> None:
        self.backend = backend
        self.batch_items = batch_items
        self.batch_characters = batch_characters
        self.context_size = context_size

    def translate(
        self, cues: list[Cue], *, cache_path: Path | None = None
    ) -> list[TranslationRecord]:
        fingerprint = content_digest("\n".join(f"{c.index}:{c.text}" for c in cues))
        cached = self._load_cache(cache_path, fingerprint)
        records: dict[int, TranslationRecord] = {}
        by_index = {cue.index: cue for cue in cues}
        for index, value in cached.items():
            cue = by_index.get(index)
            if cue is None:
                continue
            normalized = normalize_translation(value)
            qa = inspect_translation(cue, normalized)
            if qa.ok:
                records[index] = TranslationRecord(cue, normalized, qa, cached=True)

        for batch in make_batches(cues, self.batch_items, self.batch_characters):
            pending = [cue for cue in batch if cue.index not in records]
            if not pending:
                continue
            start = cues.index(pending[0])
            context = cues[max(0, start - self.context_size) : start]
            responses = self.backend.translate(pending, context=context)
            for cue in pending:
                english = normalize_translation(responses.get(cue.index, ""))
                qa = inspect_translation(cue, english)
                records[cue.index] = TranslationRecord(cue, english, qa)
            self._save_cache(cache_path, fingerprint, records)

        return [records[cue.index] for cue in cues]

    def _load_cache(self, path: Path | None, fingerprint: str) -> dict[int, str]:
        if path is None:
            return {}
        payload = read_json(path, {})
        if (
            payload.get("schema_version") != self.schema_version
            or payload.get("fingerprint") != fingerprint
            or payload.get("backend") != self.backend.name
        ):
            return {}
        rows = payload.get("translations", {})
        return {int(key): str(value) for key, value in rows.items() if str(key).isdigit()}

    def _save_cache(
        self,
        path: Path | None,
        fingerprint: str,
        records: dict[int, TranslationRecord],
    ) -> None:
        if path is None:
            return
        atomic_json_dump(
            path,
            {
                "schema_version": self.schema_version,
                "fingerprint": fingerprint,
                "backend": self.backend.name,
                "translations": {
                    str(index): record.english
                    for index, record in records.items()
                    if record.qa.ok
                },
                "qa": {
                    str(index): asdict(record.qa)
                    for index, record in records.items()
                },
            },
        )
