# Development Scripts

Collection of scripts for local development of the KB API application.

## Prerequisites

### Required Tools

- **Doppler CLI** - Environment variable management
  ```bash
  brew install dopplerhq/cli/doppler
  doppler login
  ```

- **Node.js** - Frontend (Docusaurus)
  ```bash
  # Using nvm (recommended)
  nvm install node
  ```

- **Python 3.11+** - Backend (KB API)
  ```bash
  # Using uv (recommended)
  brew install uv
  ```

### Doppler Setup

1. **Create Doppler project**
   ```bash
   # Or use existing project
   doppler projects create kb-api-dev
   ```

2. **Create development config**
   ```bash
   doppler environments create kb-api-dev dev --name "Development"
   ```

3. **Configure secrets**
   ```bash
   # Database
   doppler secrets set DATABASE_URL "postgresql://..." --project kb-api-dev --config dev

   # LLM
   doppler secrets set GEMINI_API_KEY "your-key" --project kb-api-dev --config dev

   # Web Search
   doppler secrets set TAVILY_API_KEY "tvly-..." --project kb-api-dev --config dev

   # View all secrets
   doppler secrets list --project kb-api-dev --config dev
   ```

## Scripts

### `dev-start.sh`

Starts both frontend and backend for local development.

**What it does:**
1. Checks Doppler CLI and authentication
2. Kills existing processes on ports 8000 and 3001
3. Starts backend with Doppler environment injection
4. Starts frontend (Docusaurus)
5. Waits for both services to be ready
6. Saves process PIDs for cleanup

**Usage:**
```bash
./scripts/dev-start.sh
```

**Options:**
- Use `.env` file instead of Doppler:
  ```bash
  cp .env.example .env
  # Edit .env with your values
  ./scripts/dev-start.sh
  ```

- Configure Doppler project/config:
  ```bash
  DOPPLER_PROJECT=kb-api-dev DOPPLER_CONFIG=dev ./scripts/dev-start.sh
  ```

**Outputs:**
- Frontend: http://localhost:3001
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Logs: `logs/backend.log`, `logs/frontend.log`

### `dev-stop.sh`

Stops both frontend and backend processes.

**What it does:**
1. Stops backend using saved PID or port check
2. Stops frontend using saved PID or port check
3. Cleans up PID files

**Usage:**
```bash
./scripts/dev-stop.sh
```

### `dev-restart.sh`

Restarts both frontend and backend services.

**What it does:**
1. Stops all services
2. Waits for ports to be released
3. Starts all services

**Usage:**
```bash
./scripts/dev-restart.sh
```

## Environment Variables

See `.env.example` for all available environment variables.

### Required for Backend

- `DATABASE_URL` - PostgreSQL connection string
- `GEMINI_API_KEY` - Google Gemini API key
- `TAVILY_API_KEY` - Tavily search API key (optional)

### Optional Backend Variables

- `USE_HYBRID_SEARCH` - Enable hybrid search (default: true)
- `USE_RERANKING` - Enable reranking (default: true)
- `WEB_FALLBACK_ENABLED` - Enable web search fallback (default: true)
- `TOP_K_DEFAULT` - Default retrieval count (default: 10)
- `MAX_CONTEXT_LENGTH` - Max context length (default: 4000)
- `PORT` - API port (default: 8000)
- `LOG_LEVEL` - Logging level (default: INFO)

### Required for Frontend

- `BACKEND_URL` - Backend API URL
- `RAG_SYNC_KEY` - API key for RAG sync

### Optional Frontend Variables

- `CF_CLIENT_ID` - Cloudflare Access client ID
- `CF_CLIENT_SECRET` - Cloudflare Access client secret
- `RAG_SYNC_REQUIRED` - Fail build if RAG sync fails (default: false)

## Troubleshooting

### Port Already in Use

```bash
# Check what's using the port
lsof -ti :8000
lsof -ti :3001

# Kill the process
kill -9 <PID>

# Or stop all services
./scripts/dev-stop.sh
```

### Backend Not Starting

```bash
# Check logs
tail -f logs/backend.log

# Common issues:
# 1. Database not running - Start PostgreSQL
# 2. Missing env vars - Check Doppler config
# 3. Python dependencies - Run: uv sync
```

### Frontend Not Starting

```bash
# Check logs
tail -f logs/frontend.log

# Common issues:
# 1. Node modules missing - Run: npm install
# 2. Port conflict - Stop other processes on 3001
```

### Doppler Issues

```bash
# Check authentication
doppler me

# Check project access
doppler projects list

# Check secrets
doppler secrets list --project kb-api-dev --config dev

# Test injection
doppler run --project kb-api-dev --config dev -- env | grep DATABASE_URL
```

## Development Workflow

### Typical Workflow

1. **Start development environment**
   ```bash
   ./scripts/dev-start.sh
   ```

2. **Make changes**
   - Backend: Edit files in `kb/`
   - Frontend: Edit files in `docs/` or `src/`

3. **See changes**
   - Backend hot-reloads automatically
   - Frontend hot-reloads automatically
   - API changes require backend restart

4. **Stop when done**
   ```bash
   ./scripts/dev-stop.sh
   ```

### Testing API

```bash
# Health check
curl http://localhost:8000/health

# Ask endpoint
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"What is RAG?","top_k":3}'

# Search endpoint
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query":"hybrid search","k":5}'
```

## Production Deployment

For production deployment, see:
- `docs/ci-cd-architecture.md` - CI/CD architecture documentation
- `.github/workflows/release.yml` - GitHub Actions workflow

## Tips

### Quick Backend Restart

```bash
# Restart only backend (keep frontend running)
pkill -f uvicorn
doppler run -- uv run uvicorn kb.api.app:create_app --reload
```

### View Logs in Real-Time

```bash
# Backend logs
tail -f logs/backend.log

# Frontend logs
tail -f logs/frontend.log

# Both logs
tail -f logs/*.log
```

### Run in Background

```bash
# Start services in background
nohup ./scripts/dev-start.sh > /dev/null 2>&1 &

# Check if running
ps aux | grep "dev-start\|uvicorn\|docusaurus"
```
