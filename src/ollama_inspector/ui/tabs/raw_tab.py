"""Raw data tab: full ``/api/show`` payload and sub-sections."""

from __future__ import annotations

import json

from PySide6.QtWidgets import QTabWidget, QVBoxLayout

from ollama_inspector.domain.analysis_result import ModelAnalysisResult
from ollama_inspector.ui.tabs.base_tab import BaseTab
from ollama_inspector.ui.widgets.common import make_readonly_text


class RawTab(BaseTab):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self._inner = QTabWidget()
        self._response = make_readonly_text()
        self._model_info = make_readonly_text()
        self._details = make_readonly_text()
        self._capabilities = make_readonly_text()
        self._inner.addTab(self._response, "/api/show")
        self._inner.addTab(self._model_info, "model_info")
        self._inner.addTab(self._details, "details")
        self._inner.addTab(self._capabilities, "capabilities")
        layout.addWidget(self._inner)

    def update_result(self, result: ModelAnalysisResult) -> None:
        self._response.setPlainText(_pretty(result.raw_response))
        self._model_info.setPlainText(_pretty(result.raw_model_info))
        self._details.setPlainText(_pretty(result.raw_details))
        self._capabilities.setPlainText(_pretty(result.capabilities))

    def clear(self) -> None:
        for edit in (self._response, self._model_info, self._details, self._capabilities):
            edit.clear()


def _pretty(value: object) -> str:
    try:
        return json.dumps(value, ensure_ascii=False, indent=2)
    except (TypeError, ValueError):
        return str(value)
