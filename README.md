# MCP GitLab CrunchTools

A secure MCP (Model Context Protocol) server for GitLab projects, merge requests, issues, pipelines, and search. Works with any GitLab instance (gitlab.com, self-hosted, or enterprise).

## Overview

This MCP server is designed to be:

- **Secure by default** - Comprehensive threat modeling, input validation, and token protection
- **No third-party services** - Runs locally via stdio, your API token never leaves your machine
- **Multi-instance** - Works with gitlab.com, self-hosted GitLab, or enterprise instances via configurable URL
- **Cross-platform** - Works on Linux, macOS, and Windows
- **Automatically updated** - GitHub Actions monitor for CVEs and update dependencies
- **Containerized** - Available at `quay.io/crunchtools/mcp-gitlab` built on [Hummingbird Python](https://quay.io/repository/hummingbird/python) base image

## Naming Convention

| Component | Name |
|-----------|------|
| GitHub repo | [crunchtools/mcp-gitlab](https://github.com/crunchtools/mcp-gitlab) |
| Container | `quay.io/crunchtools/mcp-gitlab` |
| Python package (PyPI) | `mcp-gitlab-crunchtools` |
| CLI command | `mcp-gitlab-crunchtools` |
| Module import | `mcp_gitlab_crunchtools` |

## Why Hummingbird?

The container image is built on the [Hummingbird Python base image](https://quay.io/repository/hummingbird/python) from [Project Hummingbird](https://github.com/hummingbird-project), which provides:

- **Minimal CVE exposure** - Built with a minimal package set, dramatically reducing the attack surface
- **Regular updates** - Security patches are applied promptly
- **Optimized for Python** - Pre-configured Python environment with uv package manager
- **Production-ready** - Proper signal handling and non-root user defaults

## Features

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

## Installation

### With uvx (Recommended)

```bash
uvx mcp-gitlab-crunchtools
```

### With pip

```bash
pip install mcp-gitlab-crunchtools
```

### With Container

```bash
podman run -e GITLAB_TOKEN=your_token \
    quay.io/crunchtools/mcp-gitlab
```

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GITLAB_TOKEN` | Yes | — | Personal Access Token |
| `GITLAB_URL` | No | `https://gitlab.com` | GitLab instance URL |

### Creating a GitLab Personal Access Token

1. **Navigate to Access Tokens**
   - Go to https://gitlab.com/-/user_settings/personal_access_tokens
   - Or: Avatar > Preferences > Access Tokens

2. **Create a Custom Token**
   - **Name**: `mcp-gitlab-crunchtools`
   - **Expiration**: Set an appropriate date (90 days recommended)
   - **Scopes**: Select scopes based on your needs

3. **Scope Selection**

   | Scope | Access Level | Capabilities |
   |-------|-------------|--------------|
   | `read_api` | Read-only | List/view projects, issues, MRs, pipelines |
   | `api` | Full access | All features including create/update |

4. **Copy and Store Token**
   - Copy the token immediately (starts with `glpat-`)
   - Store securely in a password manager

### Add to Claude Code

```bash
claude mcp add mcp-gitlab-crunchtools \
    --env GITLAB_TOKEN=your_token_here \
    -- uvx mcp-gitlab-crunchtools
```

For self-hosted GitLab:

```bash
claude mcp add mcp-gitlab-crunchtools \
    --env GITLAB_TOKEN=your_token_here \
    --env GITLAB_URL=https://gitlab.example.com \
    -- uvx mcp-gitlab-crunchtools
```

For the container version:

```bash
claude mcp add mcp-gitlab-crunchtools \
    --env GITLAB_TOKEN=your_token_here \
    -- podman run -i --rm -e GITLAB_TOKEN quay.io/crunchtools/mcp-gitlab
```

## Usage Examples

### List Your Projects

```
User: List my GitLab projects
Assistant: [calls list_projects with membership=true]
```

### View Merge Requests

```
User: Show open merge requests for my-org/backend
Assistant: [calls list_merge_requests with project_id="my-org/backend"]
```

### Create an Issue

```
User: Create an issue in my-org/backend titled "Fix login timeout"
Assistant: [calls create_issue with title="Fix login timeout"]
```

### Check Pipeline Status

```
User: Show failed pipelines for my-org/api
Assistant: [calls list_pipelines with status="failed"]
```

### Search Code

```
User: Search for "authentication" in my-org/backend
Assistant: [calls search_project with scope="blobs"]
```

## Security

This server was designed with security as a primary concern. See [SECURITY.md](SECURITY.md) for:

- Threat model and attack vectors
- Defense in depth architecture
- Token handling best practices
- Input validation rules
- Audit logging

### Key Security Features

1. **Token Protection**
   - Stored as SecretStr (never accidentally logged)
   - Environment variable only (never in files or args)
   - Sanitized from all error messages

2. **Input Validation**
   - Pydantic models for all inputs
   - Allowlist character validation for project/group IDs
   - Path traversal prevention

3. **API Hardening**
   - HTTPS enforcement (except localhost)
   - TLS certificate validation
   - Request timeouts (30s)
   - Response size limits (10MB)

4. **Automated CVE Scanning**
   - GitHub Actions scan dependencies weekly
   - Container security scanning with Trivy
   - CodeQL analysis for Python

## Development

### Setup

```bash
git clone https://github.com/crunchtools/mcp-gitlab.git
cd mcp-gitlab
uv sync
```

### Run Tests

```bash
uv run pytest
```

### Lint and Type Check

```bash
uv run ruff check src tests
uv run mypy src
```

### Build Container

```bash
podman build -t mcp-gitlab .
```

## License

AGPL-3.0-or-later

## Contributing

Contributions welcome! Please read SECURITY.md before submitting security-related changes.

## Links

- [GitLab REST API Documentation](https://docs.gitlab.com/ee/api/rest/)
- [FastMCP Documentation](https://gofastmcp.com/)
- [MCP Specification](https://modelcontextprotocol.io/)
- [crunchtools.com](https://crunchtools.com)
