"""Secure configuration handling.

This module handles all configuration including the sensitive API token.
The token is stored as a SecretStr to prevent accidental logging.
"""

import logging
import os
from urllib.parse import urlparse

from pydantic import SecretStr

from .errors import ConfigurationError

logger = logging.getLogger(__name__)


class Config:
    """Secure configuration handling.

    The API token is stored as a SecretStr and should only be accessed
    via the token property when actually needed for API calls.
    """

    def __init__(self) -> None:
        """Initialize configuration from environment variables.

        Raises:
            ConfigurationError: If required environment variables are missing or invalid.
        """
        token = os.environ.get("GITLAB_TOKEN")
        if not token:
            raise ConfigurationError(
                "GITLAB_TOKEN environment variable required. "
                "Create a Personal Access Token at "
                "https://gitlab.com/-/user_settings/personal_access_tokens"
            )

        self._token = SecretStr(token)

        gitlab_url = os.environ.get("GITLAB_URL", "https://gitlab.com").rstrip("/")

        parsed = urlparse(gitlab_url)
        if not parsed.scheme or not parsed.netloc:
            raise ConfigurationError(
                "Invalid GITLAB_URL: must be a valid URL (e.g. https://gitlab.com)"
            )

        if parsed.scheme != "https" and parsed.hostname not in ("localhost", "127.0.0.1", "::1"):
            raise ConfigurationError(
                "GITLAB_URL must use HTTPS for non-localhost URLs"
            )

        self._base_url = gitlab_url

        ssl_disabled = os.environ.get("GITLAB_SSL_VERIFY", "true").lower() in ("false", "0", "no")
        ssl_cert_file = os.environ.get("SSL_CERT_FILE")

        match (ssl_disabled, ssl_cert_file):
            case (True, _):
                self._ssl_verify: bool | str = False
                logger.warning("SSL verification disabled via GITLAB_SSL_VERIFY")
            case (False, str(cert_path)):
                self._ssl_verify = cert_path
                logger.info("Using custom CA bundle: %s", cert_path)
            case _:
                self._ssl_verify = True

        logger.info("Configuration loaded successfully (GitLab: %s)", self._base_url)

    @property
    def token(self) -> str:
        """Get token value for API calls.

        Use sparingly - only when making actual API calls.
        """
        return self._token.get_secret_value()

    @property
    def api_base_url(self) -> str:
        """GitLab API v4 base URL.

        Derived from GITLAB_URL environment variable.
        """
        return f"{self._base_url}/api/v4"

    @property
    def gitlab_url(self) -> str:
        """GitLab instance base URL."""
        return self._base_url

    @property
    def ssl_verify(self) -> bool | str:
        """SSL verification setting.

        Returns True, False, or a path to a CA bundle file.
        """
        return self._ssl_verify

    def __repr__(self) -> str:
        """Safe repr that never exposes the token."""
        return f"Config(gitlab_url={self._base_url}, token=***)"

    def __str__(self) -> str:
        """Safe str that never exposes the token."""
        return f"Config(gitlab_url={self._base_url}, token=***)"


_config: Config | None = None


def get_config() -> Config:
    """Get the global configuration instance.

    This function lazily initializes the configuration on first call.
    Subsequent calls return the same instance.

    Returns:
        The global Config instance.

    Raises:
        ConfigurationError: If configuration is invalid.
    """
    global _config
    if _config is None:
        _config = Config()
    return _config
