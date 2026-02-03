from __future__ import annotations

from kb.config import AppConfig


def create_storage_context(config: AppConfig):
    """Create a StorageContext with PGVectorStore for vector embeddings.

    Args:
        config: Application configuration containing database URL and vector store settings.

    Returns:
        StorageContext: LlamaIndex StorageContext with vector store configured.
        Returns default StorageContext if no database URL is provided.
    """
    from llama_index.core import StorageContext

    # If no database URL, use default storage context
    if not config.storage.database_url:
        return StorageContext.from_defaults(vector_store=None)

    # Create PostgreSQL connection
    import psycopg

    conn = psycopg.connect(config.storage.database_url)

    # Create PGVectorStore
    from llama_index.vector_stores.postgres import PGVectorStore

    vector_store = PGVectorStore(
        connection=conn,
        table_name=config.vector_store.table_name,
        embed_dim=config.vector_store.embed_dim,
    )

    # Create and return StorageContext
    return StorageContext.from_defaults(vector_store=vector_store)
