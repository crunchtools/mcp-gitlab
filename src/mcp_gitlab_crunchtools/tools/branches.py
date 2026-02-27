"""Branch management tools.

Tools for creating, deleting, and comparing GitLab repository branches.
"""

from typing import Any
from urllib.parse import quote

from ..client import get_client
from ..models import encode_project_id


async def create_branch(
    project_id: str,
    branch: str,
    ref: str,
) -> dict[str, Any]:
    """Create a new branch in a repository.

    Args:
        project_id: Project ID or path
        branch: Name of the new branch
        ref: Branch name or commit SHA to create from

    Returns:
        Created branch details
    """
    client = get_client()
    encoded_id = encode_project_id(project_id)
    return await client.post(
        f"/projects/{encoded_id}/repository/branches",
        json_data={"branch": branch, "ref": ref},
    )


async def delete_branch(
    project_id: str,
    branch: str,
) -> dict[str, Any]:
    """Delete a branch from a repository.

    Args:
        project_id: Project ID or path
        branch: Branch name to delete

    Returns:
        Confirmation of deletion
    """
    client = get_client()
    encoded_id = encode_project_id(project_id)
    encoded_branch = quote(branch, safe="")
    return await client.delete(
        f"/projects/{encoded_id}/repository/branches/{encoded_branch}"
    )


async def compare_branches(
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
    client = get_client()
    encoded_id = encode_project_id(project_id)

    params: dict[str, Any] = {
        "from": from_ref,
        "to": to_ref,
    }
    if straight:
        params["straight"] = "true"

    return await client.get(
        f"/projects/{encoded_id}/repository/compare", params=params
    )
