"""Provider-neutral prompt material for a structured translation request."""
from __future__ import annotations

from ai_dubbing.common.models import Cue


SYSTEM_PROMPT = """Translate each requested subtitle independently into natural spoken English.
Use neighboring cues only to resolve references. Preserve the requested IDs and
never move events between them. Prefer concise, speakable wording."""


def build_batch_prompt(cues: list[Cue], context: list[Cue]) -> str:
    context_rows = "\n".join(f"{cue.index}: {cue.text}" for cue in context)
    request_rows = "\n".join(f"{cue.index}\t{cue.text}" for cue in cues)
    return (
        f"{SYSTEM_PROMPT}\n\nContext (do not translate as output):\n{context_rows or '(none)'}"
        f"\n\nRequested rows:\n{request_rows}\n\n"
        "Return one TSV row per request: ID<TAB>ENGLISH."
    )
