# Security Design Document

This document describes the security architecture of mcp-gitlab-crunchtools.

## 1. Threat Model

### 1.1 Assets to Protect

| Asset | Sensitivity | Impact if Compromised |
|-------|-------------|----------------------|
| GitLab Personal Access Token | Critical | Full account access, code access, CI/CD manipulation |
| Project Source Code | High | Intellectual property theft, supply chain attacks |
| Merge Requests / Issues | Medium | Information disclosure, workflow manipulation |
| Pipeline Logs | Medium | Secret leakage, infrastructure details |

### 1.2 Threat Actors

| Actor | Capability | Motivation |
|-------|------------|------------|
| Malicious AI Agent | Can craft tool inputs | Data exfiltration, privilege escalation |
| Local Attacker | Access to filesystem | Token theft, configuration tampering |
| Network Attacker | Man-in-the-middle | Token interception (mitigated by TLS) |

### 1.3 Attack Vectors

| Vector | Description | Mitigation |
|--------|-------------|------------|
| **Token Leakage** | Token exposed in logs, errors, or outputs | Never log tokens, scrub from errors |
| **Input Injection** | Malicious project_id or content | Strict input validation with Pydantic |
| **Path Traversal** | Manipulated project paths | Allowlist character validation |
| **SSRF** | Redirect API calls to internal services | HTTPS enforcement, URL validation |
| **Denial of Service** | Exhaust GitLab rate limits | Rate limiting awareness |
| **Privilege Escalation** | Access projects beyond token scope | Server validates token scope |
| **Supply Chain** | Compromised dependencies | Automated CVE scanning |

## 2. Security Architecture

### 2.1 Defense in Depth Layers

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: Input Validation                                    │
│ - Pydantic models for all tool inputs                       │
│ - Allowlist for project ID characters                       │
│ - Reject unexpected fields (extra="forbid")                 │
├─────────────────────────────────────────────────────────────┤
│ Layer 2: Token Handling                                      │
│ - Environment variable only (never file, never arg)         │
│ - Never log, never include in errors                        │
│ - Use PRIVATE-TOKEN header (not in URL)                     │
├─────────────────────────────────────────────────────────────┤
│ Layer 3: API Client Hardening                               │
│ - Configurable base URL with HTTPS enforcement              │
│ - TLS certificate validation (default in httpx)             │
│ - Request timeout enforcement (30s)                         │
│ - Response size limits (10MB)                               │
├─────────────────────────────────────────────────────────────┤
│ Layer 4: Output Sanitization                                │
│ - Redact tokens from any error messages                     │
│ - Limit response sizes to prevent memory exhaustion         │
│ - Structured errors without internal details                │
├─────────────────────────────────────────────────────────────┤
│ Layer 5: Runtime Protection                                 │
│ - No filesystem access                                      │
│ - No shell execution (subprocess)                           │
│ - No dynamic code evaluation (eval/exec)                    │
│ - Type-safe with Pydantic                                   │
├─────────────────────────────────────────────────────────────┤
│ Layer 6: Supply Chain Security                              │
│ - Automated CVE scanning via GitHub Actions                 │
│ - Dependabot alerts enabled                                 │
│ - Weekly dependency audits                                  │
│ - Container built on Hummingbird for minimal CVEs           │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Token Security

The API token is handled with multiple protections:

```python
from pydantic import SecretStr

class Config:
    def __init__(self):
        token = os.environ.get("GITLAB_TOKEN")
        if not token:
            raise ConfigurationError("GITLAB_TOKEN required")

        # Store as SecretStr to prevent accidental logging
        self._token = SecretStr(token)

    @property
    def token(self) -> str:
        """Get token value - use sparingly."""
        return self._token.get_secret_value()

    def __repr__(self) -> str:
        return "Config(token=***)"
```

### 2.3 URL Security

The GitLab URL is validated to prevent SSRF:

- Must be a valid URL with scheme and netloc
- Must use HTTPS unless connecting to localhost
- Trailing slashes are stripped
- API base URL is derived as `{GITLAB_URL}/api/v4`

### 2.4 Input Validation Rules

All inputs are validated:

- **Project IDs**: Numeric or alphanumeric paths (hyphens, underscores, dots, slashes only)
- **Group IDs**: Same rules as project IDs
- **Issue/MR titles**: 1-500 characters
- **Descriptions**: Max 50,000 characters
- **State events**: Allowlist of "close" and "reopen"
- **Search scopes**: Allowlist of valid GitLab search scopes
- **Extra Fields**: Rejected (Pydantic extra="forbid")

### 2.5 Error Handling

Errors are sanitized before being returned:

```python
class GitLabApiError(UserError):
    def __init__(self, code: int, message: str):
        # Sanitize message to remove any token references
        token = os.environ.get("GITLAB_TOKEN", "")
        safe_message = message.replace(token, "***") if token else message
        super().__init__(f"GitLab API error {code}: {safe_message}")
```

## 3. Minimum Permission Scopes

### 3.1 Read-Only Token (Safest)

```
read_api
```

**Capabilities:** List projects, groups, issues, MRs, pipelines, search
**Risk:** Information disclosure only

### 3.2 Standard Token

```
api
```

**Capabilities:** Full CRUD on issues, MRs, notes
**Risk:** Can modify project data if token compromised

### 3.3 Recommended Scopes

For minimum privilege, create a token with only:
- `read_api` — if you only need to read
- `api` — if you need to create/update issues and MRs

## 4. Supply Chain Security

### 4.1 Automated CVE Scanning

This project uses GitHub Actions to automatically scan for CVEs:

1. **Weekly Scheduled Scans**: Every Monday at 9 AM UTC
2. **PR Checks**: Every pull request is scanned before merge
3. **Automatic Issues**: When CVEs are found, an issue is created
4. **Dependabot**: Enabled for automatic security updates

### 4.2 Container Security

The container image is built on **[Hummingbird Python](https://quay.io/repository/hummingbird/python)** from [Project Hummingbird](https://github.com/hummingbird-project):

| Advantage | Description |
|-----------|-------------|
| **Minimal CVE Count** | Dramatically reduced attack surface |
| **Rapid Security Updates** | Security patches applied promptly |
| **Python Optimized** | Pre-configured with uv package manager |
| **Non-Root Default** | Runs as non-root user |
| **Production Ready** | Proper signal handling, minimal footprint |

### 4.3 Events Logged

| Event | Level | Fields |
|-------|-------|--------|
| Server startup | INFO | version, GitLab URL |
| Tool invocation | INFO | tool_name, project_id (not full params) |
| GitLab API call | DEBUG | method, path (no auth headers) |
| Permission denied | WARN | tool_name, required_scope |
| Rate limited | WARN | retry_after |
| Error | ERROR | error_type (no internals) |

### 4.4 Never Logged

- API tokens (any form)
- Full request/response bodies
- Issue/MR descriptions (may contain secrets)
- Pipeline log content

## 5. Security Checklist

Before each release:

- [ ] All inputs validated through Pydantic models
- [ ] No token exposure in logs or errors
- [ ] No filesystem operations
- [ ] No shell execution
- [ ] No eval/exec
- [ ] Rate limiting considered
- [ ] Error messages don't leak internals
- [ ] Dependencies scanned for CVEs
- [ ] Container rebuilt with latest Hummingbird base

## 6. Reporting Security Issues

Please report security issues to security@crunchtools.com or open a private security advisory on GitHub.

Do NOT open public issues for security vulnerabilities.
