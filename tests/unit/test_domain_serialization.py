"""Step 2: domain model serialization round-trips."""

from __future__ import annotations

from ollama_inspector.domain.analysis_result import ModelAnalysisResult
from ollama_inspector.domain.architecture import CanonicalArchitecture
from ollama_inspector.domain.enums import EvidenceStatus, RAGRole
from ollama_inspector.domain.evidence import Evidence
from ollama_inspector.domain.fine_tuning import FineTuningAnalysis
from ollama_inspector.domain.lineage import ModelLineage
from ollama_inspector.domain.model_summary import ModelSummary
from ollama_inspector.domain.modelfile import ParsedModelfile
from ollama_inspector.domain.rag import RAGSuitability


def _minimal_result() -> ModelAnalysisResult:
    return ModelAnalysisResult(
        summary=ModelSummary(name="test:latest"),
        architecture=CanonicalArchitecture(architecture="llama"),
        parsed_modelfile=ParsedModelfile(from_model="base:latest"),
        lineage=ModelLineage(current_model="test:latest"),
        fine_tuning=FineTuningAnalysis(),
        rag=RAGSuitability(roles=[RAGRole.GENERATOR]),
    )


def test_evidence_confidence_bounds() -> None:
    ev = Evidence(
        field="x", status=EvidenceStatus.CONFIRMED, source="s", description="d"
    )
    assert ev.confidence == 1.0


def test_result_json_round_trip() -> None:
    result = _minimal_result()
    dumped = result.model_dump(mode="json")
    restored = ModelAnalysisResult.model_validate(dumped)
    assert restored.summary.name == "test:latest"
    assert restored.architecture.architecture == "llama"
    assert restored.rag.roles == [RAGRole.GENERATOR]


def test_enum_serialized_as_value() -> None:
    result = _minimal_result()
    dumped = result.model_dump(mode="json")
    assert dumped["rag"]["roles"] == ["generator"]
    assert dumped["lineage"]["derivation_type"] == "unknown_derivative"
