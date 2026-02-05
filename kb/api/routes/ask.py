"""Ask endpoint for Q&A with RAG and agent orchestration."""

import os
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
from kb.storage.hybrid_search import HybridSearcher
from kb.rag.retriever import KBRetriever
from kb.rag.reranker import ReRanker
from kb.rag.context_builder import ContextBuilder
from kb.rag.answer_generator import AnswerGenerator
from kb.llm.factory import create_llm
from kb.agents.router import AgentRouter
from kb.agents.knowledge_agent import KnowledgeAgent
from kb.agents.web_search_agent import WebSearchAgent
from kb.agents.hybrid_agent import HybridAgent
from kb.tools.web_search import WebSearchTool

router = APIRouter(prefix="/ask", tags=["ask"])

# Cache instances
_llm_instance = None
_web_search_tool = None


def get_llm():
    """Get cached LLM instance."""
    global _llm_instance
    if _llm_instance is None:
        llm_config = get_llm_config()
        _llm_instance = create_llm(llm_config)
    return _llm_instance


def get_web_search_tool(rag_config: dict = Depends(get_rag_config)):
    """Get cached web search tool."""
    global _web_search_tool
    if _web_search_tool is None:
        web_search_config = rag_config.get("web_search", {})
        _web_search_tool = WebSearchTool(
            provider=web_search_config.get("provider", "tavily"),
            api_key=web_search_config.get("api_key") or os.getenv("TAVILY_API_KEY"),
            max_results=web_search_config.get("max_results", 5),
            search_depth=web_search_config.get("search_depth", "basic"),
            timeout=web_search_config.get("timeout", 30),
        )
    return _web_search_tool


@router.post("", response_model=AskResponse)
async def ask(
    request: AskRequest,
    vector_store: VectorStore = Depends(get_vector_store),
    doc_store: DocStore = Depends(get_doc_store),
    rag_config: dict = Depends(get_rag_config),
    llm = Depends(get_llm),
    web_search_tool = Depends(get_web_search_tool),
) -> AskResponse:
    """Answer a question using RAG with agent orchestration.

    Routes questions to specialized agents (knowledge, web_search, hybrid)
    and returns grounded answers with citations.

    Args:
        request: Ask request with question and top_k
        vector_store: Vector store dependency
        doc_store: Document store dependency
        rag_config: RAG configuration
        llm: LLM instance
        web_search_tool: Web search tool instance

    Returns:
        Answer with citations and metadata

    Raises:
        HTTPException: If request fails
    """
    try:
        # Get configurations
        retrieval_config = rag_config.get("retrieval", {})
        context_config = rag_config.get("context", {})
        agent_config = rag_config.get("agent_orchestration", {})

        # Initialize retriever components
        use_hybrid = retrieval_config.get("use_hybrid_search", False)
        use_reranking = retrieval_config.get("use_reranking", False)

        hybrid_searcher = None
        reranker = None

        if use_hybrid:
            hybrid_searcher = HybridSearcher(
                vector_store=vector_store,
                doc_store=doc_store,
                alpha=retrieval_config.get("hybrid_alpha", 0.7),
            )

        if use_reranking:
            reranker = ReRanker()

        retriever = KBRetriever(
            vector_store=vector_store,
            doc_store=doc_store,
            score_threshold=retrieval_config.get("score_threshold", 0.7),
            max_chunks_per_doc=retrieval_config.get("max_chunks_per_doc", 3),
            hybrid_searcher=hybrid_searcher,
            reranker=reranker,
        )

        # Initialize context builder and answer generator
        context_builder = ContextBuilder(
            max_length=context_config.get("max_length", 4000),
            include_headings=context_config.get("include_headings", True),
        )

        generator = AnswerGenerator(llm=llm, context_builder=context_builder)

        # Initialize agents
        knowledge_agent = KnowledgeAgent(
            retriever=retriever,
            answer_generator=generator,
            score_threshold=agent_config.get("web_fallback_threshold", 0.3),
        )

        web_search_agent = WebSearchAgent(
            web_search_tool=web_search_tool,
            llm=llm,
        )

        hybrid_agent = HybridAgent(
            knowledge_agent=knowledge_agent,
            web_search_agent=web_search_agent,
            fallback_threshold=agent_config.get("web_fallback_threshold", 0.3),
        )

        # Initialize router
        use_llm_routing = agent_config.get("use_llm_routing", False)
        router = AgentRouter(llm=llm if use_llm_routing else None, use_llm_classification=use_llm_routing)

        router.register("knowledge", knowledge_agent)
        router.register("web_search", web_search_agent)
        router.register("hybrid", hybrid_agent)

        # Route to appropriate agent
        context = {
            "top_k": request.top_k,
            "use_hybrid": use_hybrid,
            "use_reranking": use_reranking,
            "max_results": rag_config.get("web_search", {}).get("max_results", 5),
        }

        agent_response = await router.route(request.question, context)

        # Debug: log agent_response
        print(f"DEBUG: agent_response keys = {agent_response.keys()}")
        print(f"DEBUG: agent_type = {agent_response.get('agent_type')}")

        # Enrich citations (if knowledge agent was used)
        agent_type = agent_response.get("agent_type", "")
        citations_data = agent_response.get("citations", [])

        if agent_type in ["knowledge", "hybrid_knowledge"] and citations_data:
            site_url = rag_config.get("docusaurus", {}).get("site_url", "https://docs.yiw.me")
            enriched_citations = _enrich_citations(doc_store, citations_data, site_url)
        else:
            enriched_citations = []

        # Build response
        return AskResponse(
            answer=agent_response["answer"],
            citations=enriched_citations,
            has_sufficient_knowledge=agent_response.get("has_sufficient_knowledge", True),
            model=agent_response.get("model", "gemini-2.5-flash"),
            tokens_used=agent_response.get("tokens_used"),
            retrieval_time_ms=agent_response.get("retrieval_time_ms", 0),
            generation_time_ms=agent_response.get("generation_time_ms", 0),
            agent_type=agent_response.get("agent_type"),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ask request failed: {str(e)}",
        ) from e


def _transform_docusaurus_url(path: str, site_url: str) -> str:
    """Transform a document path to a proper Docusaurus URL.

    Args:
        path: Document path (e.g., 'docs/cs/algorithms/index.md')
        site_url: Base site URL (e.g., 'https://docs.yiw.me')

    Returns:
        Full Docusaurus URL (e.g., 'https://docs.yiw.me/docs/cs/algorithms/index')
    """
    # Remove leading 'docs/' if present (it's already in the URL structure)
    clean_path = path.removeprefix("docs/")

    # Remove .md or .mdx extension
    if clean_path.endswith(".mdx"):
        clean_path = clean_path[:-4]
    elif clean_path.endswith(".md"):
        clean_path = clean_path[:-3]

    # Ensure no leading slash
    clean_path = clean_path.lstrip("/")

    # Ensure site_url has no trailing slash
    clean_site_url = site_url.rstrip("/")

    return f"{clean_site_url}/docs/{clean_path}"


def _enrich_citations(doc_store: DocStore, citations: List[dict], site_url: str = "https://docs.yiw.me") -> List[Citation]:
    """Enrich citations with document metadata and proper URLs.

    Args:
        doc_store: Document store instance
        citations: List of citation dicts
        site_url: Base site URL for citation links

    Returns:
        List of Citation objects with enriched metadata and transformed URLs
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

        raw_path = doc.get("path", cit.get("path", f"{doc_id}.md"))

        citation = Citation(
            id=cit["id"],
            chunk_id=cit["chunk_id"],
            doc_id=doc_id,
            title=doc.get("title", cit.get("title", "Unknown Document")),
            path=_transform_docusaurus_url(raw_path, site_url),
            heading_path=cit.get("heading_path", []),
            score=cit["score"],
        )
        enriched.append(citation)

    return enriched
