"""Group management tools.

Tools for listing and retrieving GitLab group information.
"""

from typing import Any

from ..client import get_client
from ..models import encode_group_id


async def list_groups(
    search: str | None = None,
    owned: bool = False,
    top_level_only: bool = False,
    order_by: str = "name",
    sort: str = "asc",
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    """List groups accessible by the API token.

    Args:
        search: Search for groups by name
        owned: Only list groups owned by the authenticated user
        top_level_only: Only list top-level groups
        order_by: Order by field (name, path, id)
        sort: Sort direction (asc, desc)
        page: Page number
        per_page: Results per page, max 100

    Returns:
        Dictionary containing groups list and pagination info
    """
    client = get_client()

    params: dict[str, Any] = {
        "page": page,
        "per_page": min(per_page, 100),
        "order_by": order_by,
        "sort": sort,
    }

    if search:
        params["search"] = search
    if owned:
        params["owned"] = "true"
    if top_level_only:
        params["top_level_only"] = "true"

    return await client.get("/groups", params=params)


async def get_group(
    group_id: str,
    with_projects: bool = True,
) -> dict[str, Any]:
    """Get group details by ID or path.

    Args:
        group_id: Group ID (numeric) or URL-encoded path
        with_projects: Include group projects (default: true)

    Returns:
        Group details dictionary
    """
    client = get_client()
    encoded_id = encode_group_id(group_id)

    params: dict[str, Any] = {}
    if not with_projects:
        params["with_projects"] = "false"

    return await client.get(f"/groups/{encoded_id}", params=params if params else None)


async def list_group_projects(
    group_id: str,
    search: str | None = None,
    visibility: str | None = None,
    include_subgroups: bool = False,
    order_by: str = "created_at",
    sort: str = "desc",
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    """List projects within a group.

    Args:
        group_id: Group ID or path
        search: Filter projects by name
        visibility: Filter by visibility (public, internal, private)
        include_subgroups: Include projects from subgroups
        order_by: Order by field (created_at, updated_at, name, path)
        sort: Sort direction (asc, desc)
        page: Page number
        per_page: Results per page

    Returns:
        List of projects with pagination info
    """
    client = get_client()
    encoded_id = encode_group_id(group_id)

    params: dict[str, Any] = {
        "page": page,
        "per_page": min(per_page, 100),
        "order_by": order_by,
        "sort": sort,
    }

    if search:
        params["search"] = search
    if visibility:
        params["visibility"] = visibility
    if include_subgroups:
        params["include_subgroups"] = "true"

    return await client.get(f"/groups/{encoded_id}/projects", params=params)
