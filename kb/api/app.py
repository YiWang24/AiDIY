"""FastAPI application factory."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from kb.api.routes import search, ask
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

    # Initialize dependencies best-effort.
    # In some environments (fresh deploy, network hiccups, missing external providers),
    # failing hard on startup makes the service impossible to debug. We prefer to
    # start the API and surface a degraded health status instead.
    app.state.startup_errors = []

    vs = VectorStore(
        database_url=config.database_url,
        embedding_model=config.embedding_model,
        gemini_api_key=config.gemini_api_key,
        table_name=config.vector_store_table_name,
        batch_size=config.vector_store_batch_size,
    )
    try:
        vs.initialize()
    except Exception as e:
        msg = f"VectorStore init failed: {e}"
        print(msg)
        app.state.startup_errors.append(msg)

    ds = DocStore(database_url=config.database_url)
    try:
        ds.initialize()
    except Exception as e:
        msg = f"DocStore init failed: {e}"
        print(msg)
        app.state.startup_errors.append(msg)

    if app.state.startup_errors:
        print("KB API started in degraded mode")
    else:
        print("KB API initialized successfully")

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
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(search.router)
    app.include_router(ask.router)

    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "message": "KB Q&A API",
            "version": "0.1.0",
            "endpoints": {
                "search": "/search",
                "ask": "/ask",
                "chat": "/chat (coming soon)",
            },
        }

    @app.get("/health")
    async def health():
        """Health check endpoint."""
        errors = getattr(app.state, "startup_errors", [])
        if errors:
            return {"status": "degraded", "startup_errors": errors}
        return {"status": "healthy"}

    return app
