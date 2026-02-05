"""Index signature utilities for rebuild detection."""

import hashlib
import json

from kb.pipeline.config import Config


def _default_table_name(embedding_model: str) -> str:
    model_safe = embedding_model.replace("/", "_").replace("-", "_")
    return f"kb_chunks_{model_safe}"


def compute_signature(config: Config, embedding_dim: int) -> str:
    """Compute a stable signature for index compatibility."""
    payload = {
        "embedding_model": config.embedding_model,
        "embedding_dim": embedding_dim,
        "chunking": {
            "max_section_chars": config.chunking.max_section_chars,
            "chunk_size": config.chunking.chunk_size,
            "chunk_overlap": config.chunking.chunk_overlap,
        },
        "table_name": config.vector_store_table_name or _default_table_name(config.embedding_model),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
