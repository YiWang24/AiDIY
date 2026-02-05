"""Storage adapters for KB indexing system."""

from kb.storage.docstore import DocStore
from kb.storage.vectorstore import VectorStore

__all__ = ["DocStore", "VectorStore"]
