"""Integration tests for API endpoints."""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

from kb.api.app import create_app


@pytest.fixture
def mock_vector_store():
    """Mock VectorStore for testing."""
    vs = Mock()
    vs.search = Mock(
        return_value=[
            {
                "chunk_id": "test-chunk-1",
                "doc_id": "test-doc-1",
                "content": "AgentOps provides monitoring for AI agents",
                "heading_path": ["AgentOps", "Overview"],
                "chunk_index": 0,
                "score": 0.95,
            },
            {
                "chunk_id": "test-chunk-2",
                "doc_id": "test-doc-2",
                "content": "LangChain is a framework for LLM applications",
                "heading_path": ["LangChain", "Introduction"],
                "chunk_index": 0,
                "score": 0.88,
            },
        ]
    )
    vs.close = Mock()
    vs.initialize = Mock()
    return vs


@pytest.fixture
def mock_doc_store():
    """Mock DocStore for testing."""
    ds = Mock()
    ds.list_documents = Mock(
        return_value=[
            {
                "doc_id": "test-doc-1",
                "path": "docs/ai/agentops/index.md",
                "title": "AgentOps and Security",
                "checksum": "abc123",
                "chunk_ids": ["test-chunk-1"],
            },
            {
                "doc_id": "test-doc-2",
                "path": "docs/ai/langchain/index.md",
                "title": "LangChain Framework",
                "checksum": "def456",
                "chunk_ids": ["test-chunk-2"],
            },
        ]
    )
    ds.close = Mock()
    ds.initialize = Mock()
    return ds


@pytest.fixture
def app(mock_vector_store, mock_doc_store):
    """Create test app with mocked dependencies."""

    # Create app factory that returns mocked dependencies
    def mock_get_vector_store():
        yield mock_vector_store

    def mock_get_doc_store():
        yield mock_doc_store

    # Patch before importing the app module
    with (
        patch(
            "kb.api.dependencies.get_vector_store", side_effect=mock_get_vector_store
        ),
        patch("kb.api.dependencies.get_doc_store", side_effect=mock_get_doc_store),
        patch("kb.api.app.get_vector_store", side_effect=mock_get_vector_store),
        patch("kb.api.app.get_doc_store", side_effect=mock_get_doc_store),
    ):
        # Clear the cached instances
        from kb.api import dependencies

        dependencies._vector_store_instance = mock_vector_store
        dependencies._doc_store_instance = mock_doc_store

        app = create_app()
        yield app


@pytest.fixture
def client(app):
    """Create test client."""
    yield TestClient(app)


class TestSearchEndpoint:
    """Test suite for /search endpoint."""

    def test_search_returns_results(self, client):
        """Test that search returns valid results."""
        response = client.post("/search", json={"query": "AgentOps monitoring", "k": 5})

        assert response.status_code == 200

        results = response.json()
        assert isinstance(results, list)
        assert len(results) == 2

        # Verify first result structure
        first_result = results[0]
        assert "chunk_id" in first_result
        assert "doc_id" in first_result
        assert "content" in first_result
        assert "heading_path" in first_result
        assert "score" in first_result
        assert "document" in first_result

    def test_search_includes_document_metadata(self, client):
        """Test that search includes document metadata."""
        response = client.post("/search", json={"query": "AgentOps", "k": 5})

        assert response.status_code == 200

        results = response.json()
        first_result = results[0]

        # Verify document metadata
        doc = first_result["document"]
        assert "title" in doc
        assert "path" in doc
        assert doc["title"] == "AgentOps and Security"
        assert doc["path"] == "docs/ai/agentops/index.md"

    def test_search_validates_query_not_empty(self, client):
        """Test that empty query is rejected."""
        response = client.post("/search", json={"query": "   ", "k": 5})

        assert response.status_code == 422  # Validation error

    def test_search_validates_k_range(self, client):
        """Test that k parameter is validated."""
        # k too low
        response = client.post("/search", json={"query": "test", "k": 0})
        assert response.status_code == 422

        # k too high
        response = client.post("/search", json={"query": "test", "k": 100})
        assert response.status_code == 422

    def test_search_handles_empty_results(self, mock_vector_store, client):
        """Test behavior when no results found."""
        mock_vector_store.search.return_value = []

        response = client.post("/search", json={"query": "nonexistent topic", "k": 5})

        assert response.status_code == 200
        results = response.json()
        assert results == []

    def test_search_handles_vector_store_error(self, mock_vector_store, client):
        """Test error handling when vector store fails."""
        mock_vector_store.search.side_effect = Exception("Database connection failed")

        response = client.post("/search", json={"query": "test", "k": 5})

        assert response.status_code == 500
        data = response.json()
        # FastAPI puts errors in "detail" field
        assert "detail" in data or "error" in data

    def test_search_results_ranked_by_score(self, client):
        """Test that results are ranked by score (descending)."""
        response = client.post("/search", json={"query": "test", "k": 5})

        assert response.status_code == 200

        results = response.json()
        scores = [r["score"] for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_search_preserves_heading_path(self, client):
        """Test that heading path is preserved in results."""
        response = client.post("/search", json={"query": "test", "k": 5})

        assert response.status_code == 200

        results = response.json()
        first_result = results[0]

        # Verify heading path
        assert "heading_path" in first_result
        assert isinstance(first_result["heading_path"], list)

    def test_root_endpoint(self, client):
        """Test root endpoint returns API info."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "endpoints" in data

    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestAskEndpoint:
    """Test suite for /ask endpoint."""

    @pytest.fixture
    def mock_llm(self):
        """Mock LLM for testing."""
        llm = Mock()
        llm.model = "gemini-1.5-flash"
        llm.generate = Mock(
            return_value=Mock(
                content="AgentOps provides monitoring for AI agents [1].",
                model="gemini-1.5-flash",
                tokens_used=150,
                finish_reason="stop",
            )
        )
        return llm

    @pytest.fixture
    def app_with_llm(self, mock_vector_store, mock_doc_store, mock_llm):
        """Create app with mocked LLM."""

        def mock_get_vector_store():
            yield mock_vector_store

        def mock_get_doc_store():
            yield mock_doc_store

        def mock_get_llm():
            yield mock_llm

        with (
            patch(
                "kb.api.dependencies.get_vector_store",
                side_effect=mock_get_vector_store,
            ),
            patch("kb.api.dependencies.get_doc_store", side_effect=mock_get_doc_store),
            patch("kb.api.app.get_vector_store", side_effect=mock_get_vector_store),
            patch("kb.api.app.get_doc_store", side_effect=mock_get_doc_store),
            patch("kb.api.routes.ask.get_llm", side_effect=mock_get_llm),
        ):
            from kb.api import dependencies

            dependencies._vector_store_instance = mock_vector_store
            dependencies._doc_store_instance = mock_doc_store

            # Clear LLM cache
            from kb.api.routes import ask

            ask._llm_instance = mock_llm

            app = create_app()
            yield app

    @pytest.fixture
    def ask_client(self, app_with_llm):
        """Create test client with LLM."""
        yield TestClient(app_with_llm)

    def test_ask_returns_answer_with_citations(self, ask_client):
        """Test that /ask returns valid answer with citations."""
        response = ask_client.post(
            "/ask", json={"question": "What is AgentOps?", "top_k": 5}
        )

        assert response.status_code == 200

        data = response.json()
        assert "answer" in data
        assert "citations" in data
        assert "model" in data
        assert "has_sufficient_knowledge" in data
        assert "retrieval_time_ms" in data
        assert "generation_time_ms" in data

        # Verify citations
        citations = data["citations"]
        assert isinstance(citations, list)
        if len(citations) > 0:
            first_citation = citations[0]
            assert "id" in first_citation
            assert "doc_id" in first_citation
            assert "title" in first_citation
            assert "path" in first_citation

    def test_ask_validates_question_not_empty(self, ask_client):
        """Test that empty question is rejected."""
        response = ask_client.post("/ask", json={"question": "   ", "top_k": 5})

        assert response.status_code == 422  # Validation error

    def test_ask_validates_top_k_range(self, ask_client):
        """Test that top_k parameter is validated."""
        response = ask_client.post("/ask", json={"question": "test", "top_k": 0})
        assert response.status_code == 422

        response = ask_client.post("/ask", json={"question": "test", "top_k": 100})
        assert response.status_code == 422

    def test_ask_enriches_citations_with_metadata(self, ask_client):
        """Test that citations include document metadata."""
        response = ask_client.post(
            "/ask", json={"question": "What is AgentOps?", "top_k": 5}
        )

        assert response.status_code == 200

        data = response.json()
        citations = data["citations"]

        if len(citations) > 0:
            # Verify document metadata is enriched
            first_citation = citations[0]
            assert first_citation["title"] in [
                "AgentOps and Security",
                "LangChain Framework",
            ]
            assert "path" in first_citation
