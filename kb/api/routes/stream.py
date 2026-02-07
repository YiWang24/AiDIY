"""Streaming endpoint using LangGraph agent.

Single file approach: Agent → Stream → SSE.
"""

import json
import asyncio
import time
from typing import AsyncGenerator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, field_validator

from kb.api.dependencies import get_vector_store, get_doc_store, get_llm_config
from kb.storage.vectorstore import VectorStore
from kb.storage.docstore import DocStore
from kb.pipeline.config import Config
from kb.llm import create_llm

router = APIRouter(prefix="/stream", tags=["stream"])

# Global agent state (initialized once)
_agent_initialized = False


# ========== Request Schema ==========

class StreamRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Question to answer")
    session_id: str = Field(..., min_length=1, description="Session identifier for conversation")
    top_k: int = Field(5, ge=1, le=20, description="Number of chunks to retrieve")
    mode: str = Field("auto", description="Routing mode (auto/knowledge/web_search/hybrid)")

    @field_validator("question")
    @classmethod
    def question_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("question cannot be empty or whitespace")
        return v.strip()


# ========== SSE Event Helpers ==========

async def _send_sse(event_type: str, data: dict) -> str:
    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"


async def _stream_start() -> str:
    return await _send_sse("start", {"status": "starting"})


async def _stream_retrieval_start() -> str:
    return await _send_sse("retrieval_start", {"status": "retrieving"})


async def _stream_retrieval_complete(chunks: list, retrieval_time_ms: int) -> str:
    return await _send_sse(
        "retrieval_complete",
        {"chunks": chunks, "retrieval_time_ms": retrieval_time_ms},
    )


async def _stream_generation_start() -> str:
    return await _send_sse("generation_start", {"status": "generating"})


async def _stream_generation_delta(delta: str) -> str:
    return await _send_sse("generation_delta", {"delta": delta})


async def _stream_generation_complete(answer: str, sources: list, metadata: dict) -> str:
    # Frontend expects generation_complete with { answer, citations, metadata }
    return await _send_sse("generation_complete", {
        "answer": answer,
        "citations": sources,
        "metadata": metadata,
    })


async def _stream_complete(session_id: str) -> str:
    return await _send_sse("complete", {"session_id": session_id})


async def _stream_error(error: str, detail: str = "") -> str:
    return await _send_sse("error", {"error": error, "detail": detail})


# ========== Main Stream Endpoint ==========

@router.post("")
async def stream(
    request: StreamRequest,
    vector_store: VectorStore = Depends(get_vector_store),
    doc_store: DocStore = Depends(get_doc_store),
    llm_config=Depends(get_llm_config),
):
    """LangGraph streaming endpoint.

    Process:
    1. Route question (KB vs Web)
    2. Search and retrieve
    3. Generate answer
    4. Stream response with SSE
    """

    async def event_generator() -> AsyncGenerator[str, None]:
        global _agent_initialized

        try:
            # Send start event
            yield await _stream_start()

            # Retrieve chunks (KB mode only for now)
            yield await _stream_retrieval_start()

            retrieval_started = time.time()
            chunks = await asyncio.to_thread(
                vector_store.search_by_text,
                query_text=request.question,
                top_k=request.top_k,
            )
            retrieval_time_ms = int((time.time() - retrieval_started) * 1000)

            # Normalize chunk shape for frontend
            retrieval_chunks = [
                {
                    "chunk_id": c.get("chunk_id", ""),
                    "doc_id": c.get("doc_id", ""),
                    "content": c.get("content", ""),
                    "heading_path": c.get("heading_path", []) or [],
                    "score": float(c.get("score", 0.0) or 0.0),
                }
                for c in chunks
            ]

            yield await _stream_retrieval_complete(
                chunks=retrieval_chunks,
                retrieval_time_ms=retrieval_time_ms,
            )

            # Build citations from document metadata
            doc_meta_by_id: dict[str, dict] = {}
            for c in retrieval_chunks:
                doc_id = c.get("doc_id")
                if not doc_id or doc_id in doc_meta_by_id:
                    continue
                meta = await asyncio.to_thread(doc_store.get_document, doc_id)
                if meta:
                    doc_meta_by_id[doc_id] = meta

            def _doc_path_to_route(path: str) -> str:
                p = (path or "").lstrip("/")
                # Strip extension
                for ext in (".mdx", ".md"):
                    if p.endswith(ext):
                        p = p[: -len(ext)]
                        break
                if p.endswith("/index"):
                    p = p[: -len("/index")]
                if p.startswith("docs/"):
                    p = "/docs/" + p[len("docs/"):]
                elif p.startswith("blog/"):
                    p = "/blog/" + p[len("blog/"):]
                else:
                    p = "/" + p
                # Collapse any accidental double slashes
                while "//" in p:
                    p = p.replace("//", "/")
                return p

            citations = []
            for i, c in enumerate(retrieval_chunks, 1):
                doc_id = c.get("doc_id", "")
                meta = doc_meta_by_id.get(doc_id)
                citations.append(
                    {
                        "id": i,
                        "chunk_id": c.get("chunk_id", ""),
                        "doc_id": doc_id,
                        "title": (meta or {}).get("title") or doc_id or "Source",
                        "path": _doc_path_to_route((meta or {}).get("path") or ""),
                        "heading_path": c.get("heading_path", []) or [],
                        "score": c.get("score", 0.0) or 0.0,
                    }
                )

            # Generate answer
            yield await _stream_generation_start()

            config = Config.from_yaml(str(Path(__file__).parent.parent.parent / "config.yaml"))
            llm = create_llm(
                model=(llm_config or {}).get("model", "gemini-2.5-flash"),
                api_key=config.gemini_api_key,
                temperature=(llm_config or {}).get("temperature", 0.3),
            )

            context_parts = []
            for c in retrieval_chunks:
                heading = " > ".join(c.get("heading_path") or [])
                if heading:
                    context_parts.append(f"### {heading}\n{c.get('content','')}")
                else:
                    context_parts.append(c.get("content", ""))
            context = "\n\n".join(context_parts)

            from langchain_core.messages import HumanMessage, SystemMessage

            prompt = f"""Answer the question based on the context below.

Context:
{context}

Question: {request.question}

Answer:"""

            gen_started = time.time()
            response = await llm.ainvoke(
                [
                    SystemMessage(content="You are a helpful assistant. Be accurate and cite sources when relevant."),
                    HumanMessage(content=prompt),
                ]
            )
            generation_time_ms = int((time.time() - gen_started) * 1000)

            answer = getattr(response, "content", "") or ""

            # Stream the answer word by word (simulate streaming)
            words = answer.split()

            for word in words:
                yield await _stream_generation_delta(word + " ")
                await asyncio.sleep(0.02)

            # Send complete event
            metadata = {
                "agent_type": "knowledge",
                "session_id": request.session_id,
                "retrieval_time_ms": retrieval_time_ms,
                "generation_time_ms": generation_time_ms,
                "sources_count": len(citations),
            }

            yield await _stream_generation_complete(
                answer=answer,
                sources=citations,
                metadata=metadata,
            )

            yield await _stream_complete(session_id=request.session_id)

        except Exception as e:
            yield await _stream_error(
                error="Agent processing failed",
                detail=str(e),
            )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


from pathlib import Path
