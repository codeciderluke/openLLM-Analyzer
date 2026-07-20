"""Step 6: architecture analyzer."""

from __future__ import annotations

from ollama_inspector.analyzers.architecture_analyzer import ArchitectureAnalyzer


def test_llama_canonical(show_llama) -> None:
    arch = ArchitectureAnalyzer().analyze(
        show_llama["model_info"], show_llama["details"], show_llama["capabilities"]
    )
    assert arch.architecture == "llama"
    assert arch.context_length == 131072
    assert arch.embedding_length == 4096
    assert arch.attention_heads == 32
    assert arch.kv_heads == 8
    # derived
    assert arch.head_dimension == 128  # 4096 / 32
    assert arch.gqa_ratio == 4.0  # 32 / 8
    assert "text" in arch.modalities


def test_vocab_from_tokens_when_missing() -> None:
    mi = {"general.architecture": "foo", "tokenizer.ggml.tokens": ["x", "y", "z", "w"]}
    arch = ArchitectureAnalyzer().analyze(mi, {}, [])
    assert arch.vocabulary_size == 4


def test_unknown_architecture_generic_fallback() -> None:
    mi = {"mystery.block_count": 10, "mystery.embedding_length": 512}
    arch = ArchitectureAnalyzer().analyze(mi, {}, [])
    # prefix-detected architecture name
    assert arch.architecture == "mystery"
    assert arch.block_count == 10
    assert arch.embedding_length == 512
    assert arch.raw_metadata == mi


def test_head_dimension_skipped_when_not_divisible() -> None:
    mi = {
        "general.architecture": "foo",
        "foo.embedding_length": 100,
        "foo.attention.head_count": 7,
    }
    arch = ArchitectureAnalyzer().analyze(mi, {}, [])
    assert arch.head_dimension is None


def test_family_used_when_no_architecture() -> None:
    arch = ArchitectureAnalyzer().analyze({}, {"family": "bert"}, ["embedding"])
    assert arch.architecture == "bert"
    assert "embedding" in arch.modalities


def test_vision_metadata_detected() -> None:
    mi = {
        "general.architecture": "qwen2vl",
        "qwen2vl.vision.block_count": 32,
        "qwen2vl.vision.embedding_length": 1280,
    }
    arch = ArchitectureAnalyzer().analyze(mi, {}, ["completion", "vision"])
    assert arch.vision is not None
    assert arch.vision.block_count == 32
    assert "vision" in arch.modalities
