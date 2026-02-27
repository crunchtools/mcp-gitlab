"""Milestone management tools.

Tools for managing GitLab project milestones for sprint/iteration tracking.
"""

from typing import Any

from ..client import get_client
from ..models import encode_project_id


async def list_milestones(
    project_id: str,
    state: str = "active",
    search: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    """List milestones for a project.

    Args:
        project_id: Project ID or path
        state: Filter by state (active, closed, all)
        search: Filter by title
        page: Page number
        per_page: Results per page

    Returns:
        List of milestones with pagination info
    """
    client = get_client()
    encoded_id = encode_project_id(project_id)

    params: dict[str, Any] = {
        "state": state,
        "page": page,
        "per_page": min(per_page, 100),
    }

    if search:
        params["search"] = search

    return await client.get(
        f"/projects/{encoded_id}/milestones", params=params
    )


async def create_milestone(
    project_id: str,
    title: str,
    description: str | None = None,
    due_date: str | None = None,
    start_date: str | None = None,
) -> dict[str, Any]:
    """Create a new milestone.

    Args:
        project_id: Project ID or path
        title: Milestone title
        description: Milestone description (Markdown)
        due_date: Due date (YYYY-MM-DD)
        start_date: Start date (YYYY-MM-DD)

    Returns:
        Created milestone details
    """
    client = get_client()
    encoded_id = encode_project_id(project_id)

    data: dict[str, Any] = {"title": title}
    if description:
        data["description"] = description
    if due_date:
        data["due_date"] = due_date
    if start_date:
        data["start_date"] = start_date

    return await client.post(
        f"/projects/{encoded_id}/milestones", json_data=data
    )


async def update_milestone(
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
    client = get_client()
    encoded_id = encode_project_id(project_id)

    data: dict[str, Any] = {}
    if title:
        data["title"] = title
    if description is not None:
        data["description"] = description
    if due_date:
        data["due_date"] = due_date
    if start_date:
        data["start_date"] = start_date
    if state_event:
        data["state_event"] = state_event

    return await client.put(
        f"/projects/{encoded_id}/milestones/{milestone_id}", json_data=data
    )
