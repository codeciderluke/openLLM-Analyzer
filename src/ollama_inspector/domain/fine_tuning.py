"""Fine-tuning analysis output."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ollama_inspector.domain.enums import FineTuningMethod
from ollama_inspector.domain.evidence import Evidence


class FineTuningAnalysis(BaseModel):
    """Evidence-based fine-tuning assessment.

    Values that cannot be confirmed from artifacts (dataset, epochs, LoRA
    rank, ...) stay ``None``/``Unknown`` rather than being guessed.
    """

    is_fine_tuned: bool | None = None
    method: FineTuningMethod = FineTuningMethod.UNKNOWN
    base_model: str | None = None
    adapters: list[str] = Field(default_factory=list)
    tokenizer_modified: bool | None = None
    training_dataset: str | None = None
    training_parameters_available: bool = False
    evidence: list[Evidence] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
