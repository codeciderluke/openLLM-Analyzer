"""Fine-tuning analyzer.

Reports only what artifacts prove. Training details (dataset, epochs, LoRA
rank/alpha, optimizer, ...) are left Unknown unless explicitly present, and
merged/full fine-tunes are never assumed without evidence.
"""

from __future__ import annotations

from ollama_inspector.domain.enums import EvidenceStatus, FineTuningMethod
from ollama_inspector.domain.evidence import Evidence
from ollama_inspector.domain.fine_tuning import FineTuningAnalysis
from ollama_inspector.domain.modelfile import ParsedModelfile


class FineTuningAnalyzer:
    """Produces a :class:`FineTuningAnalysis` from parsed Modelfile data."""

    def analyze(self, parsed: ParsedModelfile) -> FineTuningAnalysis:
        analysis = FineTuningAnalysis(
            base_model=parsed.from_model,
            adapters=list(parsed.adapters),
        )

        if parsed.adapters:
            self._as_lora(analysis, parsed)
        elif parsed.from_model and self._has_prompt_customization(parsed):
            self._as_prompt_customization(analysis)
        else:
            self._as_unknown(analysis)

        return analysis

    # -- branches -------------------------------------------------------

    def _as_lora(self, analysis: FineTuningAnalysis, parsed: ParsedModelfile) -> None:
        analysis.is_fine_tuned = True
        analysis.method = FineTuningMethod.LORA
        analysis.evidence.append(
            Evidence(
                field="method",
                status=EvidenceStatus.CONFIRMED,
                source="modelfile.ADAPTER",
                description="LoRA adapter confirmed via ADAPTER directive",
                value=list(parsed.adapters),
            )
        )
        # QLoRA cannot be confirmed without extra metadata.
        analysis.warnings.append(
            "QLoRA cannot be confirmed without additional metadata."
        )

    def _as_prompt_customization(self, analysis: FineTuningAnalysis) -> None:
        analysis.is_fine_tuned = False
        analysis.method = FineTuningMethod.PROMPT_CUSTOMIZATION
        analysis.evidence.append(
            Evidence(
                field="method",
                status=EvidenceStatus.DETECTED,
                source="modelfile",
                description="FROM + SYSTEM/TEMPLATE/PARAMETER (prompt customization)",
                confidence=0.8,
            )
        )
        analysis.warnings.append(
            "Prompt changes differ from training-based fine-tuning."
        )

    def _as_unknown(self, analysis: FineTuningAnalysis) -> None:
        analysis.is_fine_tuned = None
        analysis.method = FineTuningMethod.UNKNOWN
        analysis.evidence.append(
            Evidence(
                field="method",
                status=EvidenceStatus.UNKNOWN,
                source="modelfile",
                description="No fine-tuning evidence found.",
            )
        )
        analysis.warnings.append(
            "Cannot determine whether this is a merged adapter or full fine-tune."
        )

    # -- helpers --------------------------------------------------------

    @staticmethod
    def _has_prompt_customization(parsed: ParsedModelfile) -> bool:
        return bool(
            parsed.system_blocks
            or parsed.templates
            or parsed.parameters
            or parsed.messages
        )
