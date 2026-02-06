#!/bin/bash
# =================================================================
# Development Startup Script
# =================================================================
# This script starts both the frontend (Docusaurus) and backend (KB API)
# for local development using Doppler for environment variable injection.
#
# Usage:
#   ./scripts/dev-start.sh
#
# Prerequisites:
#   - Doppler CLI installed
#   - Logged in to Doppler
#   - Node.js and Python installed
#   - Database running (if using local DB)
#
# =================================================================

set -euo pipefail

# =================================================================
# Configuration
# =================================================================

# Ports
FRONTEND_PORT=3001
BACKEND_PORT=8000

# Doppler configuration (adjust if needed)
DOPPLER_PROJECT="${DOPPLER_PROJECT:-portfolio-api}"
DOPPLER_CONFIG="${DOPPLER_CONFIG:-dev_personal}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# =================================================================
# Functions
# =================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

kill_port() {
    local port=$1
    local service_name=$2

    local pid=$(lsof -ti :$port 2>/dev/null || true)
    if [ -n "$pid" ]; then
        log_info "Killing $service_name (PID: $pid) on port $port..."
        kill -9 $pid 2>/dev/null || true
        sleep 1
    else
        log_info "No process found on port $port"
    fi
}

wait_for_url() {
    local url=$1
    local service_name=$2
    local max_wait=${3:-30}
    local wait_time=0

    log_info "Waiting for $service_name to be ready at $url..."

    while [ $wait_time -lt $max_wait ]; do
        if curl -fSs "$url" > /dev/null 2>&1; then
            log_success "$service_name is ready!"
            return 0
        fi
        sleep 1
        wait_time=$((wait_time + 1))
        echo -n "."
    done

    echo ""
    log_error "$service_name failed to start within ${max_wait}s"
    return 1
}

# =================================================================
# Pre-flight Checks
# =================================================================

log_info "Starting development environment..."
echo ""

# Check if Doppler is installed
if ! command -v doppler &> /dev/null; then
    log_error "Doppler CLI is not installed"
    echo ""
    echo "Install it with:"
    echo "  brew install dopplerhq/cli/doppler"
    echo ""
    echo "Then login:"
    echo "  doppler login"
    exit 1
fi

# Check if user is logged in to Doppler
if ! doppler me &> /dev/null; then
    log_error "Not logged in to Doppler"
    echo ""
    echo "Please login first:"
    echo "  doppler login"
    exit 1
fi

log_success "Doppler is configured"

# =================================================================
# Kill Existing Processes
# =================================================================

echo ""
log_info "Cleaning up existing processes..."

kill_port $BACKEND_PORT "Backend API"
kill_port $FRONTEND_PORT "Frontend"

# Additional cleanup: kill any uvicorn processes
log_info "Cleaning up any stray uvicorn processes..."
pkill -9 uvicorn 2>/dev/null || true
pkill -9 "python.*kb.api" 2>/dev/null || true

sleep 2

# =================================================================
# Start Backend
# =================================================================

echo ""
log_info "=== Starting Backend (KB API) ==="

# Check if we should use Doppler or local .env
if [ -f ".env" ]; then
    log_warning "Found .env file, using it instead of Doppler"
    log_info "To use Doppler instead: rm .env && ./scripts/dev-start.sh"

    # Load .env and start backend
    export $(grep -v '^#' .env | xargs)
    log_info "Starting backend on port $BACKEND_PORT..."
    uv run uvicorn kb.api.app:create_app --host 0.0.0.0 --port $BACKEND_PORT > logs/backend.log 2>&1 &
    BACKEND_PID=$!
else
    log_info "Starting backend with Doppler (project: $DOPPLER_PROJECT, config: $DOPPLER_CONFIG)..."
    log_info "Backend will run on port $BACKEND_PORT"

    # Start backend with Doppler injecting environment variables
    doppler run --project "$DOPPLER_PROJECT" --config "$DOPPLER_CONFIG" -- \
        uv run uvicorn kb.api.app:create_app --host 0.0.0.0 --port $BACKEND_PORT > logs/backend.log 2>&1 &
    BACKEND_PID=$!
fi

log_success "Backend started (PID: $BACKEND_PID)"
echo "   Logs: logs/backend.log"
echo "   Health check: http://localhost:$BACKEND_PORT/health"

# =================================================================
# Start Frontend
# =================================================================

echo ""
log_info "=== Starting Frontend (Docusaurus) ==="

log_info "Installing frontend dependencies..."
if ! npm list --depth=0 > /dev/null 2>&1; then
    log_info "Installing node modules..."
    npm install --silent
fi

log_info "Starting frontend on port $FRONTEND_PORT..."
npm run start -- --no-open --host localhost --port $FRONTEND_PORT > logs/frontend.log 2>&1 &
FRONTEND_PID=$!

log_success "Frontend started (PID: $FRONTEND_PID)"
echo "   Logs: logs/frontend.log"
echo "   URL: http://localhost:$FRONTEND_PORT"

# =================================================================
# Wait for Services to be Ready
# =================================================================

echo ""
log_info "=== Waiting for services to be ready ==="
echo ""

# Create logs directory if it doesn't exist
mkdir -p logs

# Wait for backend
if ! wait_for_url "http://localhost:$BACKEND_PORT/health" "Backend API" 60; then
    log_error "Backend failed to start"
    echo ""
    echo "Check logs:"
    echo "  tail -f logs/backend.log"
    exit 1
fi

# Wait for frontend
if ! wait_for_url "http://localhost:$FRONTEND_PORT" "Frontend" 90; then
    log_error "Frontend failed to start"
    echo ""
    echo "Check logs:"
    echo "  tail -f logs/frontend.log"
    exit 1
fi

echo ""

# =================================================================
# Startup Complete
# =================================================================

log_success "=== Development environment is ready! ==="
echo ""
echo "Services:"
echo "  • Frontend: http://localhost:$FRONTEND_PORT"
echo "  • Backend:  http://localhost:$BACKEND_PORT"
echo "  • API Docs:  http://localhost:$BACKEND_PORT/docs"
echo ""
echo "Process IDs:"
echo "  • Backend PID:  $BACKEND_PID"
echo "  • Frontend PID: $FRONTEND_PID"
echo ""
echo "Logs:"
echo "  • Backend:  tail -f logs/backend.log"
echo "  • Frontend: tail -f logs/frontend.log"
echo ""
echo "To stop both services:"
echo "  • Press Ctrl+C or run: pkill -f 'uvicorn|npm run start'"
echo ""
echo "To restart:"
echo "  • Stop: pkill -f 'uvicorn|npm run start'"
echo "  • Start: ./scripts/dev-start.sh"
echo ""

# Save PIDs for later cleanup
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

# Handle script termination
trap 'log_info "Shutting down..."; kill $BACKEND_PID 2>/dev/null || true; kill $FRONTEND_PID 2>/dev/null || true; rm -f .backend.pid .frontend.pid; log_info "Done."' EXIT INT TERM

# Keep script running
log_info "Press Ctrl+C to stop all services..."
wait
