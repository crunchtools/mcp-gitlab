"""GitLab API client with security hardening.

This module provides a secure async HTTP client for the GitLab REST API v4.
All requests go through this client to ensure consistent security practices.
"""

import logging
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

# Response size limit to prevent memory exhaustion (10MB)
MAX_RESPONSE_SIZE = 10 * 1024 * 1024

# Request timeout in seconds
REQUEST_TIMEOUT = 30.0


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
                },
                timeout=httpx.Timeout(REQUEST_TIMEOUT),
                verify=True,
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
            response = await client.request(
                method=method,
                url=path,
                params=params,
                json=json_data,
            )
        except httpx.TimeoutException as e:
            raise GitLabApiError(0, f"Request timeout: {e}") from e
        except httpx.RequestError as e:
            raise GitLabApiError(0, f"Request failed: {e}") from e

        # Check response size before parsing
        content_length = response.headers.get("content-length")
        if content_length and int(content_length) > MAX_RESPONSE_SIZE:
            raise GitLabApiError(0, "Response too large")

        # Handle error responses before parsing
        if not response.is_success:
            self._handle_error_response(response)

        # Some endpoints return plain text (e.g., job trace)
        content_type = response.headers.get("content-type", "")
        if "text/plain" in content_type:
            return {"content": response.text}

        # Parse JSON response
        try:
            data = response.json()
        except ValueError as e:
            raise GitLabApiError(
                response.status_code, f"Invalid JSON response: {e}"
            ) from e

        # Wrap list responses with pagination info
        if isinstance(data, list):
            return self._wrap_list_response(data, response)

        return data  # type: ignore[no-any-return]

    def _wrap_list_response(
        self, data: list[Any], response: httpx.Response
    ) -> dict[str, Any]:
        """Wrap a list response with GitLab pagination headers.

        GitLab uses X-Total, X-Total-Pages, X-Page, X-Per-Page, X-Next-Page headers.
        """
        result: dict[str, Any] = {"items": data}

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
            result["pagination"] = pagination

        return result

    def _handle_error_response(self, response: httpx.Response) -> None:
        """Handle error responses from the API.

        Args:
            response: HTTP response

        Raises:
            Various UserError subclasses based on error type
        """
        status_code = response.status_code

        # Try to extract error message
        error_msg: str = "Unknown error"
        try:
            data = response.json()
            if isinstance(data, dict):
                raw_msg = data.get("message", data.get("error"))
                if isinstance(raw_msg, dict):
                    error_msg = str(raw_msg)
                elif raw_msg is not None:
                    error_msg = str(raw_msg)
            else:
                error_msg = str(data)
        except ValueError:
            error_msg = response.text[:200] if response.text else "Unknown error"

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

    # Convenience methods for HTTP verbs

    async def get(
        self, path: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
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


# Global client instance
_client: GitLabClient | None = None


def get_client() -> GitLabClient:
    """Get the global GitLab client instance."""
    global _client
    if _client is None:
        _client = GitLabClient()
    return _client
