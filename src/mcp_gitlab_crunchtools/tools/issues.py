"""Issue management tools.

Tools for listing, creating, and updating GitLab issues.
"""

from typing import Any

from ..client import get_client
from ..models import CreateIssueInput, UpdateIssueInput, encode_project_id


async def list_issues(
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
    """List issues for a project.

    Args:
        project_id: Project ID or path
        state: Filter by state (opened, closed, all)
        order_by: Order by field (created_at, updated_at, priority, due_date)
        sort: Sort direction (asc, desc)
        labels: Comma-separated label names
        milestone: Milestone title
        search: Search in title and description
        assignee_id: Filter by assignee user ID
        page: Page number
        per_page: Results per page

    Returns:
        List of issues with pagination info
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
    if assignee_id is not None:
        params["assignee_id"] = assignee_id

    return await client.get(f"/projects/{encoded_id}/issues", params=params)


async def get_issue(
    project_id: str,
    issue_iid: int,
) -> dict[str, Any]:
    """Get a single issue.

    Args:
        project_id: Project ID or path
        issue_iid: Issue internal ID (the number shown in the UI)

    Returns:
        Issue details
    """
    client = get_client()
    encoded_id = encode_project_id(project_id)
    return await client.get(f"/projects/{encoded_id}/issues/{issue_iid}")


async def create_issue(
    project_id: str,
    title: str,
    description: str | None = None,
    labels: str | None = None,
    assignee_ids: list[int] | None = None,
    milestone_id: int | None = None,
    confidential: bool = False,
) -> dict[str, Any]:
    """Create a new issue.

    Args:
        project_id: Project ID or path
        title: Issue title
        description: Issue description (Markdown)
        labels: Comma-separated label names
        assignee_ids: User IDs to assign
        milestone_id: Milestone ID
        confidential: Whether the issue is confidential

    Returns:
        Created issue details
    """
    validated = CreateIssueInput(
        title=title,
        description=description,
        labels=labels,
        assignee_ids=assignee_ids,
        milestone_id=milestone_id,
        confidential=confidential,
    )

    client = get_client()
    encoded_id = encode_project_id(project_id)

    data: dict[str, Any] = {"title": validated.title}

    if validated.description is not None:
        data["description"] = validated.description
    if validated.labels is not None:
        data["labels"] = validated.labels
    if validated.assignee_ids is not None:
        data["assignee_ids"] = validated.assignee_ids
    if validated.milestone_id is not None:
        data["milestone_id"] = validated.milestone_id
    if validated.confidential:
        data["confidential"] = True

    return await client.post(f"/projects/{encoded_id}/issues", json_data=data)


async def update_issue(
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
    validated = UpdateIssueInput(
        title=title,
        description=description,
        labels=labels,
        state_event=state_event,
        assignee_ids=assignee_ids,
        milestone_id=milestone_id,
        confidential=confidential,
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
    if validated.milestone_id is not None:
        data["milestone_id"] = validated.milestone_id
    if validated.confidential is not None:
        data["confidential"] = validated.confidential

    return await client.put(
        f"/projects/{encoded_id}/issues/{issue_iid}", json_data=data
    )


async def list_issue_notes(
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
        f"/projects/{encoded_id}/issues/{issue_iid}/notes", params=params
    )


async def create_issue_note(
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
    if not body or not body.strip():
        raise ValueError("Note body must not be empty")

    client = get_client()
    encoded_id = encode_project_id(project_id)

    return await client.post(
        f"/projects/{encoded_id}/issues/{issue_iid}/notes",
        json_data={"body": body},
    )
