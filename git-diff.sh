#!/bin/bash

# Git Diff MCP Server Helper Script
# This script helps build, run, and manage the Git Diff MCP server

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGE_NAME="git-diff-mcp-server"
CONTAINER_NAME="git-diff-mcp"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_usage() {
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  build                   Build the Docker image"
    echo "  run [REPO_PATH]         Run the server with repository mounted"
    echo "  test [REPO_PATH]        Test the server with a sample command"
    echo "  clean                   Clean up containers and images"
    echo "  logs                    Show server logs"
    echo "  stop                    Stop running server"
    echo ""
    echo "Options:"
    echo "  REPO_PATH               Path to git repository (default: current directory)"
    echo ""
    echo "Examples:"
    echo "  $0 build"
    echo "  $0 run /path/to/my/repo"
    echo "  $0 run                  # Uses current directory"
    echo "  $0 test"
}

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

build_image() {
    log "Building Docker image: $IMAGE_NAME"
    cd "$SCRIPT_DIR"
    
    if ! docker build -t "$IMAGE_NAME" .; then
        error "Failed to build Docker image"
    fi
    
    success "Docker image built successfully"
}

run_server() {
    local repo_path="${1:-$(pwd)}"
    
    # Convert to absolute path
    repo_path=$(realpath "$repo_path")
    
    # Check if path exists and is a git repository
    if [[ ! -d "$repo_path" ]]; then
        error "Repository path does not exist: $repo_path"
    fi
    
    if [[ ! -d "$repo_path/.git" ]]; then
        error "Path is not a git repository: $repo_path"
    fi
    
    log "Starting MCP server with repository: $repo_path"
    
    # Stop any existing container
    docker stop "$CONTAINER_NAME" 2>/dev/null || true
    docker rm "$CONTAINER_NAME" 2>/dev/null || true
    
    # Run the server
    if ! docker run -it --rm \
        --name "$CONTAINER_NAME" \
        -v "$repo_path:/repo:ro" \
        "$IMAGE_NAME"; then
        error "Failed to run server"
    fi
}

test_server() {
    local repo_path="${1:-$(pwd)}"
    
    # Convert to absolute path
    repo_path=$(realpath "$repo_path")
    
    # Check if path exists and is a git repository
    if [[ ! -d "$repo_path" ]]; then
        error "Repository path does not exist: $repo_path"
    fi
    
    if [[ ! -d "$repo_path/.git" ]]; then
        error "Path is not a git repository: $repo_path"
    fi
    
    log "Testing MCP server with repository: $repo_path"
    
    # Test with a simple MCP command
    echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | \
    docker run -i --rm \
        -v "$repo_path:/repo:ro" \
        "$IMAGE_NAME"
}

show_logs() {
    docker logs "$CONTAINER_NAME"
}

stop_server() {
    log "Stopping server..."
    docker stop "$CONTAINER_NAME" 2>/dev/null || warning "No running server found"
    docker rm "$CONTAINER_NAME" 2>/dev/null || true
    success "Server stopped"
}

clean_up() {
    log "Cleaning up Docker resources..."
    
    # Stop and remove container
    docker stop "$CONTAINER_NAME" 2>/dev/null || true
    docker rm "$CONTAINER_NAME" 2>/dev/null || true
    
    # Remove image
    docker rmi "$IMAGE_NAME" 2>/dev/null || warning "Image not found"
    
    success "Cleanup completed"
}

# Main script logic
case "${1:-help}" in
    build)
        build_image
        ;;
    run)
        build_image
        run_server "$2"
        ;;
    test)
        build_image
        test_server "$2"
        ;;
    logs)
        show_logs
        ;;
    stop)
        stop_server
        ;;
    clean)
        clean_up
        ;;
    help|--help|-h)
        print_usage
        ;;
    *)
        echo "Unknown command: $1"
        echo ""
        print_usage
        exit 1
        ;;
esac