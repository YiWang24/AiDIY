"""Citation alignment system for KB answers."""

from __future__ import annotations

from kb.citations.aligner import CitationResult, SourceMetadata, align_citations
from kb.citations.formatter import format_citations

__all__ = [
    "SourceMetadata",
    "CitationResult",
    "align_citations",
    "format_citations",
]
