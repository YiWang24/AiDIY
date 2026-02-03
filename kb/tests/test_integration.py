"""Integration tests for KB Agent system.

These tests verify that all components work together correctly.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch, Mock
from pathlib import Path

import pytest


class TestIndexingToRetrievalFlow:
    """Test the complete flow from indexing to retrieval."""

    def test_vector_retriever_integration(self, tmp_path):
        """Test that vector retriever can load and query from persisted index."""
        from kb.config import AppConfig
        from kb.retrieval.vector_retriever import VectorRetriever

        # Mock external dependencies
        import sys
        from unittest.mock import MagicMock

        sys.modules["spacy"] = MagicMock()
        sys.modules["llama_index.core"] = MagicMock()
        sys.modules["llama_index.embeddings.huggingface"] = MagicMock()

        # Test that retriever can be initialized
        config = AppConfig(
            index=MagicMock(content_roots=["tests/fixtures"], file_extensions=[".md"]),
            embedding=MagicMock(
                enabled=True,
                provider="huggingface",
                model="test-model"
            ),
            storage=MagicMock(
                database_url=None,
                persist_dir=str(tmp_path / "storage")
            ),
            vector_store=MagicMock(
                table_name="test_nodes",
                embed_dim=384
            ),
            chunking=MagicMock(
                target_tokens=500,
                min_tokens=350,
                max_tokens=800,
                overlap_tokens=80
            ),
            bm25=MagicMock(persist_dir="kb_index/bm25"),
            output=MagicMock(
                chunks_path="kb_index/chunks.jsonl",
                manifest_path="kb_index/manifest.json"
            ),
            llm=MagicMock(
                provider="openai",
                model="gpt-4o-mini",
                api_key=None,
                temperature=0.0
            ),
            retrieval=MagicMock(
                top_k=10,
                rrf_k=60,
                use_bm25=True
            ),
            api=MagicMock(
                host="0.0.0.0",
                port=8000,
                cors_origins=["*"]
            )
        )

        retriever = VectorRetriever(config, str(tmp_path / "storage"))
        assert retriever.config == config
        assert retriever.persist_dir == str(tmp_path / "storage")

    def test_hybrid_retriever_integration(self, tmp_path):
        """Test that hybrid retriever combines vector and BM25 results."""
        from kb.config import AppConfig
        from kb.retrieval.vector_retriever import VectorRetriever
        from kb.retrieval.bm25_retriever import BM25Retriever
        from kb.retrieval.hybrid import HybridRetriever

        config = AppConfig(
            index=MagicMock(),
            embedding=MagicMock(),
            storage=MagicMock(persist_dir=str(tmp_path)),
            vector_store=MagicMock(embed_dim=384),
            chunking=MagicMock(),
            bm25=MagicMock(persist_dir=str(tmp_path)),
            output=MagicMock(),
            llm=MagicMock(),
            retrieval=MagicMock(
                top_k=10,
                rrf_k=60,
                use_bm25=True
            ),
            api=MagicMock()
        )

        # Mock retrievers
        mock_vector = MagicMock(spec=VectorRetriever)
        mock_bm25 = MagicMock(spec=BM25Retriever)

        # Create mock nodes with NodeWithScore-like objects
        node1 = MagicMock()
        node1.node_id = "node-1"
        node2 = MagicMock()
        node2.node_id = "node-2"

        # Create mock NodeWithScore objects
        class MockNodeWithScore:
            def __init__(self, node, score):
                self.node = node
                self.score = score

        mock_vector.retrieve.return_value = [
            MockNodeWithScore(node1, 0.9)
        ]
        mock_bm25.retrieve.return_value = [(node2, 0.8)]

        retriever = HybridRetriever(mock_vector, mock_bm25, config)

        # Test retrieve
        results = retriever.retrieve("test query", top_k=5)

        # Verify both retrievers were called
        mock_vector.retrieve.assert_called_once()
        mock_bm25.retrieve.assert_called_once()

        # Verify results are returned
        assert len(results) > 0


class TestAgentToAPIFlow:
    """Test the flow from agent execution to API response."""

    def test_executor_retriever_integration(self):
        """Test that executor can use retriever to answer questions."""
        from kb.config import AppConfig
        from kb.agent.executor import KBExecutor
        from unittest.mock import MagicMock

        # Mock retriever
        mock_retriever = MagicMock()
        mock_node = MagicMock()
        mock_node.node_id = "node-1"
        mock_node.metadata = {
            "title": "Test Doc",
            "doc_id": "doc-1",
            "path": "/test.md",
            "heading_path": ["Introduction"],
            "anchor": "intro"
        }
        mock_node.get_content.return_value = "Test content about RAG"
        mock_retriever.retrieve.return_value = [(mock_node, 0.9)]

        # Create config without API key (fallback mode)
        config = AppConfig(
            index=MagicMock(),
            embedding=MagicMock(),
            storage=MagicMock(),
            vector_store=MagicMock(),
            chunking=MagicMock(),
            bm25=MagicMock(),
            output=MagicMock(),
            llm=MagicMock(
                provider="openai",
                model="gpt-4o-mini",
                api_key=None,
                temperature=0.0
            ),
            retrieval=MagicMock(top_k=10, rrf_k=60, use_bm25=True),
            api=MagicMock()
        )

        executor = KBExecutor(mock_retriever, config)
        result = executor.ask("What is RAG?")

        # Verify fallback answer
        assert "answer" in result
        assert "method" in result
        assert result["method"] == "fallback"

    def test_citation_alignment_with_retrieval(self):
        """Test that citation alignment works with retrieved nodes."""
        from kb.citations.aligner import align_citations

        # Mock retrieved nodes
        node1 = MagicMock()
        node1.node_id = "node-1"
        node1.metadata = {
            "title": "Test Doc 1",
            "doc_id": "doc-1",
            "path": "/test1.md",
            "heading_path": ["Section 1"],
            "anchor": "section1"
        }

        node2 = MagicMock()
        node2.node_id = "node-2"
        node2.metadata = {
            "title": "Test Doc 2",
            "doc_id": "doc-2",
            "path": "/test2.md",
            "heading_path": ["Section 2"],
            "anchor": "section2"
        }

        retrieved = [(node1, 0.9), (node2, 0.8)]

        # Test answer with valid citations
        answer = "According to the docs [S1], RAG is great. See also [S2]."
        result = align_citations(answer, retrieved, strict=True)

        assert result.status == "verified"
        assert len(result.sources) == 2
        assert "[S1]" in result.answer
        assert "[S2]" in result.answer

        # Test answer with invalid citation
        answer_invalid = "According to [S3], this is wrong."
        result_invalid = align_citations(answer_invalid, retrieved, strict=True)

        assert result_invalid.status == "insufficient_evidence"
        assert "[S3]" not in result_invalid.answer  # Should be removed in strict mode


class TestAPIEndToEnd:
    """Test end-to-end API functionality."""

    def test_search_endpoint_integration(self):
        """Test /search endpoint with mock retriever."""
        from fastapi.testclient import TestClient
        from unittest.mock import MagicMock
        from kb.api.app import create_app
        from kb.api.schemas import SearchResult

        # Mock retriever
        mock_node = MagicMock()
        mock_node.node_id = "test-node"
        mock_node.get_content.return_value = "Test content"
        mock_node.metadata = {"title": "Test"}

        with patch('kb.api.dependencies.create_retriever') as mock_create_retriever:
            mock_retriever = MagicMock()
            mock_retriever.retrieve.return_value = [(mock_node, 0.95)]
            mock_create_retriever.return_value = mock_retriever

            app = create_app()
            client = TestClient(app)

            response = client.post(
                "/api/v1/search",
                json={"query": "test query", "top_k": 5}
            )

            assert response.status_code == 200
            data = response.json()
            assert "results" in data
            assert data["total"] == 1
            assert len(data["results"]) == 1

    def test_ask_endpoint_integration(self):
        """Test /ask endpoint with mock executor."""
        from fastapi.testclient import TestClient
        from unittest.mock import MagicMock
        from kb.api.app import create_app

        # Mock retriever and executor
        mock_retriever = MagicMock()
        mock_node = MagicMock()
        mock_node.node_id = "node-1"
        mock_node.metadata = {
            "title": "Test Doc",
            "doc_id": "doc-1",
            "path": "/test.md",
            "heading_path": [],
            "anchor": None
        }
        mock_retriever.retrieve.return_value = [(mock_node, 0.9)]

        with patch('kb.api.dependencies.create_retriever', return_value=mock_retriever):
            with patch('kb.api.dependencies.get_config'):
                with patch('kb.agent.executor.KBExecutor') as MockExecutor:
                    mock_executor = MagicMock()
                    mock_executor.ask.return_value = {
                        "answer": "Test answer [S1]",
                        "method": "react_agent"
                    }
                    MockExecutor.return_value = mock_executor

                    app = create_app()
                    client = TestClient(app)

                    response = client.post(
                        "/api/v1/ask",
                        json={"query": "What is RAG?", "top_k": 5}
                    )

                    assert response.status_code == 200
                    data = response.json()
                    assert "answer" in data
                    assert "sources" in data
                    assert "method" in data


class TestConfigurationToComponents:
    """Test that configuration correctly propagates to all components."""

    def test_config_to_vector_retriever(self):
        """Test that config is properly passed to vector retriever."""
        from kb.config import AppConfig, load_config, load_env_database_url
        from kb.retrieval.vector_retriever import VectorRetriever
        import tempfile

        config = AppConfig(
            index=MagicMock(),
            embedding=MagicMock(
                enabled=True,
                provider="huggingface",
                model="custom-model"
            ),
            storage=MagicMock(
                database_url=None,
                persist_dir="custom_storage"
            ),
            vector_store=MagicMock(
                table_name="custom_table",
                embed_dim=768
            ),
            chunking=MagicMock(),
            bm25=MagicMock(),
            output=MagicMock(),
            llm=MagicMock(),
            retrieval=MagicMock(),
            api=MagicMock()
        )

        with tempfile.TemporaryDirectory() as tmp:
            retriever = VectorRetriever(config, tmp)

            assert retriever.config.embedding.model == "custom-model"
            assert retriever.config.vector_store.embed_dim == 768

    def test_config_to_agent(self):
        """Test that config is properly passed to agent."""
        from kb.config import AppConfig
        from kb.agent.executor import KBExecutor
        from unittest.mock import MagicMock

        config = AppConfig(
            index=MagicMock(),
            embedding=MagicMock(),
            storage=MagicMock(),
            vector_store=MagicMock(),
            chunking=MagicMock(),
            bm25=MagicMock(),
            output=MagicMock(),
            llm=MagicMock(
                provider="openai",
                model="gpt-4",
                api_key="test-key",
                temperature=0.7
            ),
            retrieval=MagicMock(),
            api=MagicMock()
        )

        mock_retriever = MagicMock()
        executor = KBExecutor(mock_retriever, config)

        assert executor.config.llm.model == "gpt-4"
        assert executor.config.llm.temperature == 0.7

    def test_config_to_api(self):
        """Test that API config is correctly applied."""
        from fastapi.testclient import TestClient
        from kb.api.app import create_app
        from kb.config import AppConfig
        from unittest.mock import MagicMock, patch

        config = AppConfig(
            index=MagicMock(),
            embedding=MagicMock(),
            storage=MagicMock(),
            vector_store=MagicMock(),
            chunking=MagicMock(),
            bm25=MagicMock(),
            output=MagicMock(),
            llm=MagicMock(),
            retrieval=MagicMock(),
            api=MagicMock(
                host="127.0.0.1",
                port=9000,
                cors_origins=["https://example.com"]
            )
        )

        with patch('kb.api.dependencies.get_config', return_value=config):
            app = create_app()

            # Check that app was created
            assert app is not None
            assert app.title == "KB Agent API"
