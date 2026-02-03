"""LangChain tools for KB agent."""

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field


class KBSearchInput(BaseModel):
    """Input schema for KB search tool."""

    query: str = Field(description="Search query for knowledge base")
    top_k: int = Field(default=5, description="Number of results to return")


def create_kb_tool(retriever):
    """Create a LangChain tool for KB search.

    Args:
        retriever: HybridRetriever instance

    Returns:
        StructuredTool: LangChain tool for KB search
    """

    def search(query: str, top_k: int = 5) -> str:
        """Search the knowledge base for relevant documents.

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            Formatted search results
        """
        results = retriever.retrieve(query, top_k=top_k)

        output = []
        for i, (node, score) in enumerate(results, 1):
            metadata = node.metadata
            title = metadata.get("title", "Unknown")
            content = node.get_content()[:300]

            output.append(
                f"[Source {i}] {title}\n"
                f"Relevance: {score:.3f}\n"
                f"Content: {content}...\n"
            )

        return "\n\n".join(output)

    return StructuredTool.from_function(
        func=search,
        name="kb_search",
        description="Search knowledge base documents to answer technical questions",
        args_schema=KBSearchInput,
    )
