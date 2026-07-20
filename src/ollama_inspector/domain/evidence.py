"""Evidence records attached to analysis outputs."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ollama_inspector.domain.enums import EvidenceStatus


class Evidence(BaseModel):
    """A single traceable fact produced by an analyzer.

    Every derived or detected value should carry an Evidence entry so the UI
    can show *why* a conclusion was reached and how trustworthy it is.
    """

    field: str
    status: EvidenceStatus
    source: str
    description: str
    value: object | None = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
