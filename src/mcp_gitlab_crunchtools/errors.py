"""Safe error types that can be shown to users.

This module defines exception classes that are safe to expose to MCP clients.
Internal errors should be caught and converted to UserError before propagating.
"""

import os


class UserError(Exception):
    """Base class for safe errors that can be shown to users.

    All error messages in UserError subclasses must be carefully crafted
    to avoid leaking sensitive information like API tokens or internal paths.
    """

    pass


class ConfigurationError(UserError):
    """Error in server configuration."""

    pass


class GitLabApiError(UserError):
    """Error from GitLab API.

    The message is sanitized to remove any potential token references.
    """

    def __init__(self, code: int, message: str) -> None:
        token = os.environ.get("GITLAB_TOKEN", "")
        safe_message = message.replace(token, "***") if token else message
        super().__init__(f"GitLab API error {code}: {safe_message}")


class ProjectNotFoundError(UserError):
    """Project not found or not accessible."""

    def __init__(self, identifier: str) -> None:
        safe_id = identifier[:40] + "..." if len(identifier) > 40 else identifier
        super().__init__(f"Project not found or not accessible: {safe_id}")


class PermissionDeniedError(UserError):
    """Permission denied for the requested operation."""

    def __init__(self, required_scope: str) -> None:
        super().__init__(f"Permission denied. Required scope: {required_scope}")


class RateLimitError(UserError):
    """Rate limit exceeded."""

    def __init__(self, retry_after: int | None = None) -> None:
        msg = "Rate limit exceeded."
        if retry_after:
            msg += f" Retry after {retry_after} seconds."
        super().__init__(msg)


class ValidationError(UserError):
    """Input validation error."""

    pass
