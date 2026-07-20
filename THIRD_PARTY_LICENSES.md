# Third-Party Licenses

This project (**Ollama Model & RAG Inspector**) is released under the MIT
License (see [LICENSE](LICENSE)). That license covers **this project's own
source code only**. The project depends on third-party components distributed
under their own licenses, summarized below.

## Runtime dependencies (shipped with the app / bundled in the .exe)

| Component | License | Notes |
|---|---|---|
| **PySide6 / Qt for Python** | **LGPL-3.0** | Also available under commercial and GPL licenses from The Qt Company. See the important note below. |
| shiboken6 | LGPL-3.0 | PySide6 binding runtime. |
| httpx | BSD-3-Clause | HTTP client. |
| httpcore | BSD-3-Clause | httpx transport. |
| h11 | MIT | HTTP/1.1 state machine. |
| anyio | MIT | Async compatibility layer (transitive). |
| sniffio | MIT / Apache-2.0 | Transitive. |
| idna | BSD-3-Clause | Transitive. |
| certifi | MPL-2.0 | CA bundle. |
| pydantic | MIT | Data models. |
| pydantic-core | MIT | pydantic core. |
| annotated-types | MIT | Transitive. |
| typing-extensions | PSF-2.0 | Transitive. |

## Build / development-only tools (NOT distributed with the app)

| Tool | License |
|---|---|
| PyInstaller | GPL-2.0 **with a bootloader exception** that explicitly permits building and distributing applications of any license, including proprietary. |
| pytest, pytest-qt, ruff, mypy | MIT |
| coverage | Apache-2.0 |

## Important: PySide6 / Qt (LGPL-3.0) and the bundled executable

The prebuilt `.exe` produced by `build_exe.bat` bundles the Qt shared libraries
via PyInstaller. Qt (through PySide6) is used here under the **LGPL-3.0**.
When you **distribute** that executable, LGPL-3.0 imposes obligations,
including (non-exhaustive):

1. **Provide license texts and attribution** for Qt / PySide6 (LGPL-3.0 and
   GPL-3.0 texts, and the Qt copyright notices).
2. **Allow the end user to replace the Qt libraries** with a modified version
   (LGPL §4). In practice this is easiest if you distribute the app so the Qt
   shared libraries (`.dll`/`.so`) remain replaceable — e.g. a PyInstaller
   **onedir** build (a folder where the Qt DLLs are separate files) rather than
   a single-file bundle. If you ship a one-file build, provide instructions
   and the means for a user to relink against their own Qt.
3. **Do not statically link** Qt in a way that prevents relinking (the default
   PySide6 wheels link Qt dynamically, which is compliant).

If these obligations are inconvenient for your distribution, options include:
distributing **source only** (let users build/run with their own PySide6),
switching the packaging to **onedir**, or obtaining a **commercial Qt license**.

> This summary is provided for convenience and is **not legal advice**. Verify
> each dependency's license for your specific distribution scenario. License
> texts for installed packages are available in their `*.dist-info` folders
> inside the Python environment.
