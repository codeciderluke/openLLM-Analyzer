"""Low-level file writing for reports (Qt-free)."""

from __future__ import annotations

from pathlib import Path

from ollama_inspector.domain.errors import ExportError


def write_text_file(path: Path, content: str) -> Path:
    """Write UTF-8 text to ``path``, creating parent directories."""

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    except OSError as exc:
        raise ExportError(f"Could not write the file: {path}") from exc
    return path
