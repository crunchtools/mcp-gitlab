# mcp-gitlab-crunchtools Constitution

> **Version:** 1.0.0
> **Ratified:** 2026-02-27
> **Status:** Active

This constitution establishes the core principles, constraints, and workflows that govern all development on mcp-gitlab-crunchtools.

---

## I. Core Principles

### 1. Five-Layer Security Model

Every change MUST preserve all five security layers. No exceptions.

**Layer 1 — Token Protection:**
- API credentials stored as `SecretStr` (never logged or exposed)
- Environment-variable-only storage
- Automatic scrubbing from error messages

**Layer 2 — Input Validation:**
- Pydantic models enforce strict data types with `extra="forbid"`
- Allowlists for permitted values (states, scopes, statuses)
- Project/group IDs validated against injection patterns

**Layer 3 — API Hardening:**
- Auth via `PRIVATE-TOKEN` header (never in URL)
- Mandatory TLS certificate validation (configurable for self-hosted CAs)
- Request timeouts and response size limits
- URL-encoded path parameters to prevent path traversal

**Layer 4 — Dangerous Operation Prevention:**
- No filesystem access, shell execution, or code evaluation
- No `eval()`/`exec()` functions
- Tools are pure API wrappers with no side effects

**Layer 5 — Supply Chain Security:**
- Weekly automated CVE scanning via GitHub Actions
- Hummingbird container base images (minimal CVE surface)
- Gourmand AI slop detection gating all PRs

### 2. Two-Layer Tool Architecture

Tools follow a strict two-layer pattern:
- `server.py` — `@mcp.tool()` decorated functions that validate args and delegate
- `tools/*.py` — Pure async functions that call `client.py` HTTP methods

Never put business logic in `server.py`. Never put MCP registration in `tools/*.py`.

### 3. Any-Instance Compatibility

The server MUST work with any GitLab instance:
- `GITLAB_URL` configurable (default: `https://gitlab.com`)
- `SSL_CERT_FILE` for corporate CAs
- `GITLAB_SSL_VERIFY` escape hatch for development
- HTTPS enforced for non-localhost URLs

### 4. Three Distribution Channels

Every release MUST be available through all three channels simultaneously:

| Channel | Command | Use Case |
|---------|---------|----------|
| uvx | `uvx mcp-gitlab-crunchtools` | Zero-install, Claude Code |
| pip | `pip install mcp-gitlab-crunchtools` | Virtual environments |
| Container | `podman run quay.io/crunchtools/mcp-gitlab` | Isolated, systemd |

### 5. Three Transport Modes

The server MUST support all three MCP transports:
- **stdio** (default) — spawned per-session by Claude Code
- **SSE** — legacy HTTP transport
- **streamable-http** — production HTTP, systemd-managed containers

### 6. Semantic Versioning

Follow Semantic Versioning 2.0.0 strictly.
- **MAJOR**: Breaking API changes, removed tools, renamed env vars
- **MINOR**: New tools, new tool parameters, new features
- **PATCH**: Bug fixes, documentation, test improvements

### 7. AI Code Quality

All code MUST pass Gourmand checks before merge. Zero violations required.

---

## II. Technology Stack

| Layer | Technology | Version |
|-------|------------|---------|
| Language | Python | 3.10+ |
| MCP Framework | FastMCP | Latest |
| HTTP Client | httpx | Latest |
| Validation | Pydantic | v2 |
| Container Base | Hummingbird | Latest |
| Package Manager | uv | Latest |
| Build System | hatchling | Latest |
| Linter | ruff | Latest |
| Type Checker | mypy (strict) | Latest |
| Tests | pytest + pytest-asyncio | Latest |
| Slop Detector | gourmand | Latest |

---

## III. Code Quality Gates

Every code change must pass through these gates in order:

1. **Lint** — `uv run ruff check src tests`
2. **Type Check** — `uv run mypy src`
3. **Tests** — `uv run pytest -v` (98+ tests, all passing)
4. **Gourmand** — `gourmand --full .` (zero violations)
5. **Container Build** — `podman build -f Containerfile .`

### CI Pipeline (GitHub Actions)

| Job | What it does | Gates PRs |
|-----|-------------|-----------|
| test | Lint + mypy + pytest (Python 3.10-3.12) | Yes |
| gourmand | AI slop detection | Yes |
| build-container | Containerfile builds | Yes |
| security | Weekly CVE scan + CodeQL | Scheduled |
| publish | PyPI trusted publishing | On release tag |
| container | Quay.io push + Trivy | On release tag |

---

## IV. Naming Conventions

| Context | Name |
|---------|------|
| GitHub repo | `crunchtools/mcp-gitlab` |
| PyPI package | `mcp-gitlab-crunchtools` |
| CLI command | `mcp-gitlab-crunchtools` |
| Python module | `mcp_gitlab_crunchtools` |
| Container image | `quay.io/crunchtools/mcp-gitlab` |
| systemd service | `mcp-gitlab.service` |
| HTTP port | 8015 |
| License | AGPL-3.0-or-later |

---

## V. Development Workflow

### Adding a New Tool

1. Add the async function to the appropriate `tools/*.py` file
2. Export it from `tools/__init__.py`
3. Import it in `server.py` and register with `@mcp.tool()`
4. Add a mocked test in `tests/test_tools.py`
5. Update the tool count in `test_tool_count`
6. Run all five quality gates
7. Update CLAUDE.md tool listing

### Adding a New Tool Group

1. Create `tools/new_group.py` with async functions
2. Add imports and `__all__` entries in `tools/__init__.py`
3. Add `@mcp.tool()` wrappers in `server.py`
4. Add a `TestNewGroupTools` class in `tests/test_tools.py`
5. Run all five quality gates

---

## VI. Governance

### Amendment Process

1. Create a PR with proposed changes to this constitution
2. Document rationale in PR description
3. Require maintainer approval
4. Update version number upon merge

### Ratification History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-27 | Initial constitution |
