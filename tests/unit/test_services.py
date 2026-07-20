"""Steps 4 & 10: catalog and analysis services + export."""

from __future__ import annotations

from pathlib import Path

import httpx

from ollama_inspector.domain.enums import DerivationType, FineTuningMethod
from ollama_inspector.infrastructure.ollama_client import OllamaClient
from ollama_inspector.services.export_service import ExportService
from ollama_inspector.services.model_analysis_service import ModelAnalysisService
from ollama_inspector.services.model_catalog_service import ModelCatalogService


def _client(payload_by_path) -> OllamaClient:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=payload_by_path[request.url.path])

    return OllamaClient("http://localhost:11434", transport=httpx.MockTransport(handler))


def test_catalog_service_sorts_and_normalises(tags_payload) -> None:
    client = _client({"/api/tags": tags_payload})
    models = ModelCatalogService(client).load_models()
    names = [m.name for m in models]
    assert names == sorted(names, key=str.lower)
    llama = next(m for m in models if m.name == "llama3.1:8b")
    assert llama.parameter_size == "8.0B"
    # Missing details handled gracefully.
    custom = next(m for m in models if m.name == "custom-model:latest")
    assert custom.family is None


def test_analysis_service_llama(show_llama) -> None:
    service = ModelAnalysisService(_client({"/api/show": show_llama}))
    result = service.analyze_model("llama3.1:8b")
    assert result.architecture.context_length == 131072
    assert result.lineage.derivation_type is DerivationType.PROMPT_ONLY_DERIVATIVE
    assert result.rag.generation_suitable is True
    assert result.raw_response  # raw preserved


def test_analysis_service_lora(show_lora) -> None:
    service = ModelAnalysisService(_client({"/api/show": show_lora}))
    result = service.analyze_model("support:latest")
    assert result.fine_tuning.method is FineTuningMethod.LORA
    assert result.lineage.derivation_type is DerivationType.LORA_ADAPTER


def test_export_json_and_markdown(show_llama, tmp_path: Path) -> None:
    service = ModelAnalysisService(_client({"/api/show": show_llama}))
    result = service.analyze_model("llama3.1:8b")
    export = ExportService()

    json_text = export.to_json(result)
    assert '"name"' in json_text
    assert "llama3.1:8b" in json_text

    md_text = export.to_markdown(result)
    assert "# Model Inspection Report" in md_text
    assert "## RAG Suitability" in md_text

    json_path = export.save_json(result, tmp_path / "r.json")
    md_path = export.save_markdown(result, tmp_path / "r.md")
    assert json_path.exists()
    assert md_path.exists()


def test_default_filename_sanitised(show_llama) -> None:
    service = ModelAnalysisService(_client({"/api/show": show_llama}))
    result = service.analyze_model("llama3.1:8b")
    name = ExportService.default_filename(result, "json")
    assert name == "llama3.1_8b.json"
