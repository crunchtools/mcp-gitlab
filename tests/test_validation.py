"""Tests for input validation."""

import pytest
from pydantic import ValidationError

from mcp_gitlab_crunchtools.models import (
    CreateIssueInput,
    CreateMergeRequestInput,
    UpdateIssueInput,
    UpdateMergeRequestInput,
    encode_group_id,
    encode_project_id,
)


class TestProjectIdEncoding:
    """Tests for project ID validation and encoding."""

    def test_numeric_id(self) -> None:
        """Numeric ID should pass through."""
        assert encode_project_id("12345") == "12345"

    def test_simple_path(self) -> None:
        """Simple namespace/project path should be URL-encoded."""
        result = encode_project_id("group/project")
        assert result == "group%2Fproject"

    def test_nested_path(self) -> None:
        """Nested group path should be URL-encoded."""
        result = encode_project_id("group/subgroup/project")
        assert result == "group%2Fsubgroup%2Fproject"

    def test_path_with_hyphens(self) -> None:
        """Path with hyphens should be valid."""
        result = encode_project_id("my-group/my-project")
        assert result == "my-group%2Fmy-project"

    def test_path_with_dots(self) -> None:
        """Path with dots should be valid."""
        result = encode_project_id("group/project.name")
        assert result == "group%2Fproject.name"

    def test_empty_string(self) -> None:
        """Empty string should fail."""
        with pytest.raises(ValueError, match="must not be empty"):
            encode_project_id("")

    def test_whitespace_only(self) -> None:
        """Whitespace-only string should fail."""
        with pytest.raises(ValueError, match="must not be empty"):
            encode_project_id("   ")

    def test_invalid_characters(self) -> None:
        """Special characters should fail."""
        with pytest.raises(ValueError, match="alphanumeric"):
            encode_project_id("group/project; rm -rf /")

    def test_injection_attempt(self) -> None:
        """Injection attempts with special chars should fail."""
        with pytest.raises(ValueError, match="alphanumeric"):
            encode_project_id("group/project$(whoami)")


class TestGroupIdEncoding:
    """Tests for group ID validation and encoding."""

    def test_numeric_id(self) -> None:
        """Numeric ID should pass through."""
        assert encode_group_id("999") == "999"

    def test_simple_path(self) -> None:
        """Simple group path should be URL-encoded."""
        result = encode_group_id("my-group")
        assert result == "my-group"

    def test_nested_path(self) -> None:
        """Nested group path should be URL-encoded."""
        result = encode_group_id("parent/child")
        assert result == "parent%2Fchild"

    def test_empty_string(self) -> None:
        """Empty string should fail."""
        with pytest.raises(ValueError, match="must not be empty"):
            encode_group_id("")

    def test_invalid_characters(self) -> None:
        """Special characters should fail."""
        with pytest.raises(ValueError, match="alphanumeric"):
            encode_group_id("group<script>")


class TestCreateIssueInput:
    """Tests for CreateIssueInput model."""

    def test_valid_minimal(self) -> None:
        """Minimal valid input should pass."""
        issue = CreateIssueInput(title="Fix the bug")
        assert issue.title == "Fix the bug"
        assert issue.description is None
        assert issue.confidential is False

    def test_valid_full(self) -> None:
        """Full valid input should pass."""
        issue = CreateIssueInput(
            title="Fix the bug",
            description="This is a detailed description",
            labels="bug,urgent",
            assignee_ids=[1, 2],
            milestone_id=5,
            confidential=True,
        )
        assert issue.title == "Fix the bug"
        assert issue.labels == "bug,urgent"
        assert issue.assignee_ids == [1, 2]
        assert issue.confidential is True

    def test_title_too_long(self) -> None:
        """Title exceeding max length should fail."""
        with pytest.raises(ValidationError):
            CreateIssueInput(title="a" * 501)

    def test_empty_title(self) -> None:
        """Empty title should fail."""
        with pytest.raises(ValidationError):
            CreateIssueInput(title="")

    def test_extra_fields_rejected(self) -> None:
        """Extra fields should be rejected."""
        with pytest.raises(ValidationError):
            CreateIssueInput(title="Test", extra_field="value")  # type: ignore[call-arg]


class TestUpdateIssueInput:
    """Tests for UpdateIssueInput model."""

    def test_partial_update(self) -> None:
        """Partial update with only some fields should pass."""
        update = UpdateIssueInput(title="New title")
        assert update.title == "New title"
        assert update.description is None
        assert update.state_event is None

    def test_valid_state_event_close(self) -> None:
        """Close state event should pass."""
        update = UpdateIssueInput(state_event="close")
        assert update.state_event == "close"

    def test_valid_state_event_reopen(self) -> None:
        """Reopen state event should pass."""
        update = UpdateIssueInput(state_event="reopen")
        assert update.state_event == "reopen"

    def test_invalid_state_event(self) -> None:
        """Invalid state event should fail."""
        with pytest.raises(ValidationError, match="state_event"):
            UpdateIssueInput(state_event="invalid")

    def test_all_fields_none(self) -> None:
        """All fields None should be valid."""
        update = UpdateIssueInput()
        assert update.title is None
        assert update.state_event is None


class TestCreateMergeRequestInput:
    """Tests for CreateMergeRequestInput model."""

    def test_valid_minimal(self) -> None:
        """Minimal valid input should pass."""
        mr = CreateMergeRequestInput(
            source_branch="feature",
            target_branch="main",
            title="Add feature",
        )
        assert mr.source_branch == "feature"
        assert mr.target_branch == "main"
        assert mr.title == "Add feature"
        assert mr.remove_source_branch is False

    def test_valid_full(self) -> None:
        """Full valid input should pass."""
        mr = CreateMergeRequestInput(
            source_branch="feature/auth",
            target_branch="main",
            title="Implement authentication",
            description="## Summary\nAdded OAuth2 support",
            labels="feature,auth",
            assignee_ids=[1],
            reviewer_ids=[2, 3],
            milestone_id=10,
            remove_source_branch=True,
        )
        assert mr.reviewer_ids == [2, 3]
        assert mr.remove_source_branch is True

    def test_empty_source_branch(self) -> None:
        """Empty source branch should fail."""
        with pytest.raises(ValidationError):
            CreateMergeRequestInput(
                source_branch="",
                target_branch="main",
                title="Test",
            )

    def test_title_too_long(self) -> None:
        """Title exceeding max length should fail."""
        with pytest.raises(ValidationError):
            CreateMergeRequestInput(
                source_branch="feature",
                target_branch="main",
                title="a" * 501,
            )


class TestUpdateMergeRequestInput:
    """Tests for UpdateMergeRequestInput model."""

    def test_partial_update(self) -> None:
        """Partial update should pass."""
        update = UpdateMergeRequestInput(title="Updated title")
        assert update.title == "Updated title"
        assert update.state_event is None

    def test_valid_state_event(self) -> None:
        """Valid state event should pass."""
        update = UpdateMergeRequestInput(state_event="close")
        assert update.state_event == "close"

    def test_invalid_state_event(self) -> None:
        """Invalid state event should fail."""
        with pytest.raises(ValidationError, match="state_event"):
            UpdateMergeRequestInput(state_event="merge")
