"""LangGraph Agent in a single file.

Clean implementation: State → Nodes → Graph → Stream.

Flow:
    route → kb_search/web_search → generate → output
"""

import time
import asyncio
from typing import TypedDict, Annotated, Literal

from langchain_core.messages import BaseMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END, add_messages
from langgraph.checkpoint.memory import MemorySaver

from kb.storage.vectorstore import VectorStore
from kb.llm import create_llm
from kb.pipeline.config import Config


# ========== State ==========

class AgentState(TypedDict):
    """Agent state that flows through the graph."""
    messages: Annotated[list[BaseMessage], add_messages]
    question: str
    search_results: list[dict]
    answer: str
    metadata: dict


# ========== Global State (injected at startup) ==========

_vector_store: VectorStore = None
_config: Config = None
_llm = None
_graph = None
_checkpointer = MemorySaver()


# ========== Tools ==========

@tool
async def search_knowledge_base(query: str, top_k: int = 5) -> str:
    """Search the knowledge base for relevant information.

    Use this for technical questions about:
    - Architecture and design patterns
    - API documentation
    - Implementation details
    - Tutorials and guides
    """
    # langchain-postgres PGVector is backed by sync SQLAlchemy engine by default.
    # Using async retriever methods can fail with errors like "_async_engine not found".
    # Run the sync retriever invocation in a thread instead.
    retriever = _vector_store._vectorstore.as_retriever(search_kwargs={"k": top_k})
    docs = await asyncio.to_thread(retriever.invoke, query)

    if not docs:
        return "No relevant information found."

    formatted = f"Found {len(docs)} relevant documents:\n\n"
    for i, doc in enumerate(docs, 1):
        heading = " > ".join(doc.metadata.get("heading_path", []))
        if heading:
            formatted += f"[{i}] **{heading}**\n"
        formatted += f"{doc.page_content}\n\n"
    return formatted.strip()


@tool
async def search_web(query: str, max_results: int = 5) -> str:
    """Search the web for current information.

    Use this for:
    - Current events and news
    - Recent releases or updates
    - Real-time data
    """
    try:
        from langchain_community.tools.tavily.search import TavilySearchResults
        tavily = TavilySearchResults(max_results=max_results, api_key=_config.web_search_api_key)
        results = await tavily.ainvoke({"query": query})

        if not results:
            return "No results found."

        formatted = f"Found {len(results)} web pages:\n\n"
        for i, r in enumerate(results, 1):
            formatted += f"[{i}] **{r.get('title', 'N/A')}**\n"
            formatted += f"URL: {r.get('url', '')}\n"
            formatted += f"{r.get('content', '')}\n\n"
        return formatted.strip()
    except Exception as e:
        return f"Web search failed: {e}"


# ========== Nodes ==========

async def route_node(state: AgentState) -> dict[str, any]:
    """Decide which search to perform."""
    question = state["question"].lower()
    web_keywords = ["current", "latest", "recent", "price", "news", "today", "now"]

    needs_web = any(kw in question for kw in web_keywords)
    return {"metadata": {"needs_web_search": needs_web}}


async def search_node(state: AgentState) -> dict[str, any]:
    """Perform search (KB or Web based on route)."""
    question = state["question"]
    needs_web = state.get("metadata", {}).get("needs_web_search", False)

    if needs_web:
        results = await search_web.ainvoke({"query": question})
    else:
        results = await search_knowledge_base.ainvoke({"query": question})

    return {"search_results": [{"content": results}]}


async def generate_node(state: AgentState) -> dict[str, any]:
    """Generate answer using LLM."""
    from langchain_core.messages import HumanMessage, SystemMessage

    context = "\n\n".join([r["content"] for r in state.get("search_results", [])])

    prompt = f"""Answer the question based on the context below.

Context:
{context}

Question: {state["question"]}

Answer:"""

    messages = [
        SystemMessage(content="You are a helpful assistant. Be accurate and cite sources."),
        HumanMessage(content=prompt),
    ]

    response = await _llm.ainvoke(messages)
    return {"answer": response.content}


# ========== Graph ==========

def build_graph() -> StateGraph:
    """Build the LangGraph agent."""
    workflow = StateGraph(AgentState)

    workflow.add_node("route", route_node)
    workflow.add_node("search", search_node)
    workflow.add_node("generate", generate_node)

    workflow.add_edge(START, "route")
    workflow.add_edge("route", "search")
    workflow.add_edge("search", "generate")
    workflow.add_edge("generate", END)

    return workflow.compile(checkpointer=_checkpointer)


# ========== Initialization ==========

def initialize_agent(vector_store: VectorStore, config: Config = None):
    """Initialize the agent (call once at startup)."""
    global _vector_store, _config, _llm, _graph

    _vector_store = vector_store
    _config = config or Config.from_yaml("kb/config.yaml")

    llm_config = _config.llm or {}
    _llm = create_llm(
        model=llm_config.get("model", "gemini-2.5-flash"),
        api_key=_config.gemini_api_key,
        temperature=llm_config.get("temperature", 0.3),
    )

    _graph = build_graph()


# ========== Ask ==========

async def ask(question: str, session_id: str = "default") -> dict:
    """Ask a question.

    Returns:
        Dict with answer, sources, agent_type, session_id, elapsed_ms
    """
    if _graph is None:
        raise RuntimeError("Agent not initialized. Call initialize_agent() first.")

    start_time = time.time()

    config = {"configurable": {"thread_id": session_id}}
    initial_state = {
        "messages": [],
        "question": question,
        "search_results": [],
        "answer": "",
        "metadata": {},
    }

    final_state = await _graph.ainvoke(initial_state, config=config)

    elapsed_ms = int((time.time() - start_time) * 1000)

    return {
        "answer": final_state["answer"],
        "sources": [],  # Can be enhanced
        "agent_type": "langgraph",
        "session_id": session_id,
        "elapsed_ms": elapsed_ms,
    }
