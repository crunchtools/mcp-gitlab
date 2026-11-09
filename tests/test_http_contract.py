"""The outbound HTTP contract (constitution v1.36.0, MCP Server profile Layer 3).

These use `_patch_transport`, so the client is real: the agent string is a
header the client adds and the ceiling is enforced while the client reads, so
the `_patch_client` mock cannot see either.
"""

from collections.abc import AsyncIterator
from importlib.metadata import version

import httpx
import pytest

from mcp_gitlab_crunchtools import client as client_mod
from mcp_gitlab_crunchtools.errors import GitLabApiError

from .conftest import _patch_transport


async def _chunks(chunk: bytes, times: int) -> AsyncIterator[bytes]:
    """A chunked body, which carries no content-length -- what a header check misses."""
    for _ in range(times):
        yield chunk


class TestUserAgent:
    """A request says what it is, and the version cannot drift from the release."""

    @pytest.mark.asyncio
    async def test_outgoing_request_names_the_product_and_version(self) -> None:
        seen: list[str] = []

        def handler(request: httpx.Request) -> httpx.Response:
            seen.append(request.headers["User-Agent"])
            return httpx.Response(200, json={"id": 1})

        with _patch_transport(handler):
            await client_mod.get_client()._request("GET", "/projects/1")

        expected = (
            f"mcp-gitlab-crunchtools/{version('mcp-gitlab-crunchtools')} "
            "(+https://github.com/crunchtools/mcp-gitlab)"
        )
        assert seen == [expected]
        assert "python-httpx" not in seen[0]


class TestResponseCeiling:
    """The cap is enforced while reading, not taken from a header."""

    @pytest.mark.asyncio
    async def test_chunked_body_over_the_cap_is_refused(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(client_mod, "MAX_RESPONSE_SIZE", 4096)

        def handler(_request: httpx.Request) -> httpx.Response:
            response = httpx.Response(
                200, headers={"content-type": "application/json"}, content=_chunks(b"x" * 1024, 16)
            )
            assert "content-length" not in response.headers
            return response

        with _patch_transport(handler), pytest.raises(GitLabApiError) as caught:
            await client_mod.get_client()._request("GET", "/projects/1/issues")

        message = str(caught.value)
        assert "over the 4096 byte limit" in message
        assert "/projects/1/issues" in message

    @pytest.mark.asyncio
    async def test_a_single_oversized_chunk_is_refused_before_it_is_copied(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(client_mod, "MAX_RESPONSE_SIZE", 1024)

        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200, headers={"content-type": "application/json"}, content=_chunks(b"x" * 8192, 1)
            )

        with _patch_transport(handler), pytest.raises(GitLabApiError) as caught:
            await client_mod.get_client()._request("GET", "/projects/1/issues")

        assert "over the 1024 byte limit" in str(caught.value)


class TestErrorNamesTheSite:
    """RT #1596: the message has to say which site answered, and with what."""

    @pytest.mark.asyncio
    async def test_a_non_json_error_body_is_quoted_with_the_request(self) -> None:
        """A self-hosted instance behind SSO answers with a login page."""

        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                502, headers={"content-type": "text/html"}, text="<title>Sign in</title>"
            )

        with _patch_transport(handler), pytest.raises(GitLabApiError) as caught:
            await client_mod.get_client()._request("GET", "/projects/1")

        message = str(caught.value)
        assert "Sign in" in message
        assert "text/html" in message
        assert "/projects/1" in message

    @pytest.mark.asyncio
    async def test_gitlabs_own_message_is_still_used(self) -> None:
        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(400, json={"message": "Invalid parameters"})

        with _patch_transport(handler), pytest.raises(GitLabApiError) as caught:
            await client_mod.get_client()._request("POST", "/projects/1/issues")

        assert "Invalid parameters" in str(caught.value)


class TestErrorRedaction:
    """Layer 1 applies to an error message: the URL in it carries no secret."""

    @pytest.mark.asyncio
    async def test_credential_params_are_redacted(self) -> None:
        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(502, headers={"content-type": "text/html"}, text="nope")

        with _patch_transport(handler), pytest.raises(GitLabApiError) as caught:
            await client_mod.get_client()._request(
                "GET", "/projects/1", params={"private_token": "glpat-secret", "per_page": 5}
            )

        message = str(caught.value)
        assert "glpat-secret" not in message
        assert "per_page=5" in message
