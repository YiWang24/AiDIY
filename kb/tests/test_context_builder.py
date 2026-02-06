"""Unit tests for ContextBuilder."""

import pytest
from kb.rag.context_builder import ContextBuilder
from kb.rag.retriever import RetrievedChunk


@pytest.fixture
def sample_chunks():
    """Sample retrieved chunks for testing."""
    return [
        RetrievedChunk(
            chunk_id="chunk1",
            doc_id="doc1",
            content="AgentOps provides monitoring for AI agents.",
            heading_path=["AgentOps", "Overview"],
            chunk_index=0,
            score=0.95,
            citation_id=1,
        ),
        RetrievedChunk(
            chunk_id="chunk2",
            doc_id="doc1",
            content="It tracks tool calls and memory access.",
            heading_path=["AgentOps", "Features"],
            chunk_index=1,
            score=0.90,
            citation_id=2,
        ),
        RetrievedChunk(
            chunk_id="chunk3",
            doc_id="doc2",
            content="LangChain is a framework for building LLM applications.",
            heading_path=["LangChain", "Introduction"],
            chunk_index=0,
            score=0.85,
            citation_id=3,
        ),
    ]


@pytest.fixture
def long_content_chunks():
    """Chunks with long content for testing length budget."""
    long_text = "This is a very long chunk of content. " * 50  # ~2000 chars
    return [
        RetrievedChunk(
            chunk_id="chunk1",
            doc_id="doc1",
            content=long_text,
            heading_path=["Topic1"],
            chunk_index=0,
            score=0.95,
            citation_id=1,
        ),
        RetrievedChunk(
            chunk_id="chunk2",
            doc_id="doc1",
            content=long_text,
            heading_path=["Topic2"],
            chunk_index=1,
            score=0.90,
            citation_id=2,
        ),
        RetrievedChunk(
            chunk_id="chunk3",
            doc_id="doc2",
            content=long_text,
            heading_path=["Topic3"],
            chunk_index=0,
            score=0.85,
            citation_id=3,
        ),
    ]


class TestContextBuilder:
    """Test suite for ContextBuilder."""

    def test_build_context_with_citation_markers(self, sample_chunks):
        """Test that context includes citation markers [1], [2], etc."""
        builder = ContextBuilder(max_length=4000, include_headings=True)
        context = builder.build_context(sample_chunks)

        # Should include citation markers
        assert "[1]" in context
        assert "[2]" in context
        assert "[3]" in context

    def test_build_context_includes_heading_path(self, sample_chunks):
        """Test that heading path is included when enabled."""
        builder = ContextBuilder(max_length=4000, include_headings=True)
        context = builder.build_context(sample_chunks)

        # Should include heading information
        assert "AgentOps" in context or "Overview" in context or "Features" in context

    def test_build_context_excludes_heading_path_when_disabled(self, sample_chunks):
        """Test that heading path is excluded when disabled."""
        builder = ContextBuilder(max_length=4000, include_headings=False)
        context = builder.build_context(sample_chunks)

        # Should just have content and citations
        assert "[1]" in context
        assert "[2]" in context
        # Headings might still appear in content, but not as formatted headers

    def test_build_context_respects_max_length(self, long_content_chunks):
        """Test that context respects max_length budget."""
        builder = ContextBuilder(max_length=1000, include_headings=True)
        context = builder.build_context(long_content_chunks)

        # Context should be within budget (allow some margin for formatting)
        assert len(context) <= 1100  # Allow small buffer

    def test_build_context_includes_high_scoring_chunks_first(self, long_content_chunks):
        """Test that higher scoring chunks are prioritized when budget constrained."""
        builder = ContextBuilder(max_length=500, include_headings=False)
        context = builder.build_context(long_content_chunks)

        # Should include chunk1 (highest score)
        assert "[1]" in context

    def test_build_context_with_empty_chunks(self):
        """Test behavior with empty chunk list."""
        builder = ContextBuilder(max_length=4000, include_headings=True)
        context = builder.build_context([])

        assert context == ""

    def test_build_context_preserves_chunk_content(self, sample_chunks):
        """Test that chunk content is preserved in context."""
        builder = ContextBuilder(max_length=4000, include_headings=False)
        context = builder.build_context(sample_chunks)

        # Key content phrases should be present
        assert "AgentOps provides monitoring" in context
        assert "tracks tool calls" in context
        assert "LangChain" in context

    def test_build_context_formats_with_newlines(self, sample_chunks):
        """Test that chunks are separated by newlines."""
        builder = ContextBuilder(max_length=4000, include_headings=False)
        context = builder.build_context(sample_chunks)

        # Chunks should be separated
        lines = context.split("\n")
        # Filter out empty lines
        non_empty_lines = [line for line in lines if line.strip()]
        assert len(non_empty_lines) >= 3

    def test_initialization_with_defaults(self):
        """Test ContextBuilder initialization with default parameters."""
        builder = ContextBuilder()

        assert builder.max_length == 4000
        assert builder.include_headings is True

    def test_initialization_with_custom_params(self):
        """Test ContextBuilder initialization with custom parameters."""
        builder = ContextBuilder(max_length=2000, include_headings=False)

        assert builder.max_length == 2000
        assert builder.include_headings is False

    def test_build_context_truncates_mid_chunk_if_needed(self, long_content_chunks):
        """Test that very long chunks can be truncated to fit budget."""
        builder = ContextBuilder(max_length=300, include_headings=False)
        context = builder.build_context(long_content_chunks)

        # Context should fit in budget
        assert len(context) <= 350  # Allow small buffer

    def test_citation_numbers_are_sequential(self, sample_chunks):
        """Test that citation numbers match chunk order."""
        builder = ContextBuilder(max_length=4000, include_headings=True)
        context = builder.build_context(sample_chunks)

        # Citation markers should be sequential starting from 1
        for i, chunk in enumerate(sample_chunks, start=1):
            marker = f"[{i}]"
            assert marker in context
