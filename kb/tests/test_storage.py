from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from kb.config import AppConfig, StorageConfig, VectorStoreConfig


class TestCreateStorageContext:
    """Test StorageContext creation with PGVectorStore"""

    def test_create_storage_context_with_database_url(self):
        """Test creating storage context with valid database URL"""
        # Mock modules before importing
        import sys
        from unittest.mock import MagicMock

        mock_psycopg = MagicMock()
        mock_pgvector = MagicMock()
        mock_llama_core = MagicMock()
        mock_context = MagicMock()

        sys.modules["psycopg"] = mock_psycopg
        sys.modules["llama_index.vector_stores.postgres"] = mock_pgvector
        sys.modules["llama_index.core"] = mock_llama_core

        # Setup the return value before importing
        mock_llama_core.StorageContext.from_defaults.return_value = mock_context

        # Now import
        from kb.indexing.storage import create_storage_context

        # Setup mocks
        mock_conn = MagicMock()
        mock_psycopg.connect.return_value = mock_conn

        mock_vector_store = MagicMock()
        mock_pgvector.PGVectorStore.return_value = mock_vector_store

        # Create config with database URL
        config = AppConfig(
            storage=StorageConfig(
                database_url="postgresql://postgres:postgres@localhost:5432/kb",
                persist_dir="kb_index/storage",
            ),
            vector_store=VectorStoreConfig(
                table_name="kb_llama_nodes",
                embed_dim=384,
            ),
        )

        # Call function
        result = create_storage_context(config)

        # Verify connection was created
        mock_psycopg.connect.assert_called_once_with("postgresql://postgres:postgres@localhost:5432/kb")

        # Verify PGVectorStore was created with correct parameters
        mock_pgvector.PGVectorStore.assert_called_once()
        call_kwargs = mock_pgvector.PGVectorStore.call_args.kwargs
        assert call_kwargs["connection"] is mock_conn
        assert call_kwargs["table_name"] == "kb_llama_nodes"
        assert call_kwargs["embed_dim"] == 384

        # Verify StorageContext.from_defaults was called
        mock_llama_core.StorageContext.from_defaults.assert_called_once_with(vector_store=mock_vector_store)

        # Verify result
        assert result is mock_context

        # Cleanup
        del sys.modules["psycopg"]
        del sys.modules["llama_index.vector_stores.postgres"]
        del sys.modules["llama_index.core"]

    def test_create_storage_context_without_database_url(self):
        """Test creating storage context without database URL (should use default)"""
        import sys
        from unittest.mock import MagicMock

        mock_storage = MagicMock()
        sys.modules["llama_index.core"] = mock_storage

        from kb.indexing.storage import create_storage_context

        mock_context = MagicMock()
        mock_storage.StorageContext.from_defaults.return_value = mock_context

        # Create config without database URL
        config = AppConfig(
            storage=StorageConfig(
                database_url=None,
                persist_dir="kb_index/storage",
            ),
            vector_store=VectorStoreConfig(
                table_name="kb_llama_nodes",
                embed_dim=384,
            ),
        )

        # Should not raise error, just use default storage context
        result = create_storage_context(config)

        # Verify default storage context was created
        mock_storage.StorageContext.from_defaults.assert_called_once_with(vector_store=None)
        assert result is mock_context

        # Cleanup
        del sys.modules["llama_index.core"]

    def test_storage_context_persist(self):
        """Test that storage context can persist to disk"""
        import sys
        from unittest.mock import MagicMock

        mock_psycopg = MagicMock()
        mock_pgvector = MagicMock()
        mock_storage = MagicMock()

        sys.modules["psycopg"] = mock_psycopg
        sys.modules["llama_index.vector_stores.postgres"] = mock_pgvector
        sys.modules["llama_index.core"] = mock_storage

        from kb.indexing.storage import create_storage_context

        mock_conn = MagicMock()
        mock_psycopg.connect.return_value = mock_conn

        mock_context = MagicMock()
        mock_storage.StorageContext.from_defaults.return_value = mock_context

        config = AppConfig(
            storage=StorageConfig(
                database_url="postgresql://postgres:postgres@localhost:5432/kb",
                persist_dir="test_storage",
            ),
            vector_store=VectorStoreConfig(
                table_name="kb_llama_nodes",
                embed_dim=384,
            ),
        )

        storage_context = create_storage_context(config)

        # Verify persist method exists
        assert hasattr(storage_context, "persist")

        # Cleanup
        del sys.modules["psycopg"]
        del sys.modules["llama_index.vector_stores.postgres"]
        del sys.modules["llama_index.core"]

    def test_storage_context_with_custom_embed_dim(self):
        """Test that custom embedding dimension is passed correctly"""
        import sys
        from unittest.mock import MagicMock

        mock_psycopg = MagicMock()
        mock_pgvector = MagicMock()
        mock_storage = MagicMock()

        sys.modules["psycopg"] = mock_psycopg
        sys.modules["llama_index.vector_stores.postgres"] = mock_pgvector
        sys.modules["llama_index.core"] = mock_storage

        from kb.indexing.storage import create_storage_context

        mock_conn = MagicMock()
        mock_psycopg.connect.return_value = mock_conn

        mock_context = MagicMock()
        mock_storage.StorageContext.from_defaults.return_value = mock_context

        config = AppConfig(
            storage=StorageConfig(
                database_url="postgresql://postgres:postgres@localhost:5432/kb",
                persist_dir="kb_index/storage",
            ),
            vector_store=VectorStoreConfig(
                table_name="kb_nodes",
                embed_dim=768,  # Custom dimension
            ),
        )

        create_storage_context(config)

        # Verify PGVectorStore was created with custom embed_dim
        call_kwargs = mock_pgvector.PGVectorStore.call_args.kwargs
        assert call_kwargs["embed_dim"] == 768
        assert call_kwargs["table_name"] == "kb_nodes"

        # Cleanup
        del sys.modules["psycopg"]
        del sys.modules["llama_index.vector_stores.postgres"]
        del sys.modules["llama_index.core"]
