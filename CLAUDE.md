# Git Diff MCP Server - Implementation Details

## Overview

This MCP server provides git diff functionality specifically designed to help with PR reviews by:
- Getting formatted diffs between branches
- Chunking large changes for better LLM processing
- Providing statistics and commit information
- Listing available branches

## Key Implementation Details

### Chunking Strategy
- Large diffs are automatically chunked to prevent overwhelming the LLM
- Each file's changes are kept together when possible
- Maximum chunk size of 2000 characters by default
- Preserves diff context (headers, line numbers)

### Error Handling
- Graceful handling of missing repositories
- Timeout protection for long-running git commands
- Clear error messages for common git issues
- Automatic git fetch to ensure up-to-date information

### Security Features
- Repository mounted as volume (can be read-only)
- No credential storage or transmission
- Safe directory configuration
- Timeout protection against long-running operations

### Git Operations
- Uses three-dot diff syntax (`base...target`) for merge-base comparison
- Supports both local and remote branch references
- Automatic fetching to ensure current data
- No-color output for clean parsing

## Tool Descriptions

### get_branch_diff
- **Purpose**: Main tool for getting formatted diffs
- **Parameters**: base_branch (default: "main"), target_branch (default: "HEAD")
- **Output**: Formatted diff with file separation and syntax highlighting
- **Chunking**: Automatically splits large files into manageable pieces

### get_diff_stats
- **Purpose**: Quick overview of changes
- **Parameters**: base_branch (default: "main"), target_branch (default: "HEAD")
- **Output**: Git's built-in statistics format showing files and line counts

### get_branch_list
- **Purpose**: Branch discovery and navigation
- **Parameters**: None
- **Output**: Formatted list of local and remote branches with current branch indicator

### get_commit_range
- **Purpose**: Understand what commits are being reviewed
- **Parameters**: base_branch (default: "main"), target_branch (default: "HEAD")
- **Output**: One-line commit messages in the target branch not in base

## Usage Patterns

### PR Review Workflow
1. List branches to identify the PR branch
2. Get commit range to understand what's being changed
3. Get diff stats for a quick overview
4. Get full diff for detailed review

### Best Practices
- Always specify explicit branch names when possible
- Use the commit range tool to understand the scope of changes
- For large PRs, review statistics first before getting full diff
- Mount repository as read-only when possible for safety

## Troubleshooting

### Common Issues
- **"Repository not found"**: Ensure git repo is mounted to `/repo`
- **"Git command failed"**: Check branch names and repository state
- **"No differences found"**: Branches may be identical or names incorrect
- **Timeout errors**: Very large repositories may need timeout adjustments

### Docker Mount Examples
```bash
# Mount current directory (if it's a git repo)
docker run -v $(pwd):/repo git-diff-mcp-server

# Mount specific repository
docker run -v /path/to/repo:/repo git-diff-mcp-server
```