"""FastMCP server setup for GitLab MCP.

This module creates and configures the MCP server with all tools.
"""

import logging
from typing import Any

from fastmcp import FastMCP

from .tools import (
    # Pipelines
    cancel_job,
    cancel_pipeline,
    # Issues
    create_issue,
    create_issue_note,
    # Merge Requests
    create_merge_request,
    create_mr_note,
    create_pipeline,
    delete_job,
    delete_pipeline,
    # Groups
    get_group,
    get_issue,
    get_job_log,
    get_merge_request,
    get_mr_changes,
    get_pipeline,
    # Projects
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
    retry_job,
    retry_pipeline,
    # Search
    search_global,
    search_project,
    update_issue,
    update_merge_request,
)

logger = logging.getLogger(__name__)

# Create the FastMCP server
mcp = FastMCP(
    name="mcp-gitlab-crunchtools",
    version="0.1.0",
    instructions=(
        "Secure MCP server for GitLab projects, merge requests, issues, "
        "pipelines, and search. Works with any GitLab instance."
    ),
)


# ──────────────────────────────────────────────────────────────
# Project tools
# ──────────────────────────────────────────────────────────────


@mcp.tool()
async def list_projects_tool(
    search: str | None = None,
    owned: bool = False,
    membership: bool = False,
    visibility: str | None = None,
    order_by: str = "created_at",
    sort: str = "desc",
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    """List GitLab projects accessible by the API token.

    Args:
        search: Search for projects by name
        owned: Only list projects owned by the authenticated user
        membership: Only list projects the user is a member of
        visibility: Filter by visibility (public, internal, private)
        order_by: Order by field (created_at, updated_at, name, path)
        sort: Sort direction (asc, desc)
        page: Page number for pagination (default: 1)
        per_page: Results per page, max 100 (default: 20)

    Returns:
        List of projects with pagination info
    """
    return await list_projects(
        search=search,
        owned=owned,
        membership=membership,
        visibility=visibility,
        order_by=order_by,
        sort=sort,
        page=page,
        per_page=per_page,
    )


@mcp.tool()
async def get_project_tool(
    project_id: str,
) -> dict[str, Any]:
    """Get GitLab project details by ID or path.

    Args:
        project_id: Project ID (numeric) or path (e.g., "group/project")

    Returns:
        Project details
    """
    return await get_project(project_id=project_id)


@mcp.tool()
async def list_project_branches_tool(
    project_id: str,
    search: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    """List repository branches for a GitLab project.

    Args:
        project_id: Project ID or path
        search: Filter branches by name
        page: Page number (default: 1)
        per_page: Results per page, max 100 (default: 20)

    Returns:
        List of branches with pagination info
    """
    return await list_project_branches(
        project_id=project_id, search=search, page=page, per_page=per_page
    )


@mcp.tool()
async def get_project_branch_tool(
    project_id: str,
    branch: str,
) -> dict[str, Any]:
    """Get a single repository branch.

    Args:
        project_id: Project ID or path
        branch: Branch name

    Returns:
        Branch details including commit info
    """
    return await get_project_branch(project_id=project_id, branch=branch)


@mcp.tool()
async def list_project_commits_tool(
    project_id: str,
    ref_name: str | None = None,
    since: str | None = None,
    until: str | None = None,
    path: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    """List repository commits for a GitLab project.

    Args:
        project_id: Project ID or path
        ref_name: Branch or tag name (default: default branch)
        since: Only commits after this date (ISO 8601)
        until: Only commits before this date (ISO 8601)
        path: Only commits touching this file path
        page: Page number (default: 1)
        per_page: Results per page, max 100 (default: 20)

    Returns:
        List of commits with pagination info
    """
    return await list_project_commits(
        project_id=project_id,
        ref_name=ref_name,
        since=since,
        until=until,
        path=path,
        page=page,
        per_page=per_page,
    )


# ──────────────────────────────────────────────────────────────
# Group tools
# ──────────────────────────────────────────────────────────────


@mcp.tool()
async def list_groups_tool(
    search: str | None = None,
    owned: bool = False,
    top_level_only: bool = False,
    order_by: str = "name",
    sort: str = "asc",
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    """List GitLab groups accessible by the API token.

    Args:
        search: Search for groups by name
        owned: Only list groups owned by the authenticated user
        top_level_only: Only list top-level groups
        order_by: Order by field (name, path, id)
        sort: Sort direction (asc, desc)
        page: Page number (default: 1)
        per_page: Results per page, max 100 (default: 20)

    Returns:
        List of groups with pagination info
    """
    return await list_groups(
        search=search,
        owned=owned,
        top_level_only=top_level_only,
        order_by=order_by,
        sort=sort,
        page=page,
        per_page=per_page,
    )


@mcp.tool()
async def get_group_tool(
    group_id: str,
    with_projects: bool = True,
) -> dict[str, Any]:
    """Get GitLab group details by ID or path.

    Args:
        group_id: Group ID (numeric) or path (e.g., "parent-group/child-group")
        with_projects: Include group projects (default: true)

    Returns:
        Group details
    """
    return await get_group(group_id=group_id, with_projects=with_projects)


@mcp.tool()
async def list_group_projects_tool(
    group_id: str,
    search: str | None = None,
    visibility: str | None = None,
    include_subgroups: bool = False,
    order_by: str = "created_at",
    sort: str = "desc",
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    """List projects within a GitLab group.

    Args:
        group_id: Group ID or path
        search: Filter projects by name
        visibility: Filter by visibility (public, internal, private)
        include_subgroups: Include projects from subgroups
        order_by: Order by field (created_at, updated_at, name, path)
        sort: Sort direction (asc, desc)
        page: Page number (default: 1)
        per_page: Results per page, max 100 (default: 20)

    Returns:
        List of projects with pagination info
    """
    return await list_group_projects(
        group_id=group_id,
        search=search,
        visibility=visibility,
        include_subgroups=include_subgroups,
        order_by=order_by,
        sort=sort,
        page=page,
        per_page=per_page,
    )


# ──────────────────────────────────────────────────────────────
# Merge Request tools
# ──────────────────────────────────────────────────────────────


@mcp.tool()
async def list_merge_requests_tool(
    project_id: str,
    state: str = "opened",
    order_by: str = "created_at",
    sort: str = "desc",
    labels: str | None = None,
    milestone: str | None = None,
    search: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    """List merge requests for a GitLab project.

    Args:
        project_id: Project ID or path
        state: Filter by state (opened, closed, merged, all)
        order_by: Order by field (created_at, updated_at)
        sort: Sort direction (asc, desc)
        labels: Comma-separated label names
        milestone: Milestone title
        search: Search in title and description
        page: Page number (default: 1)
        per_page: Results per page, max 100 (default: 20)

    Returns:
        List of merge requests with pagination info
    """
    return await list_merge_requests(
        project_id=project_id,
        state=state,
        order_by=order_by,
        sort=sort,
        labels=labels,
        milestone=milestone,
        search=search,
        page=page,
        per_page=per_page,
    )


@mcp.tool()
async def get_merge_request_tool(
    project_id: str,
    merge_request_iid: int,
) -> dict[str, Any]:
    """Get a single merge request by its IID.

    Args:
        project_id: Project ID or path
        merge_request_iid: Merge request internal ID (the number shown in the UI, e.g., !42)

    Returns:
        Merge request details including source/target branches, status, and approvals
    """
    return await get_merge_request(
        project_id=project_id, merge_request_iid=merge_request_iid
    )


@mcp.tool()
async def create_merge_request_tool(
    project_id: str,
    source_branch: str,
    target_branch: str,
    title: str,
    description: str | None = None,
    labels: str | None = None,
    assignee_ids: list[int] | None = None,
    reviewer_ids: list[int] | None = None,
    milestone_id: int | None = None,
    remove_source_branch: bool = False,
) -> dict[str, Any]:
    """Create a new merge request.

    Args:
        project_id: Project ID or path
        source_branch: Source branch name (must already exist)
        target_branch: Target branch name
        title: MR title
        description: MR description (Markdown)
        labels: Comma-separated label names
        assignee_ids: User IDs to assign
        reviewer_ids: User IDs to review
        milestone_id: Milestone ID
        remove_source_branch: Remove source branch after merge (default: false)

    Returns:
        Created merge request details
    """
    return await create_merge_request(
        project_id=project_id,
        source_branch=source_branch,
        target_branch=target_branch,
        title=title,
        description=description,
        labels=labels,
        assignee_ids=assignee_ids,
        reviewer_ids=reviewer_ids,
        milestone_id=milestone_id,
        remove_source_branch=remove_source_branch,
    )


@mcp.tool()
async def update_merge_request_tool(
    project_id: str,
    merge_request_iid: int,
    title: str | None = None,
    description: str | None = None,
    labels: str | None = None,
    state_event: str | None = None,
    assignee_ids: list[int] | None = None,
    reviewer_ids: list[int] | None = None,
    milestone_id: int | None = None,
    target_branch: str | None = None,
    remove_source_branch: bool | None = None,
) -> dict[str, Any]:
    """Update an existing merge request.

    Args:
        project_id: Project ID or path
        merge_request_iid: Merge request internal ID
        title: MR title
        description: MR description (Markdown)
        labels: Comma-separated label names
        state_event: State transition (close, reopen)
        assignee_ids: User IDs to assign
        reviewer_ids: User IDs to review
        milestone_id: Milestone ID
        target_branch: Target branch
        remove_source_branch: Remove source branch after merge

    Returns:
        Updated merge request details
    """
    return await update_merge_request(
        project_id=project_id,
        merge_request_iid=merge_request_iid,
        title=title,
        description=description,
        labels=labels,
        state_event=state_event,
        assignee_ids=assignee_ids,
        reviewer_ids=reviewer_ids,
        milestone_id=milestone_id,
        target_branch=target_branch,
        remove_source_branch=remove_source_branch,
    )


@mcp.tool()
async def list_mr_notes_tool(
    project_id: str,
    merge_request_iid: int,
    order_by: str = "created_at",
    sort: str = "desc",
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    """List notes (comments) on a merge request.

    Args:
        project_id: Project ID or path
        merge_request_iid: Merge request internal ID
        order_by: Order by field (created_at, updated_at)
        sort: Sort direction (asc, desc)
        page: Page number (default: 1)
        per_page: Results per page, max 100 (default: 20)

    Returns:
        List of notes with pagination info
    """
    return await list_mr_notes(
        project_id=project_id,
        merge_request_iid=merge_request_iid,
        order_by=order_by,
        sort=sort,
        page=page,
        per_page=per_page,
    )


@mcp.tool()
async def create_mr_note_tool(
    project_id: str,
    merge_request_iid: int,
    body: str,
) -> dict[str, Any]:
    """Create a note (comment) on a merge request.

    Args:
        project_id: Project ID or path
        merge_request_iid: Merge request internal ID
        body: Note content (Markdown)

    Returns:
        Created note details
    """
    return await create_mr_note(
        project_id=project_id, merge_request_iid=merge_request_iid, body=body
    )


@mcp.tool()
async def get_mr_changes_tool(
    project_id: str,
    merge_request_iid: int,
) -> dict[str, Any]:
    """Get the changes (diff) for a merge request.

    Args:
        project_id: Project ID or path
        merge_request_iid: Merge request internal ID

    Returns:
        Merge request details with file diffs
    """
    return await get_mr_changes(
        project_id=project_id, merge_request_iid=merge_request_iid
    )


# ──────────────────────────────────────────────────────────────
# Issue tools
# ──────────────────────────────────────────────────────────────


@mcp.tool()
async def list_issues_tool(
    project_id: str,
    state: str = "opened",
    order_by: str = "created_at",
    sort: str = "desc",
    labels: str | None = None,
    milestone: str | None = None,
    search: str | None = None,
    assignee_id: int | None = None,
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    """List issues for a GitLab project.

    Args:
        project_id: Project ID or path
        state: Filter by state (opened, closed, all)
        order_by: Order by field (created_at, updated_at, priority, due_date)
        sort: Sort direction (asc, desc)
        labels: Comma-separated label names
        milestone: Milestone title
        search: Search in title and description
        assignee_id: Filter by assignee user ID
        page: Page number (default: 1)
        per_page: Results per page, max 100 (default: 20)

    Returns:
        List of issues with pagination info
    """
    return await list_issues(
        project_id=project_id,
        state=state,
        order_by=order_by,
        sort=sort,
        labels=labels,
        milestone=milestone,
        search=search,
        assignee_id=assignee_id,
        page=page,
        per_page=per_page,
    )


@mcp.tool()
async def get_issue_tool(
    project_id: str,
    issue_iid: int,
) -> dict[str, Any]:
    """Get a single issue by its IID.

    Args:
        project_id: Project ID or path
        issue_iid: Issue internal ID (the number shown in the UI, e.g., #15)

    Returns:
        Issue details including labels, assignees, and milestone
    """
    return await get_issue(project_id=project_id, issue_iid=issue_iid)


@mcp.tool()
async def create_issue_tool(
    project_id: str,
    title: str,
    description: str | None = None,
    labels: str | None = None,
    assignee_ids: list[int] | None = None,
    milestone_id: int | None = None,
    confidential: bool = False,
) -> dict[str, Any]:
    """Create a new issue in a GitLab project.

    Args:
        project_id: Project ID or path
        title: Issue title
        description: Issue description (Markdown)
        labels: Comma-separated label names
        assignee_ids: User IDs to assign
        milestone_id: Milestone ID
        confidential: Whether the issue is confidential (default: false)

    Returns:
        Created issue details
    """
    return await create_issue(
        project_id=project_id,
        title=title,
        description=description,
        labels=labels,
        assignee_ids=assignee_ids,
        milestone_id=milestone_id,
        confidential=confidential,
    )


@mcp.tool()
async def update_issue_tool(
    project_id: str,
    issue_iid: int,
    title: str | None = None,
    description: str | None = None,
    labels: str | None = None,
    state_event: str | None = None,
    assignee_ids: list[int] | None = None,
    milestone_id: int | None = None,
    confidential: bool | None = None,
) -> dict[str, Any]:
    """Update an existing issue.

    Args:
        project_id: Project ID or path
        issue_iid: Issue internal ID
        title: Issue title
        description: Issue description (Markdown)
        labels: Comma-separated label names
        state_event: State transition (close, reopen)
        assignee_ids: User IDs to assign
        milestone_id: Milestone ID
        confidential: Whether the issue is confidential

    Returns:
        Updated issue details
    """
    return await update_issue(
        project_id=project_id,
        issue_iid=issue_iid,
        title=title,
        description=description,
        labels=labels,
        state_event=state_event,
        assignee_ids=assignee_ids,
        milestone_id=milestone_id,
        confidential=confidential,
    )


@mcp.tool()
async def list_issue_notes_tool(
    project_id: str,
    issue_iid: int,
    order_by: str = "created_at",
    sort: str = "desc",
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    """List notes (comments) on an issue.

    Args:
        project_id: Project ID or path
        issue_iid: Issue internal ID
        order_by: Order by field (created_at, updated_at)
        sort: Sort direction (asc, desc)
        page: Page number (default: 1)
        per_page: Results per page, max 100 (default: 20)

    Returns:
        List of notes with pagination info
    """
    return await list_issue_notes(
        project_id=project_id,
        issue_iid=issue_iid,
        order_by=order_by,
        sort=sort,
        page=page,
        per_page=per_page,
    )


@mcp.tool()
async def create_issue_note_tool(
    project_id: str,
    issue_iid: int,
    body: str,
) -> dict[str, Any]:
    """Create a note (comment) on an issue.

    Args:
        project_id: Project ID or path
        issue_iid: Issue internal ID
        body: Note content (Markdown)

    Returns:
        Created note details
    """
    return await create_issue_note(
        project_id=project_id, issue_iid=issue_iid, body=body
    )


# ──────────────────────────────────────────────────────────────
# Pipeline tools
# ──────────────────────────────────────────────────────────────


@mcp.tool()
async def list_pipelines_tool(
    project_id: str,
    status: str | None = None,
    ref: str | None = None,
    order_by: str = "id",
    sort: str = "desc",
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    """List CI/CD pipelines for a GitLab project.

    Args:
        project_id: Project ID or path
        status: Filter by status (created, waiting_for_resource, preparing,
                pending, running, success, failed, canceled, skipped, manual, scheduled)
        ref: Filter by branch or tag name
        order_by: Order by field (id, status, ref, updated_at, user_id)
        sort: Sort direction (asc, desc)
        page: Page number (default: 1)
        per_page: Results per page, max 100 (default: 20)

    Returns:
        List of pipelines with pagination info
    """
    return await list_pipelines(
        project_id=project_id,
        status=status,
        ref=ref,
        order_by=order_by,
        sort=sort,
        page=page,
        per_page=per_page,
    )


@mcp.tool()
async def get_pipeline_tool(
    project_id: str,
    pipeline_id: int,
) -> dict[str, Any]:
    """Get a single CI/CD pipeline by ID.

    Args:
        project_id: Project ID or path
        pipeline_id: Pipeline ID

    Returns:
        Pipeline details including status, duration, and ref
    """
    return await get_pipeline(project_id=project_id, pipeline_id=pipeline_id)


@mcp.tool()
async def list_pipeline_jobs_tool(
    project_id: str,
    pipeline_id: int,
    scope: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    """List jobs for a CI/CD pipeline.

    Args:
        project_id: Project ID or path
        pipeline_id: Pipeline ID
        scope: Filter by job scope (created, pending, running, failed,
               success, canceled, skipped, manual)
        page: Page number (default: 1)
        per_page: Results per page, max 100 (default: 20)

    Returns:
        List of jobs with pagination info
    """
    return await list_pipeline_jobs(
        project_id=project_id,
        pipeline_id=pipeline_id,
        scope=scope,
        page=page,
        per_page=per_page,
    )


@mcp.tool()
async def get_job_log_tool(
    project_id: str,
    job_id: int,
) -> dict[str, Any]:
    """Get the log (trace) output of a CI/CD job.

    Args:
        project_id: Project ID or path
        job_id: Job ID

    Returns:
        Dictionary with job log content as plain text
    """
    return await get_job_log(project_id=project_id, job_id=job_id)


@mcp.tool()
async def create_pipeline_tool(
    project_id: str,
    ref: str = "main",
) -> dict[str, Any]:
    """Create (trigger) a new CI/CD pipeline.

    Args:
        project_id: Project ID or path
        ref: Branch or tag name to run the pipeline for (default: main)

    Returns:
        Created pipeline details including ID and status
    """
    return await create_pipeline(project_id=project_id, ref=ref)


@mcp.tool()
async def retry_pipeline_tool(
    project_id: str,
    pipeline_id: int,
) -> dict[str, Any]:
    """Retry all failed jobs in a CI/CD pipeline.

    Args:
        project_id: Project ID or path
        pipeline_id: Pipeline ID

    Returns:
        Retried pipeline details
    """
    return await retry_pipeline(project_id=project_id, pipeline_id=pipeline_id)


@mcp.tool()
async def cancel_pipeline_tool(
    project_id: str,
    pipeline_id: int,
) -> dict[str, Any]:
    """Cancel a running CI/CD pipeline.

    Args:
        project_id: Project ID or path
        pipeline_id: Pipeline ID

    Returns:
        Canceled pipeline details
    """
    return await cancel_pipeline(project_id=project_id, pipeline_id=pipeline_id)


@mcp.tool()
async def delete_pipeline_tool(
    project_id: str,
    pipeline_id: int,
) -> dict[str, Any]:
    """Delete a CI/CD pipeline and all its jobs permanently.

    Args:
        project_id: Project ID or path
        pipeline_id: Pipeline ID

    Returns:
        Confirmation of deletion
    """
    return await delete_pipeline(project_id=project_id, pipeline_id=pipeline_id)


@mcp.tool()
async def retry_job_tool(
    project_id: str,
    job_id: int,
) -> dict[str, Any]:
    """Retry a specific failed CI/CD job.

    Args:
        project_id: Project ID or path
        job_id: Job ID

    Returns:
        Retried job details
    """
    return await retry_job(project_id=project_id, job_id=job_id)


@mcp.tool()
async def cancel_job_tool(
    project_id: str,
    job_id: int,
) -> dict[str, Any]:
    """Cancel a running CI/CD job.

    Args:
        project_id: Project ID or path
        job_id: Job ID

    Returns:
        Canceled job details
    """
    return await cancel_job(project_id=project_id, job_id=job_id)


@mcp.tool()
async def delete_job_tool(
    project_id: str,
    job_id: int,
) -> dict[str, Any]:
    """Delete a CI/CD job's artifacts and trace log.

    Args:
        project_id: Project ID or path
        job_id: Job ID

    Returns:
        Erased job details
    """
    return await delete_job(project_id=project_id, job_id=job_id)


# ──────────────────────────────────────────────────────────────
# Search tools
# ──────────────────────────────────────────────────────────────


@mcp.tool()
async def search_global_tool(
    search: str,
    scope: str = "projects",
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    """Search across all GitLab resources accessible by the token.

    Args:
        search: Search query string
        scope: Search scope (projects, issues, merge_requests, milestones,
               snippet_titles, wiki_blobs, commits, blobs, notes, users)
        page: Page number (default: 1)
        per_page: Results per page, max 100 (default: 20)

    Returns:
        Search results with pagination info
    """
    return await search_global(search=search, scope=scope, page=page, per_page=per_page)


@mcp.tool()
async def search_project_tool(
    project_id: str,
    search: str,
    scope: str = "blobs",
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    """Search within a specific GitLab project.

    Args:
        project_id: Project ID or path
        search: Search query string
        scope: Search scope (issues, merge_requests, milestones,
               wiki_blobs, commits, blobs, notes)
        page: Page number (default: 1)
        per_page: Results per page, max 100 (default: 20)

    Returns:
        Search results with pagination info
    """
    return await search_project(
        project_id=project_id, search=search, scope=scope, page=page, per_page=per_page
    )
