"""Optional YAML configuration loading with explicit dependency boundaries."""
from __future__ import annotations

from pathlib import Path
from typing import Any


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml
    except ImportError as error:  # pragma: no cover - depends on optional extra
        raise RuntimeError(
            "Install the config extra to load YAML configuration files."
        ) from error
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError("A configuration file must contain a mapping at its root.")
    return value
