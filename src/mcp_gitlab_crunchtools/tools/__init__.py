"""GitLab MCP tools.

This package contains all the MCP tool implementations for GitLab operations.
"""

from .branches import compare_branches, create_branch, delete_branch
from .files import create_file, get_file, list_repository_tree, update_file
from .groups import get_group, list_group_projects, list_groups
from .issues import (
    create_issue,
    create_issue_note,
    get_issue,
    list_issue_notes,
    list_issues,
    update_issue,
)
from .labels import create_label, delete_label, list_labels, update_label
from .merge_requests import (
    create_merge_request,
    create_mr_discussion,
    create_mr_note,
    get_merge_request,
    get_mr_changes,
    list_merge_requests,
    list_mr_discussions,
    list_mr_notes,
    update_merge_request,
)
from .milestones import create_milestone, list_milestones, update_milestone
from .pipelines import (
    cancel_job,
    cancel_pipeline,
    create_pipeline,
    delete_job,
    delete_pipeline,
    get_job_log,
    get_pipeline,
    list_pipeline_jobs,
    list_pipelines,
    retry_job,
    retry_pipeline,
)
from .projects import (
    create_project,
    delete_project,
    get_project,
    get_project_branch,
    list_project_branches,
    list_project_commits,
    list_projects,
)
from .releases import create_release, get_release, list_releases
from .search import search_global, search_project
from .snippets import create_snippet, list_snippets
from .users import get_current_user, get_user, list_users
from .wiki import create_wiki_page, get_wiki_page, list_wiki_pages

__all__ = [
    "list_projects",
    "get_project",
    "create_project",
    "delete_project",
    "list_project_branches",
    "get_project_branch",
    "list_project_commits",
    "list_groups",
    "get_group",
    "list_group_projects",
    "list_merge_requests",
    "get_merge_request",
    "create_merge_request",
    "update_merge_request",
    "list_mr_notes",
    "create_mr_note",
    "get_mr_changes",
    "list_mr_discussions",
    "create_mr_discussion",
    "list_issues",
    "get_issue",
    "create_issue",
    "update_issue",
    "list_issue_notes",
    "create_issue_note",
    "list_pipelines",
    "get_pipeline",
    "create_pipeline",
    "retry_pipeline",
    "cancel_pipeline",
    "delete_pipeline",
    "list_pipeline_jobs",
    "get_job_log",
    "retry_job",
    "cancel_job",
    "delete_job",
    "list_repository_tree",
    "get_file",
    "create_file",
    "update_file",
    "create_branch",
    "delete_branch",
    "compare_branches",
    "list_labels",
    "create_label",
    "update_label",
    "delete_label",
    "get_current_user",
    "list_users",
    "get_user",
    "list_releases",
    "get_release",
    "create_release",
    "list_milestones",
    "create_milestone",
    "update_milestone",
    "list_wiki_pages",
    "get_wiki_page",
    "create_wiki_page",
    "list_snippets",
    "create_snippet",
    "search_global",
    "search_project",
]
