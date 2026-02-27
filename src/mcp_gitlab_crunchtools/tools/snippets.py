"""Snippet management tools.

Tools for managing GitLab project snippets (shared code fragments).
"""

from typing import Any

from ..client import get_client
from ..models import encode_project_id


async def list_snippets(
    project_id: str,
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    """List snippets for a project.

    Args:
        project_id: Project ID or path
        page: Page number
        per_page: Results per page

    Returns:
        List of snippets with pagination info
    """
    client = get_client()
    encoded_id = encode_project_id(project_id)

    params: dict[str, Any] = {
        "page": page,
        "per_page": min(per_page, 100),
    }

    return await client.get(
        f"/projects/{encoded_id}/snippets", params=params
    )


async def create_snippet(
    project_id: str,
    title: str,
    file_name: str,
    content: str,
    description: str | None = None,
    visibility: str = "private",
) -> dict[str, Any]:
    """Create a new snippet in a project.

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
    client = get_client()
    encoded_id = encode_project_id(project_id)

    data: dict[str, Any] = {
        "title": title,
        "files": [{"file_path": file_name, "content": content}],
        "visibility": visibility,
    }
    if description:
        data["description"] = description

    return await client.post(
        f"/projects/{encoded_id}/snippets", json_data=data
    )
