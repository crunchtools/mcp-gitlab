"""Release management tools.

Tools for managing GitLab project releases.
"""

from typing import Any

from ..client import get_client
from ..models import encode_project_id


async def list_releases(
    project_id: str,
    order_by: str = "released_at",
    sort: str = "desc",
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    """List releases for a project.

    Args:
        project_id: Project ID or path
        order_by: Order by field (released_at, created_at)
        sort: Sort direction (asc, desc)
        page: Page number
        per_page: Results per page

    Returns:
        List of releases with pagination info
    """
    client = get_client()
    encoded_id = encode_project_id(project_id)

    params: dict[str, Any] = {
        "order_by": order_by,
        "sort": sort,
        "page": page,
        "per_page": min(per_page, 100),
    }

    return await client.get(f"/projects/{encoded_id}/releases", params=params)


async def get_release(
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
    client = get_client()
    encoded_id = encode_project_id(project_id)
    return await client.get(f"/projects/{encoded_id}/releases/{tag_name}")


async def create_release(
    project_id: str,
    tag_name: str,
    name: str | None = None,
    description: str | None = None,
    ref: str | None = None,
    released_at: str | None = None,
) -> dict[str, Any]:
    """Create a new release.

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
    client = get_client()
    encoded_id = encode_project_id(project_id)

    data: dict[str, Any] = {"tag_name": tag_name}
    if name:
        data["name"] = name
    if description:
        data["description"] = description
    if ref:
        data["ref"] = ref
    if released_at:
        data["released_at"] = released_at

    return await client.post(
        f"/projects/{encoded_id}/releases", json_data=data
    )
