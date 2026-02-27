# Claude Code Instructions

This is a secure MCP server for GitLab projects, merge requests, issues, pipelines, and search. Works with any GitLab instance (gitlab.com, self-hosted, or enterprise).

## Quick Start

### Option 1: Using uvx (Recommended)

```bash
claude mcp add mcp-gitlab-crunchtools \
    --env GITLAB_TOKEN=your_token_here \
    -- uvx mcp-gitlab-crunchtools
```

### Option 2: Using Container

```bash
claude mcp add mcp-gitlab-crunchtools \
    --env GITLAB_TOKEN=your_token_here \
    -- podman run -i --rm -e GITLAB_TOKEN quay.io/crunchtools/mcp-gitlab
```

### Option 3: Self-Hosted GitLab

```bash
claude mcp add mcp-gitlab-crunchtools \
    --env GITLAB_TOKEN=your_token_here \
    --env GITLAB_URL=https://gitlab.example.com \
    -- uvx mcp-gitlab-crunchtools
```

### Option 4: Local Development

```bash
cd ~/Projects/crunchtools/mcp-gitlab
claude mcp add mcp-gitlab-crunchtools \
    --env GITLAB_TOKEN=your_token_here \
    -- uv run mcp-gitlab-crunchtools
```

## Creating a GitLab Personal Access Token

### Step-by-Step Instructions

1. **Log in to your GitLab instance**
   - Go to https://gitlab.com (or your self-hosted URL)
   - Sign in with your account

2. **Navigate to Access Tokens**
   - Click your avatar (top left)
   - Select "Preferences"
   - Click "Access Tokens" in the left sidebar
   - Or go directly to: https://gitlab.com/-/user_settings/personal_access_tokens

3. **Create a new token**
   - **Token name**: `mcp-gitlab-crunchtools`
   - **Expiration date**: Set an appropriate expiry (recommended: 90 days)
   - **Scopes**: Select the scopes you need (see below)

4. **Copy Your Token**
   - **IMPORTANT: Copy the token immediately!**
   - The token starts with `glpat-` and is only shown once
   - Store it securely (password manager recommended)

### Scope Selection

#### Read-Only (safest)
- `read_api` — Read access to projects, issues, MRs, pipelines

#### Full Management (all MCP server features)
- `api` — Full API access for creating/updating issues, MRs, and notes

### Security Best Practices

- **Principle of least privilege**: Use `read_api` if you only need to read
- **Set expiration**: Always set an expiry date on tokens
- **Rotate regularly**: Create new tokens periodically and revoke old ones
- **Never commit tokens**: Don't put tokens in code or config files in git

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GITLAB_TOKEN` | Yes | — | Personal Access Token (starts with `glpat-`) |
| `GITLAB_URL` | No | `https://gitlab.com` | GitLab instance URL |

## Available Tools (27 tools)

### Project Management (5 tools)
- `list_projects` - List projects with filtering and search
- `get_project` - Get project details by ID or path
- `list_project_branches` - List repository branches
- `get_project_branch` - Get a single branch
- `list_project_commits` - List commits with date/path filtering

### Group Management (3 tools)
- `list_groups` - List groups with filtering
- `get_group` - Get group details by ID or path
- `list_group_projects` - List projects in a group (with subgroup support)

### Merge Requests (7 tools)
- `list_merge_requests` - List MRs by state, labels, milestone
- `get_merge_request` - Get MR details
- `create_merge_request` - Create a new MR
- `update_merge_request` - Update MR title, description, state, assignees
- `list_mr_notes` - List comments on an MR
- `create_mr_note` - Add a comment to an MR
- `get_mr_changes` - Get the diff for an MR

### Issues (6 tools)
- `list_issues` - List issues by state, labels, milestone, assignee
- `get_issue` - Get issue details
- `create_issue` - Create a new issue
- `update_issue` - Update issue title, description, state, labels
- `list_issue_notes` - List comments on an issue
- `create_issue_note` - Add a comment to an issue

### Pipelines (4 tools)
- `list_pipelines` - List CI/CD pipelines with status filtering
- `get_pipeline` - Get pipeline details
- `list_pipeline_jobs` - List jobs in a pipeline
- `get_job_log` - Get job log output

### Search (2 tools)
- `search_global` - Search across all accessible GitLab resources
- `search_project` - Search within a specific project

## Example Usage

```
User: List my GitLab projects
User: Show open merge requests for group/project
User: Create an issue in my-org/backend titled "Fix login timeout"
User: Get the diff for MR !42 in my-org/frontend
User: Show failed pipelines for my-org/api
User: Search for "authentication" in project my-org/backend
```

## Development

```bash
# Install dependencies
uv sync --all-extras

# Run tests
uv run pytest

# Lint
uv run ruff check src tests

# Type check
uv run mypy src
```
