"""Lightweight per-model summary used in the catalog list."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ModelSummary(BaseModel):
    """Summary derived from an ``/api/tags`` entry.

    Every field except ``name`` is optional because the Ollama API may omit
    parts of ``details`` depending on the model.
    """

    name: str
    model: str | None = None
    digest: str | None = None
    modified_at: str | None = None
    size_bytes: int | None = None
    format: str | None = None
    family: str | None = None
    families: list[str] = Field(default_factory=list)
    parameter_size: str | None = None
    quantization_level: str | None = None
