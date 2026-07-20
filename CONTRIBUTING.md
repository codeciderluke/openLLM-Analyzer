# Contributing

Thanks for your interest in improving **Ollama Model & RAG Inspector**!

## Development setup

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# bash:               source .venv/bin/activate
pip install -e ".[dev]"
```

## Before opening a pull request

Run the tests and the linter — both must pass:

```bash
QT_QPA_PLATFORM=offscreen PYTHONPATH=src python -m pytest -q
python -m ruff check src tests
```

(On Windows you can just run `test.bat`.)

## Design rules

These keep the codebase testable and consistent — please follow them:

- **Analyzers must not import Qt.** The analysis core is pure Python and unit
  tested without a display or a running Ollama server.
- **The UI must not analyze metadata directly** — it only renders precomputed
  `ModelAnalysisResult` data.
- **Treat all API response fields as optional.** Never assume a field exists.
- **Never hardcode model names** in analysis logic.
- **Do not guess** fine-tuning or RAG facts — if it isn't in the artifacts, it is
  `Unknown`. Preserve the raw response.
- Use `pathlib`, UTF-8, and type hints on public functions.
- Add or update tests for any behavior change; add fixtures under
  `tests/fixtures/` rather than requiring a live server.

## Style

- `ruff` governs formatting/imports/lint (line length 100). Run
  `ruff check --fix` to auto-fix.
- Keep comments in **English**.

## Reporting issues

Please include: OS, Python version, Ollama version (if relevant), the model or
GGUF file involved (name/architecture — not weights), and steps to reproduce.
Do not paste private or sensitive prompts/system text.
