"""Unit tests for KBRetriever."""

import pytest
from unittest.mock import Mock
from kb.rag.retriever import KBRetriever, RetrievedChunk


@pytest.fixture
def mock_vector_store():
    """Mock VectorStore instance."""
    vs = Mock()
    vs.search = Mock(return_value=[
        {
            "chunk_id": "chunk1",
            "doc_id": "doc1",
            "content": "AgentOps provides monitoring",
            "heading_path": ["AgentOps", "Overview"],
            "chunk_index": 0,
            "score": 0.95,
        },
        {
            "chunk_id": "chunk2",
            "doc_id": "doc1",
            "content": "AgentOps tracks tool calls",
            "heading_path": ["AgentOps", "Monitoring"],
            "chunk_index": 1,
            "score": 0.85,
        },
        {
            "chunk_id": "chunk3",
            "doc_id": "doc2",
            "content": "LangChain is a framework",
            "heading_path": ["LangChain", "Overview"],
            "chunk_index": 0,
            "score": 0.75,
        },
        {
            "chunk_id": "chunk4",
            "doc_id": "doc3",
            "content": "Unrelated low-score content",
            "heading_path": ["Other"],
            "chunk_index": 0,
            "score": 0.65,  # Below threshold
        },
    ])
    return vs


@pytest.fixture
def mock_doc_store():
    """Mock DocStore instance."""
    ds = Mock()
    ds.get_chunk_ids = Mock(return_value=["chunk1", "chunk2"])
    return ds


@pytest.fixture
def retriever(mock_vector_store, mock_doc_store):
    """Create KBRetriever instance with mocked dependencies."""
    return KBRetriever(
        vector_store=mock_vector_store,
        doc_store=mock_doc_store,
        score_threshold=0.7,
        max_chunks_per_doc=2,
    )


class TestKBRetriever:
    """Test suite for KBRetriever."""

    def test_search_filters_by_score_threshold(self, retriever):
        """Test that chunks below score threshold are filtered out."""
        results = retriever.search(query="AgentOps monitoring", top_k=10)

        # Should only include chunks with score >= 0.7
        assert len(results) == 3
        assert all(r.score >= 0.7 for r in results)

    def test_search_deduplicates_by_document(self, retriever):
        """Test that max_chunks_per_doc limits chunks per document."""
        results = retriever.search(query="AgentOps monitoring", top_k=10)

        # doc1 has 2 chunks above threshold, both should be included (max=2)
        doc1_chunks = [r for r in results if r.doc_id == "doc1"]
        assert len(doc1_chunks) == 2

    def test_search_respects_max_chunks_per_doc(self, retriever, mock_vector_store):
        """Test that max_chunks_per_doc limits chunks from same document."""
        # Add more chunks from same doc
        mock_vector_store.search.return_value.extend([
            {
                "chunk_id": "chunk5",
                "doc_id": "doc1",
                "content": "More AgentOps content",
                "heading_path": ["AgentOps", "Advanced"],
                "chunk_index": 2,
                "score": 0.90,
            },
            {
                "chunk_id": "chunk6",
                "doc_id": "doc1",
                "content": "Even more AgentOps",
                "heading_path": ["AgentOps", "Advanced"],
                "chunk_index": 3,
                "score": 0.88,
            },
        ])

        retriever.max_chunks_per_doc = 2
        results = retriever.search(query="AgentOps", top_k=10)

        # Should only have 2 chunks from doc1
        doc1_chunks = [r for r in results if r.doc_id == "doc1"]
        assert len(doc1_chunks) == 2
        # Should have highest scoring chunks
        assert doc1_chunks[0].chunk_id == "chunk1"
        assert doc1_chunks[1].chunk_id == "chunk5"

    def test_search_enriches_with_document_metadata(self, retriever):
        """Test that document metadata is included in results."""
        results = retriever.search(query="AgentOps", top_k=10)

        # Each result should have document metadata
        for result in results:
            assert hasattr(result, "doc_id")
            assert hasattr(result, "chunk_id")
            assert hasattr(result, "content")
            assert hasattr(result, "score")

    def test_search_returns_ranked_results(self, retriever):
        """Test that results are ranked by score (descending)."""
        results = retriever.search(query="AgentOps", top_k=10)

        # Scores should be in descending order
        scores = [r.score for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_search_with_empty_results(self, retriever, mock_vector_store):
        """Test behavior when no results found."""
        mock_vector_store.search.return_value = []

        results = retriever.search(query="nonexistent topic", top_k=10)

        assert len(results) == 0

    def test_search_with_all_results_below_threshold(self, retriever, mock_vector_store):
        """Test when all chunks are below score threshold."""
        mock_vector_store.search.return_value = [
            {
                "chunk_id": "chunk1",
                "doc_id": "doc1",
                "content": "Low score content",
                "heading_path": ["Topic"],
                "chunk_index": 0,
                "score": 0.5,
            }
        ]

        results = retriever.search(query="low score query", top_k=10)

        assert len(results) == 0

    def test_search_preserves_heading_path(self, retriever):
        """Test that heading path is preserved in results."""
        results = retriever.search(query="AgentOps", top_k=10)

        for result in results:
            assert hasattr(result, "heading_path")
            assert isinstance(result.heading_path, list)

    def test_initialization_with_defaults(self):
        """Test KBRetriever initialization with default parameters."""
        retriever = KBRetriever(
            vector_store=Mock(),
            doc_store=Mock(),
        )

        assert retriever.score_threshold == 0.7
        assert retriever.max_chunks_per_doc == 3

    def test_initialization_with_custom_params(self):
        """Test KBRetriever initialization with custom parameters."""
        retriever = KBRetriever(
            vector_store=Mock(),
            doc_store=Mock(),
            score_threshold=0.8,
            max_chunks_per_doc=5,
        )

        assert retriever.score_threshold == 0.8
        assert retriever.max_chunks_per_doc == 5


class TestRetrievedChunk:
    """Test suite for RetrievedChunk dataclass."""

    def test_retrieved_chunk_creation(self):
        """Test creating a RetrievedChunk instance."""
        chunk = RetrievedChunk(
            chunk_id="test-chunk",
            doc_id="test-doc",
            content="Test content",
            heading_path=["H1", "H2"],
            chunk_index=0,
            score=0.9,
            citation_id=1,
        )

        assert chunk.chunk_id == "test-chunk"
        assert chunk.doc_id == "test-doc"
        assert chunk.content == "Test content"
        assert chunk.heading_path == ["H1", "H2"]
        assert chunk.chunk_index == 0
        assert chunk.score == 0.9
        assert chunk.citation_id == 1

    def test_retrieved_chunk_to_dict(self):
        """Test converting RetrievedChunk to dictionary."""
        chunk = RetrievedChunk(
            chunk_id="test-chunk",
            doc_id="test-doc",
            content="Test content",
            heading_path=["H1", "H2"],
            chunk_index=0,
            score=0.9,
            citation_id=1,
        )

        result = chunk.to_dict()

        assert result["chunk_id"] == "test-chunk"
        assert result["doc_id"] == "test-doc"
        assert result["content"] == "Test content"
        assert result["heading_path"] == ["H1", "H2"]
        assert result["chunk_index"] == 0
        assert result["score"] == 0.9
        assert result["citation_id"] == 1
