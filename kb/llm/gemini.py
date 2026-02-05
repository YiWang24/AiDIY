"""Gemini LLM implementation using Google Generative AI API."""

import httpx
from typing import Optional

from kb.llm.base import BaseLLM, LLMResponse


class GeminiLLM(BaseLLM):
    """Google Gemini LLM implementation.

    Uses the Gemini API for text generation.
    Supports gemini-1.5-flash, gemini-1.5-pro, and gemini-3.0-flash models.
    """

    API_BASE = "https://generativelanguage.googleapis.com/v1beta"

    def __init__(
        self,
        model: str = "gemini-1.5-flash",
        api_key: str = "",
        temperature: float = 0.3,
        max_tokens: int = 1024,
        timeout: float = 60.0,
    ):
        """Initialize Gemini LLM.

        Args:
            model: Model name (e.g., "gemini-1.5-flash", "gemini-1.5-pro")
            api_key: Google API key
            temperature: Sampling temperature (0.0 - 1.0)
            max_tokens: Maximum tokens to generate
            timeout: Request timeout in seconds
        """
        super().__init__(model=model, temperature=temperature, max_tokens=max_tokens)
        self._api_key = api_key
        self._timeout = timeout

        if not self._api_key:
            raise ValueError("Google API key is required for Gemini LLM")

    def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """Generate text from prompt using Gemini API.

        Args:
            prompt: Input prompt text
            temperature: Override default temperature
            max_tokens: Override default max_tokens

        Returns:
            LLMResponse with generated content and metadata
        """
        temp = temperature if temperature is not None else self.temperature
        max_tok = max_tokens if max_tokens is not None else self.max_tokens

        # Map model name to API format
        # gemini-1.5-flash -> models/gemini-1.5-flash
        model_id = f"models/{self.model}" if not self.model.startswith("models/") else self.model

        url = f"{self.API_BASE}/{model_id}:generateContent?key={self._api_key}"

        headers = {
            "Content-Type": "application/json",
        }

        data = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": temp,
                "maxOutputTokens": max_tok,
            }
        }

        try:
            with httpx.Client(timeout=self._timeout) as client:
                response = client.post(url, json=data, headers=headers)
                response.raise_for_status()
                result = response.json()

            # Extract response content
            content = self._extract_content(result)

            # Extract token usage if available
            tokens_used = self._extract_tokens(result)

            # Extract finish reason
            finish_reason = self._extract_finish_reason(result)

            return LLMResponse(
                content=content,
                model=self.model,
                tokens_used=tokens_used,
                finish_reason=finish_reason,
            )

        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"Gemini API error: {e.response.status_code} - {e.response.text}") from e
        except Exception as e:
            raise RuntimeError(f"Gemini LLM generation failed: {str(e)}") from e

    def _extract_content(self, result: dict) -> str:
        """Extract text content from API response.

        Args:
            result: Raw API response

        Returns:
            Generated text content
        """
        try:
            return result["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as e:
            raise RuntimeError(f"Unexpected Gemini API response format: {result}") from e

    def _extract_tokens(self, result: dict) -> Optional[int]:
        """Extract token usage from API response.

        Args:
            result: Raw API response

        Returns:
            Total tokens used or None if not available
        """
        try:
            usage_metadata = result.get("usageMetadata", {})
            return usage_metadata.get("totalTokenCount")
        except Exception:
            return None

    def _extract_finish_reason(self, result: dict) -> Optional[str]:
        """Extract finish reason from API response.

        Args:
            result: Raw API response

        Returns:
            Finish reason or None if not available
        """
        try:
            return result["candidates"][0].get("finishReason")
        except (KeyError, IndexError):
            return None
