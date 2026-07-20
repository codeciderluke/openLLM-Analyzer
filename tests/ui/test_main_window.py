"""Step 15: UI tests (pytest-qt). Run headless via the offscreen platform."""

from __future__ import annotations

import httpx
import pytest

from ollama_inspector.domain.model_summary import ModelSummary
from ollama_inspector.infrastructure.ollama_client import OllamaClient
from ollama_inspector.services.model_analysis_service import ModelAnalysisService
from ollama_inspector.ui.main_window import MainWindow

pytest.importorskip("pytestqt")


class _StubSettings:
    """In-memory settings so tests never touch the real QSettings store."""

    def __init__(self) -> None:
        self._url = "http://localhost:11434"
        self._theme = "dark"

    def base_url(self) -> str:
        return self._url

    def set_base_url(self, url: str) -> None:
        self._url = url

    def export_directory(self) -> str:
        return ""

    def set_export_directory(self, path: str) -> None:  # pragma: no cover - noop
        pass

    def theme(self) -> str:
        return self._theme

    def set_theme(self, name: str) -> None:
        self._theme = name

    def local_model_directory(self) -> str:
        return ""

    def set_local_model_directory(self, path: str) -> None:  # pragma: no cover - noop
        pass

    def window_geometry(self):
        return None

    def set_window_geometry(self, value) -> None:  # pragma: no cover - noop
        pass

    def window_state(self):
        return None

    def set_window_state(self, value) -> None:  # pragma: no cover - noop
        pass


@pytest.fixture
def window(qtbot):
    win = MainWindow(settings=_StubSettings())
    qtbot.addWidget(win)
    return win


def _analysis(show_payload) -> object:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=show_payload)

    client = OllamaClient("http://localhost:11434", transport=httpx.MockTransport(handler))
    return ModelAnalysisService(client).analyze_model("llama3.1:8b")


def test_initial_state(window: MainWindow) -> None:
    assert window._url_edit.text() == "http://localhost:11434"
    assert window._list_model.rowCount() == 0
    assert not window._export_json_btn.isEnabled()


def test_populate_model_list(window: MainWindow) -> None:
    window._current_catalog_request_id = "42"
    models = [ModelSummary(name="b:latest"), ModelSummary(name="a:latest")]
    window._on_catalog_result("42", models)
    assert window._list_model.rowCount() == 2


def test_stale_catalog_result_ignored(window: MainWindow) -> None:
    window._current_catalog_request_id = "current"
    window._on_catalog_result("stale", [ModelSummary(name="x:latest")])
    assert window._list_model.rowCount() == 0


def test_search_filter(window: MainWindow, qtbot) -> None:
    window._current_catalog_request_id = "1"
    window._on_catalog_result(
        "1", [ModelSummary(name="llama:8b"), ModelSummary(name="qwen:7b")]
    )
    window._search_edit.setText("llama")
    assert window._proxy.rowCount() == 1


def test_analysis_result_updates_tabs(window: MainWindow, show_llama) -> None:
    result = _analysis(show_llama)
    window._current_analysis_request_id = "7"
    window._on_analysis_result("7", result)
    assert window._current_result is result
    assert window._export_json_btn.isEnabled()
    assert window._export_md_btn.isEnabled()


def test_stale_analysis_result_ignored(window: MainWindow, show_llama) -> None:
    result = _analysis(show_llama)
    window._current_analysis_request_id = "current"
    window._on_analysis_result("old", result)
    assert window._current_result is None
    assert not window._export_json_btn.isEnabled()
