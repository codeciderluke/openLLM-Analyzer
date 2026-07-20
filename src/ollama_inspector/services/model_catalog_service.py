"""Model catalog service: loads and normalises the model list."""

from __future__ import annotations

from typing import Any

from ollama_inspector.domain.model_summary import ModelSummary
from ollama_inspector.infrastructure.ollama_client import OllamaClient
from ollama_inspector.utils.logging_config import get_logger

logger = get_logger("model_catalog")


class ModelCatalogService:
    """Turns ``/api/tags`` entries into sorted :class:`ModelSummary` objects."""

    def __init__(self, client: OllamaClient) -> None:
        self._client = client

    def load_models(self) -> list[ModelSummary]:
        raw = self._client.list_models()
        summaries = [self._to_summary(entry) for entry in raw]
        summaries.sort(key=lambda s: s.name.lower())
        logger.info("Loaded %d models", len(summaries))
        return summaries

    @staticmethod
    def _to_summary(entry: dict[str, Any]) -> ModelSummary:
        details = entry.get("details") or {}
        if not isinstance(details, dict):
            details = {}

        families = details.get("families")
        if not isinstance(families, list):
            families = []
        families = [f for f in families if isinstance(f, str)]

        name = entry.get("name") or entry.get("model") or "unknown"
        return ModelSummary(
            name=str(name),
            model=_opt_str(entry.get("model")),
            digest=_opt_str(entry.get("digest")),
            modified_at=_opt_str(entry.get("modified_at")),
            size_bytes=_opt_int(entry.get("size")),
            format=_opt_str(details.get("format")),
            family=_opt_str(details.get("family")),
            families=families,
            parameter_size=_opt_str(details.get("parameter_size")),
            quantization_level=_opt_str(details.get("quantization_level")),
        )


def _opt_str(value: Any) -> str | None:
    return str(value) if isinstance(value, (str, int, float)) and value != "" else None


def _opt_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None
