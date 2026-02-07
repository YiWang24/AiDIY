#!/bin/bash

# ==============================================================================
# AiDIY Start Script
# Launches both frontend (Docusaurus) and backend (FastAPI) with Doppler
#
# Steps:
#   1. Kills existing processes on ports 3001 and 8000
#   2. Syncs backend dependencies with uv
#   3. Runs knowledge base pipeline (kb-build) with Doppler env vars
#   4. Starts backend API (FastAPI with uvicorn) with Doppler env vars
#   5. Starts frontend (Docusaurus) with Doppler env vars
#
# Environment Variables (from Doppler project: portfolio-api, config: dev_personal):
#
# PostgreSQL Database (Azure-style):
#   - POSTGRES_HOST: Database host (e.g., server-postgre.postgres.database.azure.com)
#   - POSTGRES_PORT: Database port (default: 5432)
#   - POSTGRES_USER: Database username
#   - POSTGRES_PASSWORD: Database password
#   - POSTGRES_DB: Database name
#   Or use legacy DATABASE_URL for PostgreSQL connection string
#
# API Keys:
#   - GEMINI_API_KEY: Gemini API for embeddings
#   - TAVILY_API_KEY: Tavily API for web search
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
BACKEND_PORT=8000

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

# Check if Doppler is installed
check_doppler() {
    if ! command -v doppler &> /dev/null; then
        log_error "Doppler CLI is not installed!"
        echo "Please install it first: https://docs.doppler.com/docs"
        exit 1
    fi
    log_success "Doppler CLI found"
}

# Check required commands
check_commands() {
    log_info "Checking required commands..."

    if ! command -v npm &> /dev/null; then
        log_error "npm is not installed!"
        exit 1
    fi

    if ! command -v python3 &> /dev/null; then
        log_error "python3 is not installed!"
        exit 1
    fi

    log_success "All required commands found"
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
            uv run kb-build --stage all); then
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
            --port 8000 \
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
    log_info "Stopping services..."

    if [ -f ".backend.pid" ]; then
        BACKEND_PID=$(cat .backend.pid)
        kill $BACKEND_PID 2>/dev/null || true
        rm logs/backend.pid
        log_info "Backend stopped"
    fi

    if [ -f ".frontend.pid" ]; then
        FRONTEND_PID=$(cat .frontend.pid)
        kill $FRONTEND_PID 2>/dev/null || true
        rm logs/frontend.pid
        log_info "Frontend stopped"
    fi

    log_success "All services stopped"
    exit 0
}

# Trap signals for cleanup
trap cleanup SIGINT SIGTERM

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

    # Run checks
    check_doppler
    check_commands


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
    echo "║  Backend:  http://localhost:8000                               ║"
    echo "║  API Docs:  http://localhost:8000/docs                           ║"
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
