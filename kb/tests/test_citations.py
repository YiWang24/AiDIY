"""Tests for citation alignment system."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from kb.citations.aligner import CitationResult, SourceMetadata, align_citations
from kb.citations.formatter import format_citations


class TestSourceMetadata:
    """Test SourceMetadata dataclass."""

    def test_create_source_metadata(self):
        """Test creating SourceMetadata instance."""
        metadata = SourceMetadata(
            node_id="test_node_123",
            doc_id="doc_456",
            path="docs/test.md",
            title="Test Document",
            heading_path=["Introduction", "Overview"],
            anchor="overview",
        )

        assert metadata.node_id == "test_node_123"
        assert metadata.doc_id == "doc_456"
        assert metadata.path == "docs/test.md"
        assert metadata.title == "Test Document"
        assert metadata.heading_path == ["Introduction", "Overview"]
        assert metadata.anchor == "overview"

    def test_source_metadata_with_optional_fields(self):
        """Test SourceMetadata with optional anchor field."""
        metadata = SourceMetadata(
            node_id="node_1",
            doc_id="doc_1",
            path="docs/test.md",
            title="Test",
            heading_path=[],
            anchor=None,
        )

        assert metadata.anchor is None


class TestCitationResult:
    """Test CitationResult dataclass."""

    def test_create_citation_result(self):
        """Test creating CitationResult instance."""
        sources = [
            SourceMetadata(
                node_id="node_1",
                doc_id="doc_1",
                path="docs/test1.md",
                title="Doc 1",
                heading_path=[],
                anchor=None,
            )
        ]

        result = CitationResult(
            answer="Test answer [S1].",
            sources=sources,
            status="verified",
        )

        assert result.answer == "Test answer [S1]."
        assert len(result.sources) == 1
        assert result.status == "verified"


class TestAlignCitations:
    """Test citation alignment function."""

    def test_align_citations_with_valid_references(self):
        """Test align_citations with all valid [S#] references."""
        # Create mock nodes
        mock_node1 = MagicMock()
        mock_node1.node_id = "node_1"
        mock_node1.metadata = {
            "doc_id": "doc_1",
            "path": "docs/test1.md",
            "title": "Document 1",
            "heading_path": ["Intro"],
            "anchor": "intro",
        }

        mock_node2 = MagicMock()
        mock_node2.node_id = "node_2"
        mock_node2.metadata = {
            "doc_id": "doc_2",
            "path": "docs/test2.md",
            "title": "Document 2",
            "heading_path": [],
            "anchor": None,
        }

        retrieved_nodes = [
            (mock_node1, 0.95),
            (mock_node2, 0.85),
        ]

        answer = "According to [S1] and [S2], this is the answer."

        result = align_citations(answer, retrieved_nodes, strict=True)

        assert result.status == "verified"
        assert len(result.sources) == 2
        assert result.sources[0].title == "Document 1"
        assert result.sources[1].title == "Document 2"
        # Original answer should be preserved
        assert "[S1]" in result.answer
        assert "[S2]" in result.answer

    def test_align_citations_with_invalid_references(self):
        """Test align_citations with some invalid [S#] references."""
        mock_node1 = MagicMock()
        mock_node1.node_id = "node_1"
        mock_node1.metadata = {
            "doc_id": "doc_1",
            "path": "docs/test1.md",
            "title": "Document 1",
            "heading_path": [],
            "anchor": None,
        }

        retrieved_nodes = [
            (mock_node1, 0.95),
        ]

        # Answer has [S1], [S2], [S3] but only [S1] is valid
        answer = "According to [S1], [S2], and [S3], this is the answer."

        result = align_citations(answer, retrieved_nodes, strict=True)

        assert result.status == "partial"
        assert len(result.sources) == 1
        # In strict mode, invalid citations should be removed
        assert "[S2]" not in result.answer
        assert "[S3]" not in result.answer
        assert "[S1]" in result.answer

    def test_align_citations_strict_false_keeps_invalid(self):
        """Test that strict=False keeps invalid citations."""
        mock_node1 = MagicMock()
        mock_node1.node_id = "node_1"
        mock_node1.metadata = {
            "doc_id": "doc_1",
            "path": "docs/test1.md",
            "title": "Document 1",
            "heading_path": [],
            "anchor": None,
        }

        retrieved_nodes = [
            (mock_node1, 0.95),
        ]

        answer = "According to [S1] and [S2], this is the answer."

        result = align_citations(answer, retrieved_nodes, strict=False)

        # When strict=False, invalid citations are kept
        assert "[S1]" in result.answer or "[S2]" in result.answer

    def test_align_citations_no_valid_references(self):
        """Test align_citations with no valid references."""
        retrieved_nodes = []

        answer = "This is an answer without any citations."

        result = align_citations(answer, retrieved_nodes, strict=True)

        assert result.status == "insufficient_evidence"
        assert len(result.sources) == 0

    def test_align_citations_extracts_all_citations(self):
        """Test that all [S#] citations are extracted."""
        mock_node1 = MagicMock()
        mock_node1.node_id = "node_1"
        mock_node1.metadata = {"title": "Doc 1", "path": "d1.md", "doc_id": "doc1", "heading_path": [], "anchor": None}

        mock_node2 = MagicMock()
        mock_node2.node_id = "node_2"
        mock_node2.metadata = {"title": "Doc 2", "path": "d2.md", "doc_id": "doc2", "heading_path": [], "anchor": None}

        mock_node3 = MagicMock()
        mock_node3.node_id = "node_3"
        mock_node3.metadata = {"title": "Doc 3", "path": "d3.md", "doc_id": "doc3", "heading_path": [], "anchor": None}

        retrieved_nodes = [
            (mock_node1, 0.9),
            (mock_node2, 0.8),
            (mock_node3, 0.7),
        ]

        answer = "See [S1], [S2], and [S3] for details."

        result = align_citations(answer, retrieved_nodes, strict=True)

        assert len(result.sources) == 3
        assert result.status == "verified"


class TestFormatCitations:
    """Test citation formatting function."""

    def test_format_citations_with_sources(self):
        """Test format_citations with valid sources."""
        sources = [
            SourceMetadata(
                node_id="node_1",
                doc_id="doc_1",
                path="docs/test.md",
                title="Test Document",
                heading_path=["Chapter 1"],
                anchor="chapter-1",
            ),
            SourceMetadata(
                node_id="node_2",
                doc_id="doc_2",
                path="docs/other.md",
                title="Other Document",
                heading_path=[],
                anchor=None,
            ),
        ]

        result = CitationResult(
            answer="Test answer [S1] and [S2].",
            sources=sources,
            status="verified",
        )

        formatted = format_citations(result)

        # Should contain answer
        assert "Test answer [S1] and [S2]." in formatted
        # Should contain source list
        assert "**Sources:**" in formatted
        # Should contain source details
        assert "Test Document" in formatted
        assert "Other Document" in formatted
        # Should contain paths
        assert "docs/test.md#chapter-1" in formatted or "docs/test.md" in formatted
        assert "docs/other.md" in formatted

    def test_format_citations_without_sources(self):
        """Test format_citations with no sources."""
        result = CitationResult(
            answer="Test answer with no sources.",
            sources=[],
            status="insufficient_evidence",
        )

        formatted = format_citations(result)

        # Should just contain the answer
        assert "Test answer with no sources." in formatted

    def test_format_citations_includes_path_and_anchor(self):
        """Test that paths and anchors are formatted correctly."""
        sources = [
            SourceMetadata(
                node_id="node_1",
                doc_id="doc_1",
                path="docs/guide.md",
                title="User Guide",
                heading_path=["Installation"],
                anchor="installation",
            ),
        ]

        result = CitationResult(
            answer="Follow [S1] for installation.",
            sources=sources,
            status="verified",
        )

        formatted = format_citations(result)

        # Should include the anchor in the path
        assert "docs/guide.md#installation" in formatted
        assert "User Guide" in formatted
