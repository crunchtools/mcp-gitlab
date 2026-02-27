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

# Use Hummingbird Python image (Red Hat UBI-based with Python pre-installed)
FROM quay.io/hummingbird/python:latest

# Labels for container metadata
LABEL name="mcp-gitlab-crunchtools" \
      version="0.1.0" \
      summary="Secure MCP server for GitLab projects, merge requests, issues, and pipelines" \
      description="A security-focused MCP server for GitLab built on Red Hat UBI" \
      maintainer="crunchtools.com" \
      url="https://github.com/crunchtools/mcp-gitlab" \
      io.k8s.display-name="MCP GitLab CrunchTools" \
      io.openshift.tags="mcp,gitlab,devops"

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Install the package and dependencies
RUN pip install --no-cache-dir .

# Verify installation
RUN python -c "from mcp_gitlab_crunchtools import main; print('Installation verified')"

# Default: stdio transport (use -i with podman run)
# HTTP:    --transport streamable-http (use -d -p 8015:8015 with podman run)
EXPOSE 8015
ENTRYPOINT ["python", "-m", "mcp_gitlab_crunchtools"]
