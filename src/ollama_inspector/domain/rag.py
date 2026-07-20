"""RAG role-suitability analysis output."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ollama_inspector.domain.enums import RAGRole
from ollama_inspector.domain.evidence import Evidence


class RAGSuitability(BaseModel):
    """Heuristic assessment of the model's suitability for RAG roles.

    This describes *role fitness* from metadata only. It does not represent
    an actual RAG connection or answer quality.
    """

    roles: list[RAGRole] = Field(default_factory=list)

    generation_suitable: bool | None = None
    embedding_suitable: bool | None = None
    long_context_suitable: bool | None = None
    multimodal_rag_suitable: bool | None = None

    generation_score: int | None = None
    embedding_score: int | None = None
    long_context_score: int | None = None

    reasons: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
