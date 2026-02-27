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

Follow [Semantic Versioning 2.0.0](https://semver.org/) strictly.

**MAJOR** (breaking changes — consumers must update):
- Removed or renamed tools
- Changed tool parameter names or types
- Renamed environment variables
- Changed default behavior of existing tools

**MINOR** (new functionality — backwards compatible):
- New tools added
- New optional parameters on existing tools
- New tool groups (e.g., adding wiki support)

**PATCH** (fixes — no functional change):
- Bug fixes in existing tools
- Test additions or improvements
- Security patches (dependency updates)

**No version bump required** (infrastructure, not shipped):
- CI/CD changes (workflows, gourmand config)
- Documentation (README, CLAUDE.md, SECURITY.md)
- Issue templates, pre-commit config
- Governance files (.specify/)

**Version bump happens at release time, not per-commit.** Multiple commits can accumulate between releases. The version in `pyproject.toml` and `server.py` is bumped when cutting a release tag.

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

## III. Testing Standards

### Mocked API Tests (MANDATORY)

Every tool MUST have a corresponding mocked test. Tests use `httpx.AsyncClient` mocking — no live API calls, no tokens required in CI.

**Pattern:**
1. Build a mock `httpx.Response` with `_mock_response()` helper
2. Patch `httpx.AsyncClient` via `_patch_client()` context manager
3. Call the tool function directly (not the `_tool` wrapper)
4. Assert response structure and values

**Required test classes per tool group:**

| Tool Group | Test Class | Minimum Tests |
|------------|-----------|---------------|
| Each read tool | `test_list_*`, `test_get_*` | Verify pagination headers, response shape |
| Each write tool | `test_create_*`, `test_update_*` | Verify POST/PUT with correct status codes |
| Each delete tool | `test_delete_*` | Verify 204 No Content handling |
| Error cases | `TestClientErrorHandling` | 401, 404, 429, 204 responses |

**Singleton reset:** The `_reset_client_singleton` autouse fixture resets `client._client` and `config._config` between every test to prevent state leakage.

**Tool count assertion:** `test_tool_count` MUST be updated whenever tools are added or removed. This catches accidental regressions.

### Input Validation Tests

Every Pydantic model in `models.py` MUST have tests in `test_validation.py`:
- Valid minimal input
- Valid full input
- Invalid/rejected inputs (empty strings, too-long values, extra fields, bad state events)
- Injection prevention (special characters in project/group IDs)

### Security Tests

- Token sanitization: `GitLabApiError` MUST scrub tokens from messages
- ID truncation: `ProjectNotFoundError` MUST truncate long identifiers
- Config safety: `repr()` and `str()` MUST never expose the token

---

## IV. Gourmand (AI Slop Detection)

All code MUST pass `gourmand --full .` with **zero violations** before merge. Gourmand is a CI gate in GitHub Actions.

### Configuration

- `gourmand.toml` — Check settings, excluded paths
- `gourmand-exceptions.toml` — Documented exceptions with justifications
- `.gourmand-cache/` — Must be in `.gitignore`

### Checks That Apply

| Check | What it catches |
|-------|----------------|
| `linter_configuration` | Missing ruff rules, no pre-commit hooks |
| `lint_suppression` | `type: ignore` without fix |
| `generic_names` | Variables named `data`, `result`, `temp` |
| `verbose_comments` | Redundant comments restating code |
| `summary_litter` | AI status/summary files in project root |
| `prefer_match` | elif chains that should be match/case |
| `primitive_obsession` | Magic numbers without named constants |
| `copy_paste_detection` | Duplicated code blocks |
| `single_use_helpers` | Unnecessary abstractions |
| `speculative_generality` | YAGNI violations |

### Exception Policy

Exceptions MUST have documented justifications in `gourmand-exceptions.toml`. Acceptable reasons:
- Standard API patterns (HTTP status codes, pagination params)
- Test-specific patterns (intentional invalid input)
- Framework requirements (CLAUDE.md for Claude Code)

Unacceptable reasons:
- "The code is special"
- "The threshold is too strict"
- Rewording to avoid detection

---

## V. Code Quality Gates

Every code change must pass through these gates in order:

1. **Lint** — `uv run ruff check src tests`
2. **Type Check** — `uv run mypy src`
3. **Tests** — `uv run pytest -v` (all passing, mocked httpx)
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

## VI. Naming Conventions

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

## VII. Development Workflow

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

## VIII. Governance

### Amendment Process

1. Create a PR with proposed changes to this constitution
2. Document rationale in PR description
3. Require maintainer approval
4. Update version number upon merge

### Ratification History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-27 | Initial constitution |
