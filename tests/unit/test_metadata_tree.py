"""Step 7: metadata tree builder."""

from __future__ import annotations

from ollama_inspector.analyzers.metadata_tree_builder import build_metadata_tree


def test_builds_nested_tree() -> None:
    flat = {
        "qwen2.block_count": 28,
        "qwen2.embedding_length": 3584,
        "qwen2.attention.head_count": 28,
        "qwen2.attention.head_count_kv": 4,
    }
    roots = build_metadata_tree(flat)
    assert len(roots) == 1
    qwen2 = roots[0]
    assert qwen2.key == "qwen2"
    child_keys = [c.key for c in qwen2.children]
    assert child_keys == ["attention", "block_count", "embedding_length"]

    attention = next(c for c in qwen2.children if c.key == "attention")
    assert [c.key for c in attention.children] == ["head_count", "head_count_kv"]
    assert attention.children[0].value == 28
    assert attention.children[0].is_leaf


def test_preserves_values_and_sorts() -> None:
    roots = build_metadata_tree({"z.b": 2, "z.a": 1})
    z = roots[0]
    assert [c.key for c in z.children] == ["a", "b"]
    assert z.children[0].value == 1


def test_empty_metadata() -> None:
    assert build_metadata_tree({}) == []


def test_list_value_preserved() -> None:
    roots = build_metadata_tree({"tokenizer.tokens": ["a", "b"]})
    leaf = roots[0].children[0]
    assert leaf.value == ["a", "b"]
    assert leaf.has_value
