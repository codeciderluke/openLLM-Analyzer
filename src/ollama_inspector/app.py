"""Application bootstrap: build the QApplication and main window."""

from __future__ import annotations

import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication

from ollama_inspector.config.settings import APPLICATION_NAME, ORGANIZATION_NAME
from ollama_inspector.infrastructure.settings_store import SettingsStore
from ollama_inspector.ui.main_window import MainWindow
from ollama_inspector.ui.theme import ThemeName, apply_theme, build_app_icon
from ollama_inspector.utils.logging_config import configure_logging


def _resolve_theme(settings: SettingsStore) -> ThemeName:
    value = settings.theme()
    return ThemeName(value) if value in tuple(ThemeName) else ThemeName.DARK


def run() -> int:
    """Create the Qt application, show the window and enter the event loop."""

    configure_logging()

    # Must be set before the QApplication is constructed. PassThrough keeps
    # fractional Full HD / high-DPI scale factors crisp instead of rounding.
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication.instance() or QApplication(sys.argv)
    app.setOrganizationName(ORGANIZATION_NAME)
    app.setApplicationName(APPLICATION_NAME)

    settings = SettingsStore()
    apply_theme(app, _resolve_theme(settings))
    app.setWindowIcon(build_app_icon())

    window = MainWindow(settings=settings)
    window.show()
    return app.exec()
