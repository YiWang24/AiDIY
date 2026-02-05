"""Base interface for tools that can be called by agents."""

from abc import ABC, abstractmethod
from typing import Dict, Any


class Tool(ABC):
    """Abstract base class for all tools.

    Tools are callable functions that agents can use to extend their capabilities.
    Examples include web search, calculators, database queries, etc.
    """

    @abstractmethod
    def name(self) -> str:
        """Return the tool name for function calling.

        The name should be snake_case and descriptive, e.g., "web_search".

        Returns:
            Tool name string
        """
        pass

    @abstractmethod
    def description(self) -> str:
        """Return a description of what the tool does.

        This description is used by the LLM to decide when to call the tool.
        It should be clear and concise, explaining when and why to use the tool.

        Returns:
            Tool description string
        """
        pass

    @abstractmethod
    def parameters_schema(self) -> Dict[str, Any]:
        """Return the JSON schema for tool parameters.

        This schema follows JSON Schema format and describes the parameters
        that the tool accepts. It's used for function calling validation.

        Returns:
            JSON Schema dictionary describing parameters

        Example:
            {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query string"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        """
        pass

    @abstractmethod
    async def execute(self, **kwargs) -> str:
        """Execute the tool with provided parameters.

        Args:
            **kwargs: Tool parameters as defined in parameters_schema

        Returns:
            String result from tool execution

        Raises:
            ValueError: If required parameters are missing
            RuntimeError: If tool execution fails
        """
        pass

    def to_function_declaration(self) -> Dict[str, Any]:
        """Convert tool to Gemini function declaration format.

        Returns:
            Function declaration dictionary for Gemini API
        """
        return {
            "name": self.name(),
            "description": self.description(),
            "parameters": self.parameters_schema(),
        }
