"""Background workers (QThreadPool + QRunnable)."""

from ollama_inspector.ui.workers.worker import CallableWorker, WorkerSignals

__all__ = ["CallableWorker", "WorkerSignals"]
