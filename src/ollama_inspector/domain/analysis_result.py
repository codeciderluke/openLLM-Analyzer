"""Aggregate analysis result for one model."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ollama_inspector.domain.architecture import CanonicalArchitecture
from ollama_inspector.domain.fine_tuning import FineTuningAnalysis
from ollama_inspector.domain.lineage import ModelLineage
from ollama_inspector.domain.model_summary import ModelSummary
from ollama_inspector.domain.modelfile import ParsedModelfile
from ollama_inspector.domain.rag import RAGSuitability


class ModelAnalysisResult(BaseModel):
    """Everything the app knows about a single analysed model.

    The raw API payload is preserved under ``raw_*`` so unknown fields are
    never discarded.
    """

    summary: ModelSummary
    architecture: CanonicalArchitecture
    parsed_modelfile: ParsedModelfile
    lineage: ModelLineage
    fine_tuning: FineTuningAnalysis
    rag: RAGSuitability

    capabilities: list[str] = Field(default_factory=list)

    modelfile: str = ""
    template: str = ""
    system_prompt: str = ""
    parameters_text: str = ""
    license_text: str = ""

    raw_details: dict[str, object] = Field(default_factory=dict)
    raw_model_info: dict[str, object] = Field(default_factory=dict)
    raw_response: dict[str, object] = Field(default_factory=dict)

    warnings: list[str] = Field(default_factory=list)
