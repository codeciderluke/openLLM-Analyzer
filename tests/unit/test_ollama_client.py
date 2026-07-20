"""Step 3: OllamaClient against a mocked transport."""

from __future__ import annotations

import httpx
import pytest

from ollama_inspector.domain.errors import (
    OllamaConnectionError,
    OllamaHTTPError,
    OllamaResponseError,
)
from ollama_inspector.infrastructure.ollama_client import OllamaClient


def _client(handler) -> OllamaClient:
    return OllamaClient("http://localhost:11434", transport=httpx.MockTransport(handler))


def test_list_models(tags_payload) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/tags"
        return httpx.Response(200, json=tags_payload)

    with _client(handler) as client:
        models = client.list_models()
    assert len(models) == 3
    assert models[0]["name"] == "llama3.1:8b"


def test_show_model(show_llama) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/show"
        return httpx.Response(200, json=show_llama)

    with _client(handler) as client:
        data = client.show_model("llama3.1:8b")
    assert data["capabilities"] == ["completion", "tools"]


def test_connection_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("refused", request=request)

    with _client(handler) as client, pytest.raises(OllamaConnectionError):
        client.list_models()


def test_http_status_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="boom")

    with _client(handler) as client, pytest.raises(OllamaHTTPError):
        client.show_model("x")


def test_invalid_json() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="not json")

    with _client(handler) as client, pytest.raises(OllamaResponseError):
        client.list_models()


def test_missing_models_key_returns_empty() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={})

    with _client(handler) as client:
        assert client.list_models() == []
