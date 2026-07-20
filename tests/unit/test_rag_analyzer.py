"""Step 9: RAG suitability analyzer."""

from __future__ import annotations

from ollama_inspector.analyzers.rag_suitability_analyzer import RAGSuitabilityAnalyzer
from ollama_inspector.domain.architecture import CanonicalArchitecture
from ollama_inspector.domain.enums import RAGRole


def test_generator_scoring_high_context() -> None:
    arch = CanonicalArchitecture(context_length=131072)
    rag = RAGSuitabilityAnalyzer().analyze(
        ["completion", "tools"], arch, has_template=True, has_system_or_chat=True
    )
    # 40 + 10 + 5 + 15 + 10 + 10 = 90
    assert rag.generation_score == 90
    assert rag.generation_suitable is True
    assert RAGRole.GENERATOR in rag.roles


def test_embedding_scoring() -> None:
    arch = CanonicalArchitecture(context_length=512, embedding_length=384)
    rag = RAGSuitabilityAnalyzer().analyze(
        ["embedding"], arch, has_template=False, has_system_or_chat=False
    )
    # 60 + 20 + 10 (no completion) = 90
    assert rag.embedding_score == 90
    assert rag.embedding_suitable is True
    assert RAGRole.EMBEDDING in rag.roles


def test_long_context_score_thresholds() -> None:
    analyzer = RAGSuitabilityAnalyzer()

    def score(ctx: int) -> int | None:
        arch = CanonicalArchitecture(context_length=ctx)
        return analyzer.analyze([], arch, False, False).long_context_score

    assert score(2048) == 20
    assert score(4096) == 40
    assert score(8192) == 60
    assert score(32768) == 80
    assert score(65536) == 100


def test_long_context_unknown() -> None:
    rag = RAGSuitabilityAnalyzer().analyze([], CanonicalArchitecture(), False, False)
    assert rag.long_context_score is None


def test_multimodal_role() -> None:
    arch = CanonicalArchitecture(context_length=8192)
    rag = RAGSuitabilityAnalyzer().analyze(
        ["completion", "vision"], arch, has_template=True, has_system_or_chat=True
    )
    assert rag.multimodal_rag_suitable is True
    assert RAGRole.MULTIMODAL_GENERATOR in rag.roles


def test_heuristic_notice_always_present() -> None:
    rag = RAGSuitabilityAnalyzer().analyze([], CanonicalArchitecture(), False, False)
    assert any("heuristic" in limitation.lower() for limitation in rag.limitations)
