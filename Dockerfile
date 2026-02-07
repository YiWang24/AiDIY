# Multi-stage build for KB RAG API
FROM python:3.11-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster dependency management
RUN pip install --no-cache-dir uv

# Copy lock + manifest first (better layer caching)
COPY kb/pyproject.toml kb/uv.lock /app/kb/

# Install runtime dependencies from lockfile (reproducible)
RUN cd /app/kb && \
    uv export --frozen --no-dev --format requirements.txt --output-file /tmp/requirements.txt && \
    uv pip install --system -r /tmp/requirements.txt

# Copy application code
COPY kb/ /app/kb/

# Install project
RUN cd /app && pip install --no-cache-dir ./kb

# Final stage
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create symlink for Python to match builder stage paths (force overwrite if exists)
RUN ln -sf /usr/local/bin/python3.11 /usr/local/bin/python

# Copy Python dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY kb/ /app/kb/

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "kb.api.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
