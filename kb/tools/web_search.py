"""Web search tool using Tavily or Brave Search APIs."""

import os
from typing import Dict, Any, Optional
import httpx

from kb.tools.base import Tool


class WebSearchTool(Tool):
    """Web search tool using Tavily API (with Brave fallback).

    Supports Tavily Search as primary provider and Brave Search as fallback.
    Returns formatted search results optimized for LLM consumption.
    """

    def __init__(
        self,
        provider: str = "tavily",
        api_key: Optional[str] = None,
        max_results: int = 5,
        search_depth: str = "basic",
        timeout: float = 30.0,
    ):
        """Initialize web search tool.

        Args:
            provider: Search provider ("tavily" or "brave")
            api_key: API key for the provider (defaults to env var)
            max_results: Maximum number of results to return
            search_depth: Search depth ("basic" or "advanced")
            timeout: Request timeout in seconds
        """
        self._provider = provider.lower()
        self._max_results = max_results
        self._search_depth = search_depth
        self._timeout = timeout

        # Get API key from parameter or environment
        if api_key:
            self._api_key = api_key
        elif self._provider == "tavily":
            self._api_key = os.getenv("TAVILY_API_KEY", "")
        elif self._provider == "brave":
            self._api_key = os.getenv("BRAVE_API_KEY", "")
        else:
            self._api_key = ""

        if not self._api_key:
            raise ValueError(f"API key required for {self._provider} provider")

    def name(self) -> str:
        """Return tool name."""
        return "web_search"

    def description(self) -> str:
        """Return tool description."""
        return (
            "Search the web for current information, news, or topics not in the knowledge base. "
            "Use this when you need real-time data or the provided context is insufficient. "
            "Returns relevant search results with titles, snippets, and URLs."
        )

    def parameters_schema(self) -> Dict[str, Any]:
        """Return JSON schema for parameters."""
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query string (e.g., 'latest AI trends 2025')",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default: 5)",
                    "default": self._max_results,
                    "minimum": 1,
                    "maximum": 10,
                },
            },
            "required": ["query"],
        }

    async def execute(self, **kwargs) -> str:
        """Execute web search.

        Args:
            **kwargs: Tool parameters (query, max_results)

        Returns:
            Formatted search results as string

        Raises:
            ValueError: If query is empty
            RuntimeError: If search fails
        """
        query = kwargs.get("query", "")
        max_results = kwargs.get("max_results", self._max_results)

        if not query or not query.strip():
            raise ValueError("Search query cannot be empty")

        num_results = max_results if max_results is not None else self._max_results

        try:
            if self._provider == "tavily":
                results = await self._search_tavily(query, num_results)
            elif self._provider == "brave":
                results = await self._search_brave(query, num_results)
            else:
                raise ValueError(f"Unsupported provider: {self._provider}")

            return self._format_results(results, query)

        except httpx.HTTPStatusError as e:
            raise RuntimeError(
                f"Web search API error: {e.response.status_code} - {e.response.text}"
            ) from e
        except Exception as e:
            raise RuntimeError(f"Web search failed: {str(e)}") from e

    async def _search_tavily(self, query: str, max_results: int) -> list[dict]:
        """Search using Tavily API.

        Args:
            query: Search query
            max_results: Maximum results

        Returns:
            List of search result dicts
        """
        url = "https://api.tavily.com/search"

        headers = {
            "Content-Type": "application/json",
        }

        data = {
            "api_key": self._api_key,
            "query": query,
            "max_results": max_results,
            "search_depth": self._search_depth,
            "include_answer": False,  # We'll generate our own answer
            "include_raw_content": False,
            "include_images": False,
        }

        with httpx.Client(timeout=self._timeout) as client:
            response = client.post(url, json=data, headers=headers)
            response.raise_for_status()
            result = response.json()

        # Extract results
        results = []
        for item in result.get("results", []):
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "snippet": item.get("content", ""),
                "score": item.get("score", 0.0),
            })

        return results

    async def _search_brave(self, query: str, max_results: int) -> list[dict]:
        """Search using Brave Search API.

        Args:
            query: Search query
            max_results: Maximum results

        Returns:
            List of search result dicts
        """
        url = "https://api.search.brave.com/res/v1/web/search"

        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self._api_key,
        }

        params = {
            "q": query,
            "count": max_results,
        }

        with httpx.Client(timeout=self._timeout) as client:
            response = client.get(url, params=params, headers=headers)
            response.raise_for_status()
            result = response.json()

        # Extract results from Brave response format
        results = []
        for item in result.get("web", {}).get("results", []):
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "snippet": item.get("description", ""),
                "score": 0.0,  # Brave doesn't provide scores
            })

        return results

    def _format_results(self, results: list[dict], query: str) -> str:
        """Format search results for LLM consumption.

        Args:
            results: List of search result dicts
            query: Original search query

        Returns:
            Formatted results string
        """
        if not results:
            return f"No results found for query: '{query}'"

        formatted = f"Search results for '{query}':\n\n"

        for i, result in enumerate(results, 1):
            formatted += f"[{i}] {result['title']}\n"
            formatted += f"    URL: {result['url']}\n"
            formatted += f"    {result['snippet']}\n\n"

        return formatted.strip()
