from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from kb.config import AppConfig, EmbeddingConfig, StorageConfig, VectorStoreConfig


class TestVectorRetriever:
    """Test VectorRetriever class"""

    def test_init(self):
        """Test VectorRetriever initialization"""
        from kb.retrieval.vector_retriever import VectorRetriever

        config = AppConfig(
            storage=StorageConfig(persist_dir="test_storage"),
            vector_store=VectorStoreConfig(embed_dim=384),
        )

        retriever = VectorRetriever(config, "test_storage")

        assert retriever.config is config
        assert retriever.persist_dir == "test_storage"
        assert retriever._index is None

    def test_load_creates_index(self):
        """Test that load() creates a VectorStoreIndex"""
        import sys
        from unittest.mock import MagicMock

        # Mock LlamaIndex modules
        mock_llama_core = MagicMock()
        mock_embeddings = MagicMock()
        sys.modules["llama_index.core"] = mock_llama_core
        sys.modules["llama_index.core.indices"] = MagicMock()
        sys.modules["llama_index.embeddings.huggingface"] = mock_embeddings

        from kb.retrieval.vector_retriever import VectorRetriever

        config = AppConfig(
            storage=StorageConfig(persist_dir="test_storage"),
            vector_store=VectorStoreConfig(embed_dim=384),
            embedding=EmbeddingConfig(model="BAAI/bge-small-en-v1.5"),
        )

        retriever = VectorRetriever(config, "test_storage")
        retriever.load()

        # Verify embed model was created
        assert retriever._embed_model is not None
        # Verify index was created
        assert retriever._index is not None

        # Cleanup
        del sys.modules["llama_index.core"]
        del sys.modules["llama_index.core.indices"]
        del sys.modules["llama_index.embeddings.huggingface"]

    def test_retrieve_returns_nodes(self):
        """Test that retrieve() returns relevant nodes"""
        import sys
        from unittest.mock import MagicMock

        # Mock modules
        mock_llama_core = MagicMock()

        # Create mock nodes
        mock_node1 = MagicMock()
        mock_node1.node_id = "node_1"
        mock_node1.get_content.return_value = "Content 1"
        mock_node1.score = 0.95

        mock_node2 = MagicMock()
        mock_node2.node_id = "node_2"
        mock_node2.get_content.return_value = "Content 2"
        mock_node2.score = 0.85

        # Create mock retriever result
        mock_retriever = MagicMock()
        mock_retriever.retrieve.return_value = [mock_node1, mock_node2]

        # Create mock index
        mock_index = MagicMock()
        mock_index.as_retriever.return_value = mock_retriever

        sys.modules["llama_index.core"] = mock_llama_core
        sys.modules["llama_index.embeddings.huggingface"] = MagicMock()

        from kb.retrieval.vector_retriever import VectorRetriever

        config = AppConfig(
            storage=StorageConfig(persist_dir="test_storage"),
            vector_store=VectorStoreConfig(embed_dim=384),
            embedding=EmbeddingConfig(model="BAAI/bge-small-en-v1.5"),
        )

        retriever = VectorRetriever(config, "test_storage")
        retriever._index = mock_index

        results = retriever.retrieve("test query", top_k=5)

        # Verify retriever was called
        mock_index.as_retriever.assert_called_once()
        mock_retriever.retrieve.assert_called_once_with("test query")

        # Cleanup
        del sys.modules["llama_index.core"]
        del sys.modules["llama_index.embeddings.huggingface"]

    def test_retrieve_with_custom_top_k(self):
        """Test retrieve() with custom top_k parameter"""
        import sys
        from unittest.mock import MagicMock

        mock_llama_core = MagicMock()
        mock_retriever = MagicMock()
        mock_retriever.retrieve.return_value = []

        mock_index = MagicMock()
        mock_index.as_retriever.return_value = mock_retriever

        sys.modules["llama_index.core"] = mock_llama_core
        sys.modules["llama_index.embeddings.huggingface"] = MagicMock()

        from kb.retrieval.vector_retriever import VectorRetriever

        config = AppConfig(
            storage=StorageConfig(persist_dir="test_storage"),
            vector_store=VectorStoreConfig(embed_dim=384),
        )

        retriever = VectorRetriever(config, "test_storage")
        retriever._index = mock_index

        retriever.retrieve("test query", top_k=20)

        # Verify similarity_top_k was passed correctly
        call_kwargs = mock_index.as_retriever.call_args.kwargs
        assert call_kwargs["similarity_top_k"] == 20

        # Cleanup
        del sys.modules["llama_index.core"]
        del sys.modules["llama_index.embeddings.huggingface"]
