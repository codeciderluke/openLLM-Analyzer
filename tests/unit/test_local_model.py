"""External/local model loading: GGUF reader + LocalModelService."""

from __future__ import annotations

import struct
from pathlib import Path

import pytest

from ollama_inspector.domain.enums import DerivationType
from ollama_inspector.domain.errors import LocalModelError
from ollama_inspector.infrastructure.gguf_reader import read_gguf_metadata
from ollama_inspector.services.local_model_service import LocalModelService

# GGUF value type constants (subset used by the builder).
_UINT32 = 4
_STRING = 8
_ARRAY = 9


def _gguf_string(text: str) -> bytes:
    raw = text.encode("utf-8")
    return struct.pack("<Q", len(raw)) + raw


def _kv_string(key: str, value: str) -> bytes:
    return _gguf_string(key) + struct.pack("<I", _STRING) + _gguf_string(value)


def _kv_u32(key: str, value: int) -> bytes:
    return _gguf_string(key) + struct.pack("<I", _UINT32) + struct.pack("<I", value)


def _kv_str_array(key: str, values: list[str]) -> bytes:
    body = _gguf_string(key) + struct.pack("<I", _ARRAY)
    body += struct.pack("<I", _STRING) + struct.pack("<Q", len(values))
    for v in values:
        body += _gguf_string(v)
    return body


def _build_gguf(kvs: list[bytes], tensor_count: int = 0) -> bytes:
    header = b"GGUF" + struct.pack("<I", 3)
    header += struct.pack("<Q", tensor_count) + struct.pack("<Q", len(kvs))
    return header + b"".join(kvs)


def _write_llama_gguf(path: Path, vocab: int = 200) -> None:
    kvs = [
        _kv_string("general.architecture", "llama"),
        _kv_string("general.name", "My Local Llama"),
        _kv_u32("general.file_type", 13),
        _kv_u32("llama.context_length", 8192),
        _kv_u32("llama.embedding_length", 4096),
        _kv_u32("llama.block_count", 32),
        _kv_u32("llama.attention.head_count", 32),
        _kv_u32("llama.attention.head_count_kv", 8),
        _kv_str_array("tokenizer.ggml.tokens", [f"t{i}" for i in range(vocab)]),
    ]
    path.write_bytes(_build_gguf(kvs))


def test_read_gguf_metadata(tmp_path: Path) -> None:
    gguf = tmp_path / "model.gguf"
    _write_llama_gguf(gguf)
    meta = read_gguf_metadata(gguf)
    assert meta.version == 3
    assert meta.architecture == "llama"
    assert meta.name == "My Local Llama"
    assert meta.quantization == "Q4_K_M"
    assert meta.metadata["llama.context_length"] == 8192
    # Large token array collapses to its length (int), preserving vocab.
    assert meta.metadata["tokenizer.ggml.tokens"] == 200


def test_read_gguf_rejects_non_gguf(tmp_path: Path) -> None:
    bad = tmp_path / "not.gguf"
    bad.write_bytes(b"XXXX not a gguf file")
    with pytest.raises(LocalModelError):
        read_gguf_metadata(bad)


def test_local_service_analyzes_gguf(tmp_path: Path) -> None:
    gguf = tmp_path / "local.gguf"
    _write_llama_gguf(gguf, vocab=128257)
    result = LocalModelService().analyze_path(gguf)
    assert result.summary.name == "My Local Llama"
    assert result.architecture.architecture == "llama"
    assert result.architecture.context_length == 8192
    assert result.architecture.head_dimension == 128
    assert result.architecture.vocabulary_size == 128257
    assert result.summary.quantization_level == "Q4_K_M"
    assert any("External GGUF" in w for w in result.warnings)


def test_local_service_analyzes_modelfile(tmp_path: Path) -> None:
    mf = tmp_path / "Modelfile"
    mf.write_text("FROM llama3.1:8b\nADAPTER ./a.gguf\n", encoding="utf-8")
    result = LocalModelService().analyze_path(mf)
    assert result.lineage.derivation_type is DerivationType.LORA_ADAPTER
    assert any("Modelfile" in w for w in result.warnings)


def test_local_service_directory_finds_gguf(tmp_path: Path) -> None:
    _write_llama_gguf(tmp_path / "weights.gguf")
    result = LocalModelService().analyze_path(tmp_path)
    assert result.architecture.architecture == "llama"


def test_local_service_missing_path(tmp_path: Path) -> None:
    with pytest.raises(LocalModelError):
        LocalModelService().analyze_path(tmp_path / "nope.gguf")
