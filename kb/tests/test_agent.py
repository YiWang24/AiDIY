from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from kb.config import AppConfig, LLMConfig


class TestPrompts:
    """Test agent prompts"""

    def test_system_prompt_exists(self):
        """Test that system prompt is defined"""
        from kb.agent.prompts import SYSTEM_PROMPT

        assert SYSTEM_PROMPT is not None
        assert len(SYSTEM_PROMPT) > 0
        assert "AiDIY" in SYSTEM_PROMPT or "assistant" in SYSTEM_PROMPT

    def test_react_prompt_template_exists(self):
        """Test that ReAct prompt template exists"""
        from kb.agent.prompts import REACT_PROMPT_TEMPLATE

        assert REACT_PROMPT_TEMPLATE is not None
        assert "{input}" in REACT_PROMPT_TEMPLATE
        assert "{agent_scratchpad}" in REACT_PROMPT_TEMPLATE


class TestKBExecutor:
    """Test KB executor with ReAct agent"""

    def test_init(self):
        """Test KBExecutor initialization"""
        import sys
        from unittest.mock import MagicMock

        sys.modules["langchain_openai"] = MagicMock()
        sys.modules["langchain"] = MagicMock()
        sys.modules["langchain.agents"] = MagicMock()
        sys.modules["langchain_core"] = MagicMock()

        from kb.agent.executor import KBExecutor
        from kb.retrieval.hybrid import HybridRetriever

        config = AppConfig(
            llm=LLMConfig(
                provider="openai",
                model="gpt-4o-mini",
                api_key=None,
            )
        )

        mock_retriever = MagicMock(spec=HybridRetriever)
        mock_retriever.retrieve.return_value = []

        executor = KBExecutor(mock_retriever, config)

        assert executor.retriever is mock_retriever
        assert executor.config is config

        # Cleanup
        del sys.modules["langchain_openai"]
        del sys.modules["langchain"]
        del sys.modules["langchain.agents"]
        del sys.modules["langchain_core"]

    def test_fallback_mode_when_no_api_key(self):
        """Test that executor falls back to direct retrieval when no API key"""
        import sys
        from unittest.mock import MagicMock

        sys.modules["langchain_openai"] = MagicMock()
        sys.modules["langchain"] = MagicMock()

        from kb.agent.executor import KBExecutor
        from kb.retrieval.hybrid import HybridRetriever

        # Config with no API key
        config = AppConfig(
            llm=LLMConfig(
                api_key=None,
            )
        )

        mock_retriever = MagicMock(spec=HybridRetriever)

        # Create mock nodes
        mock_node = MagicMock()
        mock_node.metadata = {"title": "Test"}
        mock_node.get_content.return_value = "Test content"

        mock_retriever.retrieve.return_value = [(mock_node, 0.9)]

        executor = KBExecutor(mock_retriever, config)
        result = executor.ask("test query")

        # Should return fallback result
        assert result["method"] == "fallback"
        assert "answer" in result
        assert "degraded mode" in result["answer"].lower() or "fallback" in result["answer"].lower()

        # Cleanup
        del sys.modules["langchain_openai"]
        del sys.modules["langchain"]

    def test_create_llm_returns_none_when_no_api_key(self):
        """Test that _create_llm returns None when no API key"""
        import sys
        from unittest.mock import MagicMock

        sys.modules["langchain_openai"] = MagicMock()

        from kb.agent.executor import KBExecutor
        from kb.retrieval.hybrid import HybridRetriever

        config = AppConfig(llm=LLMConfig(api_key=None))
        mock_retriever = MagicMock(spec=HybridRetriever)

        executor = KBExecutor(mock_retriever, config)

        llm = executor._create_llm()

        assert llm is None

        # Cleanup
        del sys.modules["langchain_openai"]

    def test_create_executor_without_api_key(self):
        """Test that _create_executor returns None when no API key"""
        import sys
        from unittest.mock import MagicMock

        sys.modules["langchain_openai"] = MagicMock()
        sys.modules["langchain"] = MagicMock()
        sys.modules["langchain.agents"] = MagicMock()
        sys.modules["langchain_core"] = MagicMock()

        from kb.agent.executor import KBExecutor
        from kb.retrieval.hybrid import HybridRetriever

        config = AppConfig(llm=LLMConfig(api_key=None))
        mock_retriever = MagicMock(spec=HybridRetriever)

        executor = KBExecutor(mock_retriever, config)

        result = executor._create_executor()

        assert result is None

        # Cleanup
        del sys.modules["langchain_openai"]
        del sys.modules["langchain"]
        del sys.modules["langchain.agents"]
        del sys.modules["langchain_core"]

    def test_ask_with_api_key_calls_agent(self):
        """Test that ask() uses agent when API key is available"""
        import sys
        from unittest.mock import MagicMock, patch

        sys.modules["langchain_openai"] = MagicMock()
        sys.modules["langchain"] = MagicMock()
        sys.modules["langchain.agents"] = MagicMock()
        sys.modules["langchain_core"] = MagicMock()
        sys.modules["langchain_core.tools"] = MagicMock()

        from kb.agent.executor import KBExecutor
        from kb.retrieval.hybrid import HybridRetriever

        config = AppConfig(
            llm=LLMConfig(
                api_key="sk-test-key",
            )
        )

        mock_retriever = MagicMock(spec=HybridRetriever)
        mock_retriever.retrieve.return_value = []

        executor = KBExecutor(mock_retriever, config)

        # Mock the executor
        mock_agent_executor = MagicMock()
        mock_agent_executor.invoke.return_value = {"output": "Test answer"}

        with patch.object(executor, "_create_executor", return_value=mock_agent_executor):
            result = executor.ask("test query")

        # Verify agent was called
        mock_agent_executor.invoke.assert_called_once()
        assert result["method"] == "react_agent"
        assert result["answer"] == "Test answer"

        # Cleanup
        del sys.modules["langchain_openai"]
        del sys.modules["langchain"]
        del sys.modules["langchain.agents"]
        del sys.modules["langchain_core"]
        del sys.modules["langchain_core.tools"]
