"""Small text helpers with no external dependencies."""

from __future__ import annotations

import re

_UNSAFE_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def normalize_base_url(raw: str) -> str:
    """Normalise an Ollama base URL.

    Strips surrounding whitespace and trailing slashes. Raises ``ValueError``
    when no URL scheme is present.
    """

    url = raw.strip()
    if not url:
        raise ValueError("URL is empty.")
    if "://" not in url:
        raise ValueError("A URL scheme (http:// or https://) is required.")
    return url.rstrip("/")


def safe_filename(name: str) -> str:
    """Replace characters that are illegal in filenames with underscores."""

    cleaned = _UNSAFE_FILENAME_CHARS.sub("_", name).strip()
    return cleaned or "model"


def truncate(value: str, limit: int = 120) -> str:
    """Truncate a long single-line value for compact UI display."""

    flat = value.replace("\n", " ").strip()
    if len(flat) <= limit:
        return flat
    return flat[: limit - 1] + "…"
