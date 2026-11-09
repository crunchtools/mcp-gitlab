# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/) and this project adheres to
[Semantic Versioning](https://semver.org/).

Entries prior to 2026-09-19 are back-filled from GitHub Release notes (RT #1484).

## [Unreleased]

## [0.7.0] - 2026-11-09

### Fixed

- **The response ceiling is now a ceiling.** It read the `content-length`
  header and nothing else, and that header is optional, so a reply without it
  was read whole into memory. Bodies are read in bounded pieces now, measured
  before each chunk is copied in: `aiter_bytes()` promises nothing about chunk
  size, so appending first would copy in exactly the response being refused.

- **An error that is not GitLab's JSON shape says what it was.** It arrived as
  `Unknown error`, or 200 bare characters of body with no indication of where
  they came from, so a self-hosted instance's SSO login page, a proxy error
  and the API refusing something were one message. Such a body is now quoted,
  bounded, alongside the method, URL, status and content-type of the request it
  answered. GitLab's own `message`/`error` is still used verbatim when present,
  now length-bounded.

- **The URL in an error carries no secret.** Userinfo is dropped — a
  self-hosted `GITLAB_URL` can carry credentials before the path — and
  `private_token`, `access_token` and `token`, all of which GitLab accepts in a
  query string, are redacted by name. By name rather than by dropping the query
  string, because `per_page`, `state` and `ref` are the diagnosis.

### Added

- **The client says what it is.** Requests carry
  `User-Agent: mcp-gitlab-crunchtools/<version> (+<repo url>)`, with the
  version read from installed package metadata. httpx's default
  `python-httpx/<version>` is what bot protection answers with a challenge page
  (RT #1596).

### Changed

- Client tests drive `build_request` and `send` rather than `request`, because
  the client now streams. The new `tests/test_http_contract.py` uses a real
  `httpx.AsyncClient` over `httpx.MockTransport`, because the agent string and
  the bounded read are the client's own behaviour.

- Inherits constitution v1.36.0, whose MCP Server profile 1.8.0 states the
  outbound HTTP contract (RT #1601).

## [0.6.1] - 2026-10-31

### Security

- Upgraded locked dependencies within their declared ranges to clear the
  advisories the fleet dependency audit found (anyio, authlib, certifi, cryptography, dnspython, fastmcp, joserfc, opentelemetry-api, pydantic-settings, pygments, pyjwt, python-dotenv).

## [0.6.0] - 2026-10-20

### Changed

- Container base images pinned to `quay.io/hummingbird/python:3.14*` instead of
  `latest`, which moved to Python 3.15.0 on 2026-10-20 (crunchtools/constitution#66).

## [0.5.1] - 2026-10-17

### Fixed

- Every integer ID parameter registered in `server.py` publishes `ge=1`, so a
  gateway can prove `0` and negative IDs invalid (crunchtools/constitution#35).
- `get_project_branch` and `get_release` URL-encode the branch and tag name, so
  a name containing `/` no longer hits the wrong endpoint. `delete_branch` uses
  the same new `encode_path_segment` helper.

## [0.5.0] - 2026-10-10

### Added

- The 35 tools that only read (every `list_*`, `get_*`, `search_*` tool and
  `compare_branches`) publish `readOnlyHint: true`. A gateway uses it to decide
  whether an invalid optional argument may be dropped or must refuse the call
  (crunchtools/constitution#35).
- Tests pin every registered tool into `READ_ONLY` or `WRITES`, and check that
  each read-only tool reaches GitLab with GET only and no request body.

### Changed

- Inherits constitution v1.22.0; the workflow pins and the pre-commit hook rev
  move with it.

- Constitution is now a v1.18.0 manifest: it holds only what is specific to
  this repo; fleet and profile rules apply by reference.
- Constitution validation is pinned to the inherited release via
  `.github/workflows/constitution.yml`.
- Dependabot auto-merges GitHub Actions minor and patch updates.

## [0.4.1] - 2026-03-09

Patch release with lint fixes and code quality improvements.

### Fixed
- Removed unused imports in `test_tools.py` (ruff F401).
- Code formatting cleanup via ruff format.

## [0.4.0] - 2026-02-27

No GitHub Release was created for this tag, so no authored release notes exist to
back-fill from.

## [0.3.0] - 2026-02-27

61 tools for GitLab REST API v4. Works with any GitLab instance.

### Added
- 27 new tools: Files (4) — list tree, get/create/update files with commits;
  Branches (3) — create, delete, compare; Labels (4) — full CRUD; Users (3) —
  current user, list, get by ID; Releases (3) — list, get, create; Milestones (3)
  — list, create, update; Wiki (3) — list, get, create pages; Snippets (2) —
  list, create; MR Discussions (2) — list/create threaded comments.
- Gourmand AI slop detection (zero violations, gates PRs).
- Pre-commit hooks (ruff check + format).
- spec-kit governance framework (`.specify/`), a constitution with 8 sections,
  GitHub issue templates, and a codified semver policy.

### Changed
- 98 mocked tests, up from 71.
- Named constants for all magic numbers; match/case for config logic.

## [0.2.0] - 2026-02-27

Secure MCP server for GitLab REST API v4. Works with any GitLab instance.

### Added
- 34 tools: Projects (5) — list, get, branches, commits; Groups (3) — list, get,
  group projects; Merge Requests (7) — list, get, create, update, notes, changes;
  Issues (6) — list, get, create, update, notes; Pipelines (11) — list, get,
  create, retry, cancel, delete, jobs, job log, retry/cancel/delete job;
  Search (2) — global, project.
- stdio, SSE, and streamable-http transports.
- `SSL_CERT_FILE` and `GITLAB_SSL_VERIFY` support for self-hosted instances.
- Hardened httpx client with token sanitization, input validation, and response
  size limits.
- 71 tests with mocked API responses.
