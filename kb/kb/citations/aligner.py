"""Citation alignment for verifying and validating source references."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class SourceMetadata:
    """Metadata for a citation source."""

    node_id: str
    doc_id: str
    path: str
    title: str
    heading_path: list[str]
    anchor: str | None


@dataclass
class CitationResult:
    """Result of citation alignment."""

    answer: str
    sources: list[SourceMetadata]
    status: str  # "verified", "partial", "insufficient_evidence"


def align_citations(
    answer: str,
    retrieved_nodes: list[tuple[object, float]],
    strict: bool = True
) -> CitationResult:
    """Strict citation alignment - validates [S#] references.

    Args:
        answer: The answer text containing [S#] citations
        retrieved_nodes: List of (node, score) tuples from retrieval
        strict: If True, removes invalid citations; if False, keeps them

    Returns:
        CitationResult with validated answer and source metadata
    """
    # Extract [S#] citations using regex
    pattern = r'\[S(\d+)\]'
    citations = re.findall(pattern, answer)

    # Build mapping from citation number to source metadata
    sources = {}
    for i, (node, score) in enumerate(retrieved_nodes, 1):
        metadata = node.metadata
        sources[str(i)] = SourceMetadata(
            node_id=node.node_id,
            doc_id=metadata.get("doc_id", ""),
            path=metadata.get("path", ""),
            title=metadata.get("title", ""),
            heading_path=metadata.get("heading_path", []),
            anchor=metadata.get("anchor"),
        )

    # Check which citations are valid
    valid = []
    missing = []

    for cite_num in citations:
        if cite_num in sources:
            valid.append(cite_num)
        else:
            missing.append(f"[S{cite_num}]")

    # Process answer based on strict mode
    processed_answer = answer
    if strict and missing:
        for m in missing:
            processed_answer = processed_answer.replace(m, "")

    # Determine status
    if not missing and valid:
        status = "verified"
    elif valid:
        status = "partial"
    else:
        status = "insufficient_evidence"

    return CitationResult(
        answer=processed_answer.strip(),
        sources=[sources[c] for c in valid],
        status=status,
    )
