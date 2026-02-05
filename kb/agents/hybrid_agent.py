"""Hybrid agent that combines knowledge base and web search."""

import time
from typing import Dict, Any

from kb.agents.base import Agent


class HybridAgent(Agent):
    """Agent that combines knowledge base and web search.

    Strategy:
    1. Try knowledge base first
    2. If insufficient results, supplement with web search
    3. Merge information from both sources when helpful
    """

    def __init__(
        self,
        knowledge_agent: Agent,
        web_search_agent: Agent,
        fallback_threshold: float = 0.4,
    ):
        """Initialize hybrid agent.

        Args:
            knowledge_agent: KnowledgeAgent instance
            web_search_agent: WebSearchAgent instance
            fallback_threshold: Score below which to use web search
        """
        self._knowledge = knowledge_agent
        self._web = web_search_agent
        self._fallback_threshold = fallback_threshold

    async def handle(self, question: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle question using hybrid approach.

        Args:
            question: User's question
            context: Additional context

        Returns:
            Response dictionary with merged answer
        """
        start_time = time.time()

        # 1. Try knowledge base first
        kb_result = await self._knowledge.handle(question, context)

        # 2. Check if results are sufficient
        has_sufficient_kb = kb_result.get("has_sufficient_knowledge", True)

        if has_sufficient_kb:
            # Knowledge base has good information, return as-is
            kb_result["agent_type"] = "hybrid_knowledge"
            kb_result["retrieval_time_ms"] = int((time.time() - start_time) * 1000)
            return kb_result

        # 3. Knowledge base insufficient, try web search
        web_result = await self._web.handle(question, context)

        # 4. Merge results
        kb_answer = kb_result.get("answer", "No specific information found in knowledge base.")
        web_answer = web_result.get("answer", "")

        # Create merged answer
        merged_answer = self._merge_answers(kb_answer, web_answer, question)

        # Calculate total tokens
        tokens_used = (kb_result.get("tokens_used") or 0) + (web_result.get("tokens_used") or 0)

        # Calculate times
        total_retrieval_time = (
            kb_result.get("retrieval_time_ms", 0) +
            web_result.get("retrieval_time_ms", 0)
        )
        total_generation_time = (
            kb_result.get("generation_time_ms", 0) +
            web_result.get("generation_time_ms", 0)
        )

        return {
            "answer": merged_answer,
            "agent_type": "hybrid",
            "has_sufficient_knowledge": True,  # We have info from somewhere
            "kb_chunks": kb_result.get("citations", []),
            "web_sources": web_result.get("sources", ""),
            "model": kb_result.get("model", "gemini-2.5-flash"),
            "tokens_used": tokens_used if tokens_used > 0 else None,
            "retrieval_time_ms": total_retrieval_time,
            "generation_time_ms": total_generation_time,
            "citations": [],  # Empty since sources are mixed
        }

    def can_handle(self, question: str) -> float:
        """Return confidence score for hybrid handling.

        Moderate-high confidence for most questions since hybrid
        can always fall back to web search.

        Args:
            question: User's question

        Returns:
            Confidence score (0.0 - 1.0)
        """
        # Hybrid agent is the safest choice
        # It has access to both knowledge base and web search
        return 0.65

    def _merge_answers(self, kb_answer: str, web_answer: str, question: str) -> str:
        """Merge answers from knowledge base and web search.

        Args:
            kb_answer: Answer from knowledge base
            web_answer: Answer from web search
            question: Original question

        Returns:
            Merged answer string
        """
        # If knowledge base has nothing, just return web answer
        if "not enough information" in kb_answer.lower() or "no specific information" in kb_answer.lower():
            return f"""Based on web search:

{web_answer}"""

        # If both have useful info, combine them
        return f"""Based on the knowledge base and web search:

**From Knowledge Base:**
{kb_answer}

**From Web Search:**
{web_answer}"""
