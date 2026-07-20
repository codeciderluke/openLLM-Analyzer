"""Small builders for read-only info displays shared across tabs."""

from __future__ import annotations

import json
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QPlainTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
)

from ollama_inspector.analyzers.metadata_tree_builder import TreeNode, build_metadata_tree
from ollama_inspector.domain.evidence import Evidence
from ollama_inspector.utils.text import truncate


def display_value(value: object) -> str:
    """Human-readable representation, using ``Unknown`` for missing values."""

    if value is None:
        return "Unknown"
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, list):
        return ", ".join(str(v) for v in value) if value else "—"
    return str(value)


def make_readonly_text() -> QPlainTextEdit:
    """A read-only monospace text area for raw blocks."""

    edit = QPlainTextEdit()
    edit.setReadOnly(True)
    edit.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
    edit.setPlaceholderText("—")
    return edit


def section_label(text: str) -> QLabel:
    label = QLabel(text)
    font = label.font()
    font.setBold(True)
    label.setFont(font)
    return label


def make_evidence_tree() -> QTreeWidget:
    tree = QTreeWidget()
    tree.setColumnCount(4)
    tree.setHeaderLabels(["Field", "Status", "Source", "Description"])
    tree.setRootIsDecorated(False)
    return tree


def fill_evidence_tree(tree: QTreeWidget, evidence: list[Evidence]) -> None:
    tree.clear()
    for ev in evidence:
        item = QTreeWidgetItem(
            [ev.field, ev.status.value, ev.source, truncate(ev.description, 200)]
        )
        tree.addTopLevelItem(item)
    for col in range(tree.columnCount()):
        tree.resizeColumnToContents(col)


def make_metadata_tree() -> QTreeWidget:
    tree = QTreeWidget()
    tree.setColumnCount(2)
    tree.setHeaderLabels(["Key", "Value"])
    return tree


def fill_metadata_tree(tree: QTreeWidget, metadata: dict[str, Any]) -> None:
    tree.clear()
    roots = build_metadata_tree(metadata)
    for node in roots:
        tree.addTopLevelItem(_metadata_item(node))
    tree.expandToDepth(0)
    tree.resizeColumnToContents(0)


def _metadata_item(node: TreeNode) -> QTreeWidgetItem:
    value_text = ""
    full_text = ""
    if node.has_value and node.is_leaf:
        full_text = _stringify(node.value)
        value_text = truncate(full_text, 120)
    item = QTreeWidgetItem([node.key, value_text])
    if full_text and full_text != value_text:
        # Full value available on hover / detail.
        item.setToolTip(1, full_text)
        item.setData(1, Qt.ItemDataRole.UserRole, full_text)
    for child in node.children:
        item.addChild(_metadata_item(child))
    return item


def _stringify(value: object) -> str:
    if isinstance(value, (dict, list)):
        try:
            return json.dumps(value, ensure_ascii=False)
        except (TypeError, ValueError):
            return str(value)
    return str(value)
