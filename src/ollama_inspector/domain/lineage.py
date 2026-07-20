"""Model lineage / derivation analysis output."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ollama_inspector.domain.enums import DerivationType
from ollama_inspector.domain.evidence import Evidence


class ModelLineage(BaseModel):
    """Where the current model came from, with supporting evidence."""

    current_model: str
    base_model: str | None = None
    parent_model: str | None = None
    adapter_sources: list[str] = Field(default_factory=list)
    derivation_type: DerivationType = DerivationType.UNKNOWN_DERIVATIVE
    evidence: list[Evidence] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
