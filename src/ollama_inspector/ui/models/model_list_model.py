"""List model exposing the model catalog to a QListView."""

from __future__ import annotations

from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt

from ollama_inspector.domain.model_summary import ModelSummary

SUMMARY_ROLE = int(Qt.ItemDataRole.UserRole) + 1


class ModelListModel(QAbstractListModel):
    """Holds :class:`ModelSummary` rows for display and selection."""

    def __init__(self) -> None:
        super().__init__()
        self._items: list[ModelSummary] = []

    def set_models(self, models: list[ModelSummary]) -> None:
        self.beginResetModel()
        self._items = list(models)
        self.endResetModel()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802
        if parent.isValid():
            return 0
        return len(self._items)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):  # noqa: N802
        if not index.isValid() or not (0 <= index.row() < len(self._items)):
            return None
        item = self._items[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            return item.name
        if role == Qt.ItemDataRole.ToolTipRole:
            return self._tooltip(item)
        if role == SUMMARY_ROLE:
            return item
        return None

    def summary_at(self, row: int) -> ModelSummary | None:
        if 0 <= row < len(self._items):
            return self._items[row]
        return None

    @staticmethod
    def _tooltip(item: ModelSummary) -> str:
        parts = [item.name]
        if item.parameter_size:
            parts.append(f"params: {item.parameter_size}")
        if item.quantization_level:
            parts.append(f"quant: {item.quantization_level}")
        if item.family:
            parts.append(f"family: {item.family}")
        return "\n".join(parts)
