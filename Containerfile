# MCP GitLab CrunchTools Container
# Built on Hummingbird Python image (Red Hat UBI-based) for enterprise security
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

# Builder stage: the "latest" default variant is distroless (no shell/pip),
# so dependencies are installed here and copied into the distroless final image.
FROM quay.io/hummingbird/python:latest-builder AS builder

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src/ ./src/

RUN pip install --no-cache-dir .

# Final stage: distroless runtime, no shell/dnf/pip in the shipped image.
FROM quay.io/hummingbird/python:latest

# Labels for container metadata
LABEL name="mcp-gitlab-crunchtools" \
      version="0.4.1" \
      summary="Secure MCP server for GitLab projects, merge requests, issues, and pipelines" \
      description="A security-focused MCP server for GitLab built on Red Hat UBI" \
      maintainer="crunchtools.com" \
      url="https://github.com/crunchtools/mcp-gitlab" \
      io.k8s.display-name="MCP GitLab CrunchTools" \
      io.openshift.tags="mcp,gitlab,devops" \
      org.opencontainers.image.source="https://github.com/crunchtools/mcp-gitlab" \
      org.opencontainers.image.description="Secure MCP server for GitLab projects, merge requests, issues, and pipelines" \
      org.opencontainers.image.licenses="AGPL-3.0-or-later"

# Pip installs to the user site (/tmp/.local) since HOME=/tmp and the image
# runs as the non-root default user; copy that tree straight into the final image.
COPY --from=builder --chown=65532:65532 /tmp/.local /tmp/.local
ENV PATH="/tmp/.local/bin:${PATH}"

# Verify installation. Exec form, since this stage has no /bin/sh for RUN's shell form.
RUN ["python3", "-c", "from mcp_gitlab_crunchtools import main; print('Installation verified')"]

# Default: stdio transport (use -i with podman run)
# HTTP:    --transport streamable-http (use -d -p 8015:8015 with podman run)
EXPOSE 8015
ENTRYPOINT ["python", "-m", "mcp_gitlab_crunchtools"]
