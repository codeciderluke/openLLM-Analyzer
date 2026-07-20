"""Main application window.

Wires the connection bar, model list and detail tabs. All HTTP/analysis work
runs on a QThreadPool; request IDs guard against stale results overwriting a
newer selection.
"""

from __future__ import annotations

import itertools
from pathlib import Path

from PySide6.QtCore import (
    QModelIndex,
    QSortFilterProxyModel,
    Qt,
    QThreadPool,
)
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListView,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ollama_inspector.domain.analysis_result import ModelAnalysisResult
from ollama_inspector.domain.model_summary import ModelSummary
from ollama_inspector.infrastructure.ollama_client import OllamaClient
from ollama_inspector.infrastructure.settings_store import SettingsStore
from ollama_inspector.services.export_service import ExportService
from ollama_inspector.services.local_model_service import LocalModelService
from ollama_inspector.services.model_analysis_service import ModelAnalysisService
from ollama_inspector.services.model_catalog_service import ModelCatalogService
from ollama_inspector.ui.models.model_list_model import ModelListModel
from ollama_inspector.ui.tabs import (
    FineTuningTab,
    LineageTab,
    OverviewTab,
    PromptTab,
    RagTab,
    RawTab,
    StructureTab,
)
from ollama_inspector.ui.theme import ThemeName, apply_theme, build_app_icon, toggle
from ollama_inspector.ui.workers.worker import CallableWorker
from ollama_inspector.utils.logging_config import get_logger
from ollama_inspector.utils.text import normalize_base_url

logger = get_logger("main_window")


class MainWindow(QMainWindow):
    def __init__(self, settings: SettingsStore | None = None) -> None:
        super().__init__()
        self.setWindowTitle("Ollama Model & RAG Inspector")
        self.setWindowIcon(build_app_icon())
        # Full HD friendly default: comfortably fits 1920x1080 with margins.
        self.resize(1480, 940)
        self.setMinimumSize(1100, 700)

        self._settings = settings or SettingsStore()
        self._pool = QThreadPool.globalInstance()
        self._export = ExportService()
        self._client: OllamaClient | None = None
        self._current_result: ModelAnalysisResult | None = None
        self._theme = _resolve_theme_name(self._settings.theme())

        self._request_ids = itertools.count(1)
        self._current_analysis_request_id: str | None = None
        self._current_catalog_request_id: str | None = None

        self._build_ui()
        self._restore_settings()

    # -- construction ---------------------------------------------------

    def _build_ui(self) -> None:
        central = QWidget()
        root = QVBoxLayout(central)
        root.addLayout(self._build_connection_bar())

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self._build_left_panel())
        splitter.addWidget(self._build_right_panel())
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([360, 1120])
        root.addWidget(splitter)

        self.setCentralWidget(central)
        self.statusBar().showMessage("Ready")

    def _build_connection_bar(self) -> QHBoxLayout:
        bar = QHBoxLayout()
        bar.addWidget(QLabel("Ollama URL"))
        self._url_edit = QLineEdit()
        self._url_edit.setPlaceholderText("http://localhost:11434")
        self._url_edit.returnPressed.connect(self._on_connect)
        bar.addWidget(self._url_edit, 1)

        self._connect_btn = QPushButton("Connect")
        self._connect_btn.setObjectName("primary")
        self._connect_btn.clicked.connect(self._on_connect)
        bar.addWidget(self._connect_btn)

        self._refresh_btn = QPushButton("Refresh")
        self._refresh_btn.clicked.connect(self._on_connect)
        bar.addWidget(self._refresh_btn)

        self._save_url_btn = QPushButton("Save URL")
        self._save_url_btn.clicked.connect(self._on_save_url)
        bar.addWidget(self._save_url_btn)

        bar.addWidget(_separator())

        self._open_local_btn = QPushButton("Load File")
        self._open_local_btn.setToolTip("Open and analyze an external GGUF file or Modelfile.")
        self._open_local_btn.clicked.connect(self._on_open_local)
        bar.addWidget(self._open_local_btn)

        self._export_json_btn = QPushButton("Save JSON")
        self._export_json_btn.clicked.connect(self._on_export_json)
        self._export_json_btn.setEnabled(False)
        bar.addWidget(self._export_json_btn)

        self._export_md_btn = QPushButton("Save MD")
        self._export_md_btn.clicked.connect(self._on_export_markdown)
        self._export_md_btn.setEnabled(False)
        bar.addWidget(self._export_md_btn)

        bar.addStretch(0)

        self._theme_btn = QPushButton()
        self._theme_btn.setObjectName("ghost")
        self._theme_btn.setToolTip("Toggle dark/light theme")
        self._theme_btn.clicked.connect(self._on_toggle_theme)
        self._update_theme_button()
        bar.addWidget(self._theme_btn)
        return bar

    def _build_left_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        self._search_edit = QLineEdit()
        self._search_edit.setPlaceholderText("Search models…")
        self._search_edit.setClearButtonEnabled(True)
        layout.addWidget(self._search_edit)

        self._list_model = ModelListModel()
        self._proxy = QSortFilterProxyModel()
        self._proxy.setSourceModel(self._list_model)
        self._proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._proxy.setFilterRole(Qt.ItemDataRole.DisplayRole)
        self._search_edit.textChanged.connect(self._proxy.setFilterFixedString)

        self._list_view = QListView()
        self._list_view.setModel(self._proxy)
        self._list_view.setEditTriggers(QListView.EditTrigger.NoEditTriggers)
        self._list_view.selectionModel().currentChanged.connect(self._on_model_selected)
        layout.addWidget(self._list_view, 1)
        return panel

    def _build_right_panel(self) -> QWidget:
        self._tabs = QTabWidget()
        self._overview = OverviewTab()
        self._structure = StructureTab()
        self._lineage = LineageTab()
        self._fine_tuning = FineTuningTab()
        self._prompt = PromptTab()
        self._rag = RagTab()
        self._raw = RawTab()
        self._all_tabs = [
            self._overview,
            self._structure,
            self._lineage,
            self._fine_tuning,
            self._prompt,
            self._rag,
            self._raw,
        ]
        self._tabs.addTab(self._overview, "Overview")
        self._tabs.addTab(self._structure, "Structure")
        self._tabs.addTab(self._lineage, "Lineage")
        self._tabs.addTab(self._fine_tuning, "Fine-tuning")
        self._tabs.addTab(self._prompt, "Prompt")
        self._tabs.addTab(self._rag, "RAG")
        self._tabs.addTab(self._raw, "Raw Data")
        return self._tabs

    # -- settings -------------------------------------------------------

    def _restore_settings(self) -> None:
        self._url_edit.setText(self._settings.base_url())
        geometry = self._settings.window_geometry()
        if geometry is not None:
            self.restoreGeometry(geometry)

    # -- connection / catalog ------------------------------------------

    def _on_connect(self) -> None:
        try:
            url = normalize_base_url(self._url_edit.text())
        except ValueError as exc:
            self._show_error("URL Error", str(exc))
            return
        self._url_edit.setText(url)
        self._settings.set_base_url(url)

        self._close_client()
        try:
            self._client = OllamaClient(url)
        except ValueError as exc:
            self._show_error("Connection Error", str(exc))
            return

        request_id = self._next_id()
        self._current_catalog_request_id = request_id
        client = self._client
        self._set_busy("Connecting…")
        worker = CallableWorker(request_id, lambda: ModelCatalogService(client).load_models())
        worker.signals.result.connect(self._on_catalog_result)
        worker.signals.error.connect(self._on_catalog_error)
        worker.signals.finished.connect(self._on_worker_finished)
        self._pool.start(worker)

    def _on_catalog_result(self, request_id: str, models: object) -> None:
        if request_id != self._current_catalog_request_id:
            return
        assert isinstance(models, list)
        self._list_model.set_models(models)
        self.statusBar().showMessage(f"Loaded {len(models)} models")

    def _on_catalog_error(self, request_id: str, message: str) -> None:
        if request_id != self._current_catalog_request_id:
            return
        self._show_error("Connection Failed", message)
        self.statusBar().showMessage("Connection failed")

    # -- analysis -------------------------------------------------------

    def _on_model_selected(self, current: QModelIndex, _previous: QModelIndex) -> None:
        if not current.isValid() or self._client is None:
            return
        source_index = self._proxy.mapToSource(current)
        summary: ModelSummary | None = self._list_model.summary_at(source_index.row())
        if summary is None:
            return

        request_id = self._next_id()
        self._current_analysis_request_id = request_id
        client = self._client
        name = summary.name
        self._set_busy(f"Analyzing: {name}")
        worker = CallableWorker(
            request_id, lambda: ModelAnalysisService(client).analyze_model(name)
        )
        worker.signals.result.connect(self._on_analysis_result)
        worker.signals.error.connect(self._on_analysis_error)
        worker.signals.finished.connect(self._on_worker_finished)
        self._pool.start(worker)

    def _on_analysis_result(self, request_id: str, result: object) -> None:
        # Discard stale results from a previously selected model.
        if request_id != self._current_analysis_request_id:
            return
        assert isinstance(result, ModelAnalysisResult)
        self._current_result = result
        for tab in self._all_tabs:
            tab.update_result(result)
        self._export_json_btn.setEnabled(True)
        self._export_md_btn.setEnabled(True)
        message = f"Analysis complete: {result.summary.name}"
        if result.warnings:
            message += f" ({len(result.warnings)} warnings)"
        self.statusBar().showMessage(message)

    def _on_analysis_error(self, request_id: str, message: str) -> None:
        if request_id != self._current_analysis_request_id:
            return
        self._show_error("Analysis Failed", message)
        self.statusBar().showMessage("Analysis failed — you can select another model.")

    # -- export ---------------------------------------------------------

    def _on_export_json(self) -> None:
        self._export_report("json")

    def _on_export_markdown(self) -> None:
        self._export_report("md")

    def _export_report(self, extension: str) -> None:
        if self._current_result is None:
            return
        default_dir = self._settings.export_directory() or str(Path.home())
        default_name = self._export.default_filename(self._current_result, extension)
        caption = "Save Report"
        filter_str = "JSON (*.json)" if extension == "json" else "Markdown (*.md)"
        path_str, _ = QFileDialog.getSaveFileName(
            self, caption, str(Path(default_dir) / default_name), filter_str
        )
        if not path_str:
            return
        path = Path(path_str)
        try:
            if extension == "json":
                self._export.save_json(self._current_result, path)
            else:
                self._export.save_markdown(self._current_result, path)
        except Exception as exc:  # noqa: BLE001 - surfaced to user
            self._show_error("Save Failed", str(exc))
            return
        self._settings.set_export_directory(str(path.parent))
        self.statusBar().showMessage(f"Saved: {path}")

    # -- external / local model ----------------------------------------

    def _on_open_local(self) -> None:
        start_dir = self._settings.local_model_directory() or str(Path.home())
        path_str, _ = QFileDialog.getOpenFileName(
            self,
            "Open External Model File",
            start_dir,
            "Model files (*.gguf Modelfile *.modelfile *.txt);;GGUF (*.gguf);;All files (*.*)",
        )
        if not path_str:
            return
        path = Path(path_str)
        self._settings.set_local_model_directory(str(path.parent))

        request_id = self._next_id()
        # Reuse the analysis request-ID slot so a later model selection (or
        # another file) supersedes this one via the same stale-result guard.
        self._current_analysis_request_id = request_id
        self._list_view.clearSelection()
        self._set_busy(f"Analyzing: {path.name}")
        worker = CallableWorker(
            request_id, lambda: LocalModelService().analyze_path(path)
        )
        worker.signals.result.connect(self._on_analysis_result)
        worker.signals.error.connect(self._on_analysis_error)
        worker.signals.finished.connect(self._on_worker_finished)
        self._pool.start(worker)

    # -- theme ----------------------------------------------------------

    def _on_toggle_theme(self) -> None:
        self._theme = toggle(self._theme)
        self._settings.set_theme(self._theme.value)
        app = QApplication.instance()
        if app is not None:
            apply_theme(app, self._theme)
        self._update_theme_button()
        self.statusBar().showMessage(
            "Light theme" if self._theme == ThemeName.LIGHT else "Dark theme"
        )

    def _update_theme_button(self) -> None:
        # Plain-text labels avoid missing-emoji glyphs across fonts. The label
        # names the theme the button switches *to*.
        if self._theme == ThemeName.LIGHT:
            self._theme_btn.setText("Dark Mode")
        else:
            self._theme_btn.setText("Light Mode")

    def _on_save_url(self) -> None:
        try:
            url = normalize_base_url(self._url_edit.text())
        except ValueError as exc:
            self._show_error("URL Error", str(exc))
            return
        self._settings.set_base_url(url)
        self.statusBar().showMessage("URL saved")

    # -- helpers --------------------------------------------------------

    def _next_id(self) -> str:
        return str(next(self._request_ids))

    def _set_busy(self, message: str) -> None:
        self.statusBar().showMessage(message)

    def _on_worker_finished(self, _request_id: str) -> None:
        pass

    def _show_error(self, title: str, message: str) -> None:
        # Stack traces are never shown to the user; only friendly messages.
        QMessageBox.critical(self, title, message)

    def _close_client(self) -> None:
        if self._client is not None:
            try:
                self._client.close()
            except Exception:  # noqa: BLE001
                logger.debug("Ignoring error while closing client")
            self._client = None

    def closeEvent(self, event) -> None:  # noqa: N802
        self._settings.set_window_geometry(self.saveGeometry())
        self._close_client()
        super().closeEvent(event)


def _separator() -> QFrame:
    line = QFrame()
    line.setFrameShape(QFrame.Shape.VLine)
    line.setFixedWidth(1)
    return line


def _resolve_theme_name(value: str) -> ThemeName:
    return ThemeName(value) if value in tuple(ThemeName) else ThemeName.DARK
