"""Document entity for KB indexing system."""

from dataclasses import dataclass, asdict


@dataclass(frozen=True, slots=True)
class Document:
    """Immutable document entity.

    Represents a single document in the knowledge base with metadata
    for incremental indexing and version tracking.

    Attributes:
        id: Unique document identifier (e.g., "blog:welcome-post")
        path: File path relative to content root (e.g., "blog/2025-01-17-welcome/index.md")
        title: Document title
        checksum: SHA-256 hash of document content for change detection
        version: Document version (default: "latest")
        content: Full document content (optional, lazy loaded)
        frontmatter: Frontmatter metadata dict (optional)
    """

    id: str
    path: str
    title: str
    checksum: str
    version: str = "latest"
    content: str | None = None
    frontmatter: dict | None = None

    def to_dict(self) -> dict:
        """Convert document to dictionary for serialization."""
        data = asdict(self)
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Document":
        """Create document from dictionary (JSONL format).

        Args:
            data: Dictionary with document fields

        Returns:
            Document instance
        """
        return cls(
            id=data["id"],
            path=data["path"],
            title=data["title"],
            checksum=data["checksum"],
            version=data.get("version", "latest"),
            content=data.get("content"),
            frontmatter=data.get("frontmatter"),
        )
