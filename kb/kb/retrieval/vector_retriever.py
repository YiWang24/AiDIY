from __future__ import annotations

from kb.config import AppConfig


class VectorRetriever:
    """Vector-based retrieval using LlamaIndex VectorStoreIndex."""

    def __init__(self, config: AppConfig, persist_dir: str):
        """Initialize vector retriever.

        Args:
            config: Application configuration
            persist_dir: Directory where index is persisted
        """
        self.config = config
        self.persist_dir = persist_dir
        self._index = None
        self._embed_model = None

    def load(self):
        """Load index from persistent storage.

        This loads the VectorStoreIndex from disk and initializes
        the embedding model for queries.
        """
        from llama_index.core import StorageContext, VectorStoreIndex
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding

        # Load storage context from persist directory
        storage_context = StorageContext.from_defaults(
            persist_dir=self.persist_dir
        )

        # Initialize embedding model
        self._embed_model = HuggingFaceEmbedding(
            model_name=self.config.embedding.model
        )

        # Load index from storage
        self._index = VectorStoreIndex.from_documents(
            documents=[],
            storage_context=storage_context,
            embed_model=self._embed_model,
        )

    def retrieve(self, query: str, top_k: int = 10):
        """Retrieve relevant nodes using vector similarity search.

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of retrieved nodes with similarity scores
        """
        if self._index is None:
            self.load()

        # Create retriever with specified top_k
        retriever = self._index.as_retriever(
            similarity_top_k=top_k
        )

        # Retrieve nodes
        return retriever.retrieve(query)
