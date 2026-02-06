"""Pydantic schemas for API request/response models."""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional


# ========== Request Schemas ==========


class AskRequest(BaseModel):
    """Request model for /ask endpoint."""

    question: str = Field(..., min_length=1, description="Question to answer")
    top_k: int = Field(
        default=10, ge=1, le=50, description="Number of chunks to retrieve"
    )

    @field_validator("question")
    @classmethod
    def question_must_not_be_empty(cls, v: str) -> str:
        """Validate question is not just whitespace."""
        if not v.strip():
            raise ValueError("question cannot be empty or whitespace")
        return v.strip()


class ChatRequest(BaseModel):
    """Request model for /chat endpoint."""

    question: str = Field(..., min_length=1, description="Question to answer")
    session_id: str = Field(
        ..., min_length=1, description="Session identifier for conversation"
    )
    top_k: int = Field(
        default=10, ge=1, le=50, description="Number of chunks to retrieve"
    )

    @field_validator("question")
    @classmethod
    def question_must_not_be_empty(cls, v: str) -> str:
        """Validate question is not just whitespace."""
        if not v.strip():
            raise ValueError("question cannot be empty or whitespace")
        return v.strip()


class SearchRequest(BaseModel):
    """Request model for /search endpoint."""

    query: str = Field(..., min_length=1, description="Search query")
    k: int = Field(default=5, ge=1, le=50, description="Number of results to return")

    @field_validator("query")
    @classmethod
    def query_must_not_be_empty(cls, v: str) -> str:
        """Validate query is not just whitespace."""
        if not v.strip():
            raise ValueError("query cannot be empty or whitespace")
        return v.strip()


# ========== Response Schemas ==========


class Citation(BaseModel):
    """Citation metadata for a source chunk."""

    id: int = Field(..., description="Citation number (e.g., 1 for [1])")
    chunk_id: str = Field(..., description="Unique chunk identifier")
    doc_id: str = Field(..., description="Parent document identifier")
    title: str = Field(..., description="Document title")
    path: str = Field(..., description="Document file path")
    heading_path: List[str] = Field(
        default_factory=list, description="Heading hierarchy"
    )
    score: float = Field(..., ge=0.0, le=1.0, description="Similarity score")


class AskResponse(BaseModel):
    """Response model for /ask endpoint."""

    answer: str = Field(..., description="Generated answer")
    citations: List[Citation] = Field(
        default_factory=list, description="Source citations"
    )
    has_sufficient_knowledge: bool = Field(
        ..., description="Whether KB had sufficient information"
    )
    model: str = Field(..., description="LLM model used")
    tokens_used: Optional[int] = Field(
        None, description="Tokens consumed (if available)"
    )
    retrieval_time_ms: int = Field(..., description="Retrieval latency in milliseconds")
    generation_time_ms: int = Field(
        ..., description="Generation latency in milliseconds"
    )
    agent_type: Optional[str] = Field(
        None, description="Agent type that handled the request"
    )


class ChatResponse(BaseModel):
    """Response model for /chat endpoint."""

    answer: str = Field(..., description="Generated answer")
    citations: List[Citation] = Field(
        default_factory=list, description="Source citations"
    )
    session_id: str = Field(..., description="Session identifier")
    message_id: str = Field(..., description="Unique message identifier")
    has_sufficient_knowledge: bool = Field(
        ..., description="Whether KB had sufficient information"
    )
    model: str = Field(..., description="LLM model used")
    tokens_used: Optional[int] = Field(
        None, description="Tokens consumed (if available)"
    )
    retrieval_time_ms: int = Field(..., description="Retrieval latency in milliseconds")
    generation_time_ms: int = Field(
        ..., description="Generation latency in milliseconds"
    )


class SearchResult(BaseModel):
    """Single search result from /search endpoint."""

    chunk_id: str = Field(..., description="Unique chunk identifier")
    doc_id: str = Field(..., description="Parent document identifier")
    content: str = Field(..., description="Chunk content")
    heading_path: List[str] = Field(
        default_factory=list, description="Heading hierarchy"
    )
    chunk_index: int = Field(..., description="Chunk index within document")
    score: float = Field(..., ge=0.0, le=1.0, description="Similarity score")
    document: "DocumentMetadata" = Field(..., description="Document metadata")


class DocumentMetadata(BaseModel):
    """Document metadata."""

    title: str = Field(..., description="Document title")
    path: str = Field(..., description="Document file path")


# Type alias for search response
SearchResponse = List[SearchResult]


# ========== Error Schemas ==========


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
