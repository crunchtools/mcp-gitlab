"""Search tools.

Tools for global and project-scoped search in GitLab.
"""

from typing import Any

from ..client import get_client
from ..errors import ValidationError
from ..models import SEARCH_SCOPES, encode_project_id


async def search_global(
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
        page: Page number
        per_page: Results per page

    Returns:
        Search results with pagination info
    """
    if not search or not search.strip():
        raise ValidationError("Search query must not be empty")

    if scope not in SEARCH_SCOPES:
        allowed = ", ".join(sorted(SEARCH_SCOPES))
        raise ValidationError(f"Invalid search scope. Allowed: {allowed}")

    client = get_client()

    params: dict[str, Any] = {
        "search": search.strip(),
        "scope": scope,
        "page": page,
        "per_page": min(per_page, 100),
    }

    return await client.get("/search", params=params)


async def search_project(
    project_id: str,
    search: str,
    scope: str = "blobs",
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    """Search within a specific project.

    Args:
        project_id: Project ID or path
        search: Search query string
        scope: Search scope (issues, merge_requests, milestones,
               wiki_blobs, commits, blobs, notes)
        page: Page number
        per_page: Results per page

    Returns:
        Search results with pagination info
    """
    if not search or not search.strip():
        raise ValidationError("Search query must not be empty")

    # Project search has a subset of scopes
    project_scopes = SEARCH_SCOPES - {"projects", "snippet_titles", "users"}
    if scope not in project_scopes:
        allowed = ", ".join(sorted(project_scopes))
        raise ValidationError(f"Invalid project search scope. Allowed: {allowed}")

    client = get_client()
    encoded_id = encode_project_id(project_id)

    params: dict[str, Any] = {
        "search": search.strip(),
        "scope": scope,
        "page": page,
        "per_page": min(per_page, 100),
    }

    return await client.get(f"/projects/{encoded_id}/search", params=params)
