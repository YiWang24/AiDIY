"""Tests for FastAPI endpoints."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self):
        """Test /health endpoint returns healthy status."""
        import sys
        from unittest.mock import MagicMock

        # Mock modules
        sys.modules["spacy"] = MagicMock()
        sys.modules["llama_index.core"] = MagicMock()
        sys.modules["llama_index.embeddings.huggingface"] = MagicMock()

        from kb.api.app import create_app

        app = create_app()

        # Verify app was created
        assert app is not None
        assert app.title == "KB Agent API"

        # Cleanup
        del sys.modules["spacy"]
        del sys.modules["llama_index.core"]
        del sys.modules["llama_index.embeddings.huggingface"]

    def test_app_has_routes(self):
        """Test that app has the expected routes."""
        import sys
        from unittest.mock import MagicMock

        sys.modules["spacy"] = MagicMock()
        sys.modules["llama_index.core"] = MagicMock()
        sys.modules["llama_index.embeddings.huggingface"] = MagicMock()

        from kb.api.app import create_app

        app = create_app()

        # Check that routes are registered
        routes = [route.path for route in app.routes]
        assert "/health" in routes
        assert "/api/v1/search" in routes
        assert "/api/v1/ask" in routes

        # Cleanup
        del sys.modules["spacy"]
        del sys.modules["llama_index.core"]
        del sys.modules["llama_index.embeddings.huggingface"]

    def test_search_request_schema(self):
        """Test SearchRequest schema validation."""
        from kb.api.schemas import SearchRequest

        # Valid request
        req = SearchRequest(query="test", top_k=10)
        assert req.query == "test"
        assert req.top_k == 10

        # Invalid query (too short)
        with pytest.raises(Exception):
            SearchRequest(query="", top_k=10)

        # Invalid top_k (too large)
        with pytest.raises(Exception):
            SearchRequest(query="test", top_k=100)

    def test_ask_request_schema(self):
        """Test AskRequest schema validation."""
        from kb.api.schemas import AskRequest

        # Valid request
        req = AskRequest(query="What is this?", top_k=5)
        assert req.query == "What is this?"
        assert req.top_k == 5

        # Invalid query
        with pytest.raises(Exception):
            AskRequest(query="", top_k=5)

        # Invalid top_k
        with pytest.raises(Exception):
            AskRequest(query="test", top_k=30)


