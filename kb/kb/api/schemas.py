"""Pydantic schemas for API requests and responses."""

from __future__ import annotations

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """Request schema for semantic search."""

    query: str = Field(..., min_length=1, max_length=500, description="Search query")
    top_k: int = Field(default=10, ge=1, le=50, description="Number of results to return")


class SearchResult(BaseModel):
    """Single search result."""

    node_id: str
    text: str
    metadata: dict
    score: float


class SearchResponse(BaseModel):
    """Response schema for semantic search."""

    results: list[SearchResult]
    total: int
    query: str


class AskRequest(BaseModel):
    """Request schema for asking a question."""

    query: str = Field(..., min_length=1, max_length=500, description="Question to ask")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of sources to retrieve")


class AskResponse(BaseModel):
    """Response schema for asking a question."""

    answer: str
    sources: list[dict]
    method: str
    status: str
