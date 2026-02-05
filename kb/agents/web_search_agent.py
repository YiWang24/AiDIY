"""Web search agent for answering questions using online search."""

import time
from typing import Dict, Any

from kb.agents.base import Agent
from kb.rag.prompts import QA_SYSTEM_PROMPT


class WebSearchAgent(Agent):
    """Agent for answering questions using web search.

    Performs web search and generates answers from search results.
    Useful for current information not in the knowledge base.
    """

    def __init__(self, web_search_tool, llm):
        """Initialize web search agent.

        Args:
            web_search_tool: WebSearchTool instance
            llm: LLM instance for generating answers
        """
        self._tool = web_search_tool
        self._llm = llm

    async def handle(self, question: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle question using web search.

        Args:
            question: User's question
            context: Additional context (max_results)

        Returns:
            Response dictionary with answer and sources
        """
        start_time = time.time()

        # Get max_results from context
        max_results = context.get("max_results", 5)

        # 1. Perform web search
        search_results = await self._tool.execute(
            query=question,
            max_results=max_results
        )

        retrieval_time_ms = int((time.time() - start_time) * 1000)

        # 2. Generate answer from search results
        prompt = f"""{QA_SYSTEM_PROMPT}

---

**Context:**

The following are web search results for your question:

{search_results}

---

**Question:**

{question}

**Answer:**"""

        generation_start = time.time()
        response = self._llm.generate(prompt, temperature=0.3)
        generation_time_ms = int((time.time() - generation_start) * 1000)

        return {
            "answer": response.content,
            "agent_type": "web_search",
            "sources": search_results,
            "model": response.model,
            "tokens_used": response.tokens_used,
            "retrieval_time_ms": retrieval_time_ms,
            "generation_time_ms": generation_time_ms,
            "has_sufficient_knowledge": True,  # Web search always returns something
        }

    def can_handle(self, question: str) -> float:
        """Return confidence score for web search handling.

        High confidence for questions about current events, news, etc.

        Args:
            question: User's question

        Returns:
            Confidence score (0.0 - 1.0)
        """
        question_lower = question.lower()

        # Keywords indicating need for current/real-time information
        realtime_keywords = [
            "latest", "news", "current", "recent", "today", "now",
            "price", "cost", "2025", "2024", "2023",
            "breaking", "update", "release", "announcement",
        ]

        # Count matches
        matches = sum(1 for kw in realtime_keywords if kw in question_lower)

        # Calculate confidence
        if matches >= 2:
            return 0.90
        elif matches == 1:
            return 0.75
        else:
            # Low confidence for generic questions
            return 0.40
