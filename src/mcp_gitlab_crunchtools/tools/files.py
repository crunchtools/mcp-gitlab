"""Repository file management tools.

Tools for reading, creating, and updating files in GitLab repositories.
"""

from typing import Any
from urllib.parse import quote

from ..client import get_client
from ..models import encode_project_id


async def list_repository_tree(
    project_id: str,
    path: str = "",
    ref: str | None = None,
    recursive: bool = False,
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    """List repository tree (files and directories).

    Args:
        project_id: Project ID or path
        path: Path inside the repository (default: root)
        ref: Branch, tag, or commit SHA (default: default branch)
        recursive: List files recursively
        page: Page number
        per_page: Results per page

    Returns:
        List of tree entries (blobs and trees) with pagination info
    """
    client = get_client()
    encoded_id = encode_project_id(project_id)

    params: dict[str, Any] = {
        "page": page,
        "per_page": min(per_page, 100),
    }

    if path:
        params["path"] = path
    if ref:
        params["ref"] = ref
    if recursive:
        params["recursive"] = "true"

    return await client.get(
        f"/projects/{encoded_id}/repository/tree", params=params
    )


async def get_file(
    project_id: str,
    file_path: str,
    ref: str = "HEAD",
) -> dict[str, Any]:
    """Get a file from the repository.

    Returns file metadata and content (base64 encoded).

    Args:
        project_id: Project ID or path
        file_path: Path to the file in the repository
        ref: Branch, tag, or commit SHA (default: HEAD)

    Returns:
        File metadata including content (base64), size, encoding
    """
    client = get_client()
    encoded_id = encode_project_id(project_id)
    encoded_path = quote(file_path, safe="")
    return await client.get(
        f"/projects/{encoded_id}/repository/files/{encoded_path}",
        params={"ref": ref},
    )


async def create_file(
    project_id: str,
    file_path: str,
    branch: str,
    content: str,
    commit_message: str,
    encoding: str = "text",
) -> dict[str, Any]:
    """Create a new file in the repository.

    Args:
        project_id: Project ID or path
        file_path: Path for the new file
        branch: Branch to commit to
        content: File content (text or base64 depending on encoding)
        commit_message: Commit message
        encoding: Content encoding - "text" or "base64" (default: text)

    Returns:
        Created file metadata
    """
    client = get_client()
    encoded_id = encode_project_id(project_id)
    encoded_path = quote(file_path, safe="")
    return await client.post(
        f"/projects/{encoded_id}/repository/files/{encoded_path}",
        json_data={
            "branch": branch,
            "content": content,
            "commit_message": commit_message,
            "encoding": encoding,
        },
    )


async def update_file(
    project_id: str,
    file_path: str,
    branch: str,
    content: str,
    commit_message: str,
    encoding: str = "text",
) -> dict[str, Any]:
    """Update an existing file in the repository.

    Args:
        project_id: Project ID or path
        file_path: Path to the file
        branch: Branch to commit to
        content: New file content
        commit_message: Commit message
        encoding: Content encoding - "text" or "base64" (default: text)

    Returns:
        Updated file metadata
    """
    client = get_client()
    encoded_id = encode_project_id(project_id)
    encoded_path = quote(file_path, safe="")
    return await client.put(
        f"/projects/{encoded_id}/repository/files/{encoded_path}",
        json_data={
            "branch": branch,
            "content": content,
            "commit_message": commit_message,
            "encoding": encoding,
        },
    )
