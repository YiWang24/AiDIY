"""End-to-end tests for KB Agent system.

These tests simulate real-world workflows from indexing to querying.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch
from pathlib import Path
import tempfile
import pytest


class TestE2EWorkflow:
    """Test complete end-to-end workflows."""

    def test_search_workflow(self):
        """Test complete search workflow: config -> retriever -> search -> results."""
        from fastapi.testclient import TestClient
        from kb.api.app import create_app

        # Mock the entire stack
        import sys
        sys.modules["spacy"] = MagicMock()
        sys.modules["llama_index.core"] = MagicMock()
        sys.modules["llama_index.embeddings.huggingface"] = MagicMock()

        # Create realistic mock nodes
        def create_mock_node(node_id: str, title: str, content: str, path: str):
            node = MagicMock()
            node.node_id = node_id
            node.metadata = {
                "title": title,
                "doc_id": node_id,
                "path": path,
                "heading_path": ["Introduction"],
                "anchor": "intro"
            }
            node.get_content.return_value = content
            return node

        # Setup mock retriever
        mock_retriever = MagicMock()
        mock_retriever.retrieve.return_value = [
            (create_mock_node(
                "node-1",
                "Vector Databases",
                "Vector databases store embeddings for semantic search.",
                "/docs/vector-db.md"
            ), 0.95),
            (create_mock_node(
                "node-2",
                "Embedding Models",
                "Embedding models convert text to vector representations.",
                "/docs/embeddings.md"
            ), 0.87),
            (create_mock_node(
                "node-3",
                "RAG Architecture",
                "RAG combines retrieval with generation for accurate answers.",
                "/docs/rag.md"
            ), 0.82),
        ]

        with patch('kb.api.dependencies.create_retriever', return_value=mock_retriever):
            with patch('kb.api.dependencies.get_config'):
                app = create_app()
                client = TestClient(app)

                # Execute search
                response = client.post(
                    "/api/v1/search",
                    json={"query": "vector database embeddings", "top_k": 5}
                )

                # Verify response
                assert response.status_code == 200
                data = response.json()

                assert data["query"] == "vector database embeddings"
                assert data["total"] == 3
                assert len(data["results"]) == 3

                # Verify first result is most relevant
                first_result = data["results"][0]
                assert first_result["score"] == 0.95
                assert first_result["metadata"]["title"] == "Vector Databases"
                assert "Vector databases" in first_result["text"]

                # Verify all results have required fields
                for result in data["results"]:
                    assert "node_id" in result
                    assert "text" in result
                    assert "metadata" in result
                    assert "score" in result
                    assert isinstance(result["score"], float)

    def test_ask_workflow_with_citations(self):
        """Test complete ask workflow: query -> retrieval -> agent -> citation alignment."""
        from fastapi.testclient import TestClient
        from kb.api.app import create_app

        # Mock external dependencies
        import sys
        sys.modules["spacy"] = MagicMock()
        sys.modules["llama_index.core"] = MagicMock()
        sys.modules["llama_index.embeddings.huggingface"] = MagicMock()
        sys.modules["langchain_openai"] = MagicMock()
        sys.modules["langchain"] = MagicMock()
        sys.modules["langchain.agents"] = MagicMock()
        sys.modules["langchain_core"] = MagicMock()

        # Create realistic mock nodes
        def create_mock_node(node_id: str, title: str, content: str, path: str):
            node = MagicMock()
            node.node_id = node_id
            node.metadata = {
                "title": title,
                "doc_id": node_id,
                "path": path,
                "heading_path": ["Overview"],
                "anchor": "overview"
            }
            node.get_content.return_value = content
            return node

        # Setup mock retriever
        mock_retriever = MagicMock()
        mock_retriever.retrieve.return_value = [
            (create_mock_node(
                "rag-101",
                "Introduction to RAG",
                "Retrieval-Augmented Generation (RAG) enhances LLMs by providing relevant context from a knowledge base.",
                "/docs/rag/introduction.md"
            ), 0.92),
            (create_mock_node(
                "vector-search-202",
                "Vector Search Fundamentals",
                "Vector search uses similarity metrics like cosine similarity to find relevant documents.",
                "/docs/vector/search.md"
            ), 0.88),
        ]

        # Setup mock executor
        with patch('kb.api.dependencies.create_retriever', return_value=mock_retriever):
            with patch('kb.api.dependencies.get_config'):
                with patch('kb.agent.executor.KBExecutor') as MockExecutor:
                    mock_executor = MagicMock()
                    mock_executor.ask.return_value = {
                        "answer": (
                            "Retrieval-Augmented Generation (RAG) enhances LLMs by providing "
                            "relevant context from a knowledge base [S1]. Vector search uses "
                            "similarity metrics like cosine similarity to find relevant documents [S2]."
                        ),
                        "method": "react_agent"
                    }
                    MockExecutor.return_value = mock_executor

                    app = create_app()
                    client = TestClient(app)

                    # Execute ask
                    response = client.post(
                        "/api/v1/ask",
                        json={"query": "What is RAG and how does vector search work?", "top_k": 5}
                    )

                    # Verify response
                    assert response.status_code == 200
                    data = response.json()

                    # Check answer
                    assert "answer" in data
                    assert "[S1]" in data["answer"]
                    assert "[S2]" in data["answer"]

                    # Check sources
                    assert "sources" in data
                    assert len(data["sources"]) == 2

                    # Verify source structure
                    source1 = data["sources"][0]
                    assert source1["node_id"] == "rag-101"
                    assert source1["title"] == "Introduction to RAG"
                    assert source1["path"] == "/docs/rag/introduction.md"

                    # Check method
                    assert data["method"] == "react_agent"

                    # Check status
                    assert data["status"] == "verified"

    def test_fallback_workflow_without_llm(self):
        """Test fallback workflow when LLM is not configured."""
        from fastapi.testclient import TestClient
        from kb.api.app import create_app

        # Mock external dependencies
        import sys
        sys.modules["spacy"] = MagicMock()
        sys.modules["llama_index.core"] = MagicMock()
        sys.modules["llama_index.embeddings.huggingface"] = MagicMock()

        # Create mock node
        mock_node = MagicMock()
        mock_node.node_id = "test-1"
        mock_node.metadata = {"title": "Test", "doc_id": "test-1", "path": "/test.md", "heading_path": [], "anchor": None}
        mock_node.get_content.return_value = "This is test content about RAG architecture."

        # Setup mock retriever
        mock_retriever = MagicMock()
        mock_retriever.retrieve.return_value = [(mock_node, 0.9)]

        # Setup mock executor without API key
        with patch('kb.api.dependencies.create_retriever', return_value=mock_retriever):
            with patch('kb.api.dependencies.get_config'):
                with patch('kb.agent.executor.KBExecutor') as MockExecutor:
                    mock_executor = MagicMock()
                    mock_executor.ask.return_value = {
                        "answer": "Found 1 relevant documents, but currently in fallback mode (no LLM API key).\n\nMost relevant content:\n\nThis is test content about RAG architecture.",
                        "method": "fallback"
                    }
                    MockExecutor.return_value = mock_executor

                    app = create_app()
                    client = TestClient(app)

                    # Execute ask
                    response = client.post(
                        "/api/v1/ask",
                        json={"query": "Explain RAG architecture", "top_k": 3}
                    )

                    # Verify fallback response
                    assert response.status_code == 200
                    data = response.json()

                    assert data["method"] == "fallback"
                    assert "fallback" in data["answer"].lower() or "no llm" in data["answer"].lower()

    def test_health_check_workflow(self):
        """Test health check endpoint."""
        from fastapi.testclient import TestClient
        from kb.api.app import create_app

        with patch('kb.api.dependencies.get_config'):
            app = create_app()
            client = TestClient(app)

            response = client.get("/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"


class TestE2EErrorHandling:
    """Test error handling in end-to-end workflows."""

    def test_empty_query_handling(self):
        """Test that empty queries are properly rejected."""
        from fastapi.testclient import TestClient
        from kb.api.app import create_app

        with patch('kb.api.dependencies.get_config'):
            app = create_app()
            client = TestClient(app)

            # Test search with empty query
            response = client.post(
                "/api/v1/search",
                json={"query": "", "top_k": 5}
            )

            # Should fail validation
            assert response.status_code == 422

    def test_invalid_top_k_handling(self):
        """Test that invalid top_k values are rejected."""
        from fastapi.testclient import TestClient
        from kb.api.app import create_app

        with patch('kb.api.dependencies.get_config'):
            app = create_app()
            client = TestClient(app)

            # Test search with top_k > 50 (max allowed)
            response = client.post(
                "/api/v1/search",
                json={"query": "test", "top_k": 100}
            )

            # Should fail validation
            assert response.status_code == 422

    def test_ask_query_too_long(self):
        """Test that overly long queries are rejected."""
        from fastapi.testclient import TestClient
        from kb.api.app import create_app

        with patch('kb.api.dependencies.get_config'):
            app = create_app()
            client = TestClient(app)

            # Test with query exceeding 500 characters
            long_query = "a" * 501

            response = client.post(
                "/api/v1/ask",
                json={"query": long_query, "top_k": 5}
            )

            # Should fail validation
            assert response.status_code == 422


class TestE2EDataFlow:
    """Test data flows through the system."""

    def test_config_propagation_to_retriever(self):
        """Test that configuration properly propagates to retriever."""
        from kb.config import AppConfig
        from kb.retrieval.vector_retriever import VectorRetriever

        # Mock dependencies
        import sys
        sys.modules["spacy"] = MagicMock()
        sys.modules["llama_index.core"] = MagicMock()
        sys.modules["llama_index.embeddings.huggingface"] = MagicMock()

        config = AppConfig(
            index=MagicMock(content_roots=["docs"], file_extensions=[".md"]),
            embedding=MagicMock(
                enabled=True,
                provider="huggingface",
                model="custom-model-name"
            ),
            storage=MagicMock(database_url=None, persist_dir="/tmp/test"),
            vector_store=MagicMock(table_name="custom_table", embed_dim=768),
            chunking=MagicMock(),
            bm25=MagicMock(persist_dir="/tmp/bm25"),
            output=MagicMock(),
            llm=MagicMock(),
            retrieval=MagicMock(),
            api=MagicMock()
        )

        with tempfile.TemporaryDirectory() as tmp:
            retriever = VectorRetriever(config, tmp)

            # Verify config propagated correctly
            assert retriever.config.embedding.model == "custom-model-name"
            assert retriever.config.vector_store.embed_dim == 768

    def test_retrieval_to_citation_flow(self):
        """Test that retrieved nodes flow correctly into citation alignment."""
        from kb.citations.aligner import align_citations

        # Create mock nodes
        node1 = MagicMock()
        node1.node_id = "node-1"
        node1.metadata = {
            "title": "Doc 1",
            "doc_id": "doc-1",
            "path": "/doc1.md",
            "heading_path": ["Section 1"],
            "anchor": "s1"
        }

        node2 = MagicMock()
        node2.node_id = "node-2"
        node2.metadata = {
            "title": "Doc 2",
            "doc_id": "doc-2",
            "path": "/doc2.md",
            "heading_path": ["Section 2"],
            "anchor": "s2"
        }

        retrieved = [(node1, 0.9), (node2, 0.8)]

        # Test valid citation alignment
        answer = "According to Doc 1 [S1], and Doc 2 [S2], this works well."
        result = align_citations(answer, retrieved, strict=True)

        assert result.status == "verified"
        assert len(result.sources) == 2
        assert result.sources[0].node_id == "node-1"
        assert result.sources[1].node_id == "node-2"
        assert "[S1]" in result.answer
        assert "[S2]" in result.answer
