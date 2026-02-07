#!/bin/bash

# ==============================================================================
# AiDIY Start Script
# Launches both frontend (Docusaurus) and backend (FastAPI) with Doppler
# ==============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Ports to kill
FRONTEND_PORT=3001
BACKEND_PORT=8001

# PIDs for cleanup
BACKEND_PID=""
FRONTEND_PID=""

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

kill_port() {
    local port=$1
    local service_name=$2

    # Find process using the port
    local pid=$(lsof -ti:$port 2>/dev/null || echo "")

    if [ -n "$pid" ]; then
        log_warning "Killing $service_name (PID: $pid) on port $port"
        kill -9 $pid 2>/dev/null || true
        sleep 1
        log_success "$service_name stopped"
    else
        log_info "Port $port is free (no $service_name running)"
    fi
}

kill_ports() {
    echo ""
    log_info "Checking ports $FRONTEND_PORT and $BACKEND_PORT..."
    kill_port $BACKEND_PORT "Backend API"
    kill_port $FRONTEND_PORT "Frontend"
    echo ""
}


# Sync Python dependencies with uv
sync_backend_deps() {
    log_info "Syncing backend dependencies with uv..."

    PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
    KB_DIR="$PROJECT_ROOT/kb"

    # Check if kb directory and pyproject.toml exist
    if [ ! -f "$KB_DIR/pyproject.toml" ]; then
        log_warning "pyproject.toml not found in kb/. Skipping backend sync."
        return
    fi

    # Sync dependencies with uv (continue even if it fails)
    if (cd "$KB_DIR" && uv sync); then
        log_success "Dependencies synced"
    else
        log_error "Failed to sync dependencies"
        return 1
    fi
}

# Run knowledge base pipeline
run_kb_pipeline() {
    log_info "Running knowledge base pipeline..."

    PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
    KB_DIR="$PROJECT_ROOT/kb"

    # Check if kb-build command exists
    if [ ! -d "$KB_DIR/.venv" ]; then
        log_warning "Backend virtual environment not found. Run sync first."
        return
    fi

    # Export PYTHONPATH and run kb-build with Doppler (continue even if it fails)
    export PYTHONPATH="$PROJECT_ROOT"
    if (cd "$KB_DIR" && \
        doppler run --project portfolio-api --config dev_personal -- \
            uv run kb-build); then
        log_success "Knowledge base pipeline completed"
    else
        log_warning "Knowledge base pipeline failed (continuing anyway)"
        log_info "This may be normal if database or API keys are not configured"
    fi
}

# Start backend
start_backend() {
    log_info "Starting backend API with Doppler..."

    # Get project root directory
    PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
    KB_DIR="$PROJECT_ROOT/kb"

    # Check if kb directory and .venv exist
    if [ ! -d "$KB_DIR/.venv" ]; then
        log_warning "Backend virtual environment not found. Skipping backend."
        log_info "Run: cd kb && uv sync"
        return
    fi

    # Start backend in background with Doppler and uv
    log_info "Backend: Starting FastAPI server on http://localhost:8000"
    log_info "Backend: Using Doppler project 'portfolio-api' and config 'dev_personal'"

    export PYTHONPATH="$PROJECT_ROOT"
    (cd "$KB_DIR" && \
        doppler run --project portfolio-api --config dev_personal -- \
            uv run uvicorn kb.api.app:create_app \
            --host 0.0.0.0 \
            --port 8001 \
            --reload \
            > "$PROJECT_ROOT/logs/backend.log" 2>&1 &) &

    BACKEND_PID=$!
    echo $BACKEND_PID > "$PROJECT_ROOT/logs/backend.pid"

    log_success "Backend started (PID: $BACKEND_PID)"
    log_info "Backend logs: logs/backend.log"
}

# Start frontend
start_frontend() {
    log_info "Starting frontend with Doppler..."

    # Get project root directory
    PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"

    # Check if package.json exists
    if [ ! -f "$PROJECT_ROOT/package.json" ]; then
        log_error "package.json not found!"
        exit 1
    fi

    # Install dependencies if needed
    if [ ! -d "$PROJECT_ROOT/node_modules" ]; then
        log_info "Installing frontend dependencies..."
        (cd "$PROJECT_ROOT" && npm install)
    fi

    # Start frontend in background with Doppler
    log_info "Frontend: Starting Docusaurus on http://localhost:3001"
    log_info "Frontend: Using Doppler project 'portfolio-web' and config 'dev_personal'"

    (cd "$PROJECT_ROOT" && \
        doppler run --project portfolio-web --config dev_personal -- \
            npm start \
            > logs/frontend.log 2>&1 &) &

    FRONTEND_PID=$!
    echo $FRONTEND_PID > "$PROJECT_ROOT/logs/frontend.pid"

    log_success "Frontend started (PID: $FRONTEND_PID)"
    log_info "Frontend logs: logs/frontend.log"
}

# Cleanup function
cleanup() {
    echo ""
    log_info "Stopping services..."

    PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"

    # Kill backend
    if [ -n "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        log_info "Backend stopped"
    fi
    if [ -f "$PROJECT_ROOT/logs/backend.pid" ]; then
        rm "$PROJECT_ROOT/logs/backend.pid"
    fi

    # Kill frontend
    if [ -n "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        log_info "Frontend stopped"
    fi
    if [ -f "$PROJECT_ROOT/logs/frontend.pid" ]; then
        rm "$PROJECT_ROOT/logs/frontend.pid"
    fi

    log_success "All services stopped"
    exit 0
}

# Trap signals for cleanup
trap cleanup INT TERM

# Main execution
main() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║           AiDIY - Frontend & Backend Starter              ║"
    echo "║                     with Doppler                             ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"

    # Kill existing processes on ports 3001 and 8000
    kill_ports

    # Create logs directory
    mkdir -p logs


    echo ""
    log_info "Starting services..."
    echo ""

    # Sync backend dependencies with uv
    sync_backend_deps
    echo ""

    # Run knowledge base pipeline
    run_kb_pipeline
    echo ""

    # Start backend
    start_backend
    echo ""

    # Wait a bit for backend to start
    sleep 2

    # Start frontend
    start_frontend
    echo ""

    # Display access information
    echo -e "${GREEN}"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║                      Services Started                          ║"
    echo "╠════════════════════════════════════════════════════════════╣"
    echo "║  Frontend: http://localhost:3001                               ║"
    echo "║  Backend:  http://localhost:8001                             ║"
    echo "║  API Docs:  http://localhost:8001/docs                           ║"
    echo "╠════════════════════════════════════════════════════════════╣"
    echo "║  Logs:                                                          ║"
    echo "║    - Frontend: tail -f logs/frontend.log                        ║"
    echo "║    - Backend:  tail -f logs/backend.log                         ║"
    echo "╠════════════════════════════════════════════════════════════╣"
    echo "║  Press Ctrl+C to stop all services                                ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"

}

# Run main function
main "$@"

# Keep script running
wait
