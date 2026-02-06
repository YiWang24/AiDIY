#!/bin/bash
# =================================================================
# Development Stop Script
# =================================================================
# This script stops both the frontend and backend processes.
#
# Usage:
#   ./scripts/dev-stop.sh
#
# =================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# =================================================================
# Stop Functions
# =================================================================

stop_backend() {
    local port=8000
    local pid_file=".backend.pid"

    log_info "Stopping Backend API..."

    # Try to kill using saved PID first
    if [ -f "$pid_file" ]; then
        local saved_pid=$(cat "$pid_file")
        if kill -0 "$saved_pid" 2>/dev/null; then
            kill "$saved_pid" 2>/dev/null || true
            log_info "Stopped backend (PID: $saved_pid)"
        fi
        rm -f "$pid_file"
    fi

    # Also kill any process on the port
    local pid=$(lsof -ti :$port 2>/dev/null || true)
    if [ -n "$pid" ]; then
        kill -9 "$pid" 2>/dev/null || true
        log_info "Killed backend process on port $port"
    fi

    # Kill any uvicorn processes
    pkill -9 uvicorn 2>/dev/null || true
}

stop_frontend() {
    local port=3001
    local pid_file=".frontend.pid"

    log_info "Stopping Frontend..."

    # Try to kill using saved PID first
    if [ -f "$pid_file" ]; then
        local saved_pid=$(cat "$pid_file")
        if kill -0 "$saved_pid" 2>/dev/null; then
            kill "$saved_pid" 2>/dev/null || true
            log_info "Stopped frontend (PID: $saved_pid)"
        fi
        rm -f "$pid_file"
    fi

    # Also kill any process on the port
    local pid=$(lsof -ti :$port 2>/dev/null || true)
    if [ -n "$pid" ]; then
        kill -9 "$pid" 2>/dev/null || true
        log_info "Killed frontend process on port $port"
    fi

    # Kill any npm/node processes related to docusaurus
    pkill -9 -f "npm.*start" 2>/dev/null || true
}

# =================================================================
# Main
# =================================================================

echo ""
log_info "=== Stopping Development Environment ==="
echo ""

stop_backend
echo ""
stop_frontend

echo ""
log_info "Cleanup complete!"
echo ""
echo "To start again:"
echo "  ./scripts/dev-start.sh"
