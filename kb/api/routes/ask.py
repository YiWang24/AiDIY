"""Ask endpoint for Q&A with RAG."""

import time
from typing import List

from fastapi import APIRouter, HTTPException, Depends

from kb.api.schemas import AskRequest, AskResponse, Citation
from kb.api.dependencies import (
    get_vector_store,
    get_doc_store,
    get_rag_config,
    get_llm_config,
)
from kb.storage.vectorstore import VectorStore
from kb.storage.docstore import DocStore
from kb.rag.retriever import KBRetriever
from kb.rag.context_builder import ContextBuilder
from kb.rag.answer_generator import AnswerGenerator
from kb.llm.factory import create_llm

router = APIRouter(prefix="/ask", tags=["ask"])

# Cache LLM instance
_llm_instance = None


def get_llm():
    """Get cached LLM instance."""
    global _llm_instance
    if _llm_instance is None:
        llm_config = get_llm_config()
        _llm_instance = create_llm(llm_config)
    return _llm_instance


@router.post("", response_model=AskResponse)
async def ask(
    request: AskRequest,
    vector_store: VectorStore = Depends(get_vector_store),
    doc_store: DocStore = Depends(get_doc_store),
    rag_config: dict = Depends(get_rag_config),
    llm = Depends(get_llm),
) -> AskResponse:
    """Answer a question using RAG.

    Retrieves relevant chunks from the knowledge base and generates
    a grounded answer with citations.

    Args:
        request: Ask request with question and top_k
        vector_store: Vector store dependency
        doc_store: Document store dependency
        rag_config: RAG configuration
        llm: LLM instance

    Returns:
        Answer with citations and metadata

    Raises:
        HTTPException: If request fails
    """
    try:
        start_time = time.time()

        # 1. Get RAG configuration
        retrieval_config = rag_config.get("retrieval", {})
        context_config = rag_config.get("context", {})

        # 2. Initialize retriever
        retriever = KBRetriever(
            vector_store=vector_store,
            doc_store=doc_store,
            score_threshold=retrieval_config.get("score_threshold", 0.7),
            max_chunks_per_doc=retrieval_config.get("max_chunks_per_doc", 3),
        )

        # 3. Retrieve relevant chunks
        chunks = retriever.search(query=request.question, top_k=request.top_k)

        retrieval_time_ms = int((time.time() - start_time) * 1000)

        # 4. Initialize context builder
        context_builder = ContextBuilder(
            max_length=context_config.get("max_length", 4000),
            include_headings=context_config.get("include_headings", True),
        )

        # 5. Initialize answer generator
        generator = AnswerGenerator(llm=llm, context_builder=context_builder)

        # 6. Generate answer
        result = generator.generate_answer(
            question=request.question,
            chunks=chunks,
        )

        # 7. Update retrieval time (generator returns 0, we override)
        result["retrieval_time_ms"] = retrieval_time_ms

        # 8. Enrich citations with document metadata
        enriched_citations = _enrich_citations(doc_store, result["citations"])

        # 9. Build response
        return AskResponse(
            answer=result["answer"],
            citations=enriched_citations,
            has_sufficient_knowledge=result["has_sufficient_knowledge"],
            model=result["model"],
            tokens_used=result["tokens_used"],
            retrieval_time_ms=result["retrieval_time_ms"],
            generation_time_ms=result["generation_time_ms"],
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ask request failed: {str(e)}",
        ) from e


def _enrich_citations(doc_store: DocStore, citations: List[dict]) -> List[Citation]:
    """Enrich citations with document metadata.

    Args:
        doc_store: Document store instance
        citations: List of citation dicts

    Returns:
        List of Citation objects with enriched metadata
    """
    # Get all documents for metadata lookup
    try:
        docs = doc_store.list_documents()
        doc_map = {doc["doc_id"]: doc for doc in docs}
    except Exception:
        doc_map = {}

    enriched = []
    for cit in citations:
        doc_id = cit.get("doc_id", "")
        doc = doc_map.get(doc_id, {})

        citation = Citation(
            id=cit["id"],
            chunk_id=cit["chunk_id"],
            doc_id=doc_id,
            title=doc.get("title", cit.get("title", "Unknown Document")),
            path=doc.get("path", cit.get("path", f"{doc_id}.md")),
            heading_path=cit.get("heading_path", []),
            score=cit["score"],
        )
        enriched.append(citation)

    return enriched
