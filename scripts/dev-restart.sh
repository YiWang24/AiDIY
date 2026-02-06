#!/bin/bash
# =================================================================
# Development Restart Script
# =================================================================
# This script restarts both the frontend and backend services.
#
# Usage:
#   ./scripts/dev-restart.sh
#
# =================================================================

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# =================================================================
# Main
# =================================================================

echo ""
log_info "=== Restarting Development Environment ==="
echo ""

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Stop services
log_info "Stopping services..."
"$SCRIPT_DIR/dev-stop.sh"

echo ""

# Wait a moment for ports to be released
sleep 2

# Start services
log_info "Starting services..."
"$SCRIPT_DIR/dev-start.sh"
