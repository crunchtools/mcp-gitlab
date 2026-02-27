"""Pipeline management tools.

Tools for listing, inspecting, and managing GitLab CI/CD pipelines and jobs.
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


async def create_pipeline(
    project_id: str,
    ref: str = "main",
) -> dict[str, Any]:
    """Create (trigger) a new pipeline.

    Args:
        project_id: Project ID or path
        ref: Branch or tag name to run the pipeline for (default: main)

    Returns:
        Created pipeline details
    """
    client = get_client()
    encoded_id = encode_project_id(project_id)
    return await client.post(
        f"/projects/{encoded_id}/pipeline", json_data={"ref": ref}
    )


async def retry_pipeline(
    project_id: str,
    pipeline_id: int,
) -> dict[str, Any]:
    """Retry all failed jobs in a pipeline.

    Args:
        project_id: Project ID or path
        pipeline_id: Pipeline ID

    Returns:
        Retried pipeline details
    """
    client = get_client()
    encoded_id = encode_project_id(project_id)
    return await client.post(f"/projects/{encoded_id}/pipelines/{pipeline_id}/retry")


async def cancel_pipeline(
    project_id: str,
    pipeline_id: int,
) -> dict[str, Any]:
    """Cancel a running pipeline.

    Args:
        project_id: Project ID or path
        pipeline_id: Pipeline ID

    Returns:
        Canceled pipeline details
    """
    client = get_client()
    encoded_id = encode_project_id(project_id)
    return await client.post(f"/projects/{encoded_id}/pipelines/{pipeline_id}/cancel")


async def delete_pipeline(
    project_id: str,
    pipeline_id: int,
) -> dict[str, Any]:
    """Delete a pipeline and all its jobs.

    Args:
        project_id: Project ID or path
        pipeline_id: Pipeline ID

    Returns:
        Confirmation of deletion
    """
    client = get_client()
    encoded_id = encode_project_id(project_id)
    return await client.delete(f"/projects/{encoded_id}/pipelines/{pipeline_id}")


async def retry_job(
    project_id: str,
    job_id: int,
) -> dict[str, Any]:
    """Retry a specific failed job.

    Args:
        project_id: Project ID or path
        job_id: Job ID

    Returns:
        Retried job details
    """
    client = get_client()
    encoded_id = encode_project_id(project_id)
    return await client.post(f"/projects/{encoded_id}/jobs/{job_id}/retry")


async def cancel_job(
    project_id: str,
    job_id: int,
) -> dict[str, Any]:
    """Cancel a running job.

    Args:
        project_id: Project ID or path
        job_id: Job ID

    Returns:
        Canceled job details
    """
    client = get_client()
    encoded_id = encode_project_id(project_id)
    return await client.post(f"/projects/{encoded_id}/jobs/{job_id}/cancel")


async def delete_job(
    project_id: str,
    job_id: int,
) -> dict[str, Any]:
    """Delete a job's artifacts and trace log.

    Args:
        project_id: Project ID or path
        job_id: Job ID

    Returns:
        Erased job details
    """
    client = get_client()
    encoded_id = encode_project_id(project_id)
    return await client.post(f"/projects/{encoded_id}/jobs/{job_id}/erase")
