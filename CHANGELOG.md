# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-07-20

### Added
- Read-only inspection of Ollama models via `/api/tags` and `/api/show`
  (optional `/api/ps`).
- Evidence-based analysis: architecture normalization, metadata tree, lineage,
  fine-tuning traces, and RAG role-suitability scoring.
- Modelfile parser (directives, comments, multi-line triple-quoted blocks,
  repeatable `PARAMETER`, unknown-directive capture; best-effort partial parsing).
- External model loading: local `.gguf` files (pure-Python GGUF metadata reader,
  no weights) and Modelfiles, analyzed through the same pipeline.
- PySide6 GUI: connection bar, searchable model list, and detail tabs
  (Overview / Structure / Lineage / Fine-tuning / Prompt / RAG / Raw Data).
- Background workers (`QThreadPool`) with request-ID stale-result guarding.
- JSON and Markdown report export.
- Modern dark theme with a dark/light toggle; Full HD-tuned layout; custom app
  icon.
- PyInstaller packaging (`build_exe.bat`, `OllamaInspector.spec`) with a
  generated multi-size `.ico`.
- Unit and headless UI tests; `ruff` lint configuration.
