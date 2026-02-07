"""Streaming endpoint using simplified agent.

Single file approach: Tools → Retrieval → Agent → Output.
"""

import os
import json
import asyncio
from typing import AsyncGenerator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, field_validator

from kb.api.dependencies import (
    get_vector_store,
    get_doc_store,
    get_llm_config,
)
from kb.storage.vectorstore import VectorStore
from kb.storage.docstore import DocStore

# Import the simplified agent
from kb.agent import initialize_agent, ask

router = APIRouter(prefix="/stream", tags=["stream"])

# Global agent state (initialized once)
_agent_initialized = False


# ========== Request Schema ==========


class StreamRequest(BaseModel):
    """Request model for /stream endpoint."""

    question: str = Field(..., min_length=1, description="Question to answer")
    session_id: str = Field(
        ..., min_length=1, description="Session identifier for conversation"
    )

    @field_validator("question")
    @classmethod
    def question_must_not_be_empty(cls, v: str) -> str:
        """Validate question is not just whitespace."""
        if not v.strip():
            raise ValueError("question cannot be empty or whitespace")
        return v.strip()


# ========== SSE Event Helpers ==========


async def _send_sse(event_type: str, data: dict) -> str:
    """Format data as SSE event."""
    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"


async def _stream_start() -> str:
    """Send start event."""
    return await _send_sse("start", {"status": "starting"})


async def _stream_generation_delta(delta: str) -> str:
    """Stream generation delta (token)."""
    return await _send_sse("generation_delta", {"delta": delta})


async def _stream_complete(answer: str, sources: list, metadata: dict) -> str:
    """Send complete event with final answer."""
    return await _send_sse(
        "complete",
        {
            "answer": answer,
            "sources": sources,
            "metadata": metadata,
        },
    )


async def _stream_error(error: str, detail: str = "") -> str:
    """Send error event."""
    return await _send_sse("error", {"error": error, "detail": detail})


# ========== Main Stream Endpoint ==========


@router.post("")
async def stream(
    request: StreamRequest,
    vector_store: VectorStore = Depends(get_vector_store),
    doc_store: DocStore = Depends(get_doc_store),
    llm_config=Depends(get_llm_config),
):
    """Simplified streaming endpoint.

    Process:
    1. Agent receives question
    2. Agent decides which tools to use (KB search, web search, etc.)
    3. Agent retrieves relevant information
    4. Agent generates answer with citations
    5. Stream response back to client

    SSE Events:
    - start: Processing started
    - generation_delta: Streaming token chunks
    - complete: Final answer with sources
    - error: Error occurred
    """

    async def event_generator() -> AsyncGenerator[str, None]:
        """Generate SSE events for the stream."""
        global _agent_initialized

        try:
            # Initialize agent once
            if not _agent_initialized:
                initialize_agent(
                    vector_store=vector_store,
                    doc_store=doc_store,
                    llm_config=llm_config,
                )
                _agent_initialized = True

            # Send start event
            yield await _stream_start()

            # Ask the agent
            result = await ask(
                question=request.question,
                session_id=request.session_id,
            )

            # Stream the answer word by word
            answer = result["answer"]
            words = answer.split()

            for word in words:
                yield await _stream_generation_delta(word + " ")
                await asyncio.sleep(0.03)  # Simulate streaming

            # Send complete event
            metadata = {
                "agent_type": result["agent_type"],
                "session_id": result["session_id"],
                "elapsed_ms": result["elapsed_ms"],
                "sources_count": len(result.get("sources", [])),
            }

            yield await _stream_complete(
                answer=answer,
                sources=result.get("sources", []),
                metadata=metadata,
            )

        except Exception as e:
            # Send error
            yield await _stream_error(
                error="Agent processing failed", detail=str(e)
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
