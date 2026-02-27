"""FastMCP server setup for GitLab MCP.

This module creates and configures the MCP server with all tools.
"""

import logging
from typing import Any

from fastmcp import FastMCP

from .tools import (
    cancel_job,
    cancel_pipeline,
    compare_branches,
    create_branch,
    create_file,
    create_issue,
    create_issue_note,
    create_label,
    create_merge_request,
    create_milestone,
    create_mr_discussion,
    create_mr_note,
    create_pipeline,
    create_release,
    create_snippet,
    create_wiki_page,
    delete_branch,
    delete_job,
    delete_label,
    delete_pipeline,
    get_current_user,
    get_file,
    get_group,
    get_issue,
    get_job_log,
    get_merge_request,
    get_mr_changes,
    get_pipeline,
    get_project,
    get_project_branch,
    get_release,
    get_user,
    get_wiki_page,
    list_group_projects,
    list_groups,
    list_issue_notes,
    list_issues,
    list_labels,
    list_merge_requests,
    list_milestones,
    list_mr_discussions,
    list_mr_notes,
    list_pipeline_jobs,
    list_pipelines,
    list_project_branches,
    list_project_commits,
    list_projects,
    list_releases,
    list_repository_tree,
    list_snippets,
    list_users,
    list_wiki_pages,
    retry_job,
    retry_pipeline,
    search_global,
    search_project,
    update_file,
    update_issue,
    update_label,
    update_merge_request,
    update_milestone,
)

logger = logging.getLogger(__name__)

mcp = FastMCP(
    name="mcp-gitlab-crunchtools",
    version="0.3.0",
    instructions=(
        "Secure MCP server for GitLab projects, merge requests, issues, "
        "pipelines, and search. Works with any GitLab instance."
    ),
)



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


@mcp.tool()
async def list_mr_discussions_tool(
    project_id: str,
    merge_request_iid: int,
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    """List discussions (threaded comments) on a merge request.

    Discussions include inline code review comments with file position data.

    Args:
        project_id: Project ID or path
        merge_request_iid: Merge request internal ID
        page: Page number (default: 1)
        per_page: Results per page, max 100 (default: 20)

    Returns:
        List of discussions with notes and position info
    """
    return await list_mr_discussions(
        project_id=project_id,
        merge_request_iid=merge_request_iid,
        page=page,
        per_page=per_page,
    )


@mcp.tool()
async def create_mr_discussion_tool(
    project_id: str,
    merge_request_iid: int,
    body: str,
) -> dict[str, Any]:
    """Create a new discussion on a merge request.

    Args:
        project_id: Project ID or path
        merge_request_iid: Merge request internal ID
        body: Discussion body (Markdown)

    Returns:
        Created discussion details
    """
    return await create_mr_discussion(
        project_id=project_id, merge_request_iid=merge_request_iid, body=body
    )




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




@mcp.tool()
async def list_repository_tree_tool(
    project_id: str,
    path: str = "",
    ref: str | None = None,
    recursive: bool = False,
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    """List repository tree (files and directories).

    Args:
        project_id: Project ID or path
        path: Path inside the repository (default: root)
        ref: Branch, tag, or commit SHA (default: default branch)
        recursive: List files recursively
        page: Page number (default: 1)
        per_page: Results per page, max 100 (default: 20)

    Returns:
        List of tree entries (blobs and trees) with pagination info
    """
    return await list_repository_tree(
        project_id=project_id, path=path, ref=ref, recursive=recursive,
        page=page, per_page=per_page,
    )


@mcp.tool()
async def get_file_tool(
    project_id: str,
    file_path: str,
    ref: str = "HEAD",
) -> dict[str, Any]:
    """Get a file from a GitLab repository.

    Returns file metadata and content (base64 encoded).

    Args:
        project_id: Project ID or path
        file_path: Path to the file in the repository
        ref: Branch, tag, or commit SHA (default: HEAD)

    Returns:
        File metadata including base64 content, size, and encoding
    """
    return await get_file(project_id=project_id, file_path=file_path, ref=ref)


@mcp.tool()
async def create_file_tool(
    project_id: str,
    file_path: str,
    branch: str,
    content: str,
    commit_message: str,
    encoding: str = "text",
) -> dict[str, Any]:
    """Create a new file in a GitLab repository.

    Args:
        project_id: Project ID or path
        file_path: Path for the new file
        branch: Branch to commit to
        content: File content (text or base64 depending on encoding)
        commit_message: Commit message
        encoding: Content encoding - "text" or "base64" (default: text)

    Returns:
        Created file metadata
    """
    return await create_file(
        project_id=project_id, file_path=file_path, branch=branch,
        content=content, commit_message=commit_message, encoding=encoding,
    )


@mcp.tool()
async def update_file_tool(
    project_id: str,
    file_path: str,
    branch: str,
    content: str,
    commit_message: str,
    encoding: str = "text",
) -> dict[str, Any]:
    """Update an existing file in a GitLab repository.

    Args:
        project_id: Project ID or path
        file_path: Path to the file
        branch: Branch to commit to
        content: New file content
        commit_message: Commit message
        encoding: Content encoding - "text" or "base64" (default: text)

    Returns:
        Updated file metadata
    """
    return await update_file(
        project_id=project_id, file_path=file_path, branch=branch,
        content=content, commit_message=commit_message, encoding=encoding,
    )




@mcp.tool()
async def create_branch_tool(
    project_id: str,
    branch: str,
    ref: str,
) -> dict[str, Any]:
    """Create a new branch in a GitLab repository.

    Args:
        project_id: Project ID or path
        branch: Name of the new branch
        ref: Branch name or commit SHA to create from

    Returns:
        Created branch details
    """
    return await create_branch(project_id=project_id, branch=branch, ref=ref)


@mcp.tool()
async def delete_branch_tool(
    project_id: str,
    branch: str,
) -> dict[str, Any]:
    """Delete a branch from a GitLab repository.

    Args:
        project_id: Project ID or path
        branch: Branch name to delete

    Returns:
        Confirmation of deletion
    """
    return await delete_branch(project_id=project_id, branch=branch)


@mcp.tool()
async def compare_branches_tool(
    project_id: str,
    from_ref: str,
    to_ref: str,
    straight: bool = False,
) -> dict[str, Any]:
    """Compare two branches, tags, or commits.

    Args:
        project_id: Project ID or path
        from_ref: Base branch/tag/commit
        to_ref: Head branch/tag/commit
        straight: Use straight comparison instead of merge-base (default: false)

    Returns:
        Comparison with commits, diffs, and stats
    """
    return await compare_branches(
        project_id=project_id, from_ref=from_ref, to_ref=to_ref, straight=straight,
    )




@mcp.tool()
async def list_labels_tool(
    project_id: str,
    search: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    """List labels for a GitLab project.

    Args:
        project_id: Project ID or path
        search: Filter labels by keyword
        page: Page number (default: 1)
        per_page: Results per page, max 100 (default: 20)

    Returns:
        List of labels with pagination info
    """
    return await list_labels(
        project_id=project_id, search=search, page=page, per_page=per_page,
    )


@mcp.tool()
async def create_label_tool(
    project_id: str,
    name: str,
    color: str,
    description: str | None = None,
    priority: int | None = None,
) -> dict[str, Any]:
    """Create a new label in a GitLab project.

    Args:
        project_id: Project ID or path
        name: Label name
        color: Color hex code (e.g., "#FF0000") or named color
        description: Label description
        priority: Label priority (lower = higher priority)

    Returns:
        Created label details
    """
    return await create_label(
        project_id=project_id, name=name, color=color,
        description=description, priority=priority,
    )


@mcp.tool()
async def update_label_tool(
    project_id: str,
    label_id: int,
    new_name: str | None = None,
    color: str | None = None,
    description: str | None = None,
    priority: int | None = None,
) -> dict[str, Any]:
    """Update an existing label in a GitLab project.

    Args:
        project_id: Project ID or path
        label_id: Label ID
        new_name: New label name
        color: New color hex code
        description: New description
        priority: New priority

    Returns:
        Updated label details
    """
    return await update_label(
        project_id=project_id, label_id=label_id, new_name=new_name,
        color=color, description=description, priority=priority,
    )


@mcp.tool()
async def delete_label_tool(
    project_id: str,
    label_id: int,
) -> dict[str, Any]:
    """Delete a label from a GitLab project.

    Args:
        project_id: Project ID or path
        label_id: Label ID

    Returns:
        Confirmation of deletion
    """
    return await delete_label(project_id=project_id, label_id=label_id)




@mcp.tool()
async def get_current_user_tool() -> dict[str, Any]:
    """Get the currently authenticated GitLab user.

    Returns:
        Current user details including ID, username, email, and permissions
    """
    return await get_current_user()


@mcp.tool()
async def list_users_tool(
    search: str | None = None,
    username: str | None = None,
    active: bool = True,
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    """List GitLab users.

    Args:
        search: Search for users by name or email
        username: Filter by exact username
        active: Only return active users (default: true)
        page: Page number (default: 1)
        per_page: Results per page, max 100 (default: 20)

    Returns:
        List of users with pagination info
    """
    return await list_users(
        search=search, username=username, active=active,
        page=page, per_page=per_page,
    )


@mcp.tool()
async def get_user_tool(
    user_id: int,
) -> dict[str, Any]:
    """Get a specific GitLab user by ID.

    Args:
        user_id: User ID

    Returns:
        User details including username, name, email, and state
    """
    return await get_user(user_id=user_id)




@mcp.tool()
async def list_releases_tool(
    project_id: str,
    order_by: str = "released_at",
    sort: str = "desc",
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    """List releases for a GitLab project.

    Args:
        project_id: Project ID or path
        order_by: Order by field (released_at, created_at)
        sort: Sort direction (asc, desc)
        page: Page number (default: 1)
        per_page: Results per page, max 100 (default: 20)

    Returns:
        List of releases with pagination info
    """
    return await list_releases(
        project_id=project_id, order_by=order_by, sort=sort,
        page=page, per_page=per_page,
    )


@mcp.tool()
async def get_release_tool(
    project_id: str,
    tag_name: str,
) -> dict[str, Any]:
    """Get a single release by tag name.

    Args:
        project_id: Project ID or path
        tag_name: Tag associated with the release

    Returns:
        Release details including assets and evidence
    """
    return await get_release(project_id=project_id, tag_name=tag_name)


@mcp.tool()
async def create_release_tool(
    project_id: str,
    tag_name: str,
    name: str | None = None,
    description: str | None = None,
    ref: str | None = None,
    released_at: str | None = None,
) -> dict[str, Any]:
    """Create a new release for a GitLab project.

    Args:
        project_id: Project ID or path
        tag_name: Tag name for the release (created if it doesn't exist)
        name: Release title (defaults to tag_name)
        description: Release notes (Markdown)
        ref: Commit SHA or branch to tag from (required if tag doesn't exist)
        released_at: Release date (ISO 8601, default: now)

    Returns:
        Created release details
    """
    return await create_release(
        project_id=project_id, tag_name=tag_name, name=name,
        description=description, ref=ref, released_at=released_at,
    )




@mcp.tool()
async def list_milestones_tool(
    project_id: str,
    state: str = "active",
    search: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    """List milestones for a GitLab project.

    Args:
        project_id: Project ID or path
        state: Filter by state (active, closed, all)
        search: Filter by title
        page: Page number (default: 1)
        per_page: Results per page, max 100 (default: 20)

    Returns:
        List of milestones with pagination info
    """
    return await list_milestones(
        project_id=project_id, state=state, search=search,
        page=page, per_page=per_page,
    )


@mcp.tool()
async def create_milestone_tool(
    project_id: str,
    title: str,
    description: str | None = None,
    due_date: str | None = None,
    start_date: str | None = None,
) -> dict[str, Any]:
    """Create a new milestone in a GitLab project.

    Args:
        project_id: Project ID or path
        title: Milestone title
        description: Milestone description (Markdown)
        due_date: Due date (YYYY-MM-DD)
        start_date: Start date (YYYY-MM-DD)

    Returns:
        Created milestone details
    """
    return await create_milestone(
        project_id=project_id, title=title, description=description,
        due_date=due_date, start_date=start_date,
    )


@mcp.tool()
async def update_milestone_tool(
    project_id: str,
    milestone_id: int,
    title: str | None = None,
    description: str | None = None,
    due_date: str | None = None,
    start_date: str | None = None,
    state_event: str | None = None,
) -> dict[str, Any]:
    """Update an existing milestone.

    Args:
        project_id: Project ID or path
        milestone_id: Milestone ID
        title: New title
        description: New description (Markdown)
        due_date: New due date (YYYY-MM-DD)
        start_date: New start date (YYYY-MM-DD)
        state_event: State transition (close, activate)

    Returns:
        Updated milestone details
    """
    return await update_milestone(
        project_id=project_id, milestone_id=milestone_id, title=title,
        description=description, due_date=due_date, start_date=start_date,
        state_event=state_event,
    )




@mcp.tool()
async def list_wiki_pages_tool(
    project_id: str,
    with_content: bool = False,
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    """List wiki pages for a GitLab project.

    Args:
        project_id: Project ID or path
        with_content: Include page content in response (default: false)
        page: Page number (default: 1)
        per_page: Results per page, max 100 (default: 20)

    Returns:
        List of wiki pages with pagination info
    """
    return await list_wiki_pages(
        project_id=project_id, with_content=with_content,
        page=page, per_page=per_page,
    )


@mcp.tool()
async def get_wiki_page_tool(
    project_id: str,
    slug: str,
) -> dict[str, Any]:
    """Get a single wiki page by slug.

    Args:
        project_id: Project ID or path
        slug: URL slug of the wiki page

    Returns:
        Wiki page details including content
    """
    return await get_wiki_page(project_id=project_id, slug=slug)


@mcp.tool()
async def create_wiki_page_tool(
    project_id: str,
    title: str,
    content: str,
    format: str = "markdown",
) -> dict[str, Any]:
    """Create a new wiki page in a GitLab project.

    Args:
        project_id: Project ID or path
        title: Page title
        content: Page content
        format: Content format - markdown, rdoc, asciidoc, or org (default: markdown)

    Returns:
        Created wiki page details
    """
    return await create_wiki_page(
        project_id=project_id, title=title, content=content, format=format,
    )




@mcp.tool()
async def list_snippets_tool(
    project_id: str,
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    """List snippets for a GitLab project.

    Args:
        project_id: Project ID or path
        page: Page number (default: 1)
        per_page: Results per page, max 100 (default: 20)

    Returns:
        List of snippets with pagination info
    """
    return await list_snippets(project_id=project_id, page=page, per_page=per_page)


@mcp.tool()
async def create_snippet_tool(
    project_id: str,
    title: str,
    file_name: str,
    content: str,
    description: str | None = None,
    visibility: str = "private",
) -> dict[str, Any]:
    """Create a new snippet in a GitLab project.

    Args:
        project_id: Project ID or path
        title: Snippet title
        file_name: File name for the snippet (e.g., "example.py")
        content: Snippet content
        description: Snippet description (Markdown)
        visibility: Visibility level (private, internal, public)

    Returns:
        Created snippet details
    """
    return await create_snippet(
        project_id=project_id, title=title, file_name=file_name,
        content=content, description=description, visibility=visibility,
    )
