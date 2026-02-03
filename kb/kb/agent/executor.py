"""KB executor with LangChain ReAct Agent."""

from kb.config import AppConfig


class KBExecutor:
    """Executor for KB Q&A using LangChain ReAct Agent."""

    def __init__(self, retriever, config: AppConfig):
        """Initialize KB executor.

        Args:
            retriever: HybridRetriever instance
            config: Application configuration
        """
        self.retriever = retriever
        self.config = config
        self._executor = None
        self._llm = None

    def _create_llm(self):
        """Create LLM instance if API key is available.

        Returns:
            LLM instance or None if no API key
        """
        if not self.config.llm.api_key:
            return None

        provider = self.config.llm.provider

        if provider == "openai":
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model=self.config.llm.model,
                api_key=self.config.llm.api_key,
                temperature=self.config.llm.temperature,
            )
        elif provider == "zhipuai":
            # Use zhipuai SDK directly
            try:
                from zhipuai import ZhipuAI

                return ZhipuAI(
                    api_key=self.config.llm.api_key,
                    model=self.config.llm.model,
                    temperature=self.config.llm.temperature,
                )
            except ImportError:
                # Fallback to langchain-community if zhipuai not available
                from langchain_community.chat_models.tongyi import ChatTongyi

                return ChatTongyi(
                    model=self.config.llm.model,
                    zhipuai_api_key=self.config.llm.api_key,
                    temperature=self.config.llm.temperature,
                )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    def _create_executor(self):
        """Create LangChain ReAct Agent executor.

        Returns:
            AgentExecutor instance or None if LLM not available
        """
        llm = self._create_llm()
        if llm is None:
            return None

        # Check if using zhipuai directly (not LangChain compatible)
        if self.config.llm.provider == "zhipuai" and hasattr(llm, 'chat'):
            # For zhipuai SDK, we need to wrap it for LangChain
            from langchain_core.language_models.chat_models import BaseChatModel
            from langchain_core.messages import BaseMessage, HumanMessage
            from typing import Any, List

            class ZhipuAILLMWrapper(BaseChatModel):
                """Wrapper for zhipuai SDK to work with LangChain."""

                def __init__(self, zhipuai_client):
                    super().__init__()
                    self.client = zhipuai_client

                @property
                def _llm_type(self):
                    return "zhipuai"

                def _generate(self, messages: List[BaseMessage], **kwargs) -> Any:
                    # Convert messages to zhipuai format
                    prompt = messages[0].content
                    response = self.client.chat.invoke(
                        model=self.client.model,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    return response

                @property
                def _identifying_params(self):
                    return {"model": self.client.model}

            llm = ZhipuAILLMWrapper(llm)

        # Import tools
        from kb.agent.tools import create_kb_tool

        # ReAct agent
        tools = [create_kb_tool(self.retriever)]

        # Create ReAct agent
        from langchain.agents import create_react_agent
        from langchain import hub

        # Use langchain hub's ReAct prompt
        prompt = hub.pull("hwchase17/react")

        agent = create_react_agent(llm, tools, prompt)

        from langchain.agents import AgentExecutor

        return AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            max_iterations=3,  # ReAct allows multi-step reasoning
            handle_parsing_errors=True,
        )

    def ask(self, query: str) -> dict:
        """Ask a question using the RAG agent.

        Args:
            query: User question

        Returns:
            Dict with answer and method
        """
        if self._executor is None:
            self._executor = self._create_executor()

        if self._executor is None:
            return self._fallback_answer(query)

        try:
            result = self._executor.invoke({"input": query})
            return {
                "answer": result["output"],
                "method": "react_agent",
            }
        except Exception as e:
            return self._fallback_answer(query, error=str(e))

    def _fallback_answer(self, query: str, error: str | None = None) -> dict:
        """Provide fallback answer when LLM is not available.

        Args:
            query: User question
            error: Optional error message

        Returns:
            Dict with answer and method="fallback"
        """
        results = self.retriever.retrieve(query, top_k=3)
        context = "\n\n---\n\n".join([
            node.get_content()[:300] for node, _ in results
        ])

        error_msg = f"\n\nError: {error}" if error else ""

        return {
            "answer": (
                f"Found {len(results)} relevant documents, but running in degraded mode (no LLM API key).\n\n"
                f"Most relevant content:\n\n{context}{error_msg}"
            ),
            "method": "fallback",
            "error": error,
        }
