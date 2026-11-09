"""GitLab API client with security hardening.

This module provides a secure async HTTP client for the GitLab REST API v4.
All requests go through this client to ensure consistent security practices.
"""

import json
import logging
from importlib.metadata import version
from typing import Any

import httpx

from .config import get_config
from .errors import (
    GitLabApiError,
    PermissionDeniedError,
    ProjectNotFoundError,
    RateLimitError,
)

logger = logging.getLogger(__name__)

MAX_RESPONSE_SIZE = 10 * 1024 * 1024
REQUEST_TIMEOUT = 30.0
BODY_SNIPPET_CHARS = 200
ELLIPSIS = "..."

# Identify this client by name. httpx otherwise sends `python-httpx/<version>`,
# which bot protection answers with an HTML challenge page instead of the API --
# the failure that cost an afternoon on mcp-wordpress (RT #1596). The version
# comes from installed package metadata so it cannot drift from pyproject.toml.
USER_AGENT = (
    f"mcp-gitlab-crunchtools/{version('mcp-gitlab-crunchtools')} "
    "(+https://github.com/crunchtools/mcp-gitlab)"
)

# Query parameters whose value is a secret rather than part of the request.
# GitLab accepts `private_token` and `access_token` in a query string.
REDACTED_PARAMS = frozenset({"access_token", "private_token", "token"})


def _safe_url(url: httpx.URL) -> httpx.URL:
    """A URL fit to appear in an error message (Layer 1).

    Userinfo first: a self-hosted `GITLAB_URL` can carry credentials before the
    path, where redacting query parameters never reaches them. The rest is
    redacted by name, because `per_page`, `state` and `ref` are the diagnosis.
    """
    url = url.copy_with(userinfo=b"")
    for name in REDACTED_PARAMS & set(url.params):
        url = url.copy_set_param(name, "***")
    return url


def _body_snippet(body: bytes) -> str:
    """A short, single-line excerpt of a response body, for an error message."""
    prefix = body[: BODY_SNIPPET_CHARS * 4]
    collapsed = " ".join(prefix.decode("utf-8", errors="replace").split())
    if not collapsed:
        return "<empty body>"
    if len(collapsed) > BODY_SNIPPET_CHARS or len(body) > len(prefix):
        return collapsed[: BODY_SNIPPET_CHARS - len(ELLIPSIS)] + ELLIPSIS
    return collapsed


def _error_detail(response: httpx.Response, body: bytes) -> str:
    """GitLab's own error text, or the body quoted with the request it answered.

    The fallback is what tells an SSO login page or a proxy error apart from
    the API refusing something: neither answers with GitLab's `message`/`error`
    shape, and before this they both arrived as "Unknown error".
    """
    try:
        parsed = json.loads(body)
    except ValueError:
        parsed = None
    detail = ""
    if isinstance(parsed, dict):
        raw = parsed.get("message", parsed.get("error"))
        if isinstance(raw, (dict, str, int, float)):
            detail = str(raw)[: BODY_SNIPPET_CHARS * 4]
    elif parsed is not None:
        detail = str(parsed)[: BODY_SNIPPET_CHARS * 4]
    return detail or f"{_where(response)} returned {_body_snippet(body)}"


def _where(response: httpx.Response) -> str:
    """Which request a response answered, for an error message.

    The requested URL rather than the path: `GITLAB_URL` points this client at
    gitlab.com or at a self-hosted instance, and an instance behind an SSO
    proxy answers with a login page that a path alone cannot describe.
    """
    return (
        f"{response.request.method} {_safe_url(response.request.url)} "
        f"(HTTP {response.status_code}, {response.headers.get('content-type', 'no content-type')})"
    )


class GitLabClient:
    """Async HTTP client for GitLab API v4.

    Security features:
    - Configurable base URL with HTTPS enforcement
    - Token passed via PRIVATE-TOKEN header (not URL)
    - TLS certificate validation (httpx default)
    - Request timeout enforcement
    - Response size limits
    - Pagination support via GitLab headers
    """

    def __init__(self) -> None:
        """Initialize the GitLab client."""
        self._config = get_config()
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the async HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self._config.api_base_url,
                headers={
                    "PRIVATE-TOKEN": self._config.token,
                    "Content-Type": "application/json",
                    "User-Agent": USER_AGENT,
                },
                timeout=httpx.Timeout(REQUEST_TIMEOUT),
                verify=self._config.ssl_verify,
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an API request with error handling.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            path: API path (e.g., /projects)
            params: Query parameters
            json_data: JSON body data

        Returns:
            API response data with pagination info if applicable

        Raises:
            GitLabApiError: On API errors
            RateLimitError: On rate limiting
            PermissionDeniedError: On authorization failures
        """
        client = await self._get_client()

        logger.debug("API request: %s %s", method, path)

        try:
            request = client.build_request(
                method=method,
                url=path,
                params=params,
                json=json_data,
            )
            response = await client.send(request, stream=True)
            try:
                body = await self._read_capped(response)
            finally:
                await response.aclose()
        except httpx.TimeoutException as e:
            raise GitLabApiError(0, f"Request timeout: {e}") from e
        except httpx.RequestError as e:
            raise GitLabApiError(0, f"Request failed: {e}") from e

        if not response.is_success:
            self._handle_error_response(response, body)

        if response.status_code == 204:
            return {"status": "deleted"}

        content_type = response.headers.get("content-type", "")
        if "text/plain" in content_type:
            return {"content": body.decode("utf-8", errors="replace")}

        try:
            parsed = json.loads(body)
        except ValueError as e:
            raise GitLabApiError(
                response.status_code,
                f"{_where(response)} is not JSON ({e}): {_body_snippet(body)}",
            ) from e

        if isinstance(parsed, list):
            return self._wrap_list_response(parsed, response)

        if isinstance(parsed, dict):
            return parsed
        return {"data": parsed}

    @staticmethod
    async def _read_capped(response: httpx.Response) -> bytes:
        """Read the body, aborting as soon as it would pass MAX_RESPONSE_SIZE.

        One buffer, measured before the copy: `aiter_bytes()` promises nothing
        about chunk size -- one chunk can be the whole body -- so appending
        first would copy in exactly the response being refused. The
        `content-length` check this replaces was the only limit, and it is a
        header GitLab need not send.
        """
        declared = response.headers.get("content-length")
        if declared and declared.isdigit() and int(declared) > MAX_RESPONSE_SIZE:
            raise GitLabApiError(
                response.status_code,
                f"{_where(response)} declared {declared} bytes, over the "
                f"{MAX_RESPONSE_SIZE} byte limit",
            )
        body = bytearray()
        async for chunk in response.aiter_bytes():
            if len(body) + len(chunk) > MAX_RESPONSE_SIZE:
                raise GitLabApiError(
                    response.status_code,
                    f"{_where(response)} sent over the {MAX_RESPONSE_SIZE} byte limit",
                )
            body += chunk
        return bytes(body)

    def _wrap_list_response(self, items: list[Any], response: httpx.Response) -> dict[str, Any]:
        """Wrap a list response with GitLab pagination headers."""
        wrapped: dict[str, Any] = {"items": items}

        pagination: dict[str, Any] = {}
        for header, key in [
            ("x-total", "total"),
            ("x-total-pages", "total_pages"),
            ("x-page", "page"),
            ("x-per-page", "per_page"),
            ("x-next-page", "next_page"),
            ("x-prev-page", "prev_page"),
        ]:
            value = response.headers.get(header)
            if value:
                pagination[key] = int(value)

        if pagination:
            wrapped["pagination"] = pagination

        return wrapped

    def _handle_error_response(self, response: httpx.Response, body: bytes) -> None:
        """Handle error responses from the API.

        Args:
            response: HTTP response
            body: its bounded body, already read

        Raises:
            Various UserError subclasses based on error type
        """
        status_code = response.status_code
        error_msg = _error_detail(response, body)

        if status_code == 401:
            raise PermissionDeniedError("Valid Personal Access Token")
        if status_code == 403:
            raise PermissionDeniedError("Required permission scope")
        if status_code == 404:
            raise ProjectNotFoundError(error_msg)
        if status_code == 429:
            retry_after = response.headers.get("retry-after")
            raise RateLimitError(int(retry_after) if retry_after else None)

        raise GitLabApiError(status_code, error_msg)

    async def get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Make a GET request."""
        return await self._request("GET", path, params=params)

    async def post(
        self,
        path: str,
        json_data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make a POST request."""
        return await self._request("POST", path, params=params, json_data=json_data)

    async def put(
        self,
        path: str,
        json_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make a PUT request."""
        return await self._request("PUT", path, json_data=json_data)

    async def delete(self, path: str) -> dict[str, Any]:
        """Make a DELETE request."""
        return await self._request("DELETE", path)


_client: GitLabClient | None = None


def get_client() -> GitLabClient:
    """Get the global GitLab client instance."""
    global _client
    if _client is None:
        _client = GitLabClient()
    return _client
