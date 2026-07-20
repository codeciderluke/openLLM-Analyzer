"""Canonical architecture schema normalised from raw ``model_info``."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ollama_inspector.domain.evidence import Evidence


class VisionArchitecture(BaseModel):
    """Vision-tower structural values, when present."""

    block_count: int | None = None
    embedding_length: int | None = None
    attention_heads: int | None = None
    patch_size: int | None = None


class AudioArchitecture(BaseModel):
    """Audio-tower structural values, when present."""

    block_count: int | None = None
    embedding_length: int | None = None


class CanonicalArchitecture(BaseModel):
    """Common architecture view shared across all model families.

    Unknown architectures still populate ``architecture``, ``raw_metadata``
    and any numeric structural values that could be discovered generically.
    """

    architecture: str | None = None
    modalities: list[str] = Field(default_factory=list)

    context_length: int | None = None
    embedding_length: int | None = None
    vocabulary_size: int | None = None
    block_count: int | None = None
    feed_forward_length: int | None = None

    attention_heads: int | None = None
    kv_heads: int | None = None
    head_dimension: int | None = None
    gqa_ratio: float | None = None

    vision: VisionArchitecture | None = None
    audio: AudioArchitecture | None = None

    raw_metadata: dict[str, object] = Field(default_factory=dict)
    evidence: list[Evidence] = Field(default_factory=list)
