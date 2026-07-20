"""Enumerations used across the domain model."""

from __future__ import annotations

from enum import StrEnum


class EvidenceStatus(StrEnum):
    """Confidence level for a single analysed fact."""

    CONFIRMED = "confirmed"
    DERIVED = "derived"
    DETECTED = "detected"
    DECLARED = "declared"
    UNKNOWN = "unknown"
    CONFLICT = "conflict"


class DerivationType(StrEnum):
    """How the current model was derived from a base model."""

    OFFICIAL_BASE = "official_base"
    CUSTOM_MODELFILE = "custom_modelfile"
    LORA_ADAPTER = "lora_adapter"
    MERGED_FINETUNE = "merged_finetune"
    FULL_FINETUNE = "full_finetune"
    QUANTIZED_DERIVATIVE = "quantized_derivative"
    PROMPT_ONLY_DERIVATIVE = "prompt_only_derivative"
    UNKNOWN_DERIVATIVE = "unknown_derivative"


class FineTuningMethod(StrEnum):
    """Detected fine-tuning method."""

    NONE = "none"
    PROMPT_CUSTOMIZATION = "prompt_customization"
    LORA = "lora"
    QLORA = "qlora"
    MERGED_ADAPTER = "merged_adapter"
    FULL_FINETUNE = "full_finetune"
    UNKNOWN = "unknown"


class RAGRole(StrEnum):
    """Role a model can play inside a RAG pipeline."""

    GENERATOR = "generator"
    EMBEDDING = "embedding"
    MULTIMODAL_GENERATOR = "multimodal_generator"
    UNKNOWN = "unknown"
