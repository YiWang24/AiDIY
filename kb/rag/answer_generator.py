"""Answer generation for RAG system."""

import time
from typing import List

from kb.llm.base import BaseLLM
from kb.rag.retriever import RetrievedChunk
from kb.rag.context_builder import ContextBuilder
from kb.rag import prompts


class AnswerGenerator:
    """Generates grounded answers using LLM and retrieved context.

    Orchestrates the RAG pipeline: retrieval → context building → generation.

    Attributes:
        llm: LLM instance for text generation
        context_builder: Context builder for formatting retrieved chunks
    """

    def __init__(self, llm: BaseLLM, context_builder: ContextBuilder):
        """Initialize AnswerGenerator.

        Args:
            llm: LLM instance for generation
            context_builder: Context builder for formatting
        """
        self._llm = llm
        self._context_builder = context_builder

    def generate_answer(
        self,
        question: str,
        chunks: List[RetrievedChunk],
    ) -> dict:
        """Generate grounded answer from retrieved chunks.

        Args:
            question: User's question
            chunks: Retrieved chunks with citation IDs

        Returns:
            Dictionary with:
                - answer: Generated answer text
                - citations: List of citations used in answer
                - has_sufficient_knowledge: Whether KB had sufficient info
                - model: Model name used
                - tokens_used: Tokens consumed (if available)
                - retrieval_time_ms: Time spent on retrieval (not tracked here)
                - generation_time_ms: Time spent on generation
        """
        start_time = time.time()

        # 1. Build context from chunks
        context = self._context_builder.build_context(chunks)

        # 2. Build prompt
        prompt = prompts.build_qa_prompt(question, context)

        # 3. Generate answer using LLM
        response = self._llm.generate(prompt)

        generation_time_ms = int((time.time() - start_time) * 1000)

        # 4. Extract citations from answer
        citation_ids = prompts.extract_citation_ids(response.content)

        # 5. Map citation IDs to full citation metadata
        citations = self._build_citations(chunks, citation_ids)

        # 6. Check if answer indicates insufficient knowledge
        has_sufficient_knowledge = not prompts.has_insufficient_knowledge(
            response.content
        )

        return {
            "answer": response.content,
            "citations": citations,
            "has_sufficient_knowledge": has_sufficient_knowledge,
            "model": response.model,
            "tokens_used": response.tokens_used,
            "retrieval_time_ms": 0,  # Not tracked here, set by caller
            "generation_time_ms": generation_time_ms,
        }

    def _build_citations(
        self,
        chunks: List[RetrievedChunk],
        citation_ids: List[int],
    ) -> List[dict]:
        """Build citation metadata from chunks.

        Args:
            chunks: All retrieved chunks
            citation_ids: Citation IDs referenced in answer

        Returns:
            List of citation dictionaries
        """
        # Create mapping from citation_id to chunk
        chunk_map = {chunk.citation_id: chunk for chunk in chunks}

        citations = []
        for citation_id in citation_ids:
            chunk = chunk_map.get(citation_id)
            if chunk:
                citations.append(
                    {
                        "id": citation_id,
                        "chunk_id": chunk.chunk_id,
                        "doc_id": chunk.doc_id,
                        "title": f"Document {chunk.doc_id}",  # Will be enriched by DocStore later
                        "path": f"{chunk.doc_id}.md",
                        "heading_path": chunk.heading_path,
                        "score": chunk.score,
                    }
                )

        return citations
