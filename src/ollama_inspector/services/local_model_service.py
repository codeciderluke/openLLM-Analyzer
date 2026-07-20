"""Analyse externally stored models (a local ``.gguf`` file or a Modelfile).

Builds an ``/api/show``-compatible payload and runs it through the same
:class:`ModelAnalysisService` pipeline used for Ollama models. Read-only: no
weights are loaded, nothing is written.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ollama_inspector.domain.analysis_result import ModelAnalysisResult
from ollama_inspector.domain.errors import LocalModelError
from ollama_inspector.infrastructure.gguf_reader import GgufMetadata, read_gguf_metadata
from ollama_inspector.services.model_analysis_service import ModelAnalysisService
from ollama_inspector.utils.logging_config import get_logger

logger = get_logger("local_model")

_GGUF_SUFFIX = ".gguf"
_MODELFILE_HINTS = {".modelfile", ".txt"}
_MODELFILE_NAMES = {"modelfile"}


class LocalModelService:
    """Loads and analyses a model file from an arbitrary filesystem path."""

    def __init__(self, analysis_service: ModelAnalysisService | None = None) -> None:
        self._analysis = analysis_service or ModelAnalysisService()

    def analyze_path(self, path: str | Path) -> ModelAnalysisResult:
        target = self._resolve_target(Path(path))
        if target.suffix.lower() == _GGUF_SUFFIX:
            return self._analyze_gguf(target)
        if self._looks_like_modelfile(target):
            return self._analyze_modelfile(target)
        # Unknown extension: try GGUF (binary magic check is cheap), else text.
        try:
            return self._analyze_gguf(target)
        except LocalModelError:
            return self._analyze_modelfile(target)

    # -- target resolution ---------------------------------------------

    @staticmethod
    def _resolve_target(path: Path) -> Path:
        if path.is_dir():
            ggufs = sorted(path.glob("*.gguf"))
            if ggufs:
                return ggufs[0]
            for name in ("Modelfile", "modelfile"):
                candidate = path / name
                if candidate.is_file():
                    return candidate
            raise LocalModelError(f"No .gguf or Modelfile found in folder: {path}")
        if not path.is_file():
            raise LocalModelError(f"File not found: {path}")
        return path

    @staticmethod
    def _looks_like_modelfile(path: Path) -> bool:
        return path.name.lower() in _MODELFILE_NAMES or path.suffix.lower() in _MODELFILE_HINTS

    # -- GGUF -----------------------------------------------------------

    def _analyze_gguf(self, path: Path) -> ModelAnalysisResult:
        meta = read_gguf_metadata(path)
        model_name = meta.name or path.stem
        payload = self._gguf_payload(meta, path)
        result = self._analysis.analyze_show_payload(model_name, payload)
        result.warnings.insert(0, f"External GGUF file analysis: {path.name}")
        result.warnings.append(
            "Local GGUF has no capabilities/Modelfile info, so some analysis is limited."
        )
        return result

    def _gguf_payload(self, meta: GgufMetadata, path: Path) -> dict[str, Any]:
        details: dict[str, Any] = {"format": "gguf"}
        if meta.architecture:
            details["family"] = meta.architecture
            details["families"] = [meta.architecture]
        if meta.quantization:
            details["quantization_level"] = meta.quantization
        size_label = meta.metadata.get("general.size_label")
        if isinstance(size_label, str):
            details["parameter_size"] = size_label

        template = meta.metadata.get("tokenizer.chat_template")
        template_text = template if isinstance(template, str) else ""

        return {
            "model_info": meta.metadata,
            "details": details,
            "capabilities": [],
            "template": template_text,
            "modelfile": "",
            "system": "",
            "parameters": "",
            "license": "",
            "gguf": {
                "path": str(path),
                "version": meta.version,
                "tensor_count": meta.tensor_count,
            },
        }

    # -- Modelfile ------------------------------------------------------

    def _analyze_modelfile(self, path: Path) -> ModelAnalysisResult:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            raise LocalModelError(f"Could not read the Modelfile: {path}") from exc
        if "FROM" not in text.upper():
            raise LocalModelError(f"Not a recognizable model file: {path.name}")

        payload: dict[str, Any] = {
            "modelfile": text,
            "details": {},
            "model_info": {},
            "capabilities": [],
        }
        result = self._analysis.analyze_show_payload(path.stem, payload)
        result.warnings.insert(0, f"External Modelfile analysis: {path.name}")
        return result
