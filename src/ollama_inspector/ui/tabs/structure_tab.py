"""Structure tab: canonical architecture, raw metadata tree and evidence."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSplitter, QVBoxLayout, QWidget

from ollama_inspector.domain.analysis_result import ModelAnalysisResult
from ollama_inspector.ui.tabs.base_tab import BaseTab
from ollama_inspector.ui.widgets.common import (
    fill_evidence_tree,
    fill_metadata_tree,
    make_evidence_tree,
    make_metadata_tree,
    section_label,
)
from ollama_inspector.ui.widgets.info_form import InfoForm


class StructureTab(BaseTab):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        splitter = QSplitter(Qt.Orientation.Vertical)

        canonical = QWidget()
        canonical_layout = QVBoxLayout(canonical)
        canonical_layout.addWidget(section_label("Canonical architecture"))
        self._form = InfoForm()
        for key, label in [
            ("architecture", "Architecture"),
            ("context_length", "Context length"),
            ("embedding_length", "Embedding length"),
            ("block_count", "Block count"),
            ("feed_forward_length", "Feed-forward length"),
            ("attention_heads", "Attention heads"),
            ("kv_heads", "KV heads"),
            ("head_dimension", "Head dimension"),
            ("gqa_ratio", "GQA ratio"),
            ("vocabulary_size", "Vocabulary size"),
        ]:
            self._form.add_row(key, label)
        canonical_layout.addWidget(self._form)
        splitter.addWidget(canonical)

        metadata = QWidget()
        metadata_layout = QVBoxLayout(metadata)
        metadata_layout.addWidget(section_label("Raw metadata"))
        self._metadata_tree = make_metadata_tree()
        metadata_layout.addWidget(self._metadata_tree)
        splitter.addWidget(metadata)

        evidence = QWidget()
        evidence_layout = QVBoxLayout(evidence)
        evidence_layout.addWidget(section_label("Evidence"))
        self._evidence_tree = make_evidence_tree()
        evidence_layout.addWidget(self._evidence_tree)
        splitter.addWidget(evidence)

        layout.addWidget(splitter)

    def update_result(self, result: ModelAnalysisResult) -> None:
        arch = result.architecture
        for key in [
            "architecture",
            "context_length",
            "embedding_length",
            "block_count",
            "feed_forward_length",
            "attention_heads",
            "kv_heads",
            "head_dimension",
            "gqa_ratio",
            "vocabulary_size",
        ]:
            self._form.set_value(key, getattr(arch, key))
        fill_metadata_tree(self._metadata_tree, result.raw_model_info)
        fill_evidence_tree(self._evidence_tree, arch.evidence)

    def clear(self) -> None:
        self._form.clear_values()
        self._metadata_tree.clear()
        self._evidence_tree.clear()
