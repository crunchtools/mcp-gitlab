"""Merge request management tools.

Tools for listing, creating, and updating GitLab merge requests.
"""

from typing import Any

from ..client import get_client
from ..errors import GitLabApiError, MergeRefusedError, PermissionDeniedError
from ..models import (
    CreateMergeRequestInput,
    MergeMergeRequestInput,
    UpdateMergeRequestInput,
    encode_project_id,
)

# What GitLab's merge endpoint means by each refusal.
_MERGE_REFUSALS = {
    405: "it cannot be merged (draft, closed, blocked, or its pipeline must pass first)",
    406: "it has a conflict with the target branch",
    409: "the source branch head no longer matches sha",
    422: "it cannot be merged in its current state",
}


async def list_merge_requests(
    *,
    project_id: str,
    state: str = "opened",
    order_by: str = "created_at",
    sort: str = "desc",
    labels: str | None = None,
    milestone: str | None = None,
    search: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    """List merge requests for a project.

    Args:
        project_id: Project ID or path
        state: Filter by state (opened, closed, merged, all)
        order_by: Order by field (created_at, updated_at)
        sort: Sort direction (asc, desc)
        labels: Comma-separated label names
        milestone: Milestone title
        search: Search in title and description
        page: Page number
        per_page: Results per page

    Returns:
        List of merge requests with pagination info
    """
    client = get_client()
    encoded_id = encode_project_id(project_id)

    params: dict[str, Any] = {
        "state": state,
        "order_by": order_by,
        "sort": sort,
        "page": page,
        "per_page": min(per_page, 100),
    }

    if labels:
        params["labels"] = labels
    if milestone:
        params["milestone"] = milestone
    if search:
        params["search"] = search

    return await client.get(f"/projects/{encoded_id}/merge_requests", params=params)


async def get_merge_request(
    project_id: str,
    merge_request_iid: int,
) -> dict[str, Any]:
    """Get a single merge request.

    Args:
        project_id: Project ID or path
        merge_request_iid: Merge request internal ID (the number shown in the UI)

    Returns:
        Merge request details
    """
    client = get_client()
    encoded_id = encode_project_id(project_id)
    return await client.get(f"/projects/{encoded_id}/merge_requests/{merge_request_iid}")


async def create_merge_request(
    *,
    project_id: str,
    source_branch: str,
    target_branch: str,
    title: str,
    description: str | None = None,
    labels: str | None = None,
    assignee_ids: list[int] | None = None,
    reviewer_ids: list[int] | None = None,
    milestone_id: int | None = None,
    remove_source_branch: bool = False,
) -> dict[str, Any]:
    """Create a new merge request.

    Args:
        project_id: Project ID or path
        source_branch: Source branch name
        target_branch: Target branch name
        title: MR title
        description: MR description (Markdown)
        labels: Comma-separated label names
        assignee_ids: User IDs to assign
        reviewer_ids: User IDs to review
        milestone_id: Milestone ID
        remove_source_branch: Remove source branch after merge

    Returns:
        Created merge request details
    """
    validated = CreateMergeRequestInput(
        source_branch=source_branch,
        target_branch=target_branch,
        title=title,
        description=description,
        labels=labels,
        assignee_ids=assignee_ids,
        reviewer_ids=reviewer_ids,
        milestone_id=milestone_id,
        remove_source_branch=remove_source_branch,
    )

    client = get_client()
    encoded_id = encode_project_id(project_id)

    payload: dict[str, Any] = {
        "source_branch": validated.source_branch,
        "target_branch": validated.target_branch,
        "title": validated.title,
    }

    if validated.description is not None:
        payload["description"] = validated.description
    if validated.labels is not None:
        payload["labels"] = validated.labels
    if validated.assignee_ids is not None:
        payload["assignee_ids"] = validated.assignee_ids
    if validated.reviewer_ids is not None:
        payload["reviewer_ids"] = validated.reviewer_ids
    if validated.milestone_id is not None:
        payload["milestone_id"] = validated.milestone_id
    if validated.remove_source_branch:
        payload["remove_source_branch"] = True

    return await client.post(f"/projects/{encoded_id}/merge_requests", json_data=payload)


async def update_merge_request(
    *,
    project_id: str,
    merge_request_iid: int,
    title: str | None = None,
    description: str | None = None,
    labels: str | None = None,
    state_event: str | None = None,
    assignee_ids: list[int] | None = None,
    reviewer_ids: list[int] | None = None,
    milestone_id: int | None = None,
    target_branch: str | None = None,
    remove_source_branch: bool | None = None,
) -> dict[str, Any]:
    """Update an existing merge request.

    Args:
        project_id: Project ID or path
        merge_request_iid: Merge request internal ID
        title: MR title
        description: MR description (Markdown)
        labels: Comma-separated label names
        state_event: State transition (close, reopen)
        assignee_ids: User IDs to assign
        reviewer_ids: User IDs to review
        milestone_id: Milestone ID
        target_branch: Target branch
        remove_source_branch: Remove source branch after merge

    Returns:
        Updated merge request details
    """
    validated = UpdateMergeRequestInput(
        title=title,
        description=description,
        labels=labels,
        state_event=state_event,
        assignee_ids=assignee_ids,
        reviewer_ids=reviewer_ids,
        milestone_id=milestone_id,
        target_branch=target_branch,
        remove_source_branch=remove_source_branch,
    )

    client = get_client()
    encoded_id = encode_project_id(project_id)

    payload: dict[str, Any] = {}
    if validated.title is not None:
        payload["title"] = validated.title
    if validated.description is not None:
        payload["description"] = validated.description
    if validated.labels is not None:
        payload["labels"] = validated.labels
    if validated.state_event is not None:
        payload["state_event"] = validated.state_event
    if validated.assignee_ids is not None:
        payload["assignee_ids"] = validated.assignee_ids
    if validated.reviewer_ids is not None:
        payload["reviewer_ids"] = validated.reviewer_ids
    if validated.milestone_id is not None:
        payload["milestone_id"] = validated.milestone_id
    if validated.target_branch is not None:
        payload["target_branch"] = validated.target_branch
    if validated.remove_source_branch is not None:
        payload["remove_source_branch"] = validated.remove_source_branch

    return await client.put(
        f"/projects/{encoded_id}/merge_requests/{merge_request_iid}", json_data=payload
    )


async def list_mr_notes(
    *,
    project_id: str,
    merge_request_iid: int,
    order_by: str = "created_at",
    sort: str = "desc",
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    """List notes (comments) on a merge request.

    Args:
        project_id: Project ID or path
        merge_request_iid: Merge request internal ID
        order_by: Order by field (created_at, updated_at)
        sort: Sort direction (asc, desc)
        page: Page number
        per_page: Results per page

    Returns:
        List of notes with pagination info
    """
    client = get_client()
    encoded_id = encode_project_id(project_id)

    params: dict[str, Any] = {
        "order_by": order_by,
        "sort": sort,
        "page": page,
        "per_page": min(per_page, 100),
    }

    return await client.get(
        f"/projects/{encoded_id}/merge_requests/{merge_request_iid}/notes", params=params
    )


async def create_mr_note(
    project_id: str,
    merge_request_iid: int,
    body: str,
) -> dict[str, Any]:
    """Create a note (comment) on a merge request.

    Args:
        project_id: Project ID or path
        merge_request_iid: Merge request internal ID
        body: Note content (Markdown)

    Returns:
        Created note details
    """
    if not body or not body.strip():
        raise ValueError("Note body must not be empty")

    client = get_client()
    encoded_id = encode_project_id(project_id)

    return await client.post(
        f"/projects/{encoded_id}/merge_requests/{merge_request_iid}/notes",
        json_data={"body": body},
    )


async def get_mr_changes(
    project_id: str,
    merge_request_iid: int,
) -> dict[str, Any]:
    """Get the changes (diff) for a merge request.

    Args:
        project_id: Project ID or path
        merge_request_iid: Merge request internal ID

    Returns:
        Merge request details with diff changes
    """
    client = get_client()
    encoded_id = encode_project_id(project_id)
    return await client.get(f"/projects/{encoded_id}/merge_requests/{merge_request_iid}/changes")


async def list_mr_discussions(
    project_id: str,
    merge_request_iid: int,
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    """List discussions (threaded comments) on a merge request.

    Discussions include inline code review comments with position data.

    Args:
        project_id: Project ID or path
        merge_request_iid: Merge request internal ID
        page: Page number
        per_page: Results per page

    Returns:
        List of discussions with notes and position info
    """
    client = get_client()
    encoded_id = encode_project_id(project_id)

    params: dict[str, Any] = {
        "page": page,
        "per_page": min(per_page, 100),
    }

    return await client.get(
        f"/projects/{encoded_id}/merge_requests/{merge_request_iid}/discussions",
        params=params,
    )


async def create_mr_discussion(
    project_id: str,
    merge_request_iid: int,
    body: str,
) -> dict[str, Any]:
    """Create a new discussion on a merge request.

    Args:
        project_id: Project ID or path
        merge_request_iid: Merge request internal ID
        body: Discussion body (Markdown)

    Returns:
        Created discussion details
    """
    client = get_client()
    encoded_id = encode_project_id(project_id)
    return await client.post(
        f"/projects/{encoded_id}/merge_requests/{merge_request_iid}/discussions",
        json_data={"body": body},
    )


async def merge_merge_request(
    *,
    project_id: str,
    merge_request_iid: int,
    sha: str,
    merge_when_pipeline_succeeds: bool = False,
    squash: bool | None = None,
    should_remove_source_branch: bool | None = None,
) -> dict[str, Any]:
    """Merge a merge request, or set it to merge when its pipeline succeeds.

    ``sha`` is required: GitLab merges only if the source branch head is still
    that commit, so the branch cannot move between review and merge. A draft,
    a conflict, a closed MR or a moved head is refused before the merge is sent.

    Args:
        project_id: Project ID or path
        merge_request_iid: Merge request internal ID
        sha: Full commit ID the source branch head must be
        merge_when_pipeline_succeeds: Merge once the head pipeline passes
        squash: Squash commits on merge (None keeps the MR's setting)
        should_remove_source_branch: Remove the source branch (None keeps the MR's setting)

    Returns:
        The merge outcome: merged, or the auto-merge status

    Raises:
        pydantic.ValidationError: ``sha`` is not a full 40- or 64-character
            commit ID (raised before any request).
        MergeRefusedError: the MR is a draft, has a conflict, is not open, or
            its head is not ``sha``; or GitLab refused the merge (405, 406,
            409 or 422).
        GitLabApiError: any other GitLab failure, unchanged.
    """
    validated = MergeMergeRequestInput(
        sha=sha,
        merge_when_pipeline_succeeds=merge_when_pipeline_succeeds,
        squash=squash,
        should_remove_source_branch=should_remove_source_branch,
    )

    client = get_client()
    encoded_id = encode_project_id(project_id)
    path = f"/projects/{encoded_id}/merge_requests/{merge_request_iid}"

    mr = await client.get(path)
    if mr.get("state") != "opened":
        raise MergeRefusedError(merge_request_iid, f"it is not open (state: {mr.get('state')})")
    if mr.get("draft") or mr.get("work_in_progress"):
        raise MergeRefusedError(merge_request_iid, "it is a draft")
    if mr.get("has_conflicts"):
        raise MergeRefusedError(merge_request_iid, "it has a conflict with the target branch")
    if str(mr.get("sha", "")).lower() != validated.sha:
        raise MergeRefusedError(merge_request_iid, "the source branch head no longer matches sha")

    payload: dict[str, Any] = {
        "sha": validated.sha,
        "merge_when_pipeline_succeeds": validated.merge_when_pipeline_succeeds,
    }
    if validated.squash is not None:
        payload["squash"] = validated.squash
    if validated.should_remove_source_branch is not None:
        payload["should_remove_source_branch"] = validated.should_remove_source_branch

    try:
        result = await client.put(f"{path}/merge", json_data=payload)
    except PermissionDeniedError as e:
        # The GET above succeeded with this token, so a 401/403 here means
        # the user may not merge this MR, not that the token is bad.
        raise MergeRefusedError(merge_request_iid, "this user may not merge it") from e
    except GitLabApiError as e:
        if e.code in _MERGE_REFUSALS:
            raise MergeRefusedError(merge_request_iid, _MERGE_REFUSALS[e.code]) from e
        raise

    return {
        "iid": result.get("iid", merge_request_iid),
        "state": result.get("state"),
        "merged": result.get("state") == "merged",
        "auto_merge": bool(result.get("merge_when_pipeline_succeeds")),
        "detailed_merge_status": result.get("detailed_merge_status"),
        "sha": result.get("sha"),
        "merge_commit_sha": result.get("merge_commit_sha"),
        "squash_commit_sha": result.get("squash_commit_sha"),
        "web_url": result.get("web_url"),
    }


async def get_mr_pipelines(
    project_id: str,
    merge_request_iid: int,
    page: int = 1,
    per_page: int = 20,
) -> dict[str, Any]:
    """List the pipelines of a merge request, newest first.

    Each carries the ``sha`` it ran on and its ``status``, so a caller can
    confirm the head commit passed before merging it.

    Args:
        project_id: Project ID or path
        merge_request_iid: Merge request internal ID
        page: Page number
        per_page: Results per page

    Returns:
        List of pipelines with pagination info
    """
    client = get_client()
    encoded_id = encode_project_id(project_id)

    params: dict[str, Any] = {
        "page": page,
        "per_page": min(per_page, 100),
    }

    return await client.get(
        f"/projects/{encoded_id}/merge_requests/{merge_request_iid}/pipelines", params=params
    )
