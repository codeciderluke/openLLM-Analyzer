"""Base class for detail tabs."""

from __future__ import annotations

from abc import abstractmethod

from PySide6.QtWidgets import QWidget

from ollama_inspector.domain.analysis_result import ModelAnalysisResult


class BaseTab(QWidget):
    """A detail tab that renders part of a :class:`ModelAnalysisResult`.

    Tabs only *render* pre-computed analysis; they never analyse metadata
    themselves (that belongs to the analyzers/services).
    """

    @abstractmethod
    def update_result(self, result: ModelAnalysisResult) -> None:
        """Render the given analysis result."""

    @abstractmethod
    def clear(self) -> None:
        """Reset the tab to an empty state."""
