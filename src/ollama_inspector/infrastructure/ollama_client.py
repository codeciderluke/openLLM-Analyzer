"""Synchronous Ollama HTTP client.

Read-only: only ``/api/tags``, ``/api/show`` and ``/api/ps`` are called.
Intended to be used from a worker thread, never the UI thread.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import httpx

from ollama_inspector.domain.errors import (
    OllamaConnectionError,
    OllamaHTTPError,
    OllamaResponseError,
)
from ollama_inspector.utils.logging_config import get_logger
from ollama_inspector.utils.text import normalize_base_url

logger = get_logger("ollama_client")


class OllamaClient:
    """Thin synchronous wrapper over the Ollama REST API."""

    def __init__(
        self,
        base_url: str,
        timeout_seconds: float = 15.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.base_url = normalize_base_url(base_url)
        self.timeout_seconds = timeout_seconds
        # ``transport`` is a test seam (e.g. httpx.MockTransport); production
        # code leaves it None and lets httpx use the default transport.
        self._client = httpx.Client(
            base_url=self.base_url, timeout=timeout_seconds, transport=transport
        )

    # -- public API -----------------------------------------------------

    def list_models(self) -> list[dict[str, Any]]:
        """Return the ``models`` array from ``GET /api/tags``."""

        data = self._get_json("/api/tags")
        models = data.get("models")
        if models is None:
            return []
        if not isinstance(models, list):
            raise OllamaResponseError("The 'models' field in the /api/tags response is not a list.")
        return [m for m in models if isinstance(m, dict)]

    def show_model(self, model_name: str) -> dict[str, Any]:
        """Return the full ``POST /api/show`` payload for a model."""

        payload = {"model": model_name, "verbose": True}
        data = self._post_json("/api/show", payload)
        if not isinstance(data, dict):
            raise OllamaResponseError("The /api/show response is not an object.")
        return data

    def list_running_models(self) -> list[dict[str, Any]]:
        """Return the ``models`` array from ``GET /api/ps`` (best-effort)."""

        data = self._get_json("/api/ps")
        models = data.get("models")
        if not isinstance(models, list):
            return []
        return [m for m in models if isinstance(m, dict)]

    def close(self) -> None:
        """Close the underlying HTTP connection pool."""

        self._client.close()

    def __enter__(self) -> OllamaClient:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    # -- internals ------------------------------------------------------

    def _get_json(self, path: str) -> dict[str, Any]:
        logger.debug("GET %s", path)
        return self._send(path, lambda: self._client.get(path))

    def _post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        logger.debug("POST %s", path)
        return self._send(path, lambda: self._client.post(path, json=payload))

    def _send(self, path: str, call: Callable[[], httpx.Response]) -> dict[str, Any]:
        try:
            response = call()
            response.raise_for_status()
            return self._decode(response)
        except httpx.ConnectError as exc:
            raise OllamaConnectionError(
                f"Cannot connect to the Ollama server: {self.base_url}"
            ) from exc
        except httpx.TimeoutException as exc:
            raise OllamaConnectionError(
                f"The request timed out ({self.timeout_seconds}s)."
            ) from exc
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            raise OllamaHTTPError(f"HTTP {status} error: {path}") from exc

    @staticmethod
    def _decode(response: httpx.Response) -> dict[str, Any]:
        try:
            data = response.json()
        except ValueError as exc:
            raise OllamaResponseError("Could not parse the response JSON.") from exc
        if not isinstance(data, dict):
            raise OllamaResponseError("The response is not a JSON object.")
        return data
