"""FastAPI application factory."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psycopg

from kb.api.routes import search, ask, stream
from kb.api.dependencies import get_config
from kb.storage.docstore import DocStore
from kb.storage.vectorstore import VectorStore


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager.

    Initializes storage on startup and closes on shutdown.
    """
    # Startup: initialize connections
    print("Initializing KB API...")
    config = get_config()

    # IMPORTANT:
    # Do not block API startup on external dependencies (DB, embeddings provider).
    # CI/CD health checks should be able to succeed even if downstream services
    # are temporarily unavailable. Dependencies are initialized lazily per-request.
    app.state.startup_errors = []

    vs = VectorStore(
        database_url=config.get_database_url(),
        embedding_model=config.embedding_model,
        gemini_api_key=config.gemini_api_key,
        table_name=config.vector_store_table_name,
        batch_size=config.vector_store_batch_size,
    )
    ds = DocStore(database_url=config.get_database_url())

    # Keep references for future extension (e.g., eager init behind a flag).
    app.state._vector_store = vs
    app.state._doc_store = ds

    print("KB API started")

    yield

    # Shutdown: close connections
    print("Shutting down KB API...")
    try:
        vs.close()
    except Exception:
        pass
    try:
        ds.close()
    except Exception:
        pass
    print("KB API shutdown complete")


def create_app() -> FastAPI:
    """Create and configure FastAPI application.

    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title="KB Q&A API",
        description="RAG-based Question Answering API for knowledge base",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3001",
            "http://localhost:3000",
            "http://127.0.0.1:3001",
            "http://127.0.0.1:3000",
        ],  # Frontend URLs
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(search.router)
    app.include_router(ask.router)
    app.include_router(stream.router)

    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "message": "KB Q&A API",
            "version": "0.2.0",
            "primary_endpoint": {
                "stream": "/stream",
                "description": "Unified streaming API for all agent interactions",
            },
            "legacy_endpoints": {
                "search": "/search (deprecated, use /stream)",
                "ask": "/ask (deprecated, use /stream)",
            },
        }

    @app.get("/health")
    async def health():
        """Health check endpoint."""
        errors = getattr(app.state, "startup_errors", [])
        if errors:
            return {"status": "degraded", "startup_errors": errors}
        return {"status": "healthy"}

    @app.get("/ready")
    async def ready():
        """Readiness check endpoint.

        This is intended for container health checks. It verifies required config
        is present and the database is reachable.
        """
        config = get_config()

        # Check if database config is available (either URL or postgres_* params)
        db_url = config.get_database_url()
        if not db_url:
            raise HTTPException(
                status_code=503,
                detail="Database config not set (POSTGRES_* params or DATABASE_URL required)"
            )
        if not config.gemini_api_key:
            raise HTTPException(status_code=503, detail="GEMINI_API_KEY is not set")

        try:
            with psycopg.connect(db_url, connect_timeout=2) as conn:
                with conn.cursor() as cur:
                    cur.execute("select 1")
                    cur.fetchone()
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"DB not ready: {type(e).__name__}")

        return {"status": "ready"}

    return app
