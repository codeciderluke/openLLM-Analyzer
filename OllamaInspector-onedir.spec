# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec: Ollama Model & RAG Inspector (onedir, windowed).

Onedir keeps the Qt shared libraries as separate files under _internal/, which
is the LGPL-3.0-friendly layout (the user can replace/relink Qt). Preferred for
distributing binaries. See THIRD_PARTY_LICENSES.md.
"""

from PyInstaller.utils.hooks import collect_submodules

datas = [
    ("src/ollama_inspector/ui/resources/icon.svg", "ollama_inspector/ui/resources"),
]

hiddenimports = collect_submodules("ollama_inspector")

a = Analysis(
    ["src/ollama_inspector/main.py"],
    pathex=["src"],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter",
        "pytest",
        "pytest_qt",
        "mypy",
        "ruff",
        "coverage",
        "PySide6.QtWebEngineCore",
        "PySide6.QtWebEngineWidgets",
        "PySide6.Qt3DCore",
        "PySide6.QtMultimedia",
        "PySide6.QtQuick",
        "PySide6.QtQml",
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="OllamaInspector",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="packaging/icon.ico",
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="OllamaInspector",
)
