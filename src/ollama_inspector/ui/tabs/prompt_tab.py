"""Prompt tab: Modelfile, SYSTEM, TEMPLATE, PARAMETERS, LICENSE."""

from __future__ import annotations

from PySide6.QtWidgets import QTabWidget, QVBoxLayout

from ollama_inspector.domain.analysis_result import ModelAnalysisResult
from ollama_inspector.ui.tabs.base_tab import BaseTab
from ollama_inspector.ui.widgets.common import make_readonly_text


class PromptTab(BaseTab):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self._inner = QTabWidget()
        self._modelfile = make_readonly_text()
        self._system = make_readonly_text()
        self._template = make_readonly_text()
        self._parameters = make_readonly_text()
        self._license = make_readonly_text()
        self._inner.addTab(self._modelfile, "Modelfile")
        self._inner.addTab(self._system, "SYSTEM")
        self._inner.addTab(self._template, "TEMPLATE")
        self._inner.addTab(self._parameters, "PARAMETERS")
        self._inner.addTab(self._license, "LICENSE")
        layout.addWidget(self._inner)

    def update_result(self, result: ModelAnalysisResult) -> None:
        self._modelfile.setPlainText(result.modelfile or "—")
        self._system.setPlainText(result.system_prompt or "—")
        self._template.setPlainText(result.template or "—")
        self._parameters.setPlainText(result.parameters_text or "—")
        self._license.setPlainText(result.license_text or "—")

    def clear(self) -> None:
        for edit in (
            self._modelfile,
            self._system,
            self._template,
            self._parameters,
            self._license,
        ):
            edit.clear()
