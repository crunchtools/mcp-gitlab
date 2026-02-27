"""Pipeline management tools.

Tools for listing and inspecting GitLab CI/CD pipelines and jobs.
"""

from typing import Any

from ..client import get_client
from ..models import encode_project_id


async def list_pipelines(
    project_id: str,
    status: str | None = None,
    ref: str | None = None,
    order_by: str = "id",
    sort: str = "desc",
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    """List pipelines for a project.

    Args:
        project_id: Project ID or path
        status: Filter by status (created, waiting_for_resource, preparing,
                pending, running, success, failed, canceled, skipped, manual, scheduled)
        ref: Filter by branch or tag name
        order_by: Order by field (id, status, ref, updated_at, user_id)
        sort: Sort direction (asc, desc)
        page: Page number
        per_page: Results per page

    Returns:
        List of pipelines with pagination info
    """
    client = get_client()
    encoded_id = encode_project_id(project_id)

    params: dict[str, Any] = {
        "order_by": order_by,
        "sort": sort,
        "page": page,
        "per_page": min(per_page, 100),
    }

    if status:
        params["status"] = status
    if ref:
        params["ref"] = ref

    return await client.get(f"/projects/{encoded_id}/pipelines", params=params)


async def get_pipeline(
    project_id: str,
    pipeline_id: int,
) -> dict[str, Any]:
    """Get a single pipeline.

    Args:
        project_id: Project ID or path
        pipeline_id: Pipeline ID

    Returns:
        Pipeline details
    """
    client = get_client()
    encoded_id = encode_project_id(project_id)
    return await client.get(f"/projects/{encoded_id}/pipelines/{pipeline_id}")


async def list_pipeline_jobs(
    project_id: str,
    pipeline_id: int,
    scope: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    """List jobs for a pipeline.

    Args:
        project_id: Project ID or path
        pipeline_id: Pipeline ID
        scope: Filter by job scope (created, pending, running, failed,
               success, canceled, skipped, manual)
        page: Page number
        per_page: Results per page

    Returns:
        List of jobs with pagination info
    """
    client = get_client()
    encoded_id = encode_project_id(project_id)

    params: dict[str, Any] = {
        "page": page,
        "per_page": min(per_page, 100),
    }

    if scope:
        params["scope"] = scope

    return await client.get(
        f"/projects/{encoded_id}/pipelines/{pipeline_id}/jobs", params=params
    )


async def get_job_log(
    project_id: str,
    job_id: int,
) -> dict[str, Any]:
    """Get the log (trace) output of a job.

    Args:
        project_id: Project ID or path
        job_id: Job ID

    Returns:
        Dictionary with job log content
    """
    client = get_client()
    encoded_id = encode_project_id(project_id)
    return await client.get(f"/projects/{encoded_id}/jobs/{job_id}/trace")
