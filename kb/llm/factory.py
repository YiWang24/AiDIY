"""LLM factory for creating LLM instances."""

from kb.llm.base import BaseLLM
from kb.llm.gemini import GeminiLLM


def create_llm(config: dict) -> BaseLLM:
    """Create LLM instance from configuration.

    Args:
        config: LLM configuration dict with keys:
            - provider: "gemini"
            - model: Model name (e.g., "gemini-1.5-flash")
            - api_key: API key for the provider
            - temperature: Sampling temperature (optional, default 0.3)
            - max_tokens: Max tokens to generate (optional, default 1024)

    Returns:
        BaseLLM instance configured with the provided settings

    Raises:
        ValueError: If provider is not supported or config is invalid
    """
    provider = config.get("provider", "")

    if not provider:
        raise ValueError("LLM config must specify 'provider'")

    if provider == "gemini":
        return GeminiLLM(
            model=config.get("model", "gemini-1.5-flash"),
            api_key=config.get("api_key", ""),
            temperature=config.get("temperature", 0.3),
            max_tokens=config.get("max_tokens", 1024),
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}. Supported: gemini")
