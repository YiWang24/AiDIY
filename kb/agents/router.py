"""Agent router for intelligent question routing.

Uses LLM-based classification to route questions to the most appropriate agent.
"""

from typing import Dict, Any, Optional

from kb.agents.base import Agent


# Route rules with keyword matching and agent preferences
ROUTE_RULES = {
    "knowledge": {
        "keywords": [
            "how to", "how do", "explain", "what is", "what are",
            "architecture", "implementation", "api", "design",
            "pattern", "tutorial", "guide", "example",
            "documentation", "reference", "usage",
        ],
        "domains": ["cs", "ai", "engineering", "projects"],
        "default_confidence": 0.6,
    },
    "web_search": {
        "keywords": [
            "latest", "news", "current", "recent", "today",
            "price", "cost", "2025", "2024", "2023",
            "now", "breaking", "update", "release",
        ],
        "default_confidence": 0.7,
    },
}


class AgentRouter:
    """Router for directing questions to appropriate agents.

    Uses keyword-based heuristics and optional LLM classification
    to determine the best agent for handling a question.
    """

    def __init__(self, llm=None, use_llm_classification: bool = False):
        """Initialize agent router.

        Args:
            llm: LLM instance for optional classification (can be None)
            use_llm_classification: Whether to use LLM for routing (default: keyword only)
        """
        self._llm = llm
        self._use_llm = use_llm_classification
        self._agents: Dict[str, Agent] = {}

    def register(self, name: str, agent: Agent) -> None:
        """Register an agent with the router.

        Args:
            name: Agent name (e.g., "knowledge", "web_search", "hybrid")
            agent: Agent instance
        """
        self._agents[name] = agent

    async def route(
        self,
        question: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Route question to the most appropriate agent.

        Args:
            question: User's question
            context: Additional context (top_k, use_fallback, etc.)

        Returns:
            Agent response dictionary

        Raises:
            ValueError: If no agents registered
        """
        if not self._agents:
            raise ValueError("No agents registered with router")

        # Determine which agent should handle the question
        agent_name = await self._select_agent(question, context)

        # Get the agent
        agent = self._agents.get(agent_name)
        if not agent:
            # Fallback to first available agent
            agent = next(iter(self._agents.values()))

        # Delegate to agent
        return await agent.handle(question, context)

    async def _select_agent(
        self,
        question: str,
        context: Dict[str, Any],
    ) -> str:
        """Select the best agent for the question.

        Args:
            question: User's question
            context: Additional context

        Returns:
            Agent name to use
        """
        question_lower = question.lower()

        # 1. Check explicit keyword matches
        for agent_type, rules in ROUTE_RULES.items():
            keywords = rules.get("keywords", [])
            if any(kw in question_lower for kw in keywords):
                return agent_type

        # 2. Use LLM classification if enabled and available
        if self._use_llm and self._llm:
            llm_choice = await self._llm_classify(question)
            if llm_choice and llm_choice in self._agents:
                return llm_choice

        # 3. Evaluate agent confidence scores
        best_agent = None
        best_score = 0.0

        for name, agent in self._agents.items():
            score = agent.can_handle(question)
            if score > best_score:
                best_score = score
                best_agent = name

        # 4. Default to hybrid if available and confidence is low
        if best_score < 0.5 and "hybrid" in self._agents:
            return "hybrid"

        # 5. Return best agent or first available
        return best_agent if best_agent else next(iter(self._agents.keys()))

    async def _llm_classify(self, question: str) -> Optional[str]:
        """Use LLM to classify the question type.

        Args:
            question: User's question

        Returns:
            Agent type name or None if classification fails
        """
        if not self._llm:
            return None

        classification_prompt = f"""Classify this question into one of these categories:

1. **knowledge** - Technical documentation, architecture, implementation, tutorials
2. **web_search** - Current events, news, real-time data, pricing
3. **hybrid** - Questions that could benefit from both sources

Question: "{question}"

Respond with ONLY the category name (knowledge/web_search/hybrid):"""

        try:
            response = self._llm.generate(classification_prompt, temperature=0.1)
            choice = response.content.strip().lower()

            # Validate response
            if choice in ["knowledge", "web_search", "hybrid"]:
                return choice

            # Try to extract from longer response
            for valid_choice in ["knowledge", "web_search", "hybrid"]:
                if valid_choice in choice:
                    return valid_choice

        except Exception as e:
            print(f"LLM classification failed: {e}")

        return None


def classify_question(question: str) -> tuple[str, float]:
    """Classify question using keyword heuristics (standalone helper).

    Args:
        question: User's question

    Returns:
        Tuple of (agent_type, confidence_score)
    """
    question_lower = question.lower()

    # Check each route rule
    for agent_type, rules in ROUTE_RULES.items():
        keywords = rules.get("keywords", [])
        matches = sum(1 for kw in keywords if kw in question_lower)

        if matches > 0:
            # Confidence based on number of keyword matches
            confidence = min(0.5 + (matches * 0.1), 0.95)
            return agent_type, confidence

    # Default to knowledge with low confidence
    return "hybrid", 0.4
