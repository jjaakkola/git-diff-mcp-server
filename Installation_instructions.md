# Step 1: Save the Files
```bash
# Create project directory
mkdir git-diff-mcp-server
cd git-diff-mcp-server

# Save all 6 files in this directory
# Make the helper script executable
chmod +x git-diff.sh
```

# Step 2: Build Docker Image
```bash
# Using the helper script (recommended)
./git-diff.sh build

# Or manually
docker build -t git-diff-mcp-server .¨
```

# Step 3: Create Custom Catalog
```bash
# Create catalogs directory if it doesn't exist
mkdir -p ~/.docker/mcp/catalogs

# Create or edit custom.yaml
nano ~/.docker/mcp/catalogs/custom.yaml
```

Add this entry to custom.yaml:
```yaml
version: 2
name: custom
displayName: Custom MCP Servers
registry:
  git-diff:
    description: "Get git diffs between branches for PR review assistance"
    title: "Git Diff Server"
    type: server
    dateAdded: "2025-01-15T00:00:00Z"
    image: git-diff-mcp-server:latest
    ref: ""
    readme: ""
    toolsUrl: ""
    source: ""
    upstream: ""
    icon: ""
    tools:
      - name: get_branch_diff
      - name: get_diff_stats
      - name: get_branch_list
      - name: get_commit_range
    volumes:
      - source: "${REPO_PATH}"
        target: "/repo"
        readonly: true
    metadata:
      category: productivity
      tags:
        - git
        - diff
        - pr-review
        - development
    license: MIT
    owner: local
```

# Step 4: Update Registry
```bash
# Edit registry file
nano ~/.docker/mcp/registry.yaml
```

Add this entry under the existing registry: key:
```yaml
registry:
  # ... existing servers ...
  git-diff:
    ref: ""
```

# Step 5: Configure Claude Desktop
Find your Claude Desktop config file:
- macOS: ~/Library/Application Support/Claude/claude_desktop_config.json
- Windows: %APPDATA%\Claude\claude_desktop_config.json
- Linux: ~/.config/Claude/claude_desktop_config.json

Edit the file and add your custom catalog to the args array:
```json
{
  "mcpServers": {
    "mcp-toolkit-gateway": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-v", "/var/run/docker.sock:/var/run/docker.sock",
        "-v", "/Users/your_username/.docker/mcp:/mcp",
        "docker/mcp-gateway",
        "--catalog=/mcp/catalogs/docker-mcp.yaml",
        "--catalog=/mcp/catalogs/custom.yaml",
        "--config=/mcp/config.yaml",
        "--registry=/mcp/registry.yaml",
        "--tools-config=/mcp/tools.yaml",
        "--transport=stdio"
      ],
      "env": {
        "REPO_PATH": "/path/to/your/git/repository"
      }
    }
  }
}
```

Replace `/Users/your_username` and `/path/to/your/git/repository` with your actual paths.

# Step 6: Restart Claude Desktop

- Quit Claude Desktop completely
- Start Claude Desktop again
- Your git diff tools should appear!

# Step 7: Test Your Server
```bash
# Test with helper script
./git-diff.sh test /path/to/your/repo

# Or verify it appears in the list
docker mcp server list

# Quick manual test
cd /path/to/your/git/repo
./git-diff.sh run
```

# Step 8: Usage Examples
Once configured, you can ask Claude:

- "Show me the diff between main and develop"
- "What files changed between main and my-feature-branch?"
- "List all branches in this repository"
- "What commits are in my-branch that aren't in main?"
- "Help me review this PR by comparing the changes"

The server will automatically format the output with syntax highlighting and chunk large diffs for better analysis.