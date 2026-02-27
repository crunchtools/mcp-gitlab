"""Tests for MCP tools.

These tests verify tool behavior without making actual API calls.
Integration tests with a real GitLab account should be run separately.
"""

import pytest


class TestToolRegistration:
    """Tests to verify all tools are properly registered."""

    def test_server_has_tools(self) -> None:
        """Server should have all expected tools registered."""
        from mcp_gitlab_crunchtools.server import mcp

        assert mcp is not None

    def test_imports(self) -> None:
        """All tool functions should be importable."""
        from mcp_gitlab_crunchtools.tools import (
            create_issue,
            create_issue_note,
            create_merge_request,
            create_mr_note,
            get_group,
            get_issue,
            get_job_log,
            get_merge_request,
            get_mr_changes,
            get_pipeline,
            get_project,
            get_project_branch,
            list_group_projects,
            list_groups,
            list_issue_notes,
            list_issues,
            list_merge_requests,
            list_mr_notes,
            list_pipeline_jobs,
            list_pipelines,
            list_project_branches,
            list_project_commits,
            list_projects,
            search_global,
            search_project,
            update_issue,
            update_merge_request,
        )

        # Projects (5)
        assert callable(list_projects)
        assert callable(get_project)
        assert callable(list_project_branches)
        assert callable(get_project_branch)
        assert callable(list_project_commits)

        # Groups (3)
        assert callable(list_groups)
        assert callable(get_group)
        assert callable(list_group_projects)

        # Merge Requests (7)
        assert callable(list_merge_requests)
        assert callable(get_merge_request)
        assert callable(create_merge_request)
        assert callable(update_merge_request)
        assert callable(list_mr_notes)
        assert callable(create_mr_note)
        assert callable(get_mr_changes)

        # Issues (6)
        assert callable(list_issues)
        assert callable(get_issue)
        assert callable(create_issue)
        assert callable(update_issue)
        assert callable(list_issue_notes)
        assert callable(create_issue_note)

        # Pipelines (4)
        assert callable(list_pipelines)
        assert callable(get_pipeline)
        assert callable(list_pipeline_jobs)
        assert callable(get_job_log)

        # Search (2)
        assert callable(search_global)
        assert callable(search_project)


class TestErrorSafety:
    """Tests to verify error messages don't leak sensitive data."""

    def test_gitlab_api_error_sanitizes_token(self) -> None:
        """GitLabApiError should sanitize tokens from messages."""
        import os

        from mcp_gitlab_crunchtools.errors import GitLabApiError

        os.environ["GITLAB_TOKEN"] = "glpat-secret_token_12345"

        try:
            error = GitLabApiError(401, "Invalid token: glpat-secret_token_12345")
            assert "glpat-secret_token_12345" not in str(error)
            assert "***" in str(error)
        finally:
            del os.environ["GITLAB_TOKEN"]

    def test_project_not_found_truncates_long_ids(self) -> None:
        """ProjectNotFoundError should truncate long identifiers."""
        from mcp_gitlab_crunchtools.errors import ProjectNotFoundError

        long_id = "a" * 100
        error = ProjectNotFoundError(long_id)
        error_str = str(error)

        assert long_id not in error_str
        assert "..." in error_str


class TestConfigSafety:
    """Tests for configuration security."""

    def test_config_repr_hides_token(self) -> None:
        """Config repr should never show the token."""
        import os

        os.environ["GITLAB_TOKEN"] = "glpat-secret_test_token"

        try:
            from mcp_gitlab_crunchtools.config import Config

            config = Config()
            assert "glpat-secret_test_token" not in repr(config)
            assert "glpat-secret_test_token" not in str(config)
            assert "***" in repr(config)
        finally:
            del os.environ["GITLAB_TOKEN"]

    def test_config_requires_token(self) -> None:
        """Config should require GITLAB_TOKEN."""
        import os

        from mcp_gitlab_crunchtools.config import Config
        from mcp_gitlab_crunchtools.errors import ConfigurationError

        token = os.environ.pop("GITLAB_TOKEN", None)

        try:
            import mcp_gitlab_crunchtools.config as config_module

            config_module._config = None

            with pytest.raises(ConfigurationError):
                Config()
        finally:
            if token:
                os.environ["GITLAB_TOKEN"] = token

    def test_config_default_url(self) -> None:
        """Config should default to gitlab.com."""
        import os

        os.environ["GITLAB_TOKEN"] = "glpat-test"
        os.environ.pop("GITLAB_URL", None)

        try:
            from mcp_gitlab_crunchtools.config import Config

            config = Config()
            assert config.api_base_url == "https://gitlab.com/api/v4"
            assert config.gitlab_url == "https://gitlab.com"
        finally:
            del os.environ["GITLAB_TOKEN"]

    def test_config_custom_url(self) -> None:
        """Config should accept a custom GitLab URL."""
        import os

        os.environ["GITLAB_TOKEN"] = "glpat-test"
        os.environ["GITLAB_URL"] = "https://gitlab.example.com"

        try:
            from mcp_gitlab_crunchtools.config import Config

            config = Config()
            assert config.api_base_url == "https://gitlab.example.com/api/v4"
        finally:
            del os.environ["GITLAB_TOKEN"]
            del os.environ["GITLAB_URL"]

    def test_config_strips_trailing_slash(self) -> None:
        """Config should strip trailing slash from URL."""
        import os

        os.environ["GITLAB_TOKEN"] = "glpat-test"
        os.environ["GITLAB_URL"] = "https://gitlab.example.com/"

        try:
            from mcp_gitlab_crunchtools.config import Config

            config = Config()
            assert config.api_base_url == "https://gitlab.example.com/api/v4"
        finally:
            del os.environ["GITLAB_TOKEN"]
            del os.environ["GITLAB_URL"]

    def test_config_rejects_http(self) -> None:
        """Config should reject non-HTTPS URLs for non-localhost."""
        import os

        from mcp_gitlab_crunchtools.config import Config
        from mcp_gitlab_crunchtools.errors import ConfigurationError

        os.environ["GITLAB_TOKEN"] = "glpat-test"
        os.environ["GITLAB_URL"] = "http://gitlab.example.com"

        try:
            with pytest.raises(ConfigurationError, match="HTTPS"):
                Config()
        finally:
            del os.environ["GITLAB_TOKEN"]
            del os.environ["GITLAB_URL"]

    def test_config_allows_localhost_http(self) -> None:
        """Config should allow HTTP for localhost."""
        import os

        os.environ["GITLAB_TOKEN"] = "glpat-test"
        os.environ["GITLAB_URL"] = "http://localhost:8080"

        try:
            from mcp_gitlab_crunchtools.config import Config

            config = Config()
            assert config.api_base_url == "http://localhost:8080/api/v4"
        finally:
            del os.environ["GITLAB_TOKEN"]
            del os.environ["GITLAB_URL"]
