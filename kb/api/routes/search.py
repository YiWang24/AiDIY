"""Search endpoint for raw semantic search."""

import time
from typing import List

from fastapi import APIRouter, HTTPException, Depends

from kb.api.schemas import SearchRequest, SearchResponse, SearchResult, DocumentMetadata
from kb.api.dependencies import get_vector_store, get_doc_store
from kb.storage.vectorstore import VectorStore
from kb.storage.docstore import DocStore
from kb.rag.retriever import KBRetriever

router = APIRouter(prefix="/search", tags=["search"])


@router.post("", response_model=SearchResponse)
async def search(
    request: SearchRequest,
    vector_store: VectorStore = Depends(get_vector_store),
    doc_store: DocStore = Depends(get_doc_store),
) -> SearchResponse:
    """Semantic search without LLM generation.

    Returns raw chunks from the knowledge base ranked by semantic similarity.

    Args:
        request: Search request with query and k
        vector_store: Vector store dependency
        doc_store: Document store dependency

    Returns:
        List of search results with metadata

    Raises:
        HTTPException: If search fails
    """
    try:
        start_time = time.time()

        # Perform semantic search
        raw_results = vector_store.search(query=request.query, k=request.k)

        retrieval_time_ms = int((time.time() - start_time) * 1000)

        # Enrich with document metadata
        results: List[SearchResult] = []
        for result in raw_results:
            doc_id = result.get("doc_id", "")

            # Get document metadata
            doc_metadata = _get_document_metadata(doc_store, doc_id)

            search_result = SearchResult(
                chunk_id=result.get("chunk_id", ""),
                doc_id=doc_id,
                content=result.get("content", ""),
                heading_path=result.get("heading_path", []),
                chunk_index=result.get("chunk_index", 0),
                score=result.get("score", 0.0),
                document=doc_metadata,
            )
            results.append(search_result)

        return results

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}",
        ) from e


def _get_document_metadata(doc_store: DocStore, doc_id: str) -> DocumentMetadata:
    """Get document metadata from doc_store.

    Args:
        doc_store: Document store instance
        doc_id: Document identifier

    Returns:
        Document metadata
    """
    try:
        # List all documents and find the one matching doc_id
        docs = doc_store.list_documents()

        for doc in docs:
            if doc.get("doc_id") == doc_id:
                return DocumentMetadata(
                    title=doc.get("title", ""),
                    path=doc.get("path", ""),
                )

        # Fallback if not found
        return DocumentMetadata(
            title="Unknown Document",
            path=f"unknown:{doc_id}",
        )

    except Exception:
        # Return fallback on error
        return DocumentMetadata(
            title="Unknown Document",
            path=f"unknown:{doc_id}",
        )
