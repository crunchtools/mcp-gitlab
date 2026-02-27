"""Merge request management tools.

Tools for listing, creating, and updating GitLab merge requests.
"""

from typing import Any

from ..client import get_client
from ..models import CreateMergeRequestInput, UpdateMergeRequestInput, encode_project_id


async def list_merge_requests(
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
    """List merge requests for a project.

    Args:
        project_id: Project ID or path
        state: Filter by state (opened, closed, merged, all)
        order_by: Order by field (created_at, updated_at)
        sort: Sort direction (asc, desc)
        labels: Comma-separated label names
        milestone: Milestone title
        search: Search in title and description
        page: Page number
        per_page: Results per page

    Returns:
        List of merge requests with pagination info
    """
    client = get_client()
    encoded_id = encode_project_id(project_id)

    params: dict[str, Any] = {
        "state": state,
        "order_by": order_by,
        "sort": sort,
        "page": page,
        "per_page": min(per_page, 100),
    }

    if labels:
        params["labels"] = labels
    if milestone:
        params["milestone"] = milestone
    if search:
        params["search"] = search

    return await client.get(f"/projects/{encoded_id}/merge_requests", params=params)


async def get_merge_request(
    project_id: str,
    merge_request_iid: int,
) -> dict[str, Any]:
    """Get a single merge request.

    Args:
        project_id: Project ID or path
        merge_request_iid: Merge request internal ID (the number shown in the UI)

    Returns:
        Merge request details
    """
    client = get_client()
    encoded_id = encode_project_id(project_id)
    return await client.get(f"/projects/{encoded_id}/merge_requests/{merge_request_iid}")


async def create_merge_request(
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
        source_branch: Source branch name
        target_branch: Target branch name
        title: MR title
        description: MR description (Markdown)
        labels: Comma-separated label names
        assignee_ids: User IDs to assign
        reviewer_ids: User IDs to review
        milestone_id: Milestone ID
        remove_source_branch: Remove source branch after merge

    Returns:
        Created merge request details
    """
    validated = CreateMergeRequestInput(
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

    client = get_client()
    encoded_id = encode_project_id(project_id)

    data: dict[str, Any] = {
        "source_branch": validated.source_branch,
        "target_branch": validated.target_branch,
        "title": validated.title,
    }

    if validated.description is not None:
        data["description"] = validated.description
    if validated.labels is not None:
        data["labels"] = validated.labels
    if validated.assignee_ids is not None:
        data["assignee_ids"] = validated.assignee_ids
    if validated.reviewer_ids is not None:
        data["reviewer_ids"] = validated.reviewer_ids
    if validated.milestone_id is not None:
        data["milestone_id"] = validated.milestone_id
    if validated.remove_source_branch:
        data["remove_source_branch"] = True

    return await client.post(f"/projects/{encoded_id}/merge_requests", json_data=data)


async def update_merge_request(
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
    validated = UpdateMergeRequestInput(
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

    client = get_client()
    encoded_id = encode_project_id(project_id)

    data: dict[str, Any] = {}
    if validated.title is not None:
        data["title"] = validated.title
    if validated.description is not None:
        data["description"] = validated.description
    if validated.labels is not None:
        data["labels"] = validated.labels
    if validated.state_event is not None:
        data["state_event"] = validated.state_event
    if validated.assignee_ids is not None:
        data["assignee_ids"] = validated.assignee_ids
    if validated.reviewer_ids is not None:
        data["reviewer_ids"] = validated.reviewer_ids
    if validated.milestone_id is not None:
        data["milestone_id"] = validated.milestone_id
    if validated.target_branch is not None:
        data["target_branch"] = validated.target_branch
    if validated.remove_source_branch is not None:
        data["remove_source_branch"] = validated.remove_source_branch

    return await client.put(
        f"/projects/{encoded_id}/merge_requests/{merge_request_iid}", json_data=data
    )


async def list_mr_notes(
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
        page: Page number
        per_page: Results per page

    Returns:
        List of notes with pagination info
    """
    client = get_client()
    encoded_id = encode_project_id(project_id)

    params: dict[str, Any] = {
        "order_by": order_by,
        "sort": sort,
        "page": page,
        "per_page": min(per_page, 100),
    }

    return await client.get(
        f"/projects/{encoded_id}/merge_requests/{merge_request_iid}/notes", params=params
    )


async def create_mr_note(
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
    if not body or not body.strip():
        raise ValueError("Note body must not be empty")

    client = get_client()
    encoded_id = encode_project_id(project_id)

    return await client.post(
        f"/projects/{encoded_id}/merge_requests/{merge_request_iid}/notes",
        json_data={"body": body},
    )


async def get_mr_changes(
    project_id: str,
    merge_request_iid: int,
) -> dict[str, Any]:
    """Get the changes (diff) for a merge request.

    Args:
        project_id: Project ID or path
        merge_request_iid: Merge request internal ID

    Returns:
        Merge request details with diff changes
    """
    client = get_client()
    encoded_id = encode_project_id(project_id)
    return await client.get(
        f"/projects/{encoded_id}/merge_requests/{merge_request_iid}/changes"
    )


async def list_mr_discussions(
    project_id: str,
    merge_request_iid: int,
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    """List discussions (threaded comments) on a merge request.

    Discussions include inline code review comments with position data.

    Args:
        project_id: Project ID or path
        merge_request_iid: Merge request internal ID
        page: Page number
        per_page: Results per page

    Returns:
        List of discussions with notes and position info
    """
    client = get_client()
    encoded_id = encode_project_id(project_id)

    params: dict[str, Any] = {
        "page": page,
        "per_page": min(per_page, 100),
    }

    return await client.get(
        f"/projects/{encoded_id}/merge_requests/{merge_request_iid}/discussions",
        params=params,
    )


async def create_mr_discussion(
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
    client = get_client()
    encoded_id = encode_project_id(project_id)
    return await client.post(
        f"/projects/{encoded_id}/merge_requests/{merge_request_iid}/discussions",
        json_data={"body": body},
    )
