"""Exception hierarchy for the application."""

from __future__ import annotations


class OllamaInspectorError(Exception):
    """Base class for all application errors."""


class OllamaConnectionError(OllamaInspectorError):
    """Raised when the Ollama server cannot be reached."""


class OllamaHTTPError(OllamaInspectorError):
    """Raised when the Ollama server returns an HTTP error status."""


class OllamaResponseError(OllamaInspectorError):
    """Raised when a response cannot be decoded or has an unexpected shape."""


class AnalysisError(OllamaInspectorError):
    """Raised when an analyzer fails irrecoverably."""


class LocalModelError(OllamaInspectorError):
    """Raised when a local/external model file cannot be read or parsed."""


class ExportError(OllamaInspectorError):
    """Raised when a report cannot be written."""
