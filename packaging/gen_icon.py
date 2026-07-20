"""Render the app SVG into a multi-size Windows .ico for the exe.

Uses Qt to rasterise the SVG (no Pillow dependency). Writes ``packaging/icon.ico``.
"""

from __future__ import annotations

import struct
from pathlib import Path

from PySide6.QtCore import QBuffer, QByteArray, Qt
from PySide6.QtGui import QGuiApplication, QImage, QPainter
from PySide6.QtSvg import QSvgRenderer

HERE = Path(__file__).resolve().parent
SVG_PATH = HERE.parent / "src" / "ollama_inspector" / "ui" / "resources" / "icon.svg"
ICO_PATH = HERE / "icon.ico"
SIZES = [16, 24, 32, 48, 64, 128, 256]

_APP = None


def _render_png(renderer: QSvgRenderer, size: int) -> bytes:
    image = QImage(size, size, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    renderer.render(painter)
    painter.end()

    # Keep the backing QByteArray alive for the buffer's whole lifetime.
    store = QByteArray()
    buffer = QBuffer(store)
    buffer.open(QBuffer.OpenModeFlag.WriteOnly)
    image.save(buffer, "PNG")
    buffer.close()
    return bytes(store)


def _write_ico(pngs: list[tuple[int, bytes]], path: Path) -> None:
    """Assemble a PNG-compressed .ico (Vista+ format) from rendered images."""

    count = len(pngs)
    header = struct.pack("<HHH", 0, 1, count)  # reserved, type=icon, count
    entries = b""
    offset = 6 + count * 16
    image_data = b""
    for size, png in pngs:
        dim = 0 if size >= 256 else size  # 0 means 256 in ICO
        entries += struct.pack(
            "<BBBBHHII", dim, dim, 0, 0, 1, 32, len(png), offset
        )
        image_data += png
        offset += len(png)
    path.write_bytes(header + entries + image_data)


def main() -> None:
    if not SVG_PATH.exists():
        raise SystemExit(f"SVG not found: {SVG_PATH}")
    # Hold the application in a module-level ref so it is not torn down mid-run.
    global _APP
    _APP = QGuiApplication.instance() or QGuiApplication([])
    renderer = QSvgRenderer(str(SVG_PATH))
    pngs = [(size, _render_png(renderer, size)) for size in SIZES]
    _write_ico(pngs, ICO_PATH)
    print(f"wrote {ICO_PATH} ({ICO_PATH.stat().st_size} bytes, {len(pngs)} sizes)")


if __name__ == "__main__":
    main()
