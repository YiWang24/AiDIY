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
