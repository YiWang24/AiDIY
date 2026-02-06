"""Unit tests for AnswerGenerator."""

import pytest
from unittest.mock import Mock
from kb.rag.answer_generator import AnswerGenerator
from kb.rag.retriever import RetrievedChunk
from kb.llm.base import LLMResponse


@pytest.fixture
def mock_llm():
    """Mock LLM instance."""
    llm = Mock()
    llm.model = "gemini-1.5-flash"
    return llm


@pytest.fixture
def mock_context_builder():
    """Mock ContextBuilder instance."""
    builder = Mock()
    builder.build_context = Mock(
        return_value="[1] AgentOps provides monitoring [2] LangChain framework"
    )
    return builder


@pytest.fixture
def sample_chunks():
    """Sample retrieved chunks."""
    return [
        RetrievedChunk(
            chunk_id="chunk1",
            doc_id="doc1",
            content="AgentOps provides monitoring for AI agents",
            heading_path=["AgentOps", "Overview"],
            chunk_index=0,
            score=0.95,
            citation_id=1,
        ),
        RetrievedChunk(
            chunk_id="chunk2",
            doc_id="doc2",
            content="LangChain is a framework for LLM applications",
            heading_path=["LangChain", "Introduction"],
            chunk_index=0,
            score=0.88,
            citation_id=2,
        ),
    ]


@pytest.fixture
def answer_generator(mock_llm, mock_context_builder):
    """Create AnswerGenerator instance with mocked dependencies."""
    return AnswerGenerator(llm=mock_llm, context_builder=mock_context_builder)


class TestAnswerGenerator:
    """Test suite for AnswerGenerator."""

    def test_generate_answer_success(self, answer_generator, mock_llm, sample_chunks):
        """Test successful answer generation."""
        # Mock LLM response
        mock_llm.generate.return_value = LLMResponse(
            content="AgentOps provides monitoring for AI agents [1]. LangChain is a framework [2].",
            model="gemini-1.5-flash",
            tokens_used=150,
            finish_reason="stop",
        )

        result = answer_generator.generate_answer(
            question="What is AgentOps?",
            chunks=sample_chunks,
        )

        assert (
            result["answer"]
            == "AgentOps provides monitoring for AI agents [1]. LangChain is a framework [2]."
        )
        assert result["model"] == "gemini-1.5-flash"
        assert result["tokens_used"] == 150
        assert result["has_sufficient_knowledge"] is True
        assert result["generation_time_ms"] >= 0
        assert len(result["citations"]) == 2

    def test_generate_answer_extracts_citations(
        self, answer_generator, mock_llm, sample_chunks
    ):
        """Test that citations are extracted from answer."""
        mock_llm.generate.return_value = LLMResponse(
            content="AgentOps provides monitoring [1].",
            model="gemini-1.5-flash",
            tokens_used=100,
        )

        result = answer_generator.generate_answer(
            question="What is AgentOps?",
            chunks=sample_chunks,
        )

        assert len(result["citations"]) == 1
        assert result["citations"][0]["id"] == 1
        assert result["citations"][0]["chunk_id"] == "chunk1"
        assert result["citations"][0]["doc_id"] == "doc1"

    def test_generate_answer_detects_insufficient_knowledge(
        self, answer_generator, mock_llm, sample_chunks
    ):
        """Test detection of insufficient knowledge."""
        mock_llm.generate.return_value = LLMResponse(
            content="I don't have enough information in the knowledge base to answer this question.",
            model="gemini-1.5-flash",
            tokens_used=50,
        )

        result = answer_generator.generate_answer(
            question="What is a topic not in the KB?",
            chunks=sample_chunks,
        )

        assert result["has_sufficient_knowledge"] is False

    def test_generate_answer_handles_missing_citations(
        self, answer_generator, mock_llm, sample_chunks
    ):
        """Test handling when answer doesn't include citations."""
        mock_llm.generate.return_value = LLMResponse(
            content="This is an answer without any citations.",
            model="gemini-1.5-flash",
            tokens_used=80,
        )

        result = answer_generator.generate_answer(
            question="Simple question",
            chunks=sample_chunks,
        )

        assert len(result["citations"]) == 0

    def test_generate_answer_preserves_heading_path(
        self, answer_generator, mock_llm, sample_chunks
    ):
        """Test that heading path is preserved in citations."""
        mock_llm.generate.return_value = LLMResponse(
            content="AgentOps provides monitoring [1].",
            model="gemini-1.5-flash",
            tokens_used=100,
        )

        result = answer_generator.generate_answer(
            question="What is AgentOps?",
            chunks=sample_chunks,
        )

        citation = result["citations"][0]
        assert citation["heading_path"] == ["AgentOps", "Overview"]

    def test_generate_answer_includes_score(
        self, answer_generator, mock_llm, sample_chunks
    ):
        """Test that score is included in citations."""
        mock_llm.generate.return_value = LLMResponse(
            content="AgentOps provides monitoring [1].",
            model="gemini-1.5-flash",
            tokens_used=100,
        )

        result = answer_generator.generate_answer(
            question="What is AgentOps?",
            chunks=sample_chunks,
        )

        citation = result["citations"][0]
        assert citation["score"] == 0.95

    def test_generate_answer_with_no_chunks(self, answer_generator, mock_llm):
        """Test behavior with no chunks."""
        mock_llm.generate.return_value = LLMResponse(
            content="I don't have enough information.",
            model="gemini-1.5-flash",
            tokens_used=30,
        )

        result = answer_generator.generate_answer(
            question="Unknown topic",
            chunks=[],
        )

        assert len(result["citations"]) == 0

    def test_generate_answer_uses_context_builder(
        self, answer_generator, mock_context_builder, mock_llm, sample_chunks
    ):
        """Test that context builder is called."""
        mock_llm.generate.return_value = LLMResponse(
            content="Test answer [1].",
            model="gemini-1.5-flash",
        )

        answer_generator.generate_answer(
            question="Test question",
            chunks=sample_chunks,
        )

        # Verify context builder was called
        mock_context_builder.build_context.assert_called_once_with(sample_chunks)

    def test_generate_answer_handles_llm_error(
        self, answer_generator, mock_llm, sample_chunks
    ):
        """Test handling of LLM errors."""
        mock_llm.generate.side_effect = RuntimeError("LLM API error")

        with pytest.raises(RuntimeError, match="LLM API error"):
            answer_generator.generate_answer(
                question="Test question",
                chunks=sample_chunks,
            )

    def test_initialization(self, mock_llm, mock_context_builder):
        """Test AnswerGenerator initialization."""
        generator = AnswerGenerator(llm=mock_llm, context_builder=mock_context_builder)

        assert generator._llm == mock_llm
        assert generator._context_builder == mock_context_builder
