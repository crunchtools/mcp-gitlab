"""Pydantic models for input validation.

All tool inputs are validated through these models to prevent injection attacks
and ensure data integrity before making API calls.
"""

import re
from urllib.parse import quote

from pydantic import BaseModel, ConfigDict, Field, field_validator

PROJECT_ID_NUMERIC = re.compile(r"^\d+$")
PROJECT_PATH_PATTERN = re.compile(r"^[a-zA-Z0-9\-_./]+$")

SEARCH_SCOPES = frozenset({
    "projects", "issues", "merge_requests", "milestones",
    "snippet_titles", "wiki_blobs", "commits", "blobs", "notes", "users",
})

PROJECT_VISIBILITIES = frozenset({"public", "internal", "private"})

MR_STATES = frozenset({"opened", "closed", "merged", "all"})

ISSUE_STATES = frozenset({"opened", "closed", "all"})

PIPELINE_STATUSES = frozenset({
    "created", "waiting_for_resource", "preparing", "pending",
    "running", "success", "failed", "canceled", "skipped", "manual", "scheduled",
})

MAX_PROJECT_NAME_LENGTH = 255
MAX_TITLE_LENGTH = 500
MAX_DESCRIPTION_LENGTH = 50000
MAX_LABELS_LENGTH = 1000
MAX_BRANCH_LENGTH = 255
MAX_ASSIGNEES = 10


def encode_project_id(project_id: str) -> str:
    """Validate and encode a project identifier for URL use.

    GitLab accepts either numeric IDs or URL-encoded namespace/project paths.

    Args:
        project_id: Numeric ID (e.g., "12345") or path (e.g., "group/project")

    Returns:
        URL-safe project identifier

    Raises:
        ValueError: If the project_id format is invalid
    """
    if not project_id or not project_id.strip():
        raise ValueError("project_id must not be empty")

    project_id = project_id.strip()

    if PROJECT_ID_NUMERIC.match(project_id):
        return project_id

    if not PROJECT_PATH_PATTERN.match(project_id):
        raise ValueError(
            "project_id must be a numeric ID or a path like 'group/project' "
            "(alphanumeric, hyphens, underscores, dots, and slashes only)"
        )

    return quote(project_id, safe="")


def encode_group_id(group_id: str) -> str:
    """Validate and encode a group identifier for URL use.

    Args:
        group_id: Numeric ID or URL-encoded group path

    Returns:
        URL-safe group identifier

    Raises:
        ValueError: If the group_id format is invalid
    """
    if not group_id or not group_id.strip():
        raise ValueError("group_id must not be empty")

    group_id = group_id.strip()

    if PROJECT_ID_NUMERIC.match(group_id):
        return group_id

    if not PROJECT_PATH_PATTERN.match(group_id):
        raise ValueError(
            "group_id must be a numeric ID or a path like 'group/subgroup' "
            "(alphanumeric, hyphens, underscores, dots, and slashes only)"
        )

    return quote(group_id, safe="")


class CreateIssueInput(BaseModel):
    """Validated input for issue creation."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(
        ..., min_length=1, max_length=MAX_TITLE_LENGTH, description="Issue title"
    )
    description: str | None = Field(
        default=None, max_length=MAX_DESCRIPTION_LENGTH, description="Issue description (Markdown)"
    )
    labels: str | None = Field(
        default=None, max_length=MAX_LABELS_LENGTH, description="Comma-separated label names"
    )
    assignee_ids: list[int] | None = Field(
        default=None, max_length=MAX_ASSIGNEES, description="User IDs to assign"
    )
    milestone_id: int | None = Field(
        default=None, description="Milestone ID"
    )
    confidential: bool = Field(
        default=False, description="Whether the issue is confidential"
    )


class UpdateIssueInput(BaseModel):
    """Validated input for issue updates."""

    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(
        default=None, min_length=1, max_length=MAX_TITLE_LENGTH, description="Issue title"
    )
    description: str | None = Field(
        default=None, max_length=MAX_DESCRIPTION_LENGTH, description="Issue description (Markdown)"
    )
    labels: str | None = Field(
        default=None, max_length=MAX_LABELS_LENGTH, description="Comma-separated label names"
    )
    state_event: str | None = Field(
        default=None, description="State transition: close or reopen"
    )
    assignee_ids: list[int] | None = Field(
        default=None, max_length=MAX_ASSIGNEES, description="User IDs to assign"
    )
    milestone_id: int | None = Field(
        default=None, description="Milestone ID"
    )
    confidential: bool | None = Field(
        default=None, description="Whether the issue is confidential"
    )

    @field_validator("state_event")
    @classmethod
    def validate_state_event(cls, v: str | None) -> str | None:
        if v is not None and v not in ("close", "reopen"):
            raise ValueError("state_event must be 'close' or 'reopen'")
        return v


class CreateProjectInput(BaseModel):
    """Validated input for project creation."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(
        ..., min_length=1, max_length=MAX_PROJECT_NAME_LENGTH, description="Project name"
    )
    description: str | None = Field(
        default=None, max_length=MAX_DESCRIPTION_LENGTH, description="Project description"
    )
    visibility: str = Field(
        default="private", description="Visibility level (public, internal, private)"
    )
    initialize_with_readme: bool = Field(
        default=False, description="Initialize with a README file"
    )
    namespace_id: int | None = Field(
        default=None, description="Namespace ID to create the project under (group or user)"
    )

    @field_validator("visibility")
    @classmethod
    def validate_visibility(cls, v: str) -> str:
        if v not in PROJECT_VISIBILITIES:
            raise ValueError(
                f"visibility must be one of: {', '.join(sorted(PROJECT_VISIBILITIES))}"
            )
        return v


class CreateMergeRequestInput(BaseModel):
    """Validated input for merge request creation."""

    model_config = ConfigDict(extra="forbid")

    source_branch: str = Field(
        ..., min_length=1, max_length=MAX_BRANCH_LENGTH, description="Source branch name"
    )
    target_branch: str = Field(
        ..., min_length=1, max_length=MAX_BRANCH_LENGTH, description="Target branch name"
    )
    title: str = Field(
        ..., min_length=1, max_length=MAX_TITLE_LENGTH, description="MR title"
    )
    description: str | None = Field(
        default=None, max_length=MAX_DESCRIPTION_LENGTH, description="MR description (Markdown)"
    )
    labels: str | None = Field(
        default=None, max_length=MAX_LABELS_LENGTH, description="Comma-separated label names"
    )
    assignee_ids: list[int] | None = Field(
        default=None, max_length=MAX_ASSIGNEES, description="User IDs to assign"
    )
    reviewer_ids: list[int] | None = Field(
        default=None, max_length=MAX_ASSIGNEES, description="User IDs to review"
    )
    milestone_id: int | None = Field(
        default=None, description="Milestone ID"
    )
    remove_source_branch: bool = Field(
        default=False, description="Remove source branch after merge"
    )


class UpdateMergeRequestInput(BaseModel):
    """Validated input for merge request updates."""

    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(
        default=None, min_length=1, max_length=MAX_TITLE_LENGTH, description="MR title"
    )
    description: str | None = Field(
        default=None, max_length=MAX_DESCRIPTION_LENGTH, description="MR description (Markdown)"
    )
    labels: str | None = Field(
        default=None, max_length=MAX_LABELS_LENGTH, description="Comma-separated label names"
    )
    state_event: str | None = Field(
        default=None, description="State transition: close or reopen"
    )
    assignee_ids: list[int] | None = Field(
        default=None, max_length=MAX_ASSIGNEES, description="User IDs to assign"
    )
    reviewer_ids: list[int] | None = Field(
        default=None, max_length=MAX_ASSIGNEES, description="User IDs to review"
    )
    milestone_id: int | None = Field(
        default=None, description="Milestone ID"
    )
    target_branch: str | None = Field(
        default=None, min_length=1, max_length=MAX_BRANCH_LENGTH, description="Target branch"
    )
    remove_source_branch: bool | None = Field(
        default=None, description="Remove source branch after merge"
    )

    @field_validator("state_event")
    @classmethod
    def validate_state_event(cls, v: str | None) -> str | None:
        if v is not None and v not in ("close", "reopen"):
            raise ValueError("state_event must be 'close' or 'reopen'")
        return v
