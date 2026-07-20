"""Generic callable worker for QThreadPool.

All network / analysis work runs here, never on the UI thread. Every signal
carries the originating request ID so the UI can discard stale results.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from PySide6.QtCore import QObject, QRunnable, Signal, Slot

from ollama_inspector.domain.errors import OllamaInspectorError
from ollama_inspector.utils.logging_config import get_logger

logger = get_logger("worker")


class WorkerSignals(QObject):
    """Signals emitted by :class:`CallableWorker`.

    The leading ``str`` argument is always the request ID.
    """

    started = Signal(str)
    progress = Signal(str, str)
    result = Signal(str, object)
    error = Signal(str, str)
    finished = Signal(str)


class CallableWorker(QRunnable):
    """Runs ``fn()`` on a pool thread and reports the outcome via signals."""

    def __init__(self, request_id: str, fn: Callable[[], Any]) -> None:
        super().__init__()
        self.request_id = request_id
        self._fn = fn
        self.signals = WorkerSignals()

    @Slot()
    def run(self) -> None:
        self.signals.started.emit(self.request_id)
        try:
            value = self._fn()
        except OllamaInspectorError as exc:
            logger.info("Task failed (%s): %s", self.request_id, exc)
            self.signals.error.emit(self.request_id, str(exc))
        except Exception as exc:  # noqa: BLE001 - report, don't crash the pool
            logger.exception("Unexpected error during task (%s)", self.request_id)
            self.signals.error.emit(self.request_id, f"Unexpected error: {exc}")
        else:
            self.signals.result.emit(self.request_id, value)
        finally:
            self.signals.finished.emit(self.request_id)
