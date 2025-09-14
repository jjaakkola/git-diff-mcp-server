# Git Diff MCP Server

A Model Context Protocol (MCP) server that provides git diff functionality for PR review assistance.

## Purpose

This MCP server provides a secure interface for AI assistants to analyze git differences between branches, helping with code review and understanding changes in pull requests.

## Features

### Current Implementation

- **`get_branch_diff`** - Get formatted git diff between two branches with chunking for large changes
- **`get_diff_stats`** - Get git diff statistics showing files changed and line counts
- **`get_branch_list`** - List all available local and remote branches
- **`get_commit_range`** - Get commit messages between two branches

## Prerequisites

- Docker Desktop with MCP Toolkit enabled
- Docker MCP CLI plugin (`docker mcp` command)
- A git repository to analyze

## Installation

See the step-by-step instructions provided with the files.

## Usage Examples

In Claude Desktop, you can ask:
- "Show me the diff between main and feature-branch"
- "What are the statistics for changes between develop and my-branch?"
- "List all available branches in this repository"
- "What commits are in feature-branch that aren't in main?"
- "Help me review the changes in this PR by comparing main and HEAD"

## Architecture
Claude Desktop → MCP Gateway → Git Diff MCP Server → Local Git Repository
↓
Docker Volume Mount
(/repo directory)

## Development

### Local Testing

```bash
# Run directly (make sure you're in a git repository)
REPO_PATH=$(pwd) python git_diff_server.py

# Test MCP protocol
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | python git_diff_server.py
```

### Adding New Tools

- Add the function to git_diff_server.py
- Decorate with @mcp.tool()
- Update the catalog entry with the new tool name
- Rebuild the Docker image

## Troubleshooting

### Tools Not Appearing

- Verify Docker image built successfully
- Check catalog and registry files
- Ensure Claude Desktop config includes custom catalog
- Restart Claude Desktop

### Repository Access Errors

- Ensure your git repository is properly mounted to /repo
- Check that the repository is a valid git repository
- Verify git is properly configured in the container

### Git Command Errors

- Make sure all branch names exist
- Check network connectivity for remote operations
- Ensure repository is not corrupted

## Security Considerations

- Repository is mounted read-only when possible
- No credentials stored or transmitted
- All operations are read-only git operations
- Safe directory configuration prevents git security warnings

## License
MIT License