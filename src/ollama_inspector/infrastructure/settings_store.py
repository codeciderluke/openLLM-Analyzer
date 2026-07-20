"""Persistence of user settings via QSettings.

Kept in the infrastructure layer so services/analyzers stay Qt-free. This
module imports Qt, therefore it must not be imported by any analyzer.
"""

from __future__ import annotations

from PySide6.QtCore import QSettings

from ollama_inspector.config.settings import (
    APPLICATION_NAME,
    DEFAULT_OLLAMA_URL,
    DEFAULT_THEME,
    ORGANIZATION_NAME,
    SETTINGS_BASE_URL,
    SETTINGS_EXPORT_DIR,
    SETTINGS_LOCAL_MODEL_DIR,
    SETTINGS_THEME,
    SETTINGS_WINDOW_GEOMETRY,
    SETTINGS_WINDOW_STATE,
)


class SettingsStore:
    """Typed wrapper over QSettings for the values the app persists."""

    def __init__(self) -> None:
        self._settings = QSettings(ORGANIZATION_NAME, APPLICATION_NAME)

    def base_url(self) -> str:
        return str(self._settings.value(SETTINGS_BASE_URL, DEFAULT_OLLAMA_URL))

    def set_base_url(self, url: str) -> None:
        self._settings.setValue(SETTINGS_BASE_URL, url)

    def export_directory(self) -> str:
        return str(self._settings.value(SETTINGS_EXPORT_DIR, ""))

    def set_export_directory(self, path: str) -> None:
        self._settings.setValue(SETTINGS_EXPORT_DIR, path)

    def theme(self) -> str:
        return str(self._settings.value(SETTINGS_THEME, DEFAULT_THEME))

    def set_theme(self, name: str) -> None:
        self._settings.setValue(SETTINGS_THEME, name)

    def local_model_directory(self) -> str:
        return str(self._settings.value(SETTINGS_LOCAL_MODEL_DIR, ""))

    def set_local_model_directory(self, path: str) -> None:
        self._settings.setValue(SETTINGS_LOCAL_MODEL_DIR, path)

    def window_geometry(self) -> object:
        return self._settings.value(SETTINGS_WINDOW_GEOMETRY)

    def set_window_geometry(self, value: object) -> None:
        self._settings.setValue(SETTINGS_WINDOW_GEOMETRY, value)

    def window_state(self) -> object:
        return self._settings.value(SETTINGS_WINDOW_STATE)

    def set_window_state(self, value: object) -> None:
        self._settings.setValue(SETTINGS_WINDOW_STATE, value)
