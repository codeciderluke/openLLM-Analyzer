"""RAG suitability analyzer.

Heuristic role-fitness scoring from metadata only. It never claims an actual
RAG connection or answer quality — that mandatory caveat is always attached.
"""

from __future__ import annotations

from ollama_inspector.analyzers import metadata_utils as mu
from ollama_inspector.domain.architecture import CanonicalArchitecture
from ollama_inspector.domain.enums import EvidenceStatus, RAGRole
from ollama_inspector.domain.evidence import Evidence
from ollama_inspector.domain.rag import RAGSuitability

_HEURISTIC_NOTICE = (
    "This assessment is a metadata-based heuristic. "
    "It does not reflect an actual RAG connection or answer quality."
)


class RAGSuitabilityAnalyzer:
    """Produces a :class:`RAGSuitability` assessment."""

    def analyze(
        self,
        capabilities: list[str],
        architecture: CanonicalArchitecture,
        has_template: bool,
        has_system_or_chat: bool,
    ) -> RAGSuitability:
        capabilities = capabilities or []
        has_completion = mu.has_capability(capabilities, mu.CAP_COMPLETION)
        has_embedding = mu.has_capability(capabilities, mu.CAP_EMBEDDING)
        has_vision = mu.has_capability(capabilities, mu.CAP_VISION)
        has_tools = mu.has_capability(capabilities, mu.CAP_TOOLS)
        context = architecture.context_length

        result = RAGSuitability()
        result.roles = self._roles(has_completion, has_embedding, has_vision)

        result.generation_score = self._generation_score(
            result, has_completion, has_template, has_system_or_chat, context, has_tools, has_vision
        )
        result.embedding_score = self._embedding_score(
            result, has_embedding, architecture.embedding_length, has_completion, context
        )
        result.long_context_score = self._long_context_score(result, context)

        result.generation_suitable = has_completion
        result.embedding_suitable = has_embedding
        result.multimodal_rag_suitable = has_completion and has_vision
        result.long_context_suitable = (
            None if context is None else context >= 8192
        )

        result.limitations.append(_HEURISTIC_NOTICE)
        if not has_completion and not has_embedding:
            result.limitations.append(
                "No completion/embedding capability, so the RAG role cannot be determined."
            )
        return result

    # -- roles ----------------------------------------------------------

    @staticmethod
    def _roles(has_completion: bool, has_embedding: bool, has_vision: bool) -> list[RAGRole]:
        roles: list[RAGRole] = []
        if has_completion:
            roles.append(RAGRole.GENERATOR)
        if has_embedding:
            roles.append(RAGRole.EMBEDDING)
        if has_completion and has_vision:
            roles.append(RAGRole.MULTIMODAL_GENERATOR)
        if not roles:
            roles.append(RAGRole.UNKNOWN)
        return roles

    # -- generation -----------------------------------------------------

    def _generation_score(
        self,
        result: RAGSuitability,
        has_completion: bool,
        has_template: bool,
        has_system_or_chat: bool,
        context: int | None,
        has_tools: bool,
        has_vision: bool,
    ) -> int:
        score = 0
        if has_completion:
            score += 40
            result.reasons.append("completion capability (+40)")
        if has_template:
            score += 10
            result.reasons.append("template present (+10)")
        if has_system_or_chat:
            score += 5
            result.reasons.append("system/chat configuration present (+5)")
        if context is not None and context >= 8192:
            score += 15
            result.reasons.append("context >= 8,192 (+15)")
        if context is not None and context >= 32768:
            score += 10
            result.reasons.append("context >= 32,768 (+10)")
        if has_tools:
            score += 10
            result.reasons.append("tools/structured capability (+10)")
        if has_vision and has_completion:
            score += 5
            result.reasons.append("vision + completion (+5)")

        score = min(score, 100)
        result.evidence.append(
            Evidence(
                field="generation_score",
                status=EvidenceStatus.DERIVED,
                source="heuristic",
                description="generation suitability score",
                value=score,
            )
        )
        return score

    # -- embedding ------------------------------------------------------

    def _embedding_score(
        self,
        result: RAGSuitability,
        has_embedding: bool,
        embedding_length: int | None,
        has_completion: bool,
        context: int | None,
    ) -> int:
        score = 0
        if has_embedding:
            score += 60
            result.reasons.append("embedding capability (+60)")
        if embedding_length is not None:
            score += 20
            result.reasons.append("embedding length present (+20)")
        if not has_completion:
            score += 10
            result.reasons.append("no completion capability (+10)")
        if context is not None and context >= 2048:
            score += 10
            result.reasons.append("context >= 2,048 (+10)")

        score = min(score, 100)
        result.evidence.append(
            Evidence(
                field="embedding_score",
                status=EvidenceStatus.DERIVED,
                source="heuristic",
                description="embedding suitability score",
                value=score,
            )
        )
        return score

    # -- long context ---------------------------------------------------

    def _long_context_score(
        self, result: RAGSuitability, context: int | None
    ) -> int | None:
        if context is None:
            result.limitations.append("context length unknown, no long-context score")
            return None
        if context >= 65536:
            score = 100
        elif context >= 32768:
            score = 80
        elif context >= 8192:
            score = 60
        elif context >= 4096:
            score = 40
        else:
            score = 20
        result.evidence.append(
            Evidence(
                field="long_context_score",
                status=EvidenceStatus.DERIVED,
                source="heuristic",
                description=f"score based on context length={context}",
                value=score,
            )
        )
        return score
