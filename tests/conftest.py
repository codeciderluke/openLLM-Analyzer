"""Shared pytest fixtures."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> dict[str, Any]:
    """Load a JSON fixture from ``tests/fixtures``."""

    return json.loads((FIXTURES_DIR / name).read_text(encoding="utf-8"))


@pytest.fixture
def fixtures_dir() -> Path:
    return FIXTURES_DIR


@pytest.fixture
def show_llama() -> dict[str, Any]:
    return load_fixture("show_llama.json")


@pytest.fixture
def show_embedding() -> dict[str, Any]:
    return load_fixture("show_embedding.json")


@pytest.fixture
def show_lora() -> dict[str, Any]:
    return load_fixture("show_lora.json")


@pytest.fixture
def tags_payload() -> dict[str, Any]:
    return load_fixture("tags.json")
