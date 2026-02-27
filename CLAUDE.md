# Claude Code Instructions

Secure MCP server for GitLab REST API v4 with 61 tools across 13 categories. Works with any GitLab instance.

## Quick Start

```bash
# uvx (recommended)
claude mcp add mcp-gitlab-crunchtools \
    --env GITLAB_TOKEN=your_token_here \
    -- uvx mcp-gitlab-crunchtools

# Container
claude mcp add mcp-gitlab-crunchtools \
    --env GITLAB_TOKEN=your_token_here \
    -- podman run -i --rm -e GITLAB_TOKEN quay.io/crunchtools/mcp-gitlab

# Self-hosted GitLab
claude mcp add mcp-gitlab-crunchtools \
    --env GITLAB_TOKEN=your_token_here \
    --env GITLAB_URL=https://gitlab.example.com \
    -- uvx mcp-gitlab-crunchtools

# Local development
cd ~/Projects/crunchtools/mcp-gitlab
claude mcp add mcp-gitlab-crunchtools \
    --env GITLAB_TOKEN=your_token_here \
    -- uv run mcp-gitlab-crunchtools
```

## Creating a GitLab Personal Access Token

1. Log in to your GitLab instance
2. Navigate to Preferences > Access Tokens (or `/-/user_settings/personal_access_tokens`)
3. Create a token named `mcp-gitlab-crunchtools` with 90-day expiry
4. Select scope: `read_api` (read-only) or `api` (full access)
5. Copy the token immediately (starts with `glpat-`, shown only once)

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GITLAB_TOKEN` | Yes | — | Personal Access Token |
| `GITLAB_URL` | No | `https://gitlab.com` | GitLab instance URL |
| `SSL_CERT_FILE` | No | — | Custom CA bundle for self-hosted instances |
| `GITLAB_SSL_VERIFY` | No | `true` | Set `false` to disable SSL verification |

## Available Tools (61)

| Category | Tools | Operations |
|----------|------:|------------|
| Projects | 5 | list, get, branches, branch, commits |
| Groups | 3 | list, get, group projects |
| Merge Requests | 9 | CRUD, notes, discussions, diff |
| Issues | 6 | CRUD, notes |
| Pipelines & Jobs | 11 | CRUD, retry, cancel, delete, job logs |
| Files | 4 | tree, get, create, update |
| Branches | 3 | create, delete, compare |
| Labels | 4 | CRUD |
| Users | 3 | current user, list, get |
| Releases | 3 | list, get, create |
| Milestones | 3 | list, create, update |
| Wiki | 3 | list, get, create |
| Snippets | 2 | list, create |
| Search | 2 | global, project |

Full tool inventory with API endpoints: `.specify/specs/000-baseline/spec.md`

## Example Usage

```
List my GitLab projects
Show open merge requests for group/project
Create an issue titled "Fix login timeout"
Get the diff for MR !42 in my-org/frontend
Show failed pipelines for my-org/api
Trigger a new pipeline on main
Delete the canceled pipelines
Compare branches main and feature/auth
List labels for my-org/backend
Search for "authentication" across all projects
```

## Development

```bash
uv sync --all-extras          # Install dependencies
uv run ruff check src tests   # Lint
uv run mypy src               # Type check
uv run pytest -v              # Tests (98 mocked)
gourmand --full .              # AI slop detection (zero violations)
```

Quality gates, testing standards, and architecture: `.specify/memory/constitution.md`
