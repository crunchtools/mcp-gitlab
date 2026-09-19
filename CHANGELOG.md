# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/) and this project adheres to
[Semantic Versioning](https://semver.org/).

Entries prior to 2026-09-19 are back-filled from GitHub Release notes (RT #1484).

## [Unreleased]

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
