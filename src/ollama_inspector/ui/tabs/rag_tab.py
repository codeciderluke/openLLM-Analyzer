"""RAG tab: role scores, reasons and mandatory limitations."""

from __future__ import annotations

from PySide6.QtWidgets import QVBoxLayout

from ollama_inspector.domain.analysis_result import ModelAnalysisResult
from ollama_inspector.ui.tabs.base_tab import BaseTab
from ollama_inspector.ui.widgets.common import make_readonly_text, section_label
from ollama_inspector.ui.widgets.info_form import InfoForm


class RagTab(BaseTab):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self._form = InfoForm()
        for key, label in [
            ("roles", "Roles"),
            ("generation", "Generation score"),
            ("embedding", "Embedding score"),
            ("long_context", "Long-context score"),
            ("multimodal", "Multimodal suitable"),
        ]:
            self._form.add_row(key, label)
        layout.addWidget(self._form)

        layout.addWidget(section_label("Reasons"))
        self._reasons = make_readonly_text()
        self._reasons.setMaximumHeight(140)
        layout.addWidget(self._reasons)

        layout.addWidget(section_label("Limitations"))
        self._limitations = make_readonly_text()
        layout.addWidget(self._limitations)

    def update_result(self, result: ModelAnalysisResult) -> None:
        rag = result.rag
        self._form.set_value("roles", [r.value for r in rag.roles])
        self._form.set_value("generation", _score(rag.generation_score))
        self._form.set_value("embedding", _score(rag.embedding_score))
        self._form.set_value("long_context", _score(rag.long_context_score))
        self._form.set_value("multimodal", rag.multimodal_rag_suitable)
        self._reasons.setPlainText(
            "\n".join(f"- {r}" for r in rag.reasons) if rag.reasons else "—"
        )
        self._limitations.setPlainText(
            "\n".join(f"- {r}" for r in rag.limitations) if rag.limitations else "—"
        )

    def clear(self) -> None:
        self._form.clear_values()
        self._reasons.clear()
        self._limitations.clear()


def _score(value: int | None) -> object:
    return value if value is not None else None
