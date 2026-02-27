# Baseline Specification: mcp-gitlab-crunchtools

> **Spec ID:** 000-baseline
> **Status:** Implemented
> **Version:** 0.3.2

## Overview

mcp-gitlab-crunchtools is a secure MCP server for the GitLab REST API v4. It provides 61 tools across 13 categories for managing projects, merge requests, issues, pipelines, files, branches, labels, users, releases, milestones, wiki pages, snippets, and search. Works with any GitLab instance (gitlab.com, self-hosted, corporate).

---

## Tool Inventory

### Projects (5 tools)

| Tool | Method | Endpoint | Description |
|------|--------|----------|-------------|
| `list_projects` | GET | `/projects` | List accessible projects |
| `get_project` | GET | `/projects/:id` | Get project details |
| `list_project_branches` | GET | `/projects/:id/repository/branches` | List branches |
| `get_project_branch` | GET | `/projects/:id/repository/branches/:branch` | Get branch details |
| `list_project_commits` | GET | `/projects/:id/repository/commits` | List commits |

### Groups (3 tools)

| Tool | Method | Endpoint | Description |
|------|--------|----------|-------------|
| `list_groups` | GET | `/groups` | List accessible groups |
| `get_group` | GET | `/groups/:id` | Get group details |
| `list_group_projects` | GET | `/groups/:id/projects` | List group projects |

### Merge Requests (9 tools)

| Tool | Method | Endpoint | Description |
|------|--------|----------|-------------|
| `list_merge_requests` | GET | `/projects/:id/merge_requests` | List MRs |
| `get_merge_request` | GET | `/projects/:id/merge_requests/:iid` | Get MR details |
| `create_merge_request` | POST | `/projects/:id/merge_requests` | Create MR |
| `update_merge_request` | PUT | `/projects/:id/merge_requests/:iid` | Update MR |
| `list_mr_notes` | GET | `/projects/:id/merge_requests/:iid/notes` | List MR comments |
| `create_mr_note` | POST | `/projects/:id/merge_requests/:iid/notes` | Add MR comment |
| `get_mr_changes` | GET | `/projects/:id/merge_requests/:iid/changes` | Get MR diff |
| `list_mr_discussions` | GET | `/projects/:id/merge_requests/:iid/discussions` | List threaded discussions |
| `create_mr_discussion` | POST | `/projects/:id/merge_requests/:iid/discussions` | Create discussion |

### Issues (6 tools)

| Tool | Method | Endpoint | Description |
|------|--------|----------|-------------|
| `list_issues` | GET | `/projects/:id/issues` | List issues |
| `get_issue` | GET | `/projects/:id/issues/:iid` | Get issue details |
| `create_issue` | POST | `/projects/:id/issues` | Create issue |
| `update_issue` | PUT | `/projects/:id/issues/:iid` | Update issue |
| `list_issue_notes` | GET | `/projects/:id/issues/:iid/notes` | List issue comments |
| `create_issue_note` | POST | `/projects/:id/issues/:iid/notes` | Add issue comment |

### Pipelines & Jobs (11 tools)

| Tool | Method | Endpoint | Description |
|------|--------|----------|-------------|
| `list_pipelines` | GET | `/projects/:id/pipelines` | List pipelines |
| `get_pipeline` | GET | `/projects/:id/pipelines/:pid` | Get pipeline details |
| `create_pipeline` | POST | `/projects/:id/pipeline` | Trigger new pipeline |
| `retry_pipeline` | POST | `/projects/:id/pipelines/:pid/retry` | Retry failed jobs |
| `cancel_pipeline` | POST | `/projects/:id/pipelines/:pid/cancel` | Cancel running pipeline |
| `delete_pipeline` | DELETE | `/projects/:id/pipelines/:pid` | Delete pipeline |
| `list_pipeline_jobs` | GET | `/projects/:id/pipelines/:pid/jobs` | List jobs (includes stage) |
| `get_job_log` | GET | `/projects/:id/jobs/:jid/trace` | Get job log output |
| `retry_job` | POST | `/projects/:id/jobs/:jid/retry` | Retry specific job |
| `cancel_job` | POST | `/projects/:id/jobs/:jid/cancel` | Cancel running job |
| `delete_job` | POST | `/projects/:id/jobs/:jid/erase` | Erase job artifacts/logs |

### Files (4 tools)

| Tool | Method | Endpoint | Description |
|------|--------|----------|-------------|
| `list_repository_tree` | GET | `/projects/:id/repository/tree` | List files/dirs |
| `get_file` | GET | `/projects/:id/repository/files/:path` | Get file content (base64) |
| `create_file` | POST | `/projects/:id/repository/files/:path` | Create file with commit |
| `update_file` | PUT | `/projects/:id/repository/files/:path` | Update file with commit |

### Branches (3 tools)

| Tool | Method | Endpoint | Description |
|------|--------|----------|-------------|
| `create_branch` | POST | `/projects/:id/repository/branches` | Create branch |
| `delete_branch` | DELETE | `/projects/:id/repository/branches/:branch` | Delete branch |
| `compare_branches` | GET | `/projects/:id/repository/compare` | Compare refs |

### Labels (4 tools)

| Tool | Method | Endpoint | Description |
|------|--------|----------|-------------|
| `list_labels` | GET | `/projects/:id/labels` | List labels |
| `create_label` | POST | `/projects/:id/labels` | Create label |
| `update_label` | PUT | `/projects/:id/labels/:lid` | Update label |
| `delete_label` | DELETE | `/projects/:id/labels/:lid` | Delete label |

### Users (3 tools)

| Tool | Method | Endpoint | Description |
|------|--------|----------|-------------|
| `get_current_user` | GET | `/user` | Get authenticated user |
| `list_users` | GET | `/users` | List/search users |
| `get_user` | GET | `/users/:uid` | Get user by ID |

### Releases (3 tools)

| Tool | Method | Endpoint | Description |
|------|--------|----------|-------------|
| `list_releases` | GET | `/projects/:id/releases` | List releases |
| `get_release` | GET | `/projects/:id/releases/:tag` | Get release by tag |
| `create_release` | POST | `/projects/:id/releases` | Create release |

### Milestones (3 tools)

| Tool | Method | Endpoint | Description |
|------|--------|----------|-------------|
| `list_milestones` | GET | `/projects/:id/milestones` | List milestones |
| `create_milestone` | POST | `/projects/:id/milestones` | Create milestone |
| `update_milestone` | PUT | `/projects/:id/milestones/:mid` | Update milestone |

### Wiki (3 tools)

| Tool | Method | Endpoint | Description |
|------|--------|----------|-------------|
| `list_wiki_pages` | GET | `/projects/:id/wikis` | List wiki pages |
| `get_wiki_page` | GET | `/projects/:id/wikis/:slug` | Get page content |
| `create_wiki_page` | POST | `/projects/:id/wikis` | Create wiki page |

### Snippets (2 tools)

| Tool | Method | Endpoint | Description |
|------|--------|----------|-------------|
| `list_snippets` | GET | `/projects/:id/snippets` | List snippets |
| `create_snippet` | POST | `/projects/:id/snippets` | Create snippet |

### Search (2 tools)

| Tool | Method | Endpoint | Description |
|------|--------|----------|-------------|
| `search_global` | GET | `/search` | Search across all resources |
| `search_project` | GET | `/projects/:id/search` | Search within project |

---

## Security Architecture

### Environment Variables

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `GITLAB_TOKEN` | Yes | — | Personal Access Token |
| `GITLAB_URL` | No | `https://gitlab.com` | GitLab instance URL |
| `SSL_CERT_FILE` | No | — | Custom CA bundle path |
| `GITLAB_SSL_VERIFY` | No | `true` | Disable SSL verification |

### Error Hierarchy

```
UserError (base)
├── ConfigurationError
├── GitLabApiError (sanitizes token from messages)
├── ProjectNotFoundError (truncates long identifiers)
├── PermissionDeniedError
├── RateLimitError (includes retry-after)
└── ValidationError
```

### Input Validation Constants

| Constant | Value | Purpose |
|----------|-------|---------|
| `MAX_TITLE_LENGTH` | 500 | Issue/MR titles |
| `MAX_DESCRIPTION_LENGTH` | 50000 | Issue/MR descriptions |
| `MAX_LABELS_LENGTH` | 1000 | Label strings |
| `MAX_BRANCH_LENGTH` | 255 | Branch names |
| `MAX_ASSIGNEES` | 10 | Assignee/reviewer lists |
| `MAX_RESPONSE_SIZE` | 10MB | Response body limit |
| `REQUEST_TIMEOUT` | 30s | HTTP request timeout |

---

## Module Structure

```
src/mcp_gitlab_crunchtools/
├── __init__.py          # Entry point, argparse (stdio/sse/streamable-http)
├── __main__.py          # python -m entry point
├── client.py            # Hardened httpx async client
├── config.py            # SecretStr config, SSL, URL validation
├── errors.py            # Safe error hierarchy
├── models.py            # Pydantic input validation
├── server.py            # FastMCP tool registrations (61 tools)
└── tools/
    ├── __init__.py      # Re-exports all 61 functions
    ├── branches.py      # create, delete, compare
    ├── files.py         # tree, get, create, update
    ├── groups.py        # list, get, projects
    ├── issues.py        # CRUD + notes
    ├── labels.py        # CRUD
    ├── merge_requests.py # CRUD + notes + discussions + changes
    ├── milestones.py    # list, create, update
    ├── pipelines.py     # CRUD + jobs
    ├── projects.py      # list, get, branches, commits
    ├── releases.py      # list, get, create
    ├── search.py        # global, project
    ├── snippets.py      # list, create
    ├── users.py         # current, list, get
    └── wiki.py          # list, get, create
```

---

## Test Coverage

| Category | Tests | What |
|----------|------:|------|
| Registration | 3 | Imports, callable, count |
| Error safety | 2 | Token sanitization, ID truncation |
| Config safety | 9 | Token, URL, SSL, localhost |
| Mocked API | 52 | All tool groups with httpx mocks |
| Input validation | 22 | ID encoding, Pydantic models |
| Error handling | 4 | 401, 404, 429, 204 |
| **Total** | **98** | |

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2026-02-27 | Initial scaffold: 27 tools |
| 0.2.0 | 2026-02-27 | Pipeline/job write tools, SSL config, 71 tests |
| 0.3.0 | 2026-02-27 | 27 new tools (files, branches, labels, users, etc.), 61 total |
| 0.3.1 | 2026-02-27 | Mocked tests for all tool groups, 98 tests |
| 0.3.2 | 2026-02-27 | Gourmand integration, zero violations, pre-commit hooks |
