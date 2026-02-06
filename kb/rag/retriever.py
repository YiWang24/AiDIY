"""Retrieval orchestration for RAG system."""

from dataclasses import dataclass
from typing import List, TYPE_CHECKING
from collections import defaultdict

from kb.storage.docstore import DocStore
from kb.storage.vectorstore import VectorStore

if TYPE_CHECKING:
    from kb.storage.hybrid_search import HybridSearcher
    from kb.rag.reranker import ReRanker


@dataclass(frozen=True, slots=True)
class RetrievedChunk:
    """A retrieved chunk with citation metadata.

    Attributes:
        chunk_id: Unique chunk identifier
        doc_id: Parent document identifier
        content: Chunk text content
        heading_path: List of headings from root to this chunk
        chunk_index: Sequential index within document
        score: Similarity score (0-1)
        citation_id: Citation number for referencing in answers
    """

    chunk_id: str
    doc_id: str
    content: str
    heading_path: list[str]
    chunk_index: int
    score: float
    citation_id: int

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "chunk_id": self.chunk_id,
            "doc_id": self.doc_id,
            "content": self.content,
            "heading_path": self.heading_path,
            "chunk_index": self.chunk_index,
            "score": self.score,
            "citation_id": self.citation_id,
        }


class KBRetriever:
    """Knowledge base retriever with filtering and enrichment.

    Performs semantic search on the vector store, filters by score threshold,
    deduplicates by document, and enriches results with document metadata.

    Attributes:
        vector_store: Vector store for semantic search
        doc_store: Document store for metadata enrichment
        score_threshold: Minimum similarity score (0-1)
        max_chunks_per_doc: Maximum chunks to include per document
        hybrid_searcher: Optional hybrid searcher for semantic + keyword
        reranker: Optional re-ranker for result quality improvement
    """

    def __init__(
        self,
        vector_store: VectorStore,
        doc_store: DocStore,
        score_threshold: float = 0.7,
        max_chunks_per_doc: int = 3,
        hybrid_searcher: "HybridSearcher | None" = None,
        reranker: "ReRanker | None" = None,
    ):
        """Initialize KBRetriever.

        Args:
            vector_store: Vector store for semantic search
            doc_store: Document store for metadata
            score_threshold: Minimum similarity score (default: 0.7)
            max_chunks_per_doc: Max chunks per document (default: 3)
            hybrid_searcher: Optional hybrid searcher for semantic + keyword
            reranker: Optional re-ranker for result quality
        """
        self._vector_store = vector_store
        self._doc_store = doc_store
        self.score_threshold = score_threshold
        self.max_chunks_per_doc = max_chunks_per_doc
        self._hybrid_searcher = hybrid_searcher
        self._reranker = reranker

    def search(
        self,
        query: str,
        top_k: int = 10,
        use_hybrid: bool = False,
        use_reranking: bool = False,
    ) -> List[RetrievedChunk]:
        """Search for relevant chunks.

        Performs semantic search, filters by score threshold, deduplicates
        by document, and assigns citation IDs.

        Args:
            query: Search query text
            top_k: Number of chunks to retrieve (default: 10)
            use_hybrid: Use hybrid semantic + keyword search (default: False)
            use_reranking: Apply heuristic re-ranking (default: False)

        Returns:
            List of retrieved chunks with citations, ranked by score
        """
        # 1. Perform search (semantic or hybrid)
        if use_hybrid and self._hybrid_searcher:
            raw_results = self._hybrid_searcher.search(query=query, k=top_k)
        else:
            raw_results = self._vector_store.search(query=query, k=top_k)

        # 2. Apply re-ranking if enabled
        if use_reranking and self._reranker:
            raw_results = self._reranker.rerank(raw_results, query)

        def filter_score(r: dict) -> float:
            # Hybrid search uses RRF for ranking; keep semantic similarity separately for thresholds.
            if use_hybrid:
                return float(r.get("semantic_score", 0.0) or 0.0)
            return float(r.get("score", 0.0) or 0.0)

        def sort_score(r: dict) -> float:
            # Hybrid search should keep RRF ordering; non-hybrid uses semantic similarity.
            return float(r.get("score", 0.0) or 0.0)

        # 3. Filter by score threshold
        filtered_results = [r for r in raw_results if filter_score(r) >= self.score_threshold]

        if not filtered_results:
            return []

        # 4. Sort by ranking score (descending)
        sorted_results = sorted(filtered_results, key=sort_score, reverse=True)

        # 5. Deduplicate by document (keep top N chunks per doc)
        doc_chunks: defaultdict[str, List[dict]] = defaultdict(list)
        for result in sorted_results:
            doc_id = result.get("doc_id", "")
            if len(doc_chunks[doc_id]) < self.max_chunks_per_doc:
                doc_chunks[doc_id].append(result)

        # 6. Flatten back to list maintaining order
        final_results: List[dict] = []
        for chunks in doc_chunks.values():
            final_results.extend(chunks)

        # 7. Re-sort by score after deduplication
        final_results.sort(key=lambda x: x.get("score", 0), reverse=True)

        # 8. Assign citation IDs and convert to RetrievedChunk
        retrieved_chunks = [
            RetrievedChunk(
                chunk_id=r.get("chunk_id", ""),
                doc_id=r.get("doc_id", ""),
                content=r.get("content", ""),
                heading_path=r.get("heading_path", []),
                chunk_index=r.get("chunk_index", 0),
                score=filter_score(r),
                citation_id=i + 1,
            )
            for i, r in enumerate(final_results)
        ]

        return retrieved_chunks
