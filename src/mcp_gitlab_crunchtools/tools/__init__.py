"""GitLab MCP tools.

This package contains all the MCP tool implementations for GitLab operations.
"""

from .groups import get_group, list_group_projects, list_groups
from .issues import (
    create_issue,
    create_issue_note,
    get_issue,
    list_issue_notes,
    list_issues,
    update_issue,
)
from .merge_requests import (
    create_merge_request,
    create_mr_note,
    get_merge_request,
    get_mr_changes,
    list_merge_requests,
    list_mr_notes,
    update_merge_request,
)
from .pipelines import get_job_log, get_pipeline, list_pipeline_jobs, list_pipelines
from .projects import (
    get_project,
    get_project_branch,
    list_project_branches,
    list_project_commits,
    list_projects,
)
from .search import search_global, search_project

__all__ = [
    # Projects
    "list_projects",
    "get_project",
    "list_project_branches",
    "get_project_branch",
    "list_project_commits",
    # Groups
    "list_groups",
    "get_group",
    "list_group_projects",
    # Merge Requests
    "list_merge_requests",
    "get_merge_request",
    "create_merge_request",
    "update_merge_request",
    "list_mr_notes",
    "create_mr_note",
    "get_mr_changes",
    # Issues
    "list_issues",
    "get_issue",
    "create_issue",
    "update_issue",
    "list_issue_notes",
    "create_issue_note",
    # Pipelines
    "list_pipelines",
    "get_pipeline",
    "list_pipeline_jobs",
    "get_job_log",
    # Search
    "search_global",
    "search_project",
]
