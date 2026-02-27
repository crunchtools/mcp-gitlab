"""Wiki management tools.

Tools for managing GitLab project wiki pages.
"""

from typing import Any
from urllib.parse import quote

from ..client import get_client
from ..models import encode_project_id


async def list_wiki_pages(
    project_id: str,
    with_content: bool = False,
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    """List wiki pages for a project.

    Args:
        project_id: Project ID or path
        with_content: Include page content in response (default: false)
        page: Page number
        per_page: Results per page

    Returns:
        List of wiki pages with pagination info
    """
    client = get_client()
    encoded_id = encode_project_id(project_id)

    params: dict[str, Any] = {
        "page": page,
        "per_page": min(per_page, 100),
    }

    if with_content:
        params["with_content"] = "1"

    return await client.get(
        f"/projects/{encoded_id}/wikis", params=params
    )


async def get_wiki_page(
    project_id: str,
    slug: str,
) -> dict[str, Any]:
    """Get a single wiki page by slug.

    Args:
        project_id: Project ID or path
        slug: URL slug of the wiki page

    Returns:
        Wiki page details including content
    """
    client = get_client()
    encoded_id = encode_project_id(project_id)
    encoded_slug = quote(slug, safe="")
    return await client.get(f"/projects/{encoded_id}/wikis/{encoded_slug}")


async def create_wiki_page(
    project_id: str,
    title: str,
    content: str,
    format: str = "markdown",
) -> dict[str, Any]:
    """Create a new wiki page.

    Args:
        project_id: Project ID or path
        title: Page title
        content: Page content
        format: Content format - markdown, rdoc, asciidoc, or org (default: markdown)

    Returns:
        Created wiki page details
    """
    client = get_client()
    encoded_id = encode_project_id(project_id)
    return await client.post(
        f"/projects/{encoded_id}/wikis",
        json_data={
            "title": title,
            "content": content,
            "format": format,
        },
    )
