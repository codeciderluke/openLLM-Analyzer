"""Lineage tab: derivation type and supporting evidence."""

from __future__ import annotations

from PySide6.QtWidgets import QVBoxLayout

from ollama_inspector.domain.analysis_result import ModelAnalysisResult
from ollama_inspector.ui.tabs.base_tab import BaseTab
from ollama_inspector.ui.widgets.common import (
    fill_evidence_tree,
    make_evidence_tree,
    section_label,
)
from ollama_inspector.ui.widgets.info_form import InfoForm


class LineageTab(BaseTab):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self._form = InfoForm()
        for key, label in [
            ("current", "Current model"),
            ("base", "Base model"),
            ("parent", "Parent model"),
            ("adapters", "Adapters"),
            ("derivation", "Derivation type"),
        ]:
            self._form.add_row(key, label)
        layout.addWidget(self._form)
        layout.addWidget(section_label("Evidence"))
        self._evidence_tree = make_evidence_tree()
        layout.addWidget(self._evidence_tree)

    def update_result(self, result: ModelAnalysisResult) -> None:
        lin = result.lineage
        self._form.set_value("current", lin.current_model)
        self._form.set_value("base", lin.base_model)
        self._form.set_value("parent", lin.parent_model)
        self._form.set_value("adapters", lin.adapter_sources)
        self._form.set_value("derivation", lin.derivation_type.value)
        fill_evidence_tree(self._evidence_tree, lin.evidence)

    def clear(self) -> None:
        self._form.clear_values()
        self._evidence_tree.clear()
