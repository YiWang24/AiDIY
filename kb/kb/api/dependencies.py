"""FastAPI dependency injection for config and retriever."""

from __future__ import annotations

import os
from functools import lru_cache

from fastapi import Depends


@lru_cache
def get_config():
    """Get application configuration.

    Loads configuration from file specified by KB_CONFIG env var
    or defaults to config.example.yaml.

    Returns:
        AppConfig: Application configuration
    """
    from kb.config import AppConfig, load_config, load_env_database_url

    config_path = os.getenv("KB_CONFIG", "config.example.yaml")
    config = load_config(config_path)
    config = load_env_database_url(config)

    return config


def create_retriever(config = Depends(get_config)):
    """Create hybrid retriever instance.

    Args:
        config: Application configuration

    Returns:
        HybridRetriever: Configured hybrid retriever
    """
    from kb.retrieval.vector_retriever import VectorRetriever
    from kb.retrieval.bm25_retriever import BM25Retriever
    from kb.retrieval.hybrid import HybridRetriever

    # Create vector retriever
    vector = VectorRetriever(config, config.storage.persist_dir)
    vector.load()

    # Create BM25 retriever
    bm25 = BM25Retriever(config, config.storage.persist_dir)

    # Set nodes for BM25 (load from storage)
    # For now, we'll need to load nodes from vector storage
    # This is a simplified version - production would share node storage
    bm25.set_nodes([])  # Will be populated when index is built

    # Create hybrid retriever
    return HybridRetriever(vector, bm25, config)
