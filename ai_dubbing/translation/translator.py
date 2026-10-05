"""Translation backend contracts and lightweight implementations."""
from __future__ import annotations

import json
import os
from typing import Protocol
from urllib.request import Request, urlopen

from ai_dubbing.common.models import Cue
from ai_dubbing.translation.prompts import build_batch_prompt


class TranslationBackend(Protocol):
    name: str

    def translate(self, cues: list[Cue], *, context: list[Cue]) -> dict[int, str]:
        """Return an English string for every supplied cue index."""


class MockTranslator:
    """Deterministic offline translator used by examples, tests, and CI."""

    name = "mock"
    _phrases = {
        "我们到了吗？": "Are we there?",
        "应该快了。": "We should be close.",
        "清晨，凯走出了车站。": "Kai stepped out of the station early in the morning.",
        "他看了看地图。": "He checked the map.",
        "应该就是这里了。": "This should be the place.",
    }

    def translate(self, cues: list[Cue], *, context: list[Cue]) -> dict[int, str]:
        del context
        return {
            cue.index: self._phrases.get(cue.text, "A clear example line.")
            for cue in cues
        }


class OpenAICompatibleTranslator:
    """Optional HTTP adapter for an OpenAI-shaped local or hosted endpoint.

    No credentials are stored in code or configuration. A deployment may pass a
    custom header mapping when it constructs this adapter. The examples and CI
    never instantiate it.
    """

    name = "openai-compatible"

    def __init__(
        self,
        endpoint: str,
        model: str,
        *,
        headers: dict[str, str] | None = None,
        timeout_seconds: int = 60,
    ) -> None:
        self.endpoint = endpoint.rstrip("/")
        self.model = model
        self.headers = dict(headers or {})
        self.timeout_seconds = timeout_seconds

    @classmethod
    def from_environment(cls, endpoint: str, model: str) -> "OpenAICompatibleTranslator":
        """Build an unauthenticated adapter or pass a deployment credential safely.

        A custom gateway can consume ``AI_DUBBING_LLM_CREDENTIAL``. Standard
        endpoint-specific authentication remains intentionally deployment-owned.
        """
        credential = os.environ.get("AI_DUBBING_LLM_CREDENTIAL")
        headers = {"X-Client-Credential": credential} if credential else {}
        return cls(endpoint, model, headers=headers)

    def translate(self, cues: list[Cue], *, context: list[Cue]) -> dict[int, str]:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": build_batch_prompt(cues, context)}
            ],
            "temperature": 0,
        }
        request = Request(
            self.endpoint + "/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", **self.headers},
            method="POST",
        )
        with urlopen(request, timeout=self.timeout_seconds) as response:  # nosec B310
            body = json.loads(response.read().decode("utf-8"))
        content = str(body["choices"][0]["message"]["content"])
        result: dict[int, str] = {}
        for row in content.splitlines():
            fields = row.split("\t", 1)
            if len(fields) != 2:
                continue
            try:
                result[int(fields[0].strip())] = fields[1].strip()
            except ValueError:
                continue
        return result
