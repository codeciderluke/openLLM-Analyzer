"""Static application configuration and defaults."""

from __future__ import annotations

from dataclasses import dataclass

DEFAULT_OLLAMA_URL = "http://localhost:11434"
DEFAULT_TIMEOUT_SECONDS = 15.0

ORGANIZATION_NAME = "OllamaInspector"
APPLICATION_NAME = "OllamaModelInspector"

# QSettings keys
SETTINGS_BASE_URL = "ollama/base_url"
SETTINGS_WINDOW_GEOMETRY = "window/geometry"
SETTINGS_WINDOW_STATE = "window/state"
SETTINGS_EXPORT_DIR = "export/last_directory"
SETTINGS_THEME = "ui/theme"
SETTINGS_LOCAL_MODEL_DIR = "local/last_directory"

DEFAULT_THEME = "dark"


@dataclass(frozen=True)
class AppConfig:
    """Immutable runtime configuration values."""

    base_url: str = DEFAULT_OLLAMA_URL
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS
