# Architecture

Ollama Model & RAG Inspector is a read-only PySide6 desktop app that inspects
Ollama-registered models (and external GGUF/Modelfile files) and reports basic
info, architecture metadata, lineage, fine-tuning traces, and RAG suitability —
all evidence-based, never guessed.

## Design principles

1. **Read-only.** No pull/create/delete/copy, no Modelfile edits, no inference,
   no embedding generation. Only `GET /api/tags`, `POST /api/show`, and
   optionally `GET /api/ps` are called; external files are read, never written.
2. **Generic, not model-specific.** No model name is hardcoded. Architecture is
   resolved in order: `model_info["general.architecture"]` → `details.family`
   → `details.families` → metadata key prefix → `unknown`. Unknown
   architectures still expose raw metadata and any discoverable numeric values.
3. **Evidence-based.** Every derived fact carries an `Evidence` record with a
   status: `Confirmed` / `Derived` / `Detected` / `Declared` / `Unknown` /
   `Conflict`. Anything unverifiable stays `Unknown` rather than being guessed.
4. **Partial success.** If one analyzer fails or a field is missing, the rest of
   the result is still shown, with a warning.

## Layers

The codebase separates concerns so the analysis core is fully testable without
Qt or a running Ollama server.

```
src/ollama_inspector/
├── config/           Static config + QSettings keys
├── domain/           Pydantic models, enums, errors        (no Qt)
├── infrastructure/   OllamaClient (httpx), GGUF reader,
│                     settings store, file export           (no analysis)
├── analyzers/        Modelfile / architecture / metadata-tree /
│                     lineage / fine-tuning / RAG            (pure Python, no Qt)
├── services/         Catalog / analysis / local-file / export orchestration
├── ui/               Window, workers, list model, tabs, widgets, theme (Qt)
├── utils/            Logging, URL/filename helpers
├── app.py            QApplication bootstrap
└── main.py           Entry point
```

**Layer rules (enforced by convention and tests):**

- Analyzers never import Qt.
- The UI never analyzes metadata directly — it only renders precomputed results.
- API response fields are always treated as optional.
- The raw `/api/show` payload is preserved under `raw_response`; unknown fields
  are never discarded.

## Data flow

```
/api/tags ──► ModelCatalogService ──► list[ModelSummary] ──► model list (UI)

select model
   │
   ▼
/api/show ──► ModelAnalysisService
                 ├─ ModelfileParser        (FROM / ADAPTER / SYSTEM / …)
                 ├─ ArchitectureAnalyzer    (canonical schema + derived values)
                 ├─ MetadataTreeBuilder     (dotted keys → tree)
                 ├─ LineageAnalyzer         (derivation type + evidence)
                 ├─ FineTuningAnalyzer      (LoRA / prompt / unknown)
                 └─ RAGSuitabilityAnalyzer  (role scores + limitations)
                          │
                          ▼
                 ModelAnalysisResult ──► tabs (UI) / JSON+Markdown export
```

External files (**Load File**) go through `LocalModelService`, which builds an
`/api/show`-compatible payload — a GGUF file via the pure-Python `gguf_reader`
(header + metadata KV only, no tensors/weights), or a Modelfile read directly —
and then reuses the exact same `ModelAnalysisService` pipeline.

## Concurrency

All HTTP and analysis runs on a `QThreadPool` (`CallableWorker` / `QRunnable`),
never on the UI thread, so the UI never freezes. Every worker signal carries a
request ID; when a newer request supersedes an older one, the stale result is
discarded (`if request_id != self._current_analysis_request_id: return`).

## Analysis logic (summary)

- **Modelfile parser** — case-insensitive directives, comments/blank lines
  ignored, multi-line triple-quoted blocks, repeatable `PARAMETER`, unknown
  directives captured; best-effort (returns partial results on malformed input);
  never opens adapter/file paths.
- **Architecture analyzer** — normalizes heterogeneous `model_info` into a
  common schema; derives `head_dimension = embedding_length / attention_heads`
  (only when divisible) and `gqa_ratio = attention_heads / kv_heads`; detects
  modalities from capabilities and `.vision.` / `.audio.` metadata.
- **Lineage analyzer** — prefers Modelfile `FROM`/`ADAPTER` and API parent
  fields over model-name patterns; classifies derivation
  (`LORA_ADAPTER`, `PROMPT_ONLY_DERIVATIVE`, `QUANTIZED_DERIVATIVE`,
  `CUSTOM_MODELFILE`, `OFFICIAL_BASE`, `UNKNOWN_DERIVATIVE`).
- **Fine-tuning analyzer** — `ADAPTER` ⇒ LoRA (confirmed); `FROM` +
  SYSTEM/TEMPLATE/PARAMETER ⇒ prompt customization; otherwise unknown. Training
  details (dataset, epochs, LoRA rank, …) are never guessed.
- **RAG suitability analyzer** — heuristic scores for generation, embedding, and
  long-context roles, plus a mandatory notice that the assessment is
  metadata-based and does not reflect an actual RAG connection or answer quality.

## Reports

- **JSON** — `model_dump(mode="json")`, UTF-8, indent 2, includes the raw
  response.
- **Markdown** — Summary / Architecture / Capabilities / Lineage / Fine-tuning /
  Prompt Configuration / RAG Suitability / Warnings / Evidence sections.

## Out of scope (this version)

GGUF tensor/weight analysis, Ollama manifest/blob access, weight comparison,
Hugging Face downloads, `torch`/`transformers` model loading, RAG runtime
probing, and answer-quality/hallucination evaluation.
