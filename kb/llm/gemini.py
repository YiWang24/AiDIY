"""Gemini LLM implementation using Google Generative AI API."""

import httpx
from typing import Optional, List, Any

from kb.llm.base import BaseLLM, LLMResponse


class GeminiLLM(BaseLLM):
    """Google Gemini LLM implementation.

    Uses the Gemini API for text generation.
    Supports gemini-1.5-flash, gemini-1.5-pro, and gemini-3.0-flash models.
    """

    API_BASE = "https://generativelanguage.googleapis.com/v1beta"

    def __init__(
        self,
        model: str = "gemini-2.5-flash",
        api_key: str = "",
        temperature: float = 0.3,
        max_tokens: int = 1024,
        timeout: float = 60.0,
    ):
        """Initialize Gemini LLM.

        Args:
            model: Model name (e.g., "gemini-2.5-flash", "gemini-2.5-pro")
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
        model_id = (
            f"models/{self.model}"
            if not self.model.startswith("models/")
            else self.model
        )

        url = f"{self.API_BASE}/{model_id}:generateContent?key={self._api_key}"

        headers = {
            "Content-Type": "application/json",
        }

        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temp,
                "maxOutputTokens": max_tok,
            },
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
            raise RuntimeError(
                f"Gemini API error: {e.response.status_code} - {e.response.text}"
            ) from e
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
            raise RuntimeError(
                f"Unexpected Gemini API response format: {result}"
            ) from e

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

    async def generate_with_tools(
        self,
        prompt: str,
        tools: List[Any],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        max_tool_calls: int = 5,
    ) -> LLMResponse:
        """Generate text with tool calling support.

        Uses Gemini's function calling API to allow the model to call tools.
        Automatically handles tool call loops and collects results.

        Args:
            prompt: Input prompt text
            tools: List of Tool instances available for calling
            temperature: Override default temperature
            max_tokens: Override default max_tokens
            max_tool_calls: Maximum number of tool call iterations

        Returns:
            LLMResponse with generated content (may include tool results)

        Raises:
            RuntimeError: If tool calling fails or max iterations reached
        """
        temp = temperature if temperature is not None else self.temperature
        max_tok = max_tokens if max_tokens is not None else self.max_tokens

        # Convert tools to Gemini function declarations
        function_declarations = [tool.to_function_declaration() for tool in tools]

        # Map function names back to tool instances
        tools_map = {tool.name(): tool for tool in tools}

        # Build request with tools
        model_id = (
            f"models/{self.model}"
            if not self.model.startswith("models/")
            else self.model
        )
        url = f"{self.API_BASE}/{model_id}:generateContent?key={self._api_key}"

        headers = {"Content-Type": "application/json"}

        conversation_history = []
        conversation_history.append({"role": "user", "parts": [{"text": prompt}]})

        iteration = 0
        final_content = ""
        total_tokens = 0

        while iteration < max_tool_calls:
            iteration += 1

            # Prepare request body
            data = {
                "contents": conversation_history,
                "generationConfig": {
                    "temperature": temp,
                    "maxOutputTokens": max_tok,
                },
            }

            # Add tools only on first iteration
            if iteration == 1:
                data["tools"] = [{"function_declarations": function_declarations}]

            try:
                with httpx.Client(timeout=self._timeout) as client:
                    response = client.post(url, json=data, headers=headers)
                    response.raise_for_status()
                    result = response.json()

                # Extract token usage
                tokens_used = self._extract_tokens(result)
                if tokens_used:
                    total_tokens += tokens_used

                # Extract response
                candidate = result["candidates"][0]
                content_parts = candidate.get("content", {}).get("parts", [])

                # Check for function calls
                function_calls = [
                    p.get("functionCall") for p in content_parts if "functionCall" in p
                ]

                if function_calls:
                    # Add model response to history
                    conversation_history.append(
                        {"role": "model", "parts": content_parts}
                    )

                    # Execute tool calls
                    for func_call in function_calls:
                        func_name = func_call.get("name", "")
                        func_args = func_call.get("args", {})

                        if func_name not in tools_map:
                            raise RuntimeError(f"Unknown tool called: {func_name}")

                        tool = tools_map[func_name]
                        try:
                            tool_result = await tool.execute(**func_args)
                        except Exception as e:
                            tool_result = f"Error executing {func_name}: {str(e)}"

                        # Add function response to history
                        conversation_history.append(
                            {
                                "role": "function",
                                "parts": [
                                    {
                                        "functionResponse": {
                                            "name": func_name,
                                            "response": {"result": tool_result},
                                        }
                                    }
                                ],
                            }
                        )

                    # Continue loop to get final response
                    continue

                else:
                    # No function calls, extract text response
                    final_content = self._extract_content(result)
                    break

            except httpx.HTTPStatusError as e:
                raise RuntimeError(
                    f"Gemini API error: {e.response.status_code} - {e.response.text}"
                ) from e
            except Exception as e:
                raise RuntimeError(f"Gemini LLM generation failed: {str(e)}") from e

        if iteration >= max_tool_calls:
            raise RuntimeError(
                f"Maximum tool call iterations ({max_tool_calls}) reached"
            )

        return LLMResponse(
            content=final_content,
            model=self.model,
            tokens_used=total_tokens if total_tokens > 0 else None,
            finish_reason=None,
        )
