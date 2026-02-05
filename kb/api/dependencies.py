"""FastAPI dependencies for dependency injection."""

from functools import lru_cache
from typing import Generator
import yaml
from pathlib import Path

from fastapi import Depends

from kb.storage.docstore import DocStore
from kb.storage.vectorstore import VectorStore


@lru_cache
def get_config() -> dict:
    """Get cached configuration.

    Returns:
        Configuration dictionary
    """
    config_path = Path(__file__).parent.parent / "config.yaml"

    with open(config_path) as f:
        config = yaml.safe_load(f)

    return config


def get_database_url() -> str:
    """Get database URL from config.

    Returns:
        PostgreSQL connection URL
    """
    config = get_config()
    return config["storage"]["database_url"]


# ========== Vector Store Dependency ==========

_vector_store_instance: VectorStore | None = None


def get_vector_store() -> Generator[VectorStore, None, None]:
    """Get VectorStore instance.

    Yields:
        VectorStore instance for semantic search
    """
    global _vector_store_instance

    if _vector_store_instance is None:
        config = get_config()
        embedding_config = config["embedding"]
        gemini_config = config.get("gemini", {})

        _vector_store_instance = VectorStore(
            database_url=get_database_url(),
            embedding_provider=embedding_config["provider"],
            embedding_model=embedding_config["model"],
            gemini_api_key=gemini_config.get("api_key", ""),
        )
        _vector_store_instance.initialize()

    yield _vector_store_instance


# ========== Doc Store Dependency ==========

_doc_store_instance: DocStore | None = None


def get_doc_store() -> Generator[DocStore, None, None]:
    """Get DocStore instance.

    Yields:
        DocStore instance for document metadata
    """
    global _doc_store_instance

    if _doc_store_instance is None:
        _doc_store_instance = DocStore(database_url=get_database_url())
        _doc_store_instance.initialize()

    yield _doc_store_instance


# ========== RAG Configuration ==========

def get_rag_config() -> dict:
    """Get RAG configuration.

    Returns:
        RAG configuration dictionary
    """
    config = get_config()
    return config.get("rag", {})


def get_llm_config() -> dict:
    """Get LLM configuration.

    Returns:
        LLM configuration dictionary
    """
    config = get_config()
    return config.get("llm", {})
