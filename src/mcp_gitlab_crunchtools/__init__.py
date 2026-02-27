"""MCP GitLab CrunchTools - Secure MCP server for GitLab.

A security-focused MCP server for GitLab projects, merge requests,
issues, pipelines, and search. Works with any GitLab instance
(gitlab.com, self-hosted, or enterprise).

Usage:
    mcp-gitlab-crunchtools

    python -m mcp_gitlab_crunchtools

    uvx mcp-gitlab-crunchtools

Environment Variables:
    GITLAB_TOKEN: Required. GitLab Personal Access Token.
    GITLAB_URL: Optional. GitLab instance URL (default: https://gitlab.com).

Example with Claude Code:
    claude mcp add mcp-gitlab-crunchtools \\
        --env GITLAB_TOKEN=your_token_here \\
        -- uvx mcp-gitlab-crunchtools
"""

import argparse

from .server import mcp

__version__ = "0.1.0"
__all__ = ["main", "mcp"]


def main() -> None:
    """Main entry point for the MCP server."""
    parser = argparse.ArgumentParser(description="MCP server for GitLab")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
        help="Transport protocol (default: stdio)",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to for HTTP transports (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8015,
        help="Port to bind to for HTTP transports (default: 8015)",
    )
    args = parser.parse_args()

    if args.transport == "stdio":
        mcp.run()
    else:
        mcp.run(transport=args.transport, host=args.host, port=args.port)
