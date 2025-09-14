#!/usr/bin/env python3
"""
Git Diff MCP Server - Get git diffs between branches for PR review assistance
"""

import os
import sys
import logging
import subprocess
from datetime import datetime, timezone

from mcp.server.fastmcp import FastMCP

# Configure logging to stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger("git-diff-server")

# Initialize MCP server - NO PROMPT PARAMETER!
mcp = FastMCP("git-diff")

# Configuration
REPO_PATH = "/repo"

# === UTILITY FUNCTIONS ===

def run_git_command(command):
    """Run a git command in the repository directory."""
    try:
        result = subprocess.run(
            command,
            cwd=REPO_PATH,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result
    except subprocess.TimeoutExpired:
        logger.error("Git command timed out")
        return None
    except Exception as e:
        logger.error(f"Error running git command: {e}")
        return None

def format_diff_output(diff_text, max_chunk_size=2000):
    """Format diff output for better LLM consumption."""
    if not diff_text.strip():
        return "No differences found between the specified branches."
    
    lines = diff_text.split('\n')
    formatted_output = []
    current_file = None
    current_chunk = []
    chunk_line_count = 0
    
    for line in lines:
        if line.startswith('diff --git'):
            # New file detected
            if current_file and current_chunk:
                # Save previous file's chunk
                formatted_output.append({
                    'file': current_file,
                    'content': '\n'.join(current_chunk),
                    'lines': chunk_line_count
                })
            
            # Extract file path
            parts = line.split(' ')
            if len(parts) >= 4:
                current_file = parts[3][2:]  # Remove 'b/' prefix
            else:
                current_file = "unknown"
            
            current_chunk = [line]
            chunk_line_count = 0
            
        elif line.startswith('+++') or line.startswith('---'):
            current_chunk.append(line)
        elif line.startswith('@@'):
            current_chunk.append(line)
        elif line.startswith('+') or line.startswith('-') or line.startswith(' '):
            current_chunk.append(line)
            chunk_line_count += 1
            
            # If chunk is getting too large, split it
            if len('\n'.join(current_chunk)) > max_chunk_size:
                formatted_output.append({
                    'file': current_file,
                    'content': '\n'.join(current_chunk),
                    'lines': chunk_line_count
                })
                current_chunk = [f"... (continuing {current_file})"]
                chunk_line_count = 0
        else:
            current_chunk.append(line)
    
    # Don't forget the last chunk
    if current_file and current_chunk:
        formatted_output.append({
            'file': current_file,
            'content': '\n'.join(current_chunk),
            'lines': chunk_line_count
        })
    
    return formatted_output

# === MCP TOOLS ===

@mcp.tool()
async def get_branch_diff(base_branch: str = "main", target_branch: str = "HEAD") -> str:
    """Get git diff between two branches formatted for PR review."""
    logger.info(f"Getting diff between {base_branch} and {target_branch}")
    
    if not base_branch.strip():
        return "❌ Error: Base branch is required"
    
    if not target_branch.strip():
        target_branch = "HEAD"
    
    # Check if repository exists
    if not os.path.exists(REPO_PATH):
        return f"❌ Error: Repository not found at {REPO_PATH}. Make sure to mount your git repository."
    
    try:
        # Fetch latest changes
        fetch_result = run_git_command(["git", "fetch", "--all"])
        if fetch_result and fetch_result.returncode != 0:
            logger.warning(f"Git fetch failed: {fetch_result.stderr}")
        
        # Get the diff
        diff_result = run_git_command([
            "git", "diff", 
            f"{base_branch}...{target_branch}",
            "--no-color"
        ])
        
        if not diff_result:
            return "❌ Error: Failed to execute git diff command"
        
        if diff_result.returncode != 0:
            return f"❌ Git Error: {diff_result.stderr.strip()}"
        
        diff_text = diff_result.stdout
        
        if not diff_text.strip():
            return f"✅ No differences found between {base_branch} and {target_branch}"
        
        # Format the diff for better consumption
        formatted_chunks = format_diff_output(diff_text)
        
        if isinstance(formatted_chunks, str):
            return formatted_chunks
        
        # Build the output
        output = [f"📊 Git Diff: {base_branch}...{target_branch}"]
        output.append(f"Found {len(formatted_chunks)} file(s) with changes:\n")
        
        for i, chunk in enumerate(formatted_chunks, 1):
            output.append(f"📁 File {i}: {chunk['file']}")
            output.append(f"Lines changed: {chunk['lines']}")
            output.append("```diff")
            output.append(chunk['content'])
            output.append("```\n")
        
        return '\n'.join(output)
        
    except Exception as e:
        logger.error(f"Error getting diff: {e}")
        return f"❌ Error: {str(e)}"

@mcp.tool()
async def get_diff_stats(base_branch: str = "main", target_branch: str = "HEAD") -> str:
    """Get git diff statistics between two branches."""
    logger.info(f"Getting diff stats between {base_branch} and {target_branch}")
    
    if not base_branch.strip():
        return "❌ Error: Base branch is required"
    
    if not target_branch.strip():
        target_branch = "HEAD"
    
    # Check if repository exists
    if not os.path.exists(REPO_PATH):
        return f"❌ Error: Repository not found at {REPO_PATH}. Make sure to mount your git repository."
    
    try:
        # Get diff statistics
        stats_result = run_git_command([
            "git", "diff", 
            f"{base_branch}...{target_branch}",
            "--stat"
        ])
        
        if not stats_result:
            return "❌ Error: Failed to execute git diff --stat command"
        
        if stats_result.returncode != 0:
            return f"❌ Git Error: {stats_result.stderr.strip()}"
        
        stats_text = stats_result.stdout.strip()
        
        if not stats_text:
            return f"✅ No differences found between {base_branch} and {target_branch}"
        
        return f"📊 Diff Statistics: {base_branch}...{target_branch}\n\n```\n{stats_text}\n```"
        
    except Exception as e:
        logger.error(f"Error getting diff stats: {e}")
        return f"❌ Error: {str(e)}"

@mcp.tool()
async def get_branch_list() -> str:
    """List all available branches in the repository."""
    logger.info("Getting list of branches")
    
    # Check if repository exists
    if not os.path.exists(REPO_PATH):
        return f"❌ Error: Repository not found at {REPO_PATH}. Make sure to mount your git repository."
    
    try:
        # Get local branches
        local_result = run_git_command(["git", "branch"])
        
        # Get remote branches
        remote_result = run_git_command(["git", "branch", "-r"])
        
        if not local_result or not remote_result:
            return "❌ Error: Failed to get branch information"
        
        output = ["🌿 Available Branches:\n"]
        
        if local_result.returncode == 0 and local_result.stdout.strip():
            output.append("**Local Branches:**")
            local_branches = []
            for line in local_result.stdout.strip().split('\n'):
                branch = line.strip()
                if branch.startswith('*'):
                    branch = branch[1:].strip() + " (current)"
                local_branches.append(f"  - {branch}")
            output.extend(local_branches)
            output.append("")
        
        if remote_result.returncode == 0 and remote_result.stdout.strip():
            output.append("**Remote Branches:**")
            remote_branches = []
            for line in remote_result.stdout.strip().split('\n'):
                branch = line.strip()
                if not branch.endswith('/HEAD'):
                    remote_branches.append(f"  - {branch}")
            output.extend(remote_branches)
        
        return '\n'.join(output)
        
    except Exception as e:
        logger.error(f"Error getting branches: {e}")
        return f"❌ Error: {str(e)}"

@mcp.tool()
async def get_commit_range(base_branch: str = "main", target_branch: str = "HEAD") -> str:
    """Get commit messages between two branches."""
    logger.info(f"Getting commits between {base_branch} and {target_branch}")
    
    if not base_branch.strip():
        return "❌ Error: Base branch is required"
    
    if not target_branch.strip():
        target_branch = "HEAD"
    
    # Check if repository exists
    if not os.path.exists(REPO_PATH):
        return f"❌ Error: Repository not found at {REPO_PATH}. Make sure to mount your git repository."
    
    try:
        # Get commit log
        log_result = run_git_command([
            "git", "log", 
            f"{base_branch}..{target_branch}",
            "--oneline",
            "--no-merges"
        ])
        
        if not log_result:
            return "❌ Error: Failed to execute git log command"
        
        if log_result.returncode != 0:
            return f"❌ Git Error: {log_result.stderr.strip()}"
        
        commits = log_result.stdout.strip()
        
        if not commits:
            return f"✅ No new commits found between {base_branch} and {target_branch}"
        
        commit_lines = commits.split('\n')
        output = [f"📝 Commits in {target_branch} not in {base_branch}:"]
        output.append(f"Found {len(commit_lines)} commit(s):\n")
        
        for commit in commit_lines:
            output.append(f"  • {commit}")
        
        return '\n'.join(output)
        
    except Exception as e:
        logger.error(f"Error getting commits: {e}")
        return f"❌ Error: {str(e)}"

# === SERVER STARTUP ===
if __name__ == "__main__":
    logger.info("Starting Git Diff MCP server...")
    
    # Check if repository path exists
    if not os.path.exists(REPO_PATH):
        logger.warning(f"Repository path {REPO_PATH} does not exist. Make sure to mount your git repository.")
    
    try:
        mcp.run(transport='stdio')
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)