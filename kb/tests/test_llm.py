"""Unit tests for LLM module."""

import pytest
from unittest.mock import Mock, patch
from kb.llm.base import BaseLLM, LLMResponse
from kb.llm.gemini import GeminiLLM
from kb.llm.factory import create_llm


class TestLLMResponse:
    """Test suite for LLMResponse dataclass."""

    def test_creation(self):
        """Test creating LLMResponse."""
        response = LLMResponse(
            content="Test answer",
            model="gemini-1.5-flash",
            tokens_used=100,
            finish_reason="stop",
        )

        assert response.content == "Test answer"
        assert response.model == "gemini-1.5-flash"
        assert response.tokens_used == 100
        assert response.finish_reason == "stop"

    def test_creation_with_optional_fields(self):
        """Test creating LLMResponse without optional fields."""
        response = LLMResponse(
            content="Test answer",
            model="gemini-1.5-flash",
        )

        assert response.content == "Test answer"
        assert response.tokens_used is None
        assert response.finish_reason is None


class TestGeminiLLM:
    """Test suite for GeminiLLM."""

    def test_initialization(self):
        """Test GeminiLLM initialization."""
        llm = GeminiLLM(
            model="gemini-1.5-flash",
            api_key="test-key",
            temperature=0.5,
            max_tokens=2048,
        )

        assert llm.model == "gemini-1.5-flash"
        assert llm.temperature == 0.5
        assert llm.max_tokens == 2048
        assert llm._api_key == "test-key"

    def test_initialization_defaults(self):
        """Test GeminiLLM initialization with defaults."""
        llm = GeminiLLM(
            model="gemini-1.5-flash",
            api_key="test-key",
        )

        assert llm.temperature == 0.3
        assert llm.max_tokens == 1024

    def test_initialization_requires_api_key(self):
        """Test that initialization fails without API key."""
        with pytest.raises(ValueError, match="API key"):
            GeminiLLM(
                model="gemini-1.5-flash",
                api_key="",
            )

    @patch("kb.llm.gemini.httpx.Client")
    def test_generate_success(self, mock_client_class):
        """Test successful generation."""
        # Mock the HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [{"text": "Test answer"}]
                    },
                    "finishReason": "stop"
                }
            ],
            "usageMetadata": {
                "totalTokenCount": 50
            }
        }

        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        llm = GeminiLLM(
            model="gemini-1.5-flash",
            api_key="test-key",
        )

        response = llm.generate("Test prompt")

        assert response.content == "Test answer"
        assert response.model == "gemini-1.5-flash"
        assert response.tokens_used == 50
        assert response.finish_reason == "stop"

    @patch("kb.llm.gemini.httpx.Client")
    def test_generate_with_overrides(self, mock_client_class):
        """Test generation with parameter overrides."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [{"text": "Test answer"}]
                    },
                    "finishReason": "stop"
                }
            ],
        }

        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        llm = GeminiLLM(
            model="gemini-1.5-flash",
            api_key="test-key",
            temperature=0.3,
            max_tokens=1024,
        )

        response = llm.generate(
            "Test prompt",
            temperature=0.8,
            max_tokens=500,
        )

        # Verify the call used the overrides
        call_args = mock_client.post.call_args
        data = call_args.kwargs["json"]
        assert data["generationConfig"]["temperature"] == 0.8
        assert data["generationConfig"]["maxOutputTokens"] == 500

    @patch("kb.llm.gemini.httpx.Client")
    def test_generate_api_error(self, mock_client_class):
        """Test handling of API errors."""
        import httpx

        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "API Error",
            request=Mock(),
            response=mock_response
        )

        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        llm = GeminiLLM(
            model="gemini-1.5-flash",
            api_key="test-key",
        )

        with pytest.raises(RuntimeError, match="Gemini API error"):
            llm.generate("Test prompt")


class TestLLMFactory:
    """Test suite for LLM factory."""

    def test_create_gemini_llm(self):
        """Test creating Gemini LLM from config."""
        config = {
            "provider": "gemini",
            "model": "gemini-1.5-flash",
            "api_key": "test-key",
            "temperature": 0.5,
            "max_tokens": 2048,
        }

        llm = create_llm(config)

        assert isinstance(llm, GeminiLLM)
        assert llm.model == "gemini-1.5-flash"
        assert llm.temperature == 0.5
        assert llm.max_tokens == 2048

    def test_create_gemini_with_defaults(self):
        """Test creating Gemini LLM with default config."""
        config = {
            "provider": "gemini",
            "api_key": "test-key",
        }

        llm = create_llm(config)

        assert isinstance(llm, GeminiLLM)
        assert llm.model == "gemini-1.5-flash"
        assert llm.temperature == 0.3
        assert llm.max_tokens == 1024

    def test_create_without_provider(self):
        """Test that factory fails without provider."""
        config = {
            "api_key": "test-key",
        }

        with pytest.raises(ValueError, match="must specify"):
            create_llm(config)

    def test_create_with_unsupported_provider(self):
        """Test that factory fails with unsupported provider."""
        config = {
            "provider": "unsupported",
            "api_key": "test-key",
        }

        with pytest.raises(ValueError, match="Unsupported"):
            create_llm(config)
