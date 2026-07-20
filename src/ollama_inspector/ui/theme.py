"""Application theming: dark/light palettes, QSS and the app icon.

A single design-token :class:`Palette` drives both the Qt ``QPalette`` (so
native controls match) and a shared QSS template, so dark and light stay
visually consistent. Tuned for Full HD (1920x1080) desktops.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
from pathlib import Path
from string import Template

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPalette, QPixmap
from PySide6.QtSvg import QSvgRenderer

RESOURCES_DIR = Path(__file__).parent / "resources"
ICON_PATH = RESOURCES_DIR / "icon.svg"


class ThemeName(StrEnum):
    DARK = "dark"
    LIGHT = "light"


@dataclass(frozen=True)
class Palette:
    """Design tokens for one theme."""

    bg: str
    surface: str
    surface2: str
    surface3: str
    border: str
    border_strong: str
    text: str
    muted: str
    accent: str
    accent_hover: str
    accent_pressed: str
    accent_fg: str
    selection: str
    code_bg: str
    danger: str


DARK = Palette(
    bg="#0f121a",
    surface="#161a24",
    surface2="#1c212d",
    surface3="#232936",
    border="#2a3140",
    border_strong="#39415a",
    text="#e6e9f0",
    muted="#8b94a7",
    accent="#7c9cff",
    accent_hover="#93adff",
    accent_pressed="#6a8bf0",
    accent_fg="#0f121a",
    selection="rgba(124, 156, 255, 0.18)",
    code_bg="#12151d",
    danger="#ff6b6b",
)

LIGHT = Palette(
    bg="#f3f5fb",
    surface="#ffffff",
    surface2="#eef1f8",
    surface3="#e3e8f3",
    border="#d7ddec",
    border_strong="#b7c1da",
    text="#1a2030",
    muted="#5f6b83",
    accent="#3b6fe0",
    accent_hover="#3363d3",
    accent_pressed="#2b57bf",
    accent_fg="#ffffff",
    selection="rgba(59, 111, 224, 0.15)",
    code_bg="#f6f8fc",
    danger="#d64545",
)


def palette_for(name: ThemeName) -> Palette:
    return LIGHT if name == ThemeName.LIGHT else DARK


def toggle(name: ThemeName) -> ThemeName:
    return ThemeName.LIGHT if name == ThemeName.DARK else ThemeName.DARK


_QSS = Template(
    """
* {
    font-family: "Segoe UI", "Malgun Gothic", "Apple SD Gothic Neo", sans-serif;
    font-size: 10pt;
}
QWidget { background: $bg; color: $text; }
QMainWindow, QDialog { background: $bg; }
QLabel { background: transparent; }
QLabel[role="heading"] { font-size: 11pt; font-weight: 600; }

QLineEdit {
    background: $surface2;
    border: 1px solid $border;
    border-radius: 8px;
    padding: 7px 11px;
    selection-background-color: $accent;
    selection-color: $accent_fg;
}
QLineEdit:focus { border: 1px solid $accent; }
QLineEdit::placeholder { color: $muted; }

QPushButton {
    background: $surface2;
    border: 1px solid $border;
    border-radius: 8px;
    padding: 7px 15px;
    color: $text;
}
QPushButton:hover { background: $surface3; border-color: $border_strong; }
QPushButton:pressed { background: $surface; }
QPushButton:disabled { color: $muted; background: $surface; border-color: $border; }

QPushButton#primary {
    background: $accent;
    border: 1px solid $accent;
    color: $accent_fg;
    font-weight: 600;
}
QPushButton#primary:hover { background: $accent_hover; border-color: $accent_hover; }
QPushButton#primary:pressed { background: $accent_pressed; }
QPushButton#primary:disabled { background: $border; border-color: $border; color: $muted; }

QPushButton#ghost {
    background: transparent;
    border: 1px solid $border;
    border-radius: 8px;
    padding: 7px 12px;
    min-width: 40px;
}
QPushButton#ghost:hover { background: $surface2; border-color: $border_strong; }

QListView {
    background: $surface;
    border: 1px solid $border;
    border-radius: 12px;
    padding: 6px;
    outline: none;
}
QListView::item {
    padding: 8px 10px;
    border-radius: 7px;
    margin: 1px 0;
}
QListView::item:hover { background: $surface2; }
QListView::item:selected { background: $selection; color: $text; }

QTabWidget::pane {
    border: 1px solid $border;
    border-radius: 12px;
    top: -1px;
    background: $surface;
}
QTabBar { qproperty-drawBase: 0; }
QTabBar::tab {
    background: transparent;
    color: $muted;
    padding: 9px 18px;
    margin-right: 2px;
    border: none;
    border-bottom: 2px solid transparent;
}
QTabBar::tab:hover { color: $text; }
QTabBar::tab:selected { color: $text; border-bottom: 2px solid $accent; }

QPlainTextEdit, QTextEdit {
    background: $code_bg;
    border: 1px solid $border;
    border-radius: 12px;
    padding: 10px;
    selection-background-color: $accent;
    selection-color: $accent_fg;
    font-family: "JetBrains Mono", "Cascadia Code", "Consolas", monospace;
    font-size: 10pt;
}

QTreeWidget, QTreeView {
    background: $code_bg;
    border: 1px solid $border;
    border-radius: 12px;
    alternate-background-color: $surface;
    outline: none;
}
QTreeView::item { padding: 4px 4px; }
QTreeView::item:hover { background: $surface2; }
QTreeView::item:selected { background: $selection; color: $text; }
QHeaderView::section {
    background: $surface2;
    color: $muted;
    padding: 7px 11px;
    border: none;
    border-right: 1px solid $border;
    border-bottom: 1px solid $border;
}
QHeaderView::section:last { border-right: none; }

QSplitter::handle { background: transparent; }
QSplitter::handle:horizontal { width: 8px; }
QSplitter::handle:vertical { height: 8px; }

QScrollBar:vertical { background: transparent; width: 12px; margin: 3px; }
QScrollBar::handle:vertical { background: $border; border-radius: 5px; min-height: 28px; }
QScrollBar::handle:vertical:hover { background: $border_strong; }
QScrollBar:horizontal { background: transparent; height: 12px; margin: 3px; }
QScrollBar::handle:horizontal { background: $border; border-radius: 5px; min-width: 28px; }
QScrollBar::handle:horizontal:hover { background: $border_strong; }
QScrollBar::add-line, QScrollBar::sub-line { height: 0; width: 0; }
QScrollBar::add-page, QScrollBar::sub-page { background: transparent; }

QStatusBar { background: $bg; color: $muted; border-top: 1px solid $border; }
QStatusBar::item { border: none; }

QToolTip {
    background: $surface2;
    color: $text;
    border: 1px solid $border_strong;
    border-radius: 6px;
    padding: 5px 8px;
}
"""
)


def build_stylesheet(palette: Palette) -> str:
    return _QSS.substitute(asdict(palette))


def build_qpalette(p: Palette) -> QPalette:
    """A matching QPalette so Fusion-drawn native bits align with the QSS."""

    def c(value: str) -> QColor:
        return QColor(value)

    qp = QPalette()
    qp.setColor(QPalette.ColorRole.Window, c(p.bg))
    qp.setColor(QPalette.ColorRole.WindowText, c(p.text))
    qp.setColor(QPalette.ColorRole.Base, c(p.surface2))
    qp.setColor(QPalette.ColorRole.AlternateBase, c(p.surface))
    qp.setColor(QPalette.ColorRole.Text, c(p.text))
    qp.setColor(QPalette.ColorRole.Button, c(p.surface2))
    qp.setColor(QPalette.ColorRole.ButtonText, c(p.text))
    qp.setColor(QPalette.ColorRole.ToolTipBase, c(p.surface2))
    qp.setColor(QPalette.ColorRole.ToolTipText, c(p.text))
    qp.setColor(QPalette.ColorRole.PlaceholderText, c(p.muted))
    qp.setColor(QPalette.ColorRole.Highlight, c(p.accent))
    qp.setColor(QPalette.ColorRole.HighlightedText, c(p.accent_fg))
    qp.setColor(QPalette.ColorRole.Link, c(p.accent))

    disabled = QPalette.ColorGroup.Disabled
    qp.setColor(disabled, QPalette.ColorRole.Text, c(p.muted))
    qp.setColor(disabled, QPalette.ColorRole.ButtonText, c(p.muted))
    qp.setColor(disabled, QPalette.ColorRole.WindowText, c(p.muted))
    return qp


def apply_theme(app, name: ThemeName) -> None:
    """Apply Fusion base + palette + QSS for the given theme, app-wide."""

    app.setStyle("Fusion")
    palette = palette_for(name)
    app.setPalette(build_qpalette(palette))
    app.setStyleSheet(build_stylesheet(palette))


def build_app_icon() -> QIcon:
    """Render the SVG app icon into a multi-size :class:`QIcon`."""

    icon = QIcon()
    if not ICON_PATH.exists():
        return icon
    renderer = QSvgRenderer(str(ICON_PATH))
    for size in (16, 20, 24, 32, 48, 64, 128, 256):
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        icon.addPixmap(pixmap)
    return icon
