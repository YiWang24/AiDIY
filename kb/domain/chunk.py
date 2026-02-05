"""Chunk entity for KB indexing system."""

from dataclasses import dataclass, asdict, field


@dataclass(frozen=True, slots=True)
class Chunk:
    """Immutable chunk entity.

    Represents a text chunk extracted from a document with hierarchical
    context (heading path) for semantic search.

    Attributes:
        chunk_id: Stable unique identifier (SHA-256 hash)
        doc_id: Parent document identifier
        content: Chunk text content
        heading_path: List of headings from root to this chunk (e.g., ["H1", "H2", "H3"])
        chunk_index: Sequential index within document
        metadata: Additional metadata dict (optional)
    """

    chunk_id: str
    doc_id: str
    content: str
    heading_path: list[str] = field(default_factory=list)
    chunk_index: int = 0
    metadata: dict | None = None

    def to_dict(self) -> dict:
        """Convert chunk to dictionary for serialization."""
        return asdict(self)
