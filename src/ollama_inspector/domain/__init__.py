"""Domain models and enums (framework-agnostic, no Qt imports)."""

from ollama_inspector.domain.analysis_result import ModelAnalysisResult
from ollama_inspector.domain.architecture import (
    AudioArchitecture,
    CanonicalArchitecture,
    VisionArchitecture,
)
from ollama_inspector.domain.enums import (
    DerivationType,
    EvidenceStatus,
    FineTuningMethod,
    RAGRole,
)
from ollama_inspector.domain.errors import (
    AnalysisError,
    ExportError,
    LocalModelError,
    OllamaConnectionError,
    OllamaHTTPError,
    OllamaInspectorError,
    OllamaResponseError,
)
from ollama_inspector.domain.evidence import Evidence
from ollama_inspector.domain.fine_tuning import FineTuningAnalysis
from ollama_inspector.domain.lineage import ModelLineage
from ollama_inspector.domain.model_summary import ModelSummary
from ollama_inspector.domain.modelfile import ParsedModelfile
from ollama_inspector.domain.rag import RAGSuitability

__all__ = [
    "AnalysisError",
    "AudioArchitecture",
    "CanonicalArchitecture",
    "DerivationType",
    "Evidence",
    "EvidenceStatus",
    "ExportError",
    "FineTuningAnalysis",
    "FineTuningMethod",
    "LocalModelError",
    "ModelAnalysisResult",
    "ModelLineage",
    "ModelSummary",
    "OllamaConnectionError",
    "OllamaHTTPError",
    "OllamaInspectorError",
    "OllamaResponseError",
    "ParsedModelfile",
    "RAGRole",
    "RAGSuitability",
    "VisionArchitecture",
]
