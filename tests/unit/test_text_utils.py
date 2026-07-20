"""Utility helpers."""

from __future__ import annotations

import pytest

from ollama_inspector.utils.text import normalize_base_url, safe_filename, truncate


def test_normalize_strips_trailing_slash() -> None:
    assert normalize_base_url("http://localhost:11434/") == "http://localhost:11434"


def test_normalize_requires_scheme() -> None:
    with pytest.raises(ValueError):
        normalize_base_url("localhost:11434")


def test_normalize_empty() -> None:
    with pytest.raises(ValueError):
        normalize_base_url("   ")


def test_safe_filename_replaces_illegal() -> None:
    assert safe_filename("llama3.1:8b") == "llama3.1_8b"
    assert safe_filename("a/b\\c") == "a_b_c"


def test_truncate() -> None:
    assert truncate("short") == "short"
    assert truncate("x" * 200, limit=10).endswith("…")
