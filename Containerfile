# MCP GitLab CrunchTools Container
# Built on Hummingbird Python image for enterprise security
#
# Build:
#   podman build -t quay.io/crunchtools/mcp-gitlab .
#
# Run:
#   podman run -e GITLAB_TOKEN=your_token quay.io/crunchtools/mcp-gitlab
#
# With Claude Code:
#   claude mcp add mcp-gitlab-crunchtools \
#     --env GITLAB_TOKEN=your_token \
#     -- podman run -i --rm -e GITLAB_TOKEN quay.io/crunchtools/mcp-gitlab

# Stage 1: Lock (turn uv.lock into the exact dependency set to install)
FROM quay.io/hummingbird/python:3.14-builder AS lock
USER 0
RUN pip install --no-cache-dir uv==0.13.7
WORKDIR /lock
COPY pyproject.toml uv.lock ./
RUN uv export --frozen --no-dev --no-emit-project \
      --format requirements-txt -o /requirements.txt

# Stage 2: Builder (has shell, dnf, build tools)
FROM quay.io/hummingbird/python:3.14-builder AS builder
USER 0
WORKDIR /app
RUN python3 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"
# Dependencies come from uv.lock, not from a fresh resolve. `pip install .`
# read only pyproject.toml, whose floors carry no upper bound, so the image
# shipped whatever had been released that morning -- a dependency set no test
# had ever run against (RT#1564; same bug fixed in mcp-gemini PR #72).
# --no-deps stops pip re-resolving what the lock already decided.
COPY --from=lock /requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --no-deps -r /tmp/requirements.txt
COPY pyproject.toml README.md ./
COPY src/ ./src/
RUN pip install --no-cache-dir --no-deps .

# Stage 3: Runtime (distroless — no shell, no package manager)
FROM quay.io/hummingbird/python:3.14

# Labels for container metadata
LABEL name="mcp-gitlab-crunchtools" \
      version="0.7.1" \
      summary="Secure MCP server for GitLab projects, merge requests, issues, and pipelines" \
      description="A security-focused MCP server for GitLab built on Hummingbird" \
      maintainer="crunchtools.com" \
      url="https://github.com/crunchtools/mcp-gitlab" \
      io.k8s.display-name="MCP GitLab CrunchTools" \
      io.openshift.tags="mcp,gitlab,devops" \
      org.opencontainers.image.source="https://github.com/crunchtools/mcp-gitlab" \
      org.opencontainers.image.description="Secure MCP server for GitLab projects, merge requests, issues, and pipelines" \
      org.opencontainers.image.licenses="AGPL-3.0-or-later"

COPY --from=builder /app/venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Verify installation. Exec form, since this stage has no /bin/sh for RUN's shell form.
RUN ["python3", "-c", "from mcp_gitlab_crunchtools import main; print('Installation verified')"]

# Default: stdio transport (use -i with podman run)
# HTTP:    --transport streamable-http (use -d -p 8015:8015 with podman run)
EXPOSE 8015
ENTRYPOINT ["python", "-m", "mcp_gitlab_crunchtools"]
