"""Citation formatting for displaying sources with answers."""


def format_citations(result) -> str:
    """Format answer with citations for display.

    Args:
        result: CitationResult with answer and sources

    Returns:
        Formatted string with answer and source list
    """
    from kb.citations.aligner import CitationResult

    if not isinstance(result, CitationResult):
        result = CitationResult(
            answer=result.get("answer", ""),
            sources=[],
            status=result.get("status", "unknown"),
        )

    output = [result.answer]

    if result.sources:
        output.append("\n\n**Sources:**")
        for i, source in enumerate(result.sources, 1):
            path = source.path
            if source.anchor:
                path += f"#{source.anchor}"

            output.append(
                f"\n[S{i}] {source.title}\n"
                f"    Path: `{path}`"
            )

    return "\n".join(output)
