"""Project management tools.

Tools for listing and retrieving GitLab project information,
branches, and commits.
"""

from typing import Any

from ..client import get_client
from ..models import CreateProjectInput, encode_project_id


async def list_projects(
    search: str | None = None,
    owned: bool = False,
    membership: bool = False,
    visibility: str | None = None,
    order_by: str = "created_at",
    sort: str = "desc",
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    """List projects accessible by the API token.

    Args:
        search: Search for projects by name
        owned: Only list projects owned by the authenticated user
        membership: Only list projects the user is a member of
        visibility: Filter by visibility (public, internal, private)
        order_by: Order by field (created_at, updated_at, name, path)
        sort: Sort direction (asc, desc)
        page: Page number for pagination
        per_page: Results per page, max 100

    Returns:
        Dictionary containing projects list and pagination info
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
    if membership:
        params["membership"] = "true"
    if visibility:
        params["visibility"] = visibility

    return await client.get("/projects", params=params)


async def get_project(
    project_id: str,
) -> dict[str, Any]:
    """Get project details by ID or path.

    Args:
        project_id: Project ID (numeric) or URL-encoded path (e.g., "group/project")

    Returns:
        Project details dictionary
    """
    client = get_client()
    encoded_id = encode_project_id(project_id)
    return await client.get(f"/projects/{encoded_id}")


async def list_project_branches(
    project_id: str,
    search: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    """List repository branches for a project.

    Args:
        project_id: Project ID or path
        search: Filter branches by name
        page: Page number
        per_page: Results per page

    Returns:
        List of branches with pagination info
    """
    client = get_client()
    encoded_id = encode_project_id(project_id)

    params: dict[str, Any] = {
        "page": page,
        "per_page": min(per_page, 100),
    }

    if search:
        params["search"] = search

    return await client.get(f"/projects/{encoded_id}/repository/branches", params=params)


async def get_project_branch(
    project_id: str,
    branch: str,
) -> dict[str, Any]:
    """Get a single repository branch.

    Args:
        project_id: Project ID or path
        branch: Branch name

    Returns:
        Branch details
    """
    client = get_client()
    encoded_id = encode_project_id(project_id)
    return await client.get(f"/projects/{encoded_id}/repository/branches/{branch}")


async def list_project_commits(
    project_id: str,
    ref_name: str | None = None,
    since: str | None = None,
    until: str | None = None,
    path: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    """List repository commits for a project.

    Args:
        project_id: Project ID or path
        ref_name: Branch or tag name (default: default branch)
        since: Only commits after this date (ISO 8601)
        until: Only commits before this date (ISO 8601)
        path: Only commits touching this file path
        page: Page number
        per_page: Results per page

    Returns:
        List of commits with pagination info
    """
    client = get_client()
    encoded_id = encode_project_id(project_id)

    params: dict[str, Any] = {
        "page": page,
        "per_page": min(per_page, 100),
    }

    if ref_name:
        params["ref_name"] = ref_name
    if since:
        params["since"] = since
    if until:
        params["until"] = until
    if path:
        params["path"] = path

    return await client.get(f"/projects/{encoded_id}/repository/commits", params=params)


async def create_project(
    name: str,
    description: str | None = None,
    visibility: str = "private",
    initialize_with_readme: bool = False,
    namespace_id: int | None = None,
) -> dict[str, Any]:
    """Create a new project.

    Args:
        name: Project name
        description: Project description
        visibility: Visibility level (public, internal, private)
        initialize_with_readme: Initialize with a README file
        namespace_id: Namespace ID to create the project under (group or user)

    Returns:
        Created project details
    """
    validated = CreateProjectInput(
        name=name,
        description=description,
        visibility=visibility,
        initialize_with_readme=initialize_with_readme,
        namespace_id=namespace_id,
    )

    client = get_client()

    data: dict[str, Any] = {
        "name": validated.name,
        "visibility": validated.visibility,
    }

    if validated.description is not None:
        data["description"] = validated.description
    if validated.initialize_with_readme:
        data["initialize_with_readme"] = True
    if validated.namespace_id is not None:
        data["namespace_id"] = validated.namespace_id

    return await client.post("/projects", json_data=data)


async def delete_project(
    project_id: str,
) -> dict[str, Any]:
    """Delete a project.

    Args:
        project_id: Project ID (numeric) or URL-encoded path (e.g., "group/project")

    Returns:
        Confirmation of deletion
    """
    client = get_client()
    encoded_id = encode_project_id(project_id)
    return await client.delete(f"/projects/{encoded_id}")
