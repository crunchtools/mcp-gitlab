"""Shared test fixtures for mcp-gitlab tests."""

import os
from collections.abc import Callable, Generator
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest


@pytest.fixture(autouse=True)
def _reset_client_singleton() -> Generator[None, None, None]:
    """Reset the global client and config singletons between tests."""
    import mcp_gitlab_crunchtools.client as client_mod
    import mcp_gitlab_crunchtools.config as config_mod

    client_mod._client = None
    config_mod._config = None
    yield
    client_mod._client = None
    config_mod._config = None


def _mock_response(
    status_code: int = 200,
    json_data: dict | list | None = None,
    text: str = "",
    content_type: str = "application/json",
    headers: dict | None = None,
) -> httpx.Response:
    """Build a mock httpx.Response."""
    resp_headers = {"content-type": content_type}
    if headers:
        resp_headers.update(headers)
    return httpx.Response(
        status_code=status_code,
        headers=resp_headers,
        json=json_data if json_data is not None else None,
        text=text if json_data is None else None,
        request=httpx.Request("GET", "https://gitlab.com/api/v4/test"),
    )


def _patch_client(mock_response: httpx.Response):
    """Patch the AsyncClient so every request is answered with one response.

    Sets GITLAB_TOKEN so config initializes, then mocks the HTTP layer. The
    client streams now: `build_request` then `send(..., stream=True)`. A real
    `httpx.Client` builds the request, so assertions on the method, url, params
    and json a caller passed still mean what they did, while `send` is scripted.

    What a mock of the client cannot see is the client's own behaviour -- the
    User-Agent it adds and the bounded read it performs. Those are tested
    through `_patch_transport` (constitution v1.36.0, Layer 3).
    """
    import mcp_gitlab_crunchtools.client as client_mod
    import mcp_gitlab_crunchtools.config as config_mod

    client_mod._client = None
    config_mod._config = None

    os.environ.setdefault("GITLAB_TOKEN", "glpat-test-mock-token")

    builder = httpx.Client(base_url="https://gitlab.com/api/v4")
    mock_http = AsyncMock(spec=httpx.AsyncClient)
    mock_http.build_request = MagicMock(side_effect=builder.build_request)
    mock_http.send = AsyncMock(return_value=mock_response)

    return patch.object(httpx, "AsyncClient", return_value=mock_http)


def _patch_transport(handler: Callable[[httpx.Request], httpx.Response]):
    """Patch AsyncClient so real clients send through a mock transport.

    Unlike `_patch_client`, the httpx client itself is real: the handler sees
    each request as it would go on the wire, default headers included. Use it
    where the headers of a request, or the streaming read, are what is under
    test.
    """
    import mcp_gitlab_crunchtools.client as client_mod
    import mcp_gitlab_crunchtools.config as config_mod

    client_mod._client = None
    config_mod._config = None

    os.environ.setdefault("GITLAB_TOKEN", "glpat-test-mock-token")

    real_client = httpx.AsyncClient

    def build(**kwargs: Any) -> httpx.AsyncClient:
        kwargs.pop("transport", None)
        return real_client(transport=httpx.MockTransport(handler), **kwargs)

    return patch.object(httpx, "AsyncClient", side_effect=build)
