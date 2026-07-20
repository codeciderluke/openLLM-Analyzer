"""Model analysis service.

Runs the ``/api/show`` pipeline: Modelfile parse -> architecture -> lineage
-> fine-tuning -> RAG. A single analyzer failure degrades to defaults plus a
warning rather than discarding the whole result (partial success).
"""

from __future__ import annotations

from typing import Any

from ollama_inspector.analyzers.architecture_analyzer import ArchitectureAnalyzer
from ollama_inspector.analyzers.fine_tuning_analyzer import FineTuningAnalyzer
from ollama_inspector.analyzers.lineage_analyzer import LineageAnalyzer
from ollama_inspector.analyzers.modelfile_parser import ModelfileParser
from ollama_inspector.analyzers.rag_suitability_analyzer import RAGSuitabilityAnalyzer
from ollama_inspector.domain.analysis_result import ModelAnalysisResult
from ollama_inspector.domain.architecture import CanonicalArchitecture
from ollama_inspector.domain.enums import DerivationType, FineTuningMethod
from ollama_inspector.domain.fine_tuning import FineTuningAnalysis
from ollama_inspector.domain.lineage import ModelLineage
from ollama_inspector.domain.model_summary import ModelSummary
from ollama_inspector.domain.modelfile import ParsedModelfile
from ollama_inspector.domain.rag import RAGSuitability
from ollama_inspector.infrastructure.ollama_client import OllamaClient
from ollama_inspector.utils.logging_config import get_logger

logger = get_logger("model_analysis")


class ModelAnalysisService:
    """Coordinates the analyzers for a single model."""

    def __init__(self, client: OllamaClient | None = None) -> None:
        # ``client`` is only required for :meth:`analyze_model`; local/external
        # analysis goes straight through :meth:`analyze_show_payload`.
        self._client = client
        self._modelfile_parser = ModelfileParser()
        self._architecture = ArchitectureAnalyzer()
        self._lineage = LineageAnalyzer()
        self._fine_tuning = FineTuningAnalyzer()
        self._rag = RAGSuitabilityAnalyzer()

    def analyze_model(self, model_name: str) -> ModelAnalysisResult:
        if self._client is None:
            raise RuntimeError("Ollama client is not configured.")
        raw = self._client.show_model(model_name)
        return self.analyze_show_payload(model_name, raw)

    def analyze_show_payload(
        self, model_name: str, raw: dict[str, Any]
    ) -> ModelAnalysisResult:
        """Analyse an already-fetched ``/api/show`` payload (also used in tests)."""

        warnings: list[str] = []
        details = _as_dict(raw.get("details"))
        model_info = _as_dict(raw.get("model_info"))
        capabilities = _as_str_list(raw.get("capabilities"))

        modelfile_text = _as_str(raw.get("modelfile"))
        template_text = _as_str(raw.get("template"))
        system_text = _as_str(raw.get("system"))
        parameters_text = _as_str(raw.get("parameters"))
        license_text = _as_str(raw.get("license"))

        summary = self._build_summary(model_name, details)

        parsed = self._safe(
            lambda: self._modelfile_parser.parse(modelfile_text),
            ParsedModelfile(),
            "Modelfile parsing",
            warnings,
        )
        architecture = self._safe(
            lambda: self._architecture.analyze(model_info, details, capabilities),
            CanonicalArchitecture(raw_metadata=dict(model_info)),
            "Architecture analysis",
            warnings,
        )
        lineage = self._safe(
            lambda: self._lineage.analyze(model_name, parsed, details, model_info),
            ModelLineage(
                current_model=model_name,
                derivation_type=DerivationType.UNKNOWN_DERIVATIVE,
            ),
            "Lineage analysis",
            warnings,
        )
        fine_tuning = self._safe(
            lambda: self._fine_tuning.analyze(parsed),
            FineTuningAnalysis(method=FineTuningMethod.UNKNOWN),
            "Fine-tuning analysis",
            warnings,
        )
        has_template = bool(template_text.strip() or parsed.templates)
        has_system_or_chat = bool(system_text.strip() or parsed.messages or parsed.system_blocks)
        rag = self._safe(
            lambda: self._rag.analyze(
                capabilities, architecture, has_template, has_system_or_chat
            ),
            RAGSuitability(),
            "RAG suitability analysis",
            warnings,
        )

        return ModelAnalysisResult(
            summary=summary,
            architecture=architecture,
            parsed_modelfile=parsed,
            lineage=lineage,
            fine_tuning=fine_tuning,
            rag=rag,
            capabilities=capabilities,
            modelfile=modelfile_text,
            template=template_text,
            system_prompt=system_text,
            parameters_text=parameters_text,
            license_text=license_text,
            raw_details=details,
            raw_model_info=model_info,
            raw_response=raw,
            warnings=warnings,
        )

    # -- helpers --------------------------------------------------------

    @staticmethod
    def _build_summary(model_name: str, details: dict[str, Any]) -> ModelSummary:
        families = details.get("families")
        if not isinstance(families, list):
            families = []
        families = [f for f in families if isinstance(f, str)]
        return ModelSummary(
            name=model_name,
            family=_opt_str(details.get("family")),
            families=families,
            format=_opt_str(details.get("format")),
            parameter_size=_opt_str(details.get("parameter_size")),
            quantization_level=_opt_str(details.get("quantization_level")),
        )

    def _safe(self, fn, default, label: str, warnings: list[str]):
        try:
            return fn()
        except Exception:  # noqa: BLE001 - analyzer isolation is intentional
            logger.exception("%s failed", label)
            warnings.append(f"{label} failed: showing partial results only.")
            return default


def _as_dict(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _as_str(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _as_str_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [v for v in value if isinstance(v, str)]


def _opt_str(value: Any) -> str | None:
    return str(value) if isinstance(value, str) and value != "" else None
