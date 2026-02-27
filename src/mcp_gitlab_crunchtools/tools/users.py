"""User management tools.

Tools for looking up GitLab users and the current authenticated user.
"""

from typing import Any

from ..client import get_client


async def get_current_user() -> dict[str, Any]:
    """Get the currently authenticated user.

    Returns:
        Current user details including ID, username, email, and permissions
    """
    client = get_client()
    return await client.get("/user")


async def list_users(
    search: str | None = None,
    username: str | None = None,
    active: bool = True,
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    """List GitLab users.

    Args:
        search: Search for users by name or email
        username: Filter by exact username
        active: Only return active users (default: true)
        page: Page number
        per_page: Results per page

    Returns:
        List of users with pagination info
    """
    client = get_client()

    params: dict[str, Any] = {
        "page": page,
        "per_page": min(per_page, 100),
    }

    if search:
        params["search"] = search
    if username:
        params["username"] = username
    if active:
        params["active"] = "true"

    return await client.get("/users", params=params)


async def get_user(
    user_id: int,
) -> dict[str, Any]:
    """Get a specific user by ID.

    Args:
        user_id: User ID

    Returns:
        User details including username, name, email, and state
    """
    client = get_client()
    return await client.get(f"/users/{user_id}")
