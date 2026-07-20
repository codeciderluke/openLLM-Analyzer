"""Export service: render analysis results as JSON or Markdown reports."""

from __future__ import annotations

import json
from pathlib import Path

from ollama_inspector.domain.analysis_result import ModelAnalysisResult
from ollama_inspector.domain.evidence import Evidence
from ollama_inspector.infrastructure.file_exporter import write_text_file
from ollama_inspector.utils.text import safe_filename


class ExportService:
    """Produces JSON / Markdown report text and writes it to disk."""

    # -- JSON -----------------------------------------------------------

    def to_json(self, result: ModelAnalysisResult) -> str:
        return json.dumps(result.model_dump(mode="json"), ensure_ascii=False, indent=2)

    def save_json(self, result: ModelAnalysisResult, path: Path) -> Path:
        return write_text_file(path, self.to_json(result))

    # -- Markdown -------------------------------------------------------

    def to_markdown(self, result: ModelAnalysisResult) -> str:
        s = result.summary
        arch = result.architecture
        lines: list[str] = ["# Model Inspection Report", ""]

        lines += ["## Summary", ""]
        lines += _kv("Name", s.name)
        lines += _kv("Digest", s.digest)
        lines += _kv("Modified", s.modified_at)
        lines += _kv("Size (bytes)", s.size_bytes)
        lines += _kv("Format", s.format)
        lines += _kv("Family", s.family)
        lines += _kv("Parameter size", s.parameter_size)
        lines += _kv("Quantization", s.quantization_level)
        lines.append("")

        lines += ["## Architecture", ""]
        lines += _kv("Architecture", arch.architecture)
        lines += _kv("Modalities", ", ".join(arch.modalities) or None)
        lines += _kv("Context length", arch.context_length)
        lines += _kv("Embedding length", arch.embedding_length)
        lines += _kv("Block count", arch.block_count)
        lines += _kv("Attention heads", arch.attention_heads)
        lines += _kv("KV heads", arch.kv_heads)
        lines += _kv("Head dimension", arch.head_dimension)
        lines += _kv("GQA ratio", arch.gqa_ratio)
        lines.append("")

        lines += ["## Capabilities", ""]
        lines.append(", ".join(result.capabilities) if result.capabilities else "_none_")
        lines.append("")

        lines += ["## Lineage", ""]
        lines += _kv("Current model", result.lineage.current_model)
        lines += _kv("Base model", result.lineage.base_model)
        lines += _kv("Parent model", result.lineage.parent_model)
        lines += _kv("Adapters", ", ".join(result.lineage.adapter_sources) or None)
        lines += _kv("Derivation type", result.lineage.derivation_type)
        lines.append("")

        lines += ["## Fine-tuning", ""]
        lines += _kv("Fine-tuned", _tri_state(result.fine_tuning.is_fine_tuned))
        lines += _kv("Method", result.fine_tuning.method)
        lines += _kv("Base model", result.fine_tuning.base_model)
        lines += _kv("Adapters", ", ".join(result.fine_tuning.adapters) or None)
        lines += _kv("Training dataset", result.fine_tuning.training_dataset or "Unknown")
        lines.append("")

        lines += ["## Prompt Configuration", ""]
        lines += _block("SYSTEM", result.system_prompt)
        lines += _block("TEMPLATE", result.template)
        lines += _block("PARAMETERS", result.parameters_text)
        lines += _block("LICENSE", result.license_text)
        lines.append("")

        rag = result.rag
        lines += ["## RAG Suitability", ""]
        lines += _kv("Roles", ", ".join(r.value for r in rag.roles) or None)
        lines += _kv("Generation score", rag.generation_score)
        lines += _kv("Embedding score", rag.embedding_score)
        lines += _kv("Long-context score", rag.long_context_score)
        lines += _kv("Multimodal suitable", _tri_state(rag.multimodal_rag_suitable))
        if rag.reasons:
            lines.append("")
            lines.append("Reasons:")
            lines += [f"- {r}" for r in rag.reasons]
        if rag.limitations:
            lines.append("")
            lines.append("Limitations:")
            lines += [f"- {r}" for r in rag.limitations]
        lines.append("")

        lines += ["## Warnings", ""]
        if result.warnings:
            lines += [f"- {w}" for w in result.warnings]
        else:
            lines.append("_none_")
        lines.append("")

        lines += ["## Evidence", ""]
        evidence = self._collect_evidence(result)
        if evidence:
            lines.append("| Field | Status | Source | Description |")
            lines.append("|---|---|---|---|")
            for ev in evidence:
                lines.append(
                    f"| {_esc(ev.field)} | {ev.status.value} | "
                    f"{_esc(ev.source)} | {_esc(ev.description)} |"
                )
        else:
            lines.append("_none_")
        lines.append("")

        return "\n".join(lines)

    def save_markdown(self, result: ModelAnalysisResult, path: Path) -> Path:
        return write_text_file(path, self.to_markdown(result))

    # -- filenames ------------------------------------------------------

    @staticmethod
    def default_filename(result: ModelAnalysisResult, extension: str) -> str:
        base = safe_filename(result.summary.name)
        return f"{base}.{extension.lstrip('.')}"

    # -- helpers --------------------------------------------------------

    @staticmethod
    def _collect_evidence(result: ModelAnalysisResult) -> list[Evidence]:
        collected: list[Evidence] = []
        collected.extend(result.architecture.evidence)
        collected.extend(result.lineage.evidence)
        collected.extend(result.fine_tuning.evidence)
        collected.extend(result.rag.evidence)
        return collected


def _kv(label: str, value: object) -> list[str]:
    if value is None:
        return [f"- **{label}:** Unknown"]
    return [f"- **{label}:** {value}"]


def _tri_state(value: bool | None) -> str:
    if value is None:
        return "Unknown"
    return "Yes" if value else "No"


def _block(label: str, text: str) -> list[str]:
    if not text.strip():
        return [f"- **{label}:** _none_"]
    return [f"**{label}:**", "", "```", text.strip(), "```", ""]


def _esc(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")
