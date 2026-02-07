"""FastAPI dependencies for dependency injection."""

from functools import lru_cache
from typing import Generator
from pathlib import Path

from kb.storage.docstore import DocStore
from kb.storage.vectorstore import VectorStore
from kb.pipeline.config import Config


@lru_cache
def get_config() -> Config:
    """Get cached configuration.

    Returns:
        Configuration object
    """
    config_path = Path(__file__).parent.parent / "config.yaml"
    return Config.from_yaml(str(config_path))


def get_database_url() -> str:
    """Get database URL from config.

    Returns:
        PostgreSQL connection URL (built from postgres_* params or database_url)
    """
    config = get_config()
    return config.get_database_url()


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

        _vector_store_instance = VectorStore(
            database_url=get_database_url(),
            embedding_model=config.embedding_model,
            gemini_api_key=config.gemini_api_key,
            table_name=config.vector_store_table_name,
            batch_size=config.vector_store_batch_size,
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


# ========== LLM Configuration ==========

def get_llm_config() -> dict:
    """Get LLM configuration.

    Returns:
        LLM configuration dictionary
    """
    config = get_config()
    return config.llm
