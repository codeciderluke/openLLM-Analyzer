"""Helpers for safely reading heterogeneous ``model_info`` metadata."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

# Capability strings used by Ollama (kept as data, not hardcoded per-model).
CAP_COMPLETION = "completion"
CAP_EMBEDDING = "embedding"
CAP_VISION = "vision"
CAP_AUDIO = "audio"
CAP_TOOLS = "tools"
CAP_INSERT = "insert"
CAP_THINKING = "thinking"


def as_int(value: Any) -> int | None:
    """Best-effort conversion of a metadata value to ``int``."""

    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str):
        text = value.strip()
        try:
            return int(text)
        except ValueError:
            try:
                fval = float(text)
            except ValueError:
                return None
            return int(fval) if fval.is_integer() else None
    return None


def first_present(metadata: Mapping[str, Any], keys: list[str]) -> Any | None:
    """Return the first non-null value among ``keys`` in ``metadata``."""

    for key in keys:
        if key in metadata and metadata[key] is not None:
            return metadata[key]
    return None


def first_int(metadata: Mapping[str, Any], keys: list[str]) -> tuple[int | None, str | None]:
    """Return the first int-coercible value and the key it came from."""

    for key in keys:
        if key in metadata and metadata[key] is not None:
            coerced = as_int(metadata[key])
            if coerced is not None:
                return coerced, key
    return None, None


def has_capability(capabilities: list[str], name: str) -> bool:
    """Case-insensitive membership check over a capability list."""

    lowered = {c.lower() for c in capabilities if isinstance(c, str)}
    return name.lower() in lowered


def sequence_length(value: Any) -> int | None:
    """Length of a list/tuple value, else ``None`` (e.g. tokenizer tokens)."""

    if isinstance(value, (list, tuple)):
        return len(value)
    return None
