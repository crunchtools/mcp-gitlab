# mcp-gitlab-crunchtools Constitution

> **Version:** 1.1.0
> **Ratified:** 2026-02-27
> **Amended:** 2026-10-02
> **Status:** Active
> **Inherits:** [crunchtools/constitution](https://github.com/crunchtools/constitution) v1.22.0
> **Profile:** MCP Server

This file holds what is specific to mcp-gitlab. The fleet rules and the MCP
Server profile (five-layer security model, two-layer tools, distribution
channels, transports, quality gates, Gourmand) apply at the inherited version
and are checked against this repo's files by `constitution.yml`. They are not
restated here.

## Security Model Specifics

- **Credentials:** `GITLAB_TOKEN` (required), held as `SecretStr`, read from
  the environment only. `GitLabApiError` scrubs it from messages, and
  `Config.__repr__()`/`__str__()` never expose it.
- **Input limits:** Pydantic models with `extra="forbid"`; search scopes,
  project visibilities, MR and issue states and pipeline statuses are
  allowlisted; project and group IDs must match `^[a-zA-Z0-9\-_./]+$`.
  `ProjectNotFoundError` truncates long identifiers.
- **API:** `PRIVATE-TOKEN` header, never the URL; path parameters are
  URL-encoded; requests time out after 30s; responses are capped at 10MB.
- **Surface:** pure API wrappers. No filesystem access, shell execution or
  code evaluation.

## Any-Instance Compatibility

The server works with any GitLab instance:

| Variable | Purpose |
|----------|---------|
| `GITLAB_URL` | Instance base (default `https://gitlab.com`); HTTPS required for non-localhost URLs |
| `SSL_CERT_FILE` | CA bundle for corporate CAs |
| `GITLAB_SSL_VERIFY` | Development escape hatch |

## Tool Groups

Projects, groups, branches, files, issues, labels, milestones, merge
requests, pipelines, releases, snippets, wiki, users and search. Client
error handling is tested for 401, 404, 429 and 204 responses in
`TestClientErrorHandling`.

## Instance

| Context | Name |
|---------|------|
| GitHub repo | `crunchtools/mcp-gitlab` |
| PyPI package | `mcp-gitlab-crunchtools` |
| Container image | `quay.io/crunchtools/mcp-gitlab` |
| systemd service | `mcp-gitlab.service` |
| HTTP port | 8015 |

## History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-27 | Initial constitution |
| 1.0.1 | 2026-03-16 | Add Section VI (Container Conventions); renumber VI-VIII to VII-IX |
| 1.0.2 | 2026-09-25 | Inherit constitution v1.17.0 (Gatehouse gates) |
| 1.1.0 | 2026-10-02 | Manifest under constitution v1.18.0: profile restatement removed, mcp-gitlab specifics kept |
