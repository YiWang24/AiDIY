"""LLM factory helpers.

Centralizes creation of chat models used by the KB agent.
"""

from __future__ import annotations

from langchain_core.language_models.chat_models import BaseChatModel


def create_llm(*, model: str, api_key: str, temperature: float = 0.3) -> BaseChatModel:
    """Create a chat LLM instance.

    Args:
        model: Model name, e.g. "gemini-2.5-flash".
        api_key: Gemini API key.
        temperature: Sampling temperature.

    Returns:
        A LangChain chat model supporting async invocation.
    """
    if not api_key:
        raise ValueError("GEMINI_API_KEY is required")

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            "langchain-google-genai is required to use Gemini chat models"
        ) from exc

    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=api_key,
        temperature=temperature,
    )
