"""Generate the English user manual as a PDF (docs/UserManual.pdf).

Uses PySide6's QTextDocument + QPdfWriter, so no extra dependencies are
required. Run: python packaging/gen_manual.py
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QMarginsF, Qt, QUrl
from PySide6.QtGui import (
    QFontDatabase,
    QGuiApplication,
    QImage,
    QPageLayout,
    QPageSize,
    QPainter,
    QPdfWriter,
    QTextDocument,
)
from PySide6.QtSvg import QSvgRenderer

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SVG_PATH = ROOT / "src" / "ollama_inspector" / "ui" / "resources" / "icon.svg"
OUT_PATH = ROOT / "docs" / "UserManual.pdf"
VERSION = "1.0.0"

_FONTS = [
    r"C:\Windows\Fonts\segoeui.ttf",
    r"C:\Windows\Fonts\segoeuib.ttf",
    r"C:\Windows\Fonts\consola.ttf",
    r"C:\Windows\Fonts\malgun.ttf",
]

_APP = None


def _icon_image(size: int = 96) -> QImage:
    image = QImage(size, size, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    QSvgRenderer(str(SVG_PATH)).render(painter)
    painter.end()
    return image


def _html() -> str:
    return f"""
<html><body>
<table width="100%"><tr>
  <td width="90"><img src="app-icon" width="76" height="76"/></td>
  <td>
    <h1 style="margin-bottom:2px;">Ollama Model &amp; RAG Inspector</h1>
    <div style="color:#555;font-size:11pt;">User Manual &nbsp;&middot;&nbsp; Version {VERSION}</div>
  </td>
</tr></table>
<hr/>

<p>A read-only desktop application (PySide6) that inspects models registered on
an <b>Ollama</b> server, and external <b>GGUF</b>/<b>Modelfile</b> files on disk.
It reports basic info, architecture metadata, Modelfile configuration, model
lineage, fine-tuning traces, and RAG role-suitability. Every conclusion is
<b>evidence-based, never guessed</b>.</p>

<h2>1. Key principles</h2>
<ul>
  <li><b>Read-only &amp; safe.</b> No pull, create, delete, copy, Modelfile edit,
      or inference. Only <code>/api/tags</code>, <code>/api/show</code>, and
      optionally <code>/api/ps</code> are called.</li>
  <li><b>Generic.</b> No model name is hardcoded; unknown architectures still
      show raw metadata and any discoverable structural values.</li>
  <li><b>Evidence-based.</b> Every fact carries a status; anything unverifiable
      stays <i>Unknown</i> instead of being guessed.</li>
  <li><b>Partial success.</b> If one analyzer fails, the rest is still shown with
      a warning.</li>
</ul>

<h2>2. Requirements</h2>
<ul>
  <li>Python 3.11 or newer.</li>
  <li>An Ollama server to inspect (default <code>http://localhost:11434</code>),
      and/or local <code>.gguf</code> / Modelfile files.</li>
</ul>

<h2>3. Installation</h2>
<p><b>Windows (batch helpers):</b></p>
<pre style="background:#f2f4f8;">setup.bat   :: create .venv and install the app + dev tools
run.bat     :: launch the GUI (auto-runs setup.bat if needed)
test.bat    :: run tests + lint headless</pre>
<p><b>Manual (any OS):</b></p>
<pre style="background:#f2f4f8;">python -m venv .venv
pip install -e ".[dev]"
python -m ollama_inspector.main</pre>

<h2>4. Getting started</h2>
<ol>
  <li>Confirm or edit the <b>Ollama URL</b> and click <b>Connect</b>.</li>
  <li>Pick a model from the left list. The <b>search box</b> filters by name.</li>
  <li>Browse the detail tabs (below).</li>
  <li>Save a report with <b>Save JSON</b> or <b>Save MD</b>.</li>
</ol>
<p>The UI never freezes: all network and analysis work runs on background
threads, and a request-ID guard discards stale results when you switch models
quickly.</p>

<h2>5. The tabs</h2>
<table border="1" cellpadding="6" cellspacing="0" width="100%" style="border-color:#ccc;">
<tr style="background:#eef1f8;"><th align="left">Tab</th><th align="left">Shows</th></tr>
<tr><td><b>Overview</b></td><td>Name, digest, size, format, family, parameter size,
  quantization, capabilities, architecture, modalities, context length, attention.</td></tr>
<tr><td><b>Structure</b></td><td>Canonical architecture values, the raw metadata
  tree, and supporting evidence.</td></tr>
<tr><td><b>Lineage</b></td><td>Current / base / parent model, adapters, and the
  detected derivation type with evidence.</td></tr>
<tr><td><b>Fine-tuning</b></td><td>Fine-tuned yes/no/unknown, method, adapters,
  training-metadata presence, and the list of facts left Unknown.</td></tr>
<tr><td><b>Prompt</b></td><td>Modelfile, SYSTEM, TEMPLATE, PARAMETERS, LICENSE.</td></tr>
<tr><td><b>RAG</b></td><td>Roles and heuristic scores (generation, embedding,
  long-context), multimodal suitability, reasons, and limitations.</td></tr>
<tr><td><b>Raw Data</b></td><td>The full <code>/api/show</code> payload,
  <code>model_info</code>, <code>details</code>, and capabilities.</td></tr>
</table>

<h2>6. Evidence statuses</h2>
<table border="1" cellpadding="6" cellspacing="0" width="100%" style="border-color:#ccc;">
<tr style="background:#eef1f8;"><th align="left">Status</th><th align="left">Meaning</th></tr>
<tr><td><b>Confirmed</b></td><td>Read directly from the API or Modelfile.</td></tr>
<tr><td><b>Derived</b></td><td>Computed from confirmed values.</td></tr>
<tr><td><b>Detected</b></td><td>Inferred from a rule or pattern.</td></tr>
<tr><td><b>Declared</b></td><td>From external configuration or user input.</td></tr>
<tr><td><b>Unknown</b></td><td>Could not be determined.</td></tr>
<tr><td><b>Conflict</b></td><td>Data sources disagree.</td></tr>
</table>

<h2>7. Inspecting external models</h2>
<p>Click <b>Load File</b> to inspect a model stored outside Ollama:</p>
<ul>
  <li>A local <b><code>.gguf</code></b> file &mdash; its GGUF metadata header is
      parsed in pure Python (<i>no weights are loaded</i>) and run through the
      same analyzers.</li>
  <li>A <b>Modelfile</b>, or a <b>folder</b> containing either.</li>
</ul>
<p>Because a raw GGUF has no capability/Modelfile information, some fields will
be limited &mdash; the app says so rather than guessing.</p>

<h2>8. Themes</h2>
<p>Use the top-right <b>Dark Mode / Light Mode</b> button to switch themes at any
time. The choice is remembered between sessions. The layout is tuned for Full HD
displays.</p>

<h2>9. Exporting reports</h2>
<ul>
  <li><b>JSON</b> &mdash; the full result including the raw response
      (UTF-8, indent 2).</li>
  <li><b>Markdown</b> &mdash; Summary, Architecture, Capabilities, Lineage,
      Fine-tuning, Prompt Configuration, RAG Suitability, Warnings, Evidence.</li>
</ul>

<h2>10. Building a standalone executable (Windows)</h2>
<pre style="background:#f2f4f8;">build_exe.bat            :: generates the icon and builds dist\\OllamaInspector.exe</pre>
<p>Two PyInstaller specs are provided: <code>OllamaInspector.spec</code> (single
file) and <code>OllamaInspector-onedir.spec</code> (a folder where the Qt
libraries are separate files). The bundled executable includes Qt, used under
the <b>LGPL-3.0</b>; distributing it carries LGPL obligations &mdash; see
<code>THIRD_PARTY_LICENSES.md</code>.</p>

<h2>11. Troubleshooting</h2>
<table border="1" cellpadding="6" cellspacing="0" width="100%" style="border-color:#ccc;">
<tr style="background:#eef1f8;"><th align="left">Symptom</th><th align="left">What to do</th></tr>
<tr><td>Connection failed</td><td>Check the URL and that <code>ollama serve</code>
  is running. The app stays open; fix the URL and click Connect again.</td></tr>
<tr><td>Analysis failed for one model</td><td>The model list is kept; the error is
  shown and you can select a different model.</td></tr>
<tr><td>"Not a GGUF file"</td><td>The file is not a valid GGUF (or is version&nbsp;1);
  try a Modelfile or a GGUF v2/v3 file.</td></tr>
</table>

<h2>12. Scope &amp; limitations</h2>
<p>The primary data source is the Ollama HTTP API. For external files, only GGUF
<i>metadata</i> (header + key/values) is read. The app does <b>not</b> read GGUF
tensors/weights, access Ollama manifests/blobs, run inference, or evaluate
answer quality. RAG scores are metadata-based heuristics and do not reflect an
actual RAG connection.</p>

<h2>13. License</h2>
<p>This project is released under the <b>MIT License</b>. Bundled/third-party
components keep their own licenses &mdash; notably PySide6/Qt (LGPL-3.0). See
<code>LICENSE</code> and <code>THIRD_PARTY_LICENSES.md</code>.</p>

<hr/>
<div style="color:#888;font-size:9pt;">Ollama Model &amp; RAG Inspector v{VERSION}
&mdash; https://github.com/codeciderluke/openLLM-Analyzer</div>
</body></html>
"""


def main() -> None:
    global _APP
    _APP = QGuiApplication.instance() or QGuiApplication([])
    for font in _FONTS:
        QFontDatabase.addApplicationFont(font)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    writer = QPdfWriter(str(OUT_PATH))
    writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
    writer.setResolution(96)
    writer.setPageMargins(QMarginsF(16, 14, 16, 14), QPageLayout.Unit.Millimeter)
    writer.setTitle("Ollama Model & RAG Inspector - User Manual")

    doc = QTextDocument()
    doc.addResource(
        QTextDocument.ResourceType.ImageResource, QUrl("app-icon"), _icon_image()
    )
    doc.setDefaultStyleSheet(
        "body{font-family:'Segoe UI',sans-serif;font-size:10.5pt;color:#1a2030;}"
        "h1{font-size:19pt;} h2{font-size:13pt;color:#2b3550;margin-top:14px;}"
        "code,pre{font-family:'Consolas',monospace;font-size:9.5pt;}"
        "pre{padding:6px;}"
    )
    doc.setHtml(_html())
    page_px = writer.pageLayout().paintRectPixels(writer.resolution())
    doc.setPageSize(page_px.size())
    doc.print_(writer)
    print(f"wrote {OUT_PATH} ({OUT_PATH.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
