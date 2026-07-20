"""Lineage analyzer.

Determines how the current model was derived, preferring hard evidence
(Modelfile ``FROM`` / ``ADAPTER``, API parent fields) over model-name patterns.
Name patterns are only ever used as low-confidence detection.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ollama_inspector.domain.enums import DerivationType, EvidenceStatus
from ollama_inspector.domain.evidence import Evidence
from ollama_inspector.domain.lineage import ModelLineage
from ollama_inspector.domain.modelfile import ParsedModelfile

# Generic API keys that may carry a base/parent reference across families.
_API_BASE_KEYS = ["general.base_model.0.name", "general.base_model.name", "general.basename"]


class LineageAnalyzer:
    """Produces a :class:`ModelLineage` from parsed Modelfile + API data."""

    def analyze(
        self,
        model_name: str,
        parsed: ParsedModelfile,
        details: Mapping[str, Any] | None,
        model_info: Mapping[str, Any] | None,
    ) -> ModelLineage:
        details = details or {}
        model_info = model_info or {}
        lineage = ModelLineage(current_model=model_name)

        has_prompt_customization = bool(
            parsed.system_blocks
            or parsed.templates
            or parsed.parameters
            or parsed.messages
        )
        quantization = self._quantization(details)

        # 1) Modelfile FROM
        if parsed.from_model:
            lineage.base_model = parsed.from_model
            lineage.parent_model = parsed.from_model
            lineage.evidence.append(
                Evidence(
                    field="base_model",
                    status=EvidenceStatus.CONFIRMED,
                    source="modelfile.FROM",
                    description="Modelfile FROM directive",
                    value=parsed.from_model,
                )
            )

        # 2) Modelfile ADAPTER
        if parsed.adapters:
            lineage.adapter_sources = list(parsed.adapters)
            lineage.evidence.append(
                Evidence(
                    field="adapter_sources",
                    status=EvidenceStatus.CONFIRMED,
                    source="modelfile.ADAPTER",
                    description="Modelfile ADAPTER directive",
                    value=list(parsed.adapters),
                )
            )

        # 3) API parent/base fields (fill gaps only)
        if lineage.base_model is None:
            api_base = self._api_base(model_info, details)
            if api_base is not None:
                lineage.base_model = api_base
                lineage.evidence.append(
                    Evidence(
                        field="base_model",
                        status=EvidenceStatus.DETECTED,
                        source="api",
                        description="base/parent field in API metadata",
                        value=api_base,
                        confidence=0.6,
                    )
                )

        lineage.derivation_type = self._classify(
            parsed=parsed,
            has_prompt_customization=has_prompt_customization,
            quantization=quantization,
        )
        self._add_classification_evidence(lineage, quantization, has_prompt_customization)
        return lineage

    # -- classification -------------------------------------------------

    def _classify(
        self,
        parsed: ParsedModelfile,
        has_prompt_customization: bool,
        quantization: str | None,
    ) -> DerivationType:
        if parsed.adapters:
            return DerivationType.LORA_ADAPTER
        if parsed.from_model:
            if has_prompt_customization:
                return DerivationType.PROMPT_ONLY_DERIVATIVE
            if quantization:
                return DerivationType.QUANTIZED_DERIVATIVE
            return DerivationType.CUSTOM_MODELFILE
        if not has_prompt_customization:
            return DerivationType.OFFICIAL_BASE
        return DerivationType.UNKNOWN_DERIVATIVE

    def _add_classification_evidence(
        self, lineage: ModelLineage, quantization: str | None, has_customization: bool
    ) -> None:
        dt = lineage.derivation_type
        if dt is DerivationType.QUANTIZED_DERIVATIVE and quantization:
            lineage.evidence.append(
                Evidence(
                    field="derivation_type",
                    status=EvidenceStatus.DETECTED,
                    source="details.quantization_level",
                    description="FROM + quantization, no other customization",
                    value=quantization,
                    confidence=0.7,
                )
            )
        if dt is DerivationType.UNKNOWN_DERIVATIVE:
            lineage.warnings.append("Insufficient evidence to determine model lineage.")

    # -- helpers --------------------------------------------------------

    @staticmethod
    def _quantization(details: Mapping[str, Any]) -> str | None:
        value = details.get("quantization_level")
        if isinstance(value, str) and value.strip():
            return value.strip()
        return None

    @staticmethod
    def _api_base(model_info: Mapping[str, Any], details: Mapping[str, Any]) -> str | None:
        parent = details.get("parent_model")
        if isinstance(parent, str) and parent.strip():
            return parent.strip()
        for key in _API_BASE_KEYS:
            value = model_info.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return None
