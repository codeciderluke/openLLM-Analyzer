"""Fine-tuning tab: confirmed facts, unknowns and warnings."""

from __future__ import annotations

from PySide6.QtWidgets import QVBoxLayout

from ollama_inspector.domain.analysis_result import ModelAnalysisResult
from ollama_inspector.ui.tabs.base_tab import BaseTab
from ollama_inspector.ui.widgets.common import (
    display_value,
    make_readonly_text,
    section_label,
)
from ollama_inspector.ui.widgets.info_form import InfoForm

_UNKNOWN_FIELDS = [
    "dataset",
    "epochs",
    "learning rate",
    "optimizer",
    "batch size",
    "LoRA rank",
    "LoRA alpha",
    "target modules",
    "training framework",
]


class FineTuningTab(BaseTab):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self._form = InfoForm()
        for key, label in [
            ("fine_tuned", "Fine-tuned"),
            ("method", "Method"),
            ("base", "Base model"),
            ("adapters", "Adapters"),
            ("training_meta", "Training metadata"),
        ]:
            self._form.add_row(key, label)
        layout.addWidget(self._form)

        layout.addWidget(section_label("Unknown information"))
        self._unknown = make_readonly_text()
        self._unknown.setMaximumHeight(140)
        layout.addWidget(self._unknown)

        layout.addWidget(section_label("Warnings"))
        self._warnings = make_readonly_text()
        layout.addWidget(self._warnings)

    def update_result(self, result: ModelAnalysisResult) -> None:
        ft = result.fine_tuning
        self._form.set_value("fine_tuned", _tri_state(ft.is_fine_tuned))
        self._form.set_value("method", ft.method.value)
        self._form.set_value("base", ft.base_model)
        self._form.set_value("adapters", ft.adapters)
        self._form.set_value(
            "training_meta",
            "present" if ft.training_parameters_available else "absent",
        )
        self._unknown.setPlainText(
            "\n".join(f"- {name}: Unknown" for name in _UNKNOWN_FIELDS)
        )
        self._warnings.setPlainText(
            "\n".join(f"- {w}" for w in ft.warnings) if ft.warnings else "—"
        )

    def clear(self) -> None:
        self._form.clear_values()
        self._unknown.clear()
        self._warnings.clear()


def _tri_state(value: bool | None) -> str:
    return display_value(value) if value is not None else "Unknown"
