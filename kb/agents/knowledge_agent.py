"""Knowledge agent for RAG-based Q&A from the knowledge base."""

import time
from typing import Dict, Any

from kb.agents.base import Agent


class KnowledgeAgent(Agent):
    """Agent for answering questions using the knowledge base (RAG).

    Retrieves relevant chunks using hybrid search + reranking,
    then generates grounded answers with citations.
    """

    def __init__(
        self,
        retriever,
        answer_generator,
        score_threshold: float = 0.4,
    ):
        """Initialize knowledge agent.

        Args:
            retriever: KBRetriever instance for searching
            answer_generator: AnswerGenerator instance for generating answers
            score_threshold: Minimum score to consider knowledge sufficient
        """
        self._retriever = retriever
        self._generator = answer_generator
        self._score_threshold = score_threshold

    async def handle(self, question: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle question using knowledge base.

        Args:
            question: User's question
            context: Additional context (top_k, use_hybrid, use_reranking)

        Returns:
            Response dictionary with answer and metadata
        """
        start_time = time.time()

        # Get retrieval config from context
        top_k = context.get("top_k", 10)
        use_hybrid = context.get("use_hybrid", True)
        use_reranking = context.get("use_reranking", True)

        # 1. Retrieve with hybrid search + reranking
        chunks = self._retriever.search(
            query=question,
            top_k=top_k,
            use_hybrid=use_hybrid,
            use_reranking=use_reranking,
        )

        retrieval_time_ms = int((time.time() - start_time) * 1000)

        # 2. Check if results are sufficient
        has_sufficient_knowledge = True
        if not chunks:
            has_sufficient_knowledge = False
        else:
            max_score = chunks[0].get("score", 0.0) if chunks else 0.0
            if max_score < self._score_threshold:
                has_sufficient_knowledge = False

        # 3. Generate answer
        result = self._generator.generate_answer(question, chunks)

        # 4. Add metadata (must be after generate_answer to avoid overwriting)
        result["retrieval_time_ms"] = retrieval_time_ms

        # 5. Add agent type (must be last to not be overwritten)
        result["agent_type"] = "knowledge"
        result["has_sufficient_knowledge"] = has_sufficient_knowledge

        return result

    def can_handle(self, question: str) -> float:
        """Return confidence score for knowledge base handling.

        High confidence for technical/documentation questions.

        Args:
            question: User's question

        Returns:
            Confidence score (0.0 - 1.0)
        """
        question_lower = question.lower()

        # Keywords indicating technical/documentation questions
        tech_keywords = [
            "how", "explain", "architecture", "implementation",
            "api", "design", "pattern", "tutorial", "guide",
            "example", "documentation", "reference", "usage",
            "what is", "what are", "how to", "how do",
        ]

        # Count matches
        matches = sum(1 for kw in tech_keywords if kw in question_lower)

        # Calculate confidence
        if matches >= 2:
            return 0.85
        elif matches == 1:
            return 0.70
        else:
            # Still give moderate confidence for generic questions
            return 0.55
