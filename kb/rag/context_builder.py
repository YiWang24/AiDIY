"""Context building for RAG prompts."""

from typing import List

from kb.rag.retriever import RetrievedChunk


class ContextBuilder:
    """Builds formatted context from retrieved chunks.

    Formats chunks with citation markers and manages context length budget.

    Attributes:
        max_length: Maximum characters for context (default: 4000)
        include_headings: Whether to include heading path (default: True)
    """

    def __init__(self, max_length: int = 4000, include_headings: bool = True):
        """Initialize ContextBuilder.

        Args:
            max_length: Maximum context length in characters
            include_headings: Include heading hierarchy in context
        """
        self.max_length = max_length
        self.include_headings = include_headings

    def build_context(self, chunks: List[RetrievedChunk]) -> str:
        """Build formatted context from chunks.

        Formats chunks with citation markers [1], [2], etc. and respects
        the max_length budget by prioritizing high-scoring chunks.

        Args:
            chunks: List of retrieved chunks (already ranked by score)

        Returns:
            Formatted context string with citation markers
        """
        if not chunks:
            return ""

        context_parts: List[str] = []
        current_length = 0

        for chunk in chunks:
            # Format this chunk
            chunk_text = self._format_chunk(chunk)

            # Check if adding this chunk would exceed budget
            if current_length + len(chunk_text) > self.max_length:
                # Try to fit a truncated version
                remaining = self.max_length - current_length
                if remaining > 100:  # Only truncate if we have meaningful space
                    truncated = self._truncate_chunk(chunk, remaining)
                    if truncated:
                        context_parts.append(truncated)
                break

            context_parts.append(chunk_text)
            current_length += len(chunk_text)

        return "\n\n".join(context_parts)

    def _format_chunk(self, chunk: RetrievedChunk) -> str:
        """Format a single chunk with citation marker.

        Args:
            chunk: Retrieved chunk to format

        Returns:
            Formatted chunk text with citation marker
        """
        citation = f"[{chunk.citation_id}]"
        content = chunk.content.strip()

        if self.include_headings and chunk.heading_path:
            heading = " > ".join(chunk.heading_path)
            return f"{citation} **{heading}**\n{content}"

        return f"{citation} {content}"

    def _truncate_chunk(self, chunk: RetrievedChunk, max_chars: int) -> str | None:
        """Truncate a chunk to fit within budget.

        Args:
            chunk: Retrieved chunk to truncate
            max_chars: Maximum characters for this chunk

        Returns:
            Truncated chunk text or None if can't fit
        """
        citation = f"[{chunk.citation_id}]"
        content = chunk.content.strip()

        # Reserve space for citation and formatting
        overhead = len(citation) + 10  # Extra for formatting
        available = max_chars - overhead

        if available < 50:  # Too short to be useful
            return None

        # Truncate content with ellipsis
        truncated = content[:available]
        if len(content) > available:
            truncated += "..."

        if self.include_headings and chunk.heading_path:
            heading = " > ".join(chunk.heading_path)
            return f"{citation} **{heading}**\n{truncated}"

        return f"{citation} {truncated}"
