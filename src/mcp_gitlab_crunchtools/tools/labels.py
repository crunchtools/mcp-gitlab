"""Label management tools.

Tools for managing GitLab project labels.
"""

from typing import Any

from ..client import get_client
from ..models import encode_project_id


async def list_labels(
    project_id: str,
    search: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    """List labels for a project.

    Args:
        project_id: Project ID or path
        search: Filter labels by keyword
        page: Page number
        per_page: Results per page

    Returns:
        List of labels with pagination info
    """
    client = get_client()
    encoded_id = encode_project_id(project_id)

    params: dict[str, Any] = {
        "page": page,
        "per_page": min(per_page, 100),
    }

    if search:
        params["search"] = search

    return await client.get(f"/projects/{encoded_id}/labels", params=params)


async def create_label(
    project_id: str,
    name: str,
    color: str,
    description: str | None = None,
    priority: int | None = None,
) -> dict[str, Any]:
    """Create a new label in a project.

    Args:
        project_id: Project ID or path
        name: Label name
        color: Color hex code (e.g., "#FF0000") or named color
        description: Label description
        priority: Label priority (lower = higher priority)

    Returns:
        Created label details
    """
    client = get_client()
    encoded_id = encode_project_id(project_id)

    data: dict[str, Any] = {"name": name, "color": color}
    if description:
        data["description"] = description
    if priority is not None:
        data["priority"] = priority

    return await client.post(f"/projects/{encoded_id}/labels", json_data=data)


async def update_label(
    project_id: str,
    label_id: int,
    new_name: str | None = None,
    color: str | None = None,
    description: str | None = None,
    priority: int | None = None,
) -> dict[str, Any]:
    """Update an existing label.

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
    client = get_client()
    encoded_id = encode_project_id(project_id)

    data: dict[str, Any] = {}
    if new_name:
        data["new_name"] = new_name
    if color:
        data["color"] = color
    if description is not None:
        data["description"] = description
    if priority is not None:
        data["priority"] = priority

    return await client.put(
        f"/projects/{encoded_id}/labels/{label_id}", json_data=data
    )


async def delete_label(
    project_id: str,
    label_id: int,
) -> dict[str, Any]:
    """Delete a label from a project.

    Args:
        project_id: Project ID or path
        label_id: Label ID

    Returns:
        Confirmation of deletion
    """
    client = get_client()
    encoded_id = encode_project_id(project_id)
    return await client.delete(f"/projects/{encoded_id}/labels/{label_id}")
