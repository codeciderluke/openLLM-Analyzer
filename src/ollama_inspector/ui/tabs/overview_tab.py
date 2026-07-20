"""Overview tab: basic info, capabilities and top-level architecture."""

from __future__ import annotations

from PySide6.QtWidgets import QVBoxLayout

from ollama_inspector.domain.analysis_result import ModelAnalysisResult
from ollama_inspector.ui.tabs.base_tab import BaseTab
from ollama_inspector.ui.widgets.info_form import InfoForm


class OverviewTab(BaseTab):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self._form = InfoForm()
        for key, label in [
            ("name", "Name"),
            ("digest", "Digest"),
            ("modified", "Modified"),
            ("size", "File size"),
            ("format", "Format"),
            ("family", "Family"),
            ("parameter_size", "Parameter size"),
            ("quantization", "Quantization"),
            ("capabilities", "Capabilities"),
            ("architecture", "Architecture"),
            ("modalities", "Modalities"),
            ("context_length", "Context length"),
            ("attention", "Attention"),
        ]:
            self._form.add_row(key, label)
        layout.addWidget(self._form)
        layout.addStretch(1)

    def update_result(self, result: ModelAnalysisResult) -> None:
        s = result.summary
        arch = result.architecture
        self._form.set_value("name", s.name)
        self._form.set_value("digest", s.digest)
        self._form.set_value("modified", s.modified_at)
        self._form.set_value("size", _format_size(s.size_bytes))
        self._form.set_value("format", s.format)
        self._form.set_value("family", s.family)
        self._form.set_value("parameter_size", s.parameter_size)
        self._form.set_value("quantization", s.quantization_level)
        self._form.set_value("capabilities", result.capabilities)
        self._form.set_value("architecture", arch.architecture)
        self._form.set_value("modalities", arch.modalities)
        self._form.set_value("context_length", arch.context_length)
        self._form.set_value("attention", _attention_summary(arch))

    def clear(self) -> None:
        self._form.clear_values()


def _format_size(size_bytes: int | None) -> object:
    if size_bytes is None:
        return None
    gib = size_bytes / (1024**3)
    if gib >= 1:
        return f"{gib:.2f} GiB ({size_bytes:,} bytes)"
    mib = size_bytes / (1024**2)
    return f"{mib:.1f} MiB ({size_bytes:,} bytes)"


def _attention_summary(arch) -> object:
    if arch.attention_heads is None and arch.kv_heads is None:
        return None
    parts = [f"heads={arch.attention_heads}"]
    if arch.kv_heads is not None:
        parts.append(f"kv={arch.kv_heads}")
    if arch.head_dimension is not None:
        parts.append(f"head_dim={arch.head_dimension}")
    if arch.gqa_ratio is not None:
        parts.append(f"gqa={arch.gqa_ratio:g}")
    return ", ".join(parts)
