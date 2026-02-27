"""Tests for MCP tools.

These tests verify tool behavior without making actual API calls.
Integration tests with a real GitLab account should be run separately.
"""

from unittest.mock import AsyncMock, patch

import httpx
import pytest


class TestToolRegistration:
    """Tests to verify all tools are properly registered."""

    def test_server_has_tools(self) -> None:
        """Server should have all expected tools registered."""
        from mcp_gitlab_crunchtools.server import mcp

        assert mcp is not None

    def test_imports(self) -> None:
        """All tool functions should be importable."""
        import mcp_gitlab_crunchtools.tools as tools_mod
        from mcp_gitlab_crunchtools.tools import __all__

        for name in __all__:
            func = getattr(tools_mod, name)
            assert callable(func), f"{name} is not callable"

    def test_tool_count(self) -> None:
        """Server should have exactly 61 tools registered."""
        from mcp_gitlab_crunchtools.tools import __all__

        assert len(__all__) == 61


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

    def test_config_ssl_verify_default(self) -> None:
        """Config should default to SSL verification enabled."""
        import os

        os.environ["GITLAB_TOKEN"] = "glpat-test"
        os.environ.pop("GITLAB_SSL_VERIFY", None)
        os.environ.pop("SSL_CERT_FILE", None)

        try:
            from mcp_gitlab_crunchtools.config import Config

            config = Config()
            assert config.ssl_verify is True
        finally:
            del os.environ["GITLAB_TOKEN"]

    def test_config_ssl_verify_disabled(self) -> None:
        """Config should allow disabling SSL verification."""
        import os

        os.environ["GITLAB_TOKEN"] = "glpat-test"
        os.environ["GITLAB_SSL_VERIFY"] = "false"

        try:
            from mcp_gitlab_crunchtools.config import Config

            config = Config()
            assert config.ssl_verify is False
        finally:
            del os.environ["GITLAB_TOKEN"]
            del os.environ["GITLAB_SSL_VERIFY"]

    def test_config_ssl_cert_file(self) -> None:
        """Config should use SSL_CERT_FILE when set."""
        import os

        os.environ["GITLAB_TOKEN"] = "glpat-test"
        os.environ["SSL_CERT_FILE"] = "/etc/pki/tls/certs/ca-bundle.crt"
        os.environ.pop("GITLAB_SSL_VERIFY", None)

        try:
            from mcp_gitlab_crunchtools.config import Config

            config = Config()
            assert config.ssl_verify == "/etc/pki/tls/certs/ca-bundle.crt"
        finally:
            del os.environ["GITLAB_TOKEN"]
            del os.environ["SSL_CERT_FILE"]




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


@pytest.fixture(autouse=True)
def _reset_client_singleton():
    """Reset the global client and config singletons between tests."""
    import mcp_gitlab_crunchtools.client as client_mod
    import mcp_gitlab_crunchtools.config as config_mod

    client_mod._client = None
    config_mod._config = None
    yield
    client_mod._client = None
    config_mod._config = None


def _patch_client(mock_response: httpx.Response):
    """Patch the httpx AsyncClient to return a mock response.

    Sets GITLAB_TOKEN so config initializes, then mocks the HTTP layer.
    """
    import os

    import mcp_gitlab_crunchtools.client as client_mod
    import mcp_gitlab_crunchtools.config as config_mod

    client_mod._client = None
    config_mod._config = None

    os.environ.setdefault("GITLAB_TOKEN", "glpat-test-mock-token")

    mock_http = AsyncMock(spec=httpx.AsyncClient)
    mock_http.request = AsyncMock(return_value=mock_response)

    return patch.object(
        httpx, "AsyncClient", return_value=mock_http,
    )




class TestPipelineTools:
    """Tests for pipeline tools with mocked API responses."""

    @pytest.mark.asyncio
    async def test_list_pipelines(self) -> None:
        """list_pipelines should return items with pagination."""
        from mcp_gitlab_crunchtools.tools import list_pipelines

        resp = _mock_response(
            json_data=[
                {"id": 100, "status": "success", "ref": "main"},
                {"id": 99, "status": "failed", "ref": "main"},
            ],
            headers={"x-total": "2", "x-page": "1", "x-per-page": "20"},
        )

        with _patch_client(resp):
            result = await list_pipelines(project_id="12345")

        assert len(result["items"]) == 2
        assert result["items"][0]["id"] == 100
        assert result["pagination"]["total"] == 2

    @pytest.mark.asyncio
    async def test_get_pipeline(self) -> None:
        """get_pipeline should return pipeline details."""
        from mcp_gitlab_crunchtools.tools import get_pipeline

        resp = _mock_response(
            json_data={"id": 100, "status": "success", "ref": "main", "duration": 120},
        )

        with _patch_client(resp):
            result = await get_pipeline(project_id="12345", pipeline_id=100)

        assert result["id"] == 100
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_create_pipeline(self) -> None:
        """create_pipeline should POST and return new pipeline."""
        from mcp_gitlab_crunchtools.tools import create_pipeline

        resp = _mock_response(
            status_code=201,
            json_data={"id": 101, "status": "created", "ref": "main"},
        )

        with _patch_client(resp):
            result = await create_pipeline(project_id="12345", ref="main")

        assert result["id"] == 101
        assert result["status"] == "created"

    @pytest.mark.asyncio
    async def test_retry_pipeline(self) -> None:
        """retry_pipeline should POST and return retried pipeline."""
        from mcp_gitlab_crunchtools.tools import retry_pipeline

        resp = _mock_response(
            json_data={"id": 100, "status": "running", "ref": "main"},
        )

        with _patch_client(resp):
            result = await retry_pipeline(project_id="12345", pipeline_id=100)

        assert result["status"] == "running"

    @pytest.mark.asyncio
    async def test_cancel_pipeline(self) -> None:
        """cancel_pipeline should POST and return canceled pipeline."""
        from mcp_gitlab_crunchtools.tools import cancel_pipeline

        resp = _mock_response(
            json_data={"id": 100, "status": "canceled", "ref": "main"},
        )

        with _patch_client(resp):
            result = await cancel_pipeline(project_id="12345", pipeline_id=100)

        assert result["status"] == "canceled"

    @pytest.mark.asyncio
    async def test_delete_pipeline(self) -> None:
        """delete_pipeline should handle 204 No Content."""
        from mcp_gitlab_crunchtools.tools import delete_pipeline

        resp = _mock_response(status_code=204, text="", content_type="text/plain")

        with _patch_client(resp):
            result = await delete_pipeline(project_id="12345", pipeline_id=100)

        assert result["status"] == "deleted"


class TestJobTools:
    """Tests for job tools with mocked API responses."""

    @pytest.mark.asyncio
    async def test_list_pipeline_jobs(self) -> None:
        """list_pipeline_jobs should return jobs with stage info."""
        from mcp_gitlab_crunchtools.tools import list_pipeline_jobs

        resp = _mock_response(
            json_data=[
                {"id": 500, "name": "test", "stage": "test", "status": "success"},
                {"id": 501, "name": "build", "stage": "build", "status": "success"},
            ],
            headers={"x-total": "2", "x-page": "1"},
        )

        with _patch_client(resp):
            result = await list_pipeline_jobs(
                project_id="12345", pipeline_id=100
            )

        assert len(result["items"]) == 2
        assert result["items"][0]["stage"] == "test"
        assert result["items"][1]["stage"] == "build"

    @pytest.mark.asyncio
    async def test_get_job_log(self) -> None:
        """get_job_log should return plain text content."""
        from mcp_gitlab_crunchtools.tools import get_job_log

        resp = _mock_response(
            text="Running tests...\nAll 42 tests passed.",
            content_type="text/plain",
        )

        with _patch_client(resp):
            result = await get_job_log(project_id="12345", job_id=500)

        assert "42 tests passed" in result["content"]

    @pytest.mark.asyncio
    async def test_retry_job(self) -> None:
        """retry_job should POST and return retried job."""
        from mcp_gitlab_crunchtools.tools import retry_job

        resp = _mock_response(
            json_data={"id": 502, "name": "test", "status": "pending"},
        )

        with _patch_client(resp):
            result = await retry_job(project_id="12345", job_id=500)

        assert result["status"] == "pending"

    @pytest.mark.asyncio
    async def test_cancel_job(self) -> None:
        """cancel_job should POST and return canceled job."""
        from mcp_gitlab_crunchtools.tools import cancel_job

        resp = _mock_response(
            json_data={"id": 500, "name": "build", "status": "canceled"},
        )

        with _patch_client(resp):
            result = await cancel_job(project_id="12345", job_id=500)

        assert result["status"] == "canceled"

    @pytest.mark.asyncio
    async def test_delete_job(self) -> None:
        """delete_job should POST erase and return erased job."""
        from mcp_gitlab_crunchtools.tools import delete_job

        resp = _mock_response(
            json_data={"id": 500, "name": "test", "status": "success", "artifacts": []},
        )

        with _patch_client(resp):
            result = await delete_job(project_id="12345", job_id=500)

        assert result["id"] == 500




class TestProjectTools:
    """Tests for project tools with mocked API responses."""

    @pytest.mark.asyncio
    async def test_list_projects(self) -> None:
        """list_projects should return paginated project list."""
        from mcp_gitlab_crunchtools.tools import list_projects

        resp = _mock_response(
            json_data=[{"id": 1, "name": "project-a"}, {"id": 2, "name": "project-b"}],
            headers={"x-total": "2", "x-page": "1", "x-per-page": "20"},
        )

        with _patch_client(resp):
            result = await list_projects()

        assert len(result["items"]) == 2

    @pytest.mark.asyncio
    async def test_get_project(self) -> None:
        """get_project should return project details."""
        from mcp_gitlab_crunchtools.tools import get_project

        resp = _mock_response(
            json_data={"id": 1, "name": "project-a", "default_branch": "main"},
        )

        with _patch_client(resp):
            result = await get_project(project_id="1")

        assert result["name"] == "project-a"

    @pytest.mark.asyncio
    async def test_get_project_by_path(self) -> None:
        """get_project should URL-encode path-style project IDs."""
        from mcp_gitlab_crunchtools.tools import get_project

        resp = _mock_response(
            json_data={"id": 1, "name": "my-project", "path_with_namespace": "group/my-project"},
        )

        with _patch_client(resp) as mock_client:
            await get_project(project_id="group/my-project")
            call_args = mock_client.return_value.request.call_args
            assert "group%2Fmy-project" in call_args.kwargs.get("url", "")

    @pytest.mark.asyncio
    async def test_list_project_commits(self) -> None:
        """list_project_commits should return commit list."""
        from mcp_gitlab_crunchtools.tools import list_project_commits

        resp = _mock_response(
            json_data=[
                {"id": "abc123", "title": "Fix bug", "author_name": "Alice"},
                {"id": "def456", "title": "Add feature", "author_name": "Bob"},
            ],
            headers={"x-total": "2"},
        )

        with _patch_client(resp):
            result = await list_project_commits(project_id="1")

        assert len(result["items"]) == 2
        assert result["items"][0]["title"] == "Fix bug"


class TestIssueTools:
    """Tests for issue tools with mocked API responses."""

    @pytest.mark.asyncio
    async def test_create_issue(self) -> None:
        """create_issue should POST and return created issue."""
        from mcp_gitlab_crunchtools.tools import create_issue

        resp = _mock_response(
            status_code=201,
            json_data={"id": 10, "iid": 1, "title": "Bug report", "state": "opened"},
        )

        with _patch_client(resp):
            result = await create_issue(project_id="1", title="Bug report")

        assert result["title"] == "Bug report"
        assert result["state"] == "opened"

    @pytest.mark.asyncio
    async def test_update_issue_close(self) -> None:
        """update_issue should handle state transitions."""
        from mcp_gitlab_crunchtools.tools import update_issue

        resp = _mock_response(
            json_data={"id": 10, "iid": 1, "title": "Bug report", "state": "closed"},
        )

        with _patch_client(resp):
            result = await update_issue(
                project_id="1", issue_iid=1, state_event="close"
            )

        assert result["state"] == "closed"

    @pytest.mark.asyncio
    async def test_create_issue_note(self) -> None:
        """create_issue_note should POST and return note."""
        from mcp_gitlab_crunchtools.tools import create_issue_note

        resp = _mock_response(
            status_code=201,
            json_data={"id": 50, "body": "Fixed in v2.0", "noteable_iid": 1},
        )

        with _patch_client(resp):
            result = await create_issue_note(
                project_id="1", issue_iid=1, body="Fixed in v2.0"
            )

        assert result["body"] == "Fixed in v2.0"


class TestMergeRequestTools:
    """Tests for merge request tools with mocked API responses."""

    @pytest.mark.asyncio
    async def test_create_merge_request(self) -> None:
        """create_merge_request should POST and return created MR."""
        from mcp_gitlab_crunchtools.tools import create_merge_request

        resp = _mock_response(
            status_code=201,
            json_data={
                "id": 20, "iid": 5, "title": "Add auth",
                "source_branch": "feature", "target_branch": "main", "state": "opened",
            },
        )

        with _patch_client(resp):
            result = await create_merge_request(
                project_id="1",
                source_branch="feature",
                target_branch="main",
                title="Add auth",
            )

        assert result["iid"] == 5
        assert result["source_branch"] == "feature"

    @pytest.mark.asyncio
    async def test_get_mr_changes(self) -> None:
        """get_mr_changes should return diff data."""
        from mcp_gitlab_crunchtools.tools import get_mr_changes

        resp = _mock_response(
            json_data={
                "id": 20, "iid": 5,
                "changes": [{"old_path": "a.py", "new_path": "a.py", "diff": "@@ -1 +1 @@"}],
            },
        )

        with _patch_client(resp):
            result = await get_mr_changes(project_id="1", merge_request_iid=5)

        assert len(result["changes"]) == 1


class TestSearchTools:
    """Tests for search tools with mocked API responses."""

    @pytest.mark.asyncio
    async def test_search_global(self) -> None:
        """search_global should return search results."""
        from mcp_gitlab_crunchtools.tools import search_global

        resp = _mock_response(
            json_data=[{"id": 1, "name": "auth-service"}],
            headers={"x-total": "1"},
        )

        with _patch_client(resp):
            result = await search_global(search="auth", scope="projects")

        assert len(result["items"]) == 1
        assert result["items"][0]["name"] == "auth-service"




class TestClientErrorHandling:
    """Tests for HTTP client error responses."""

    @pytest.mark.asyncio
    async def test_401_raises_permission_denied(self) -> None:
        """401 response should raise PermissionDeniedError."""
        from mcp_gitlab_crunchtools.errors import PermissionDeniedError
        from mcp_gitlab_crunchtools.tools import list_projects

        resp = _mock_response(
            status_code=401,
            json_data={"message": "401 Unauthorized"},
        )

        with _patch_client(resp), pytest.raises(PermissionDeniedError):
            await list_projects()

    @pytest.mark.asyncio
    async def test_404_raises_not_found(self) -> None:
        """404 response should raise ProjectNotFoundError."""
        from mcp_gitlab_crunchtools.errors import ProjectNotFoundError
        from mcp_gitlab_crunchtools.tools import get_project

        resp = _mock_response(
            status_code=404,
            json_data={"message": "404 Project Not Found"},
        )

        with _patch_client(resp), pytest.raises(ProjectNotFoundError):
            await get_project(project_id="99999")

    @pytest.mark.asyncio
    async def test_429_raises_rate_limit(self) -> None:
        """429 response should raise RateLimitError."""
        from mcp_gitlab_crunchtools.errors import RateLimitError
        from mcp_gitlab_crunchtools.tools import list_projects

        resp = _mock_response(
            status_code=429,
            json_data={"message": "429 Too Many Requests"},
            headers={"retry-after": "60"},
        )

        with _patch_client(resp), pytest.raises(RateLimitError):
            await list_projects()

    @pytest.mark.asyncio
    async def test_204_returns_deleted_status(self) -> None:
        """204 No Content should return {status: deleted}."""
        from mcp_gitlab_crunchtools.tools import delete_pipeline

        resp = _mock_response(status_code=204, text="", content_type="text/plain")

        with _patch_client(resp):
            result = await delete_pipeline(project_id="1", pipeline_id=100)

        assert result == {"status": "deleted"}




class TestFileTools:
    """Tests for file tools with mocked API responses."""

    @pytest.mark.asyncio
    async def test_list_repository_tree(self) -> None:
        """list_repository_tree should return tree entries."""
        from mcp_gitlab_crunchtools.tools import list_repository_tree

        resp = _mock_response(
            json_data=[
                {"id": "abc", "name": "src", "type": "tree", "path": "src"},
                {"id": "def", "name": "README.md", "type": "blob", "path": "README.md"},
            ],
            headers={"x-total": "2"},
        )

        with _patch_client(resp):
            result = await list_repository_tree(project_id="1")

        assert len(result["items"]) == 2
        assert result["items"][0]["type"] == "tree"
        assert result["items"][1]["type"] == "blob"

    @pytest.mark.asyncio
    async def test_get_file(self) -> None:
        """get_file should return file metadata and content."""
        from mcp_gitlab_crunchtools.tools import get_file

        resp = _mock_response(
            json_data={
                "file_name": "README.md",
                "file_path": "README.md",
                "size": 1024,
                "encoding": "base64",
                "content": "IyBIZWxsbw==",
                "ref": "main",
            },
        )

        with _patch_client(resp):
            result = await get_file(project_id="1", file_path="README.md")

        assert result["file_name"] == "README.md"
        assert result["content"] == "IyBIZWxsbw=="

    @pytest.mark.asyncio
    async def test_create_file(self) -> None:
        """create_file should POST and return file metadata."""
        from mcp_gitlab_crunchtools.tools import create_file

        resp = _mock_response(
            status_code=201,
            json_data={"file_path": "new_file.py", "branch": "main"},
        )

        with _patch_client(resp):
            result = await create_file(
                project_id="1", file_path="new_file.py", branch="main",
                content="print('hello')", commit_message="Add new file",
            )

        assert result["file_path"] == "new_file.py"

    @pytest.mark.asyncio
    async def test_update_file(self) -> None:
        """update_file should PUT and return file metadata."""
        from mcp_gitlab_crunchtools.tools import update_file

        resp = _mock_response(
            json_data={"file_path": "README.md", "branch": "main"},
        )

        with _patch_client(resp):
            result = await update_file(
                project_id="1", file_path="README.md", branch="main",
                content="# Updated", commit_message="Update readme",
            )

        assert result["file_path"] == "README.md"




class TestBranchTools:
    """Tests for branch tools with mocked API responses."""

    @pytest.mark.asyncio
    async def test_create_branch(self) -> None:
        """create_branch should POST and return branch details."""
        from mcp_gitlab_crunchtools.tools import create_branch

        resp = _mock_response(
            status_code=201,
            json_data={"name": "feature/auth", "merged": False, "protected": False},
        )

        with _patch_client(resp):
            result = await create_branch(
                project_id="1", branch="feature/auth", ref="main",
            )

        assert result["name"] == "feature/auth"

    @pytest.mark.asyncio
    async def test_delete_branch(self) -> None:
        """delete_branch should handle 204 No Content."""
        from mcp_gitlab_crunchtools.tools import delete_branch

        resp = _mock_response(status_code=204, text="", content_type="text/plain")

        with _patch_client(resp):
            result = await delete_branch(project_id="1", branch="feature/old")

        assert result["status"] == "deleted"

    @pytest.mark.asyncio
    async def test_compare_branches(self) -> None:
        """compare_branches should return diff data."""
        from mcp_gitlab_crunchtools.tools import compare_branches

        resp = _mock_response(
            json_data={
                "commits": [{"id": "abc123", "title": "Fix bug"}],
                "diffs": [{"old_path": "a.py", "new_path": "a.py"}],
                "compare_timeout": False,
            },
        )

        with _patch_client(resp):
            result = await compare_branches(
                project_id="1", from_ref="main", to_ref="feature",
            )

        assert len(result["commits"]) == 1
        assert len(result["diffs"]) == 1




class TestLabelTools:
    """Tests for label tools with mocked API responses."""

    @pytest.mark.asyncio
    async def test_list_labels(self) -> None:
        """list_labels should return label list."""
        from mcp_gitlab_crunchtools.tools import list_labels

        resp = _mock_response(
            json_data=[
                {"id": 1, "name": "bug", "color": "#FF0000"},
                {"id": 2, "name": "feature", "color": "#00FF00"},
            ],
            headers={"x-total": "2"},
        )

        with _patch_client(resp):
            result = await list_labels(project_id="1")

        assert len(result["items"]) == 2

    @pytest.mark.asyncio
    async def test_create_label(self) -> None:
        """create_label should POST and return label."""
        from mcp_gitlab_crunchtools.tools import create_label

        resp = _mock_response(
            status_code=201,
            json_data={"id": 3, "name": "urgent", "color": "#FF0000"},
        )

        with _patch_client(resp):
            result = await create_label(
                project_id="1", name="urgent", color="#FF0000",
            )

        assert result["name"] == "urgent"

    @pytest.mark.asyncio
    async def test_update_label(self) -> None:
        """update_label should PUT and return updated label."""
        from mcp_gitlab_crunchtools.tools import update_label

        resp = _mock_response(
            json_data={"id": 3, "name": "critical", "color": "#CC0000"},
        )

        with _patch_client(resp):
            result = await update_label(
                project_id="1", label_id=3, new_name="critical",
            )

        assert result["name"] == "critical"

    @pytest.mark.asyncio
    async def test_delete_label(self) -> None:
        """delete_label should handle 204 No Content."""
        from mcp_gitlab_crunchtools.tools import delete_label

        resp = _mock_response(status_code=204, text="", content_type="text/plain")

        with _patch_client(resp):
            result = await delete_label(project_id="1", label_id=3)

        assert result["status"] == "deleted"




class TestUserTools:
    """Tests for user tools with mocked API responses."""

    @pytest.mark.asyncio
    async def test_get_current_user(self) -> None:
        """get_current_user should return authenticated user."""
        from mcp_gitlab_crunchtools.tools import get_current_user

        resp = _mock_response(
            json_data={"id": 42, "username": "smccarty", "name": "Scott McCarty"},
        )

        with _patch_client(resp):
            result = await get_current_user()

        assert result["username"] == "smccarty"

    @pytest.mark.asyncio
    async def test_list_users(self) -> None:
        """list_users should return user list."""
        from mcp_gitlab_crunchtools.tools import list_users

        resp = _mock_response(
            json_data=[
                {"id": 1, "username": "alice", "state": "active"},
                {"id": 2, "username": "bob", "state": "active"},
            ],
            headers={"x-total": "2"},
        )

        with _patch_client(resp):
            result = await list_users(search="a")

        assert len(result["items"]) == 2

    @pytest.mark.asyncio
    async def test_get_user(self) -> None:
        """get_user should return user details."""
        from mcp_gitlab_crunchtools.tools import get_user

        resp = _mock_response(
            json_data={"id": 42, "username": "smccarty", "state": "active"},
        )

        with _patch_client(resp):
            result = await get_user(user_id=42)

        assert result["id"] == 42




class TestReleaseTools:
    """Tests for release tools with mocked API responses."""

    @pytest.mark.asyncio
    async def test_list_releases(self) -> None:
        """list_releases should return release list."""
        from mcp_gitlab_crunchtools.tools import list_releases

        resp = _mock_response(
            json_data=[
                {"tag_name": "v1.0.0", "name": "v1.0.0"},
                {"tag_name": "v0.9.0", "name": "v0.9.0"},
            ],
            headers={"x-total": "2"},
        )

        with _patch_client(resp):
            result = await list_releases(project_id="1")

        assert len(result["items"]) == 2
        assert result["items"][0]["tag_name"] == "v1.0.0"

    @pytest.mark.asyncio
    async def test_get_release(self) -> None:
        """get_release should return release details."""
        from mcp_gitlab_crunchtools.tools import get_release

        resp = _mock_response(
            json_data={
                "tag_name": "v1.0.0", "name": "v1.0.0",
                "description": "First release",
            },
        )

        with _patch_client(resp):
            result = await get_release(project_id="1", tag_name="v1.0.0")

        assert result["description"] == "First release"

    @pytest.mark.asyncio
    async def test_create_release(self) -> None:
        """create_release should POST and return release."""
        from mcp_gitlab_crunchtools.tools import create_release

        resp = _mock_response(
            status_code=201,
            json_data={"tag_name": "v2.0.0", "name": "v2.0.0"},
        )

        with _patch_client(resp):
            result = await create_release(
                project_id="1", tag_name="v2.0.0", name="v2.0.0",
                description="Major release", ref="main",
            )

        assert result["tag_name"] == "v2.0.0"




class TestMilestoneTools:
    """Tests for milestone tools with mocked API responses."""

    @pytest.mark.asyncio
    async def test_list_milestones(self) -> None:
        """list_milestones should return milestone list."""
        from mcp_gitlab_crunchtools.tools import list_milestones

        resp = _mock_response(
            json_data=[
                {"id": 1, "title": "Sprint 1", "state": "active"},
                {"id": 2, "title": "Sprint 2", "state": "active"},
            ],
            headers={"x-total": "2"},
        )

        with _patch_client(resp):
            result = await list_milestones(project_id="1")

        assert len(result["items"]) == 2

    @pytest.mark.asyncio
    async def test_create_milestone(self) -> None:
        """create_milestone should POST and return milestone."""
        from mcp_gitlab_crunchtools.tools import create_milestone

        resp = _mock_response(
            status_code=201,
            json_data={
                "id": 3, "title": "Sprint 3", "state": "active",
                "due_date": "2026-03-15",
            },
        )

        with _patch_client(resp):
            result = await create_milestone(
                project_id="1", title="Sprint 3", due_date="2026-03-15",
            )

        assert result["title"] == "Sprint 3"

    @pytest.mark.asyncio
    async def test_update_milestone(self) -> None:
        """update_milestone should PUT and return updated milestone."""
        from mcp_gitlab_crunchtools.tools import update_milestone

        resp = _mock_response(
            json_data={"id": 1, "title": "Sprint 1", "state": "closed"},
        )

        with _patch_client(resp):
            result = await update_milestone(
                project_id="1", milestone_id=1, state_event="close",
            )

        assert result["state"] == "closed"




class TestMRDiscussionTools:
    """Tests for MR discussion tools with mocked API responses."""

    @pytest.mark.asyncio
    async def test_list_mr_discussions(self) -> None:
        """list_mr_discussions should return threaded discussions."""
        from mcp_gitlab_crunchtools.tools import list_mr_discussions

        resp = _mock_response(
            json_data=[
                {
                    "id": "disc1",
                    "notes": [
                        {"id": 100, "body": "Looks good", "author": {"username": "alice"}},
                    ],
                },
                {
                    "id": "disc2",
                    "notes": [
                        {"id": 101, "body": "Needs fix on line 42", "author": {"username": "bob"}},
                        {"id": 102, "body": "Fixed", "author": {"username": "charlie"}},
                    ],
                },
            ],
            headers={"x-total": "2"},
        )

        with _patch_client(resp):
            result = await list_mr_discussions(project_id="1", merge_request_iid=5)

        assert len(result["items"]) == 2
        assert len(result["items"][1]["notes"]) == 2

    @pytest.mark.asyncio
    async def test_create_mr_discussion(self) -> None:
        """create_mr_discussion should POST and return discussion."""
        from mcp_gitlab_crunchtools.tools import create_mr_discussion

        resp = _mock_response(
            status_code=201,
            json_data={
                "id": "disc3",
                "notes": [{"id": 200, "body": "New thread"}],
            },
        )

        with _patch_client(resp):
            result = await create_mr_discussion(
                project_id="1", merge_request_iid=5, body="New thread",
            )

        assert result["id"] == "disc3"




class TestWikiTools:
    """Tests for wiki tools with mocked API responses."""

    @pytest.mark.asyncio
    async def test_list_wiki_pages(self) -> None:
        """list_wiki_pages should return page list."""
        from mcp_gitlab_crunchtools.tools import list_wiki_pages

        resp = _mock_response(
            json_data=[
                {"slug": "home", "title": "Home"},
                {"slug": "getting-started", "title": "Getting Started"},
            ],
            headers={"x-total": "2"},
        )

        with _patch_client(resp):
            result = await list_wiki_pages(project_id="1")

        assert len(result["items"]) == 2

    @pytest.mark.asyncio
    async def test_get_wiki_page(self) -> None:
        """get_wiki_page should return page with content."""
        from mcp_gitlab_crunchtools.tools import get_wiki_page

        resp = _mock_response(
            json_data={
                "slug": "home", "title": "Home",
                "content": "# Welcome", "format": "markdown",
            },
        )

        with _patch_client(resp):
            result = await get_wiki_page(project_id="1", slug="home")

        assert result["content"] == "# Welcome"

    @pytest.mark.asyncio
    async def test_create_wiki_page(self) -> None:
        """create_wiki_page should POST and return page."""
        from mcp_gitlab_crunchtools.tools import create_wiki_page

        resp = _mock_response(
            status_code=201,
            json_data={"slug": "new-page", "title": "New Page"},
        )

        with _patch_client(resp):
            result = await create_wiki_page(
                project_id="1", title="New Page", content="# New",
            )

        assert result["slug"] == "new-page"




class TestSnippetTools:
    """Tests for snippet tools with mocked API responses."""

    @pytest.mark.asyncio
    async def test_list_snippets(self) -> None:
        """list_snippets should return snippet list."""
        from mcp_gitlab_crunchtools.tools import list_snippets

        resp = _mock_response(
            json_data=[
                {"id": 1, "title": "Config example", "visibility": "private"},
            ],
            headers={"x-total": "1"},
        )

        with _patch_client(resp):
            result = await list_snippets(project_id="1")

        assert len(result["items"]) == 1

    @pytest.mark.asyncio
    async def test_create_snippet(self) -> None:
        """create_snippet should POST and return snippet."""
        from mcp_gitlab_crunchtools.tools import create_snippet

        resp = _mock_response(
            status_code=201,
            json_data={
                "id": 2, "title": "Helper script",
                "file_name": "helper.py", "visibility": "internal",
            },
        )

        with _patch_client(resp):
            result = await create_snippet(
                project_id="1", title="Helper script",
                file_name="helper.py", content="print('hi')",
                visibility="internal",
            )

        assert result["title"] == "Helper script"
