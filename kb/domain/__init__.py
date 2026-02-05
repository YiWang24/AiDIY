"""Domain entities for KB indexing system.

This module contains immutable data structures that represent core concepts
in the knowledge base indexing pipeline.
"""

from kb.domain.document import Document
from kb.domain.chunk import Chunk

__all__ = ["Document", "Chunk"]
