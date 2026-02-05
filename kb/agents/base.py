"""Base agent interface for agent orchestration system."""

from abc import ABC, abstractmethod
from typing import Dict, Any


class Agent(ABC):
    """Abstract base class for all agents.

    Agents are specialized handlers that process questions and generate answers.
    Each agent type (knowledge, web_search, hybrid) implements this interface.
    """

    @abstractmethod
    async def handle(self, question: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a question and return response.

        Args:
            question: User's question
            context: Additional context (top_k, use_fallback, etc.)

        Returns:
            Response dictionary with:
                - answer: str (generated answer)
                - agent_type: str (agent identifier)
                - has_sufficient_knowledge: bool (optional)
                - chunks: list (optional, for knowledge agent)
                - sources: list (optional, for web search agent)
                - model: str (optional, model used)
                - tokens_used: int (optional)
                - retrieval_time_ms: int (optional)
                - generation_time_ms: int (optional)
        """
        pass

    @abstractmethod
    def can_handle(self, question: str) -> float:
        """Return confidence score for handling this question.

        Args:
            question: User's question

        Returns:
            Confidence score between 0.0 and 1.0
            - 0.9-1.0: Highly confident (should definitely use this agent)
            - 0.7-0.9: Good fit
            - 0.5-0.7: Possible fit
            - <0.5: Poor fit (should not use this agent)
        """
        pass
