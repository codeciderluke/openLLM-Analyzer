"""Step 8: lineage analyzer."""

from __future__ import annotations

from ollama_inspector.analyzers.lineage_analyzer import LineageAnalyzer
from ollama_inspector.analyzers.modelfile_parser import ModelfileParser
from ollama_inspector.domain.enums import DerivationType


def _lineage(modelfile: str, details=None):
    parsed = ModelfileParser().parse(modelfile)
    return LineageAnalyzer().analyze("current:latest", parsed, details or {}, {})


def test_lora_adapter() -> None:
    lineage = _lineage("FROM base:latest\nADAPTER ./a.gguf")
    assert lineage.derivation_type is DerivationType.LORA_ADAPTER
    assert lineage.base_model == "base:latest"
    assert lineage.adapter_sources == ["./a.gguf"]


def test_prompt_only_derivative() -> None:
    lineage = _lineage("FROM base:latest\nSYSTEM hello")
    assert lineage.derivation_type is DerivationType.PROMPT_ONLY_DERIVATIVE


def test_quantized_derivative() -> None:
    lineage = _lineage("FROM base:latest", details={"quantization_level": "Q4_K_M"})
    assert lineage.derivation_type is DerivationType.QUANTIZED_DERIVATIVE


def test_custom_modelfile_from_only() -> None:
    lineage = _lineage("FROM base:latest")
    assert lineage.derivation_type is DerivationType.CUSTOM_MODELFILE


def test_official_base_no_evidence() -> None:
    lineage = _lineage("")
    assert lineage.derivation_type is DerivationType.OFFICIAL_BASE


def test_api_parent_fills_base() -> None:
    parsed = ModelfileParser().parse("")
    lineage = LineageAnalyzer().analyze(
        "current:latest", parsed, {"parent_model": "root:latest"}, {}
    )
    assert lineage.base_model == "root:latest"
