"""Tests for chunking strategy."""

from kb.pipeline.chunk import ChunkingStrategy
from kb.pipeline.config import ChunkingConfig
from kb.domain.document import Document


def test_simple_document_splitting():
    """Test splitting a simple document with headings."""
    doc = Document(
        id="test:doc1",
        path="test.md",
        title="Test",
        checksum="abc123",
        content="""# Introduction

This is the introduction.

## Getting Started

This is the getting started section.

## Advanced Topics

This is advanced content.
""",
    )

    chunker = ChunkingStrategy()
    chunks = chunker.split(doc)

    # Should have multiple chunks
    assert len(chunks) > 0

    # First chunk should be from Introduction
    assert chunks[0].heading_path == ["Introduction"]
    assert chunks[0].doc_id == "test:doc1"

    # Check chunk IDs are stable (deterministic)
    chunker2 = ChunkingStrategy()
    chunks2 = chunker2.split(doc)

    assert len(chunks) == len(chunks2)
    for c1, c2 in zip(chunks, chunks2):
        assert c1.chunk_id == c2.chunk_id


def test_chunk_id_stability():
    """Test that chunk IDs are stable across multiple runs."""
    doc = Document(
        id="test:stability",
        path="test.md",
        title="Test",
        checksum="abc123",
        content="""# Section 1

Content here.

# Section 2

More content.
""",
    )

    chunker = ChunkingStrategy()

    # Run 3 times
    chunks1 = chunker.split(doc)
    chunks2 = chunker.split(doc)
    chunks3 = chunker.split(doc)

    # All should have same IDs
    assert len(chunks1) == len(chunks2) == len(chunks3)

    for c1, c2, c3 in zip(chunks1, chunks2, chunks3):
        assert c1.chunk_id == c2.chunk_id == c3.chunk_id


def test_nested_heading_path():
    """Test that heading paths capture the hierarchy."""
    doc = Document(
        id="test:nested",
        path="test.md",
        title="Test",
        checksum="abc123",
        content="""# Main

## Subsection

Content here.

### Detail

More detail.
""",
    )

    chunker = ChunkingStrategy()
    chunks = chunker.split(doc)

    # Should capture nested hierarchy
    heading_paths = [c.heading_path for c in chunks]
    assert any("Detail" in path for path in heading_paths)


def test_long_section_splitting():
    """Test that long sections are recursively split."""
    # Create a very long section
    long_content = "# Long Section\n\n" + "Paragraph text. " * 500

    doc = Document(
        id="test:long",
        path="test.md",
        title="Test",
        checksum="abc123",
        content=long_content,
    )

    config = ChunkingConfig(max_section_chars=1000, chunk_size=200)
    chunker = ChunkingStrategy(config)
    chunks = chunker.split(doc)

    # Should be split into multiple chunks
    assert len(chunks) > 1

    # All chunks should be from the same heading
    for chunk in chunks:
        assert chunk.heading_path == ["Long Section"]


def test_empty_document():
    """Test handling empty document."""
    doc = Document(
        id="test:empty",
        path="test.md",
        title="Test",
        checksum="abc123",
        content="",
    )

    chunker = ChunkingStrategy()
    chunks = chunker.split(doc)

    assert len(chunks) == 0
