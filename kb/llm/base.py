"""Base LLM interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class LLMResponse:
    """Response from LLM generation.

    Attributes:
        content: Generated text content
        model: Model name used for generation
        tokens_used: Number of tokens consumed (if available)
        finish_reason: Reason generation finished (e.g., "stop", "length")
    """

    content: str
    model: str
    tokens_used: Optional[int] = None
    finish_reason: Optional[str] = None


class BaseLLM(ABC):
    """Abstract base class for LLM implementations.

    All LLM providers (Gemini, OpenAI, etc.) must implement this interface.
    """

    def __init__(
        self,
        model: str,
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ):
        """Initialize LLM.

        Args:
            model: Model name (e.g., "gemini-1.5-flash")
            temperature: Sampling temperature (0.0 - 1.0)
            max_tokens: Maximum tokens to generate
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    @abstractmethod
    def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """Generate text from prompt.

        Args:
            prompt: Input prompt text
            temperature: Override default temperature
            max_tokens: Override default max_tokens

        Returns:
            LLMResponse with generated content and metadata
        """
        pass
