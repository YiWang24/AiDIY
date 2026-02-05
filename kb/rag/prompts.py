"""Prompt templates for RAG Q&A system."""


# ========== Q&A Prompts ==========

QA_SYSTEM_PROMPT = """You are a helpful AI assistant that answers questions based on a knowledge base.

**IMPORTANT INSTRUCTIONS:**

1. **Use ONLY the provided context** to answer the question. Do not use outside knowledge or make up information.

2. **Cite your sources** using the citation markers [1], [2], [3], etc. that appear in the context. For example:
   - "AgentOps provides monitoring [1]."
   - "LangChain is a framework for LLM applications [2][3]."

3. **Be accurate and factual**. If the context doesn't contain enough information to answer the question, say: "I don't have enough information in the knowledge base to answer this question."

4. **Be concise but complete**. Provide a direct answer to the question without unnecessary elaboration.

5. **Preserve technical terms**. Keep domain-specific terms and names exactly as they appear in the context.

**Remember: Your answers must be grounded in the provided context. Do not hallucinate or add information not present in the sources.**"""


def build_qa_prompt(question: str, context: str) -> str:
    """Build Q&A prompt with question and context.

    Args:
        question: User's question
        context: Retrieved context with citation markers

    Returns:
        Complete prompt for LLM
    """
    return f"""{QA_SYSTEM_PROMPT}

---

**Context:**

{context}

---

**Question:**

{question}

**Answer:**"""


# ========== Chat Prompts ==========

CHAT_SYSTEM_PROMPT = """You are a helpful AI assistant that answers questions based on a knowledge base.

**IMPORTANT INSTRUCTIONS:**

1. **Use ONLY the provided context** to answer questions. Do not use outside knowledge.

2. **Cite your sources** using citation markers [1], [2], etc.

3. **Consider conversation history** when answering. Reference previous exchanges if relevant.

4. **If context is insufficient**, say: "I don't have enough information to answer this."

5. **Be conversational but professional**. Provide helpful, accurate responses."""


def build_chat_prompt(question: str, context: str, conversation_history: list[dict]) -> str:
    """Build chat prompt with question, context, and conversation history.

    Args:
        question: Current user question
        context: Retrieved context with citation markers
        conversation_history: List of previous messages with "role" and "content"

    Returns:
        Complete prompt for LLM
    """
    prompt_parts = [CHAT_SYSTEM_PROMPT]

    # Add conversation history if available
    if conversation_history:
        prompt_parts.append("\n**Conversation History:**\n")
        for msg in conversation_history[-5:]:  # Last 5 messages for context
            role = msg.get("role", "user").title()
            content = msg.get("content", "")
            prompt_parts.append(f"{role}: {content}\n")

    prompt_parts.extend([
        "---\n",
        f"**Context:**\n\n{context}\n",
        "---\n",
        f"**Question:**\n\n{question}\n",
        "**Answer:**"
    ])

    return "".join(prompt_parts)


# ========== Citation Extraction ==========


def extract_citation_ids(answer: str) -> list[int]:
    """Extract citation IDs from LLM answer.

    Args:
        answer: Generated answer text

    Returns:
        List of unique citation IDs in order of appearance
    """
    import re

    # Find all citation markers like [1], [2], etc.
    pattern = r"\[(\d+)\]"
    matches = re.findall(pattern, answer)

    # Convert to integers and preserve order while removing duplicates
    seen = set()
    unique_ids = []
    for match in matches:
        num = int(match)
        if num not in seen:
            seen.add(num)
            unique_ids.append(num)

    return unique_ids


def has_insufficient_knowledge(answer: str) -> bool:
    """Check if answer indicates insufficient knowledge.

    Args:
        answer: Generated answer text

    Returns:
        True if answer indicates insufficient information
    """
    # Phrases that indicate insufficient knowledge
    insufficient_phrases = [
        "i don't have enough information",
        "i don't have sufficient information",
        "not enough information",
        "cannot answer from the given context",
        "the context does not contain",
        "i cannot answer",
        "information is not provided",
    ]

    answer_lower = answer.lower()
    return any(phrase in answer_lower for phrase in insufficient_phrases)


# ========== Tool Calling Prompts ==========

TOOL_CALLING_SYSTEM_PROMPT = """You are a helpful AI assistant with access to tools.

**Available Tools:**
{tools_description}

**Tool Usage Guidelines:**
1. Use tools when you need information beyond the provided context
2. Call web_search for current information or topics not in the knowledge base
3. Always explain what you're searching for before calling tools
4. Synthesize tool results into clear, helpful answers

**Response Format:**
- If using tools: Explain your action → Call tool → Present results
- If not using tools: Answer directly based on context

**Remember:**
- Tools help you provide more accurate and up-to-date information
- Always cite your sources when using information from tools
- Be transparent about when you're using external information
"""


def build_tool_calling_prompt(
    question: str,
    context: str = "",
    tools_description: str = "",
) -> str:
    """Build prompt for tool calling scenario.

    Args:
        question: User's question
        context: Optional context from knowledge base
        tools_description: Description of available tools

    Returns:
        Complete prompt for LLM with tool calling
    """
    prompt_parts = [TOOL_CALLING_SYSTEM_PROMPT.format(tools_description=tools_description)]

    if context:
        prompt_parts.extend([
            "---",
            f"**Context:**\n\n{context}\n",
        ])

    prompt_parts.extend([
        "---",
        f"**Question:**\n\n{question}\n",
        "**Answer:**"
    ])

    return "\n".join(prompt_parts)


# ========== Hybrid Agent Prompts ==========

HYBRID_AGENT_SYSTEM_PROMPT = """You are an AI assistant with both knowledge base and web search access.

**Information Sources:**
1. **Knowledge Base**: Use this for technical documentation, architecture, implementations
2. **Web Search**: Use this for current information, news, or topics not covered

**Decision Process:**
1. Check if knowledge base has sufficient information (score > 0.6)
2. If not, use web search to supplement
3. Combine information from both sources when helpful
4. Always cite which source provided each piece of information

**Citation Format:**
- [KB 1], [KB 2] for knowledge base sources
- [Web 1], [Web 2] for web search sources

**Guidelines:**
- Prioritize knowledge base for stable, well-documented topics
- Use web search for current events, pricing, recent releases
- When combining sources, clearly distinguish between them
- If sources conflict, acknowledge the discrepancy
"""


def build_hybrid_prompt(
    question: str,
    kb_context: str = "",
    web_context: str = "",
) -> str:
    """Build prompt for hybrid agent scenario.

    Args:
        question: User's question
        kb_context: Context from knowledge base
        web_context: Context from web search

    Returns:
        Complete prompt for LLM with both sources
    """
    prompt_parts = [HYBRID_AGENT_SYSTEM_PROMPT]

    if kb_context:
        prompt_parts.extend([
            "---",
            "**Knowledge Base Context:**",
            kb_context,
        ])

    if web_context:
        prompt_parts.extend([
            "---",
            "**Web Search Context:**",
            web_context,
        ])

    prompt_parts.extend([
        "---",
        f"**Question:**\n\n{question}\n",
        "**Answer:**"
    ])

    return "\n".join(prompt_parts)
