"""Tests for domain entities (Document and Chunk)."""

import pytest

from kb.domain.document import Document
from kb.domain.chunk import Chunk


class TestDocument:
    """Test Document entity creation and validation."""

    def test_create_document_with_required_fields(self):
        """Test creating a document with minimal required fields."""
        doc = Document(
            id="doc1",
            path="docs/test.md",
            title="Test Document",
            checksum="abc123",
        )

        assert doc.id == "doc1"
        assert doc.path == "docs/test.md"
        assert doc.title == "Test Document"
        assert doc.checksum == "abc123"
        assert doc.version == "latest"  # Default value
        assert doc.content is None  # Optional field
        assert doc.frontmatter is None  # Optional field

    def test_create_document_with_all_fields(self):
        """Test creating a document with all fields."""
        frontmatter = {"tags": ["test"], "author": "test"}
        doc = Document(
            id="doc1",
            path="docs/test.md",
            title="Test Document",
            checksum="abc123",
            version="v1.0",
            content="# Test Content\n\nThis is test content.",
            frontmatter=frontmatter,
        )

        assert doc.id == "doc1"
        assert doc.version == "v1.0"
        assert doc.content.startswith("# Test Content")
        assert doc.frontmatter == frontmatter

    def test_document_from_dict(self):
        """Test creating a document from a dictionary (JSONL format)."""
        data = {
            "id": "doc1",
            "path": "docs/test.md",
            "title": "Test Document",
            "checksum": "abc123",
            "version": "v1.0",
            "content": "# Content",
            "frontmatter": {"tags": ["test"]},
        }

        doc = Document.from_dict(data)

        assert doc.id == "doc1"
        assert doc.path == "docs/test.md"
        assert doc.title == "Test Document"
        assert doc.checksum == "abc123"
        assert doc.version == "v1.0"
        assert doc.content == "# Content"
        assert doc.frontmatter == {"tags": ["test"]}

    def test_document_to_dict(self):
        """Test converting a document to a dictionary."""
        doc = Document(
            id="doc1",
            path="docs/test.md",
            title="Test Document",
            checksum="abc123",
            content="# Content",
            frontmatter={"tags": ["test"]},
        )

        data = doc.to_dict()

        assert data["id"] == "doc1"
        assert data["path"] == "docs/test.md"
        assert data["title"] == "Test Document"
        assert data["checksum"] == "abc123"
        assert data["content"] == "# Content"
        assert data["frontmatter"] == {"tags": ["test"]}

    def test_document_immutability(self):
        """Test that Document is frozen (immutable)."""
        doc = Document(
            id="doc1",
            path="docs/test.md",
            title="Test Document",
            checksum="abc123",
        )

        with pytest.raises(Exception):  # FrozenInstanceError
            doc.title = "New Title"

    def test_document_with_frontmatter_none(self):
        """Test document with None frontmatter uses empty dict in to_dict."""
        doc = Document(
            id="doc1",
            path="docs/test.md",
            title="Test Document",
            checksum="abc123",
        )

        data = doc.to_dict()

        # Should have frontmatter key with None or empty dict
        assert "frontmatter" in data


class TestChunk:
    """Test Chunk entity creation and validation."""

    def test_create_chunk_with_required_fields(self):
        """Test creating a chunk with minimal required fields."""
        chunk = Chunk(
            chunk_id="chunk1",
            doc_id="doc1",
            content="This is chunk content.",
        )

        assert chunk.chunk_id == "chunk1"
        assert chunk.doc_id == "doc1"
        assert chunk.content == "This is chunk content."
        assert chunk.heading_path == []  # Default empty list
        assert chunk.chunk_index == 0  # Default
        assert chunk.metadata is None  # Optional

    def test_create_chunk_with_all_fields(self):
        """Test creating a chunk with all fields."""
        metadata = {
            "tokens": 150,
            "headings": ["H1", "H2"],
        }
        chunk = Chunk(
            chunk_id="chunk1",
            doc_id="doc1",
            content="This is chunk content.",
            heading_path=["Introduction", "Getting Started"],
            chunk_index=1,
            metadata=metadata,
        )

        assert chunk.heading_path == ["Introduction", "Getting Started"]
        assert chunk.chunk_index == 1
        assert chunk.metadata == metadata

    def test_chunk_to_dict(self):
        """Test converting a chunk to a dictionary."""
        chunk = Chunk(
            chunk_id="chunk1",
            doc_id="doc1",
            content="This is chunk content.",
            heading_path=["Introduction"],
            chunk_index=0,
            metadata={"tokens": 100},
        )

        data = chunk.to_dict()

        assert data["chunk_id"] == "chunk1"
        assert data["doc_id"] == "doc1"
        assert data["content"] == "This is chunk content."
        assert data["heading_path"] == ["Introduction"]
        assert data["chunk_index"] == 0
        assert data["metadata"] == {"tokens": 100}

    def test_chunk_immutability(self):
        """Test that Chunk is frozen (immutable)."""
        chunk = Chunk(
            chunk_id="chunk1",
            doc_id="doc1",
            content="Content",
        )

        with pytest.raises(Exception):  # FrozenInstanceError
            chunk.content = "New content"

    def test_chunk_metadata_defaults_to_none(self):
        """Test that chunk metadata defaults to None."""
        chunk = Chunk(
            chunk_id="chunk1",
            doc_id="doc1",
            content="Content",
        )

        assert chunk.metadata is None
        assert chunk.to_dict().get("metadata") is None
