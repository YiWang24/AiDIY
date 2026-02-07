"""Simplified Agent + RAG in one file.

No classes, just functions. Tools → Retrieval → Agent → Output.
"""

from typing import Any
from langchain_core.tools import tool
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableConfig

from kb.storage.vectorstore import VectorStore
from kb.llm import create_llm
from kb.storage.docstore import DocStore


# ========== Tool: Knowledge Base Search ==========

@tool
async def search_knowledge_base(query: str, top_k: int = 5) -> str:
    """Search the knowledge base for relevant information.

    Use this for technical questions about:
    - Architecture and design patterns
    - API documentation
    - Implementation details
    - Tutorials and guides

    Args:
        query: Search query
        top_k: Number of results to return (default: 5)

    Returns:
        Formatted search results from knowledge base
    """
    # Get retriever from closure (will be injected)
    retriever = _get_retriever()

    # Perform search
    results = retriever.invoke(query, search_kwargs={"k": top_k})

    # Format results
    if not results:
        return "No relevant information found in knowledge base."

    formatted = f"Found {len(results)} relevant documents in knowledge base:\n\n"
    for i, doc in enumerate(results, 1):
        metadata = doc.metadata
        heading = " > ".join(metadata.get("heading_path", []))
        if heading:
            formatted += f"[{i}] **{heading}**\n"
        formatted += f"{doc.page_content}\n\n"

    return formatted.strip()


# ========== Tool: Web Search (placeholder - implement if needed) ==========

@tool
async def search_web(query: str, max_results: int = 5) -> str:
    """Search the web for current information.

    Use this for:
    - Current events and news
    - Recent releases or updates
    - Real-time data
    - Topics not in the knowledge base

    Args:
        query: Search query
        max_results: Maximum number of results

    Returns:
        Web search results
    """
    # Placeholder - implement with Tavily or Brave if needed
    return "Web search not yet implemented."


# ========== Global state (injected at startup) ==========

_vector_store: VectorStore = None
_doc_store: DocStore = None
_retriever = None
_llm = None
_agent_executor = None


def _get_retriever():
    """Get the retriever instance."""
    global _retriever
    if _retriever is None:
        _retriever = _vector_store._vectorstore.as_retriever(
            search_kwargs={"k": 5}
        )
    return _retriever


# ========== Agent Creation ==========

def initialize_agent(
    vector_store: VectorStore,
    doc_store: DocStore = None,
    llm_config: Any = None,
):
    """Initialize the agent with vector store and LLM.

    Call this once at startup.

    Args:
        vector_store: PGVector store instance
        doc_store: Document store (optional, for future use)
        llm_config: LLM config (uses default if None)
    """
    global _vector_store, _doc_store, _llm, _agent_executor

    _vector_store = vector_store
    _doc_store = doc_store
    _llm = create_llm(llm_config or "gemini-2.0-flash-exp")

    # Create tools list
    tools = [search_knowledge_base]

    # System prompt
    system_prompt = """You are a helpful AI assistant with access to a knowledge base.

**Available Tools:**
1. search_knowledge_base - Search technical documentation and implementation details
2. search_web - Search the web for current information

**Guidelines:**
- Use search_knowledge_base for technical questions about the codebase
- Use search_web for current events or real-time information
- Always cite your sources using [1], [2], etc.
- Be concise and accurate
- If you can't find relevant information, say so"""

    # Create prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # Create agent
    agent = create_tool_calling_agent(_llm, tools, prompt)
    _agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=False,
        return_intermediate_steps=False,
    )


async def ask(
    question: str,
    session_id: str = None,
) -> dict:
    """Ask the agent a question.

    Args:
        question: User's question
        session_id: Optional session ID for conversation history

    Returns:
        Dictionary with:
            - answer: str
            - sources: list of citations
            - agent_type: str
            - session_id: str
    """
    if _agent_executor is None:
        raise RuntimeError("Agent not initialized. Call initialize_agent() first.")

    # Invoke agent
    import time
    start_time = time.time()

    result = await _agent_executor.ainvoke(
        {"input": question},
        config=RunnableConfig(callbacks=[]),
    )

    elapsed_ms = int((time.time() - start_time) * 1000)

    # Extract answer
    answer = result.get("output", "")

    # Extract tool calls for sources
    sources = []
    intermediate_steps = result.get("intermediate_steps", [])
    for step in intermediate_steps:
        action, observation = step
        if action.tool == "search_knowledge_base":
            # Parse observation for citations
            sources.append({
                "type": "knowledge_base",
                "content": observation[:200] + "..." if len(observation) > 200 else observation,
            })

    return {
        "answer": answer,
        "sources": sources,
        "agent_type": "agent",
        "session_id": session_id,
        "elapsed_ms": elapsed_ms,
    }
