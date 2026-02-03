"""FastAPI routes for KB API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, HTTPException, Depends

if TYPE_CHECKING:
    from kb.api.dependencies import HybridRetriever

from kb.api.schemas import AskRequest, AskResponse, SearchRequest, SearchResponse
from kb.citations import align_citations

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
async def search(
    request: SearchRequest,
    retriever: "HybridRetriever" = Depends(lambda: None),  # Placeholder
):
    """Semantic search over the knowledge base.

    Args:
        request: Search request with query and top_k
        retriever: Hybrid retriever instance

    Returns:
        SearchResponse with results
    """
    try:
        # Import here to avoid circular imports
        from kb.api.dependencies import create_retriever

        if retriever is None:
            retriever = create_retriever()

        results = retriever.retrieve(request.query, top_k=request.top_k)

        return SearchResponse(
            results=[
                SearchResult(
                    node_id=node.node_id,
                    text=node.get_content(),
                    metadata=node.metadata,
                    score=score,
                )
                for node, score in results
            ],
            total=len(results),
            query=request.query,
        )
    except Exception as e:
        # Log the actual error for debugging but don't expose to client
        raise HTTPException(status_code=500, detail="Search service unavailable")


@router.post("/ask", response_model=AskResponse)
async def ask(
    request: AskRequest,
    retriever: "HybridRetriever" = Depends(lambda: None),  # Placeholder
    config = Depends(lambda: None),  # Placeholder
):
    """Ask a question using the RAG agent.

    Args:
        request: Ask request with query and top_k
        retriever: Hybrid retriever instance
        config: Application configuration

    Returns:
        AskResponse with answer and sources
    """
    try:
        # Import here to avoid circular imports
        from kb.api.dependencies import create_retriever, get_config
        from kb.agent.executor import KBExecutor

        if config is None:
            config = get_config()
        if retriever is None:
            retriever = create_retriever(config)

        # Create executor and ask question
        executor = KBExecutor(retriever, config)
        result = executor.ask(request.query)

        # Perform citation alignment on the answer
        retrieved = retriever.retrieve(request.query, top_k=request.top_k)
        citation_result = align_citations(result["answer"], retrieved, strict=True)

        # Convert sources to dict format
        sources_dict = [
            {
                "node_id": s.node_id,
                "doc_id": s.doc_id,
                "path": s.path,
                "title": s.title,
                "heading_path": s.heading_path,
                "anchor": s.anchor,
            }
            for s in citation_result.sources
        ]

        return AskResponse(
            answer=citation_result.answer,
            sources=sources_dict,
            method=result["method"],
            status=citation_result.status,
        )
    except Exception as e:
        # Log the actual error for debugging but don't expose to client
        raise HTTPException(status_code=500, detail="Ask service unavailable")


# Import required classes
from kb.config import AppConfig
from kb.api.schemas import SearchResult
