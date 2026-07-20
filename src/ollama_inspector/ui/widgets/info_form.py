"""A simple key/value form whose values can be updated by key."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFormLayout, QLabel, QWidget

from ollama_inspector.ui.widgets.common import display_value


class InfoForm(QWidget):
    """A read-only form of labelled value rows, addressable by key."""

    def __init__(self) -> None:
        super().__init__()
        self._layout = QFormLayout(self)
        self._layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self._values: dict[str, QLabel] = {}

    def add_row(self, key: str, label: str) -> None:
        value_label = QLabel("—")
        value_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        value_label.setWordWrap(True)
        self._values[key] = value_label
        self._layout.addRow(f"{label}:", value_label)

    def set_value(self, key: str, value: object) -> None:
        label = self._values.get(key)
        if label is not None:
            label.setText(display_value(value))

    def clear_values(self) -> None:
        for label in self._values.values():
            label.setText("—")
