"""KB indexing and query service."""

__version__ = "0.1.0"

# Domain entities
from kb.domain.document import Document
from kb.domain.chunk import Chunk

# Storage adapters
from kb.storage.docstore import DocStore
from kb.storage.vectorstore import VectorStore

# Pipeline components
from kb.pipeline.config import ChunkingConfig, Config
from kb.pipeline.clean import clean_documents
from kb.pipeline.chunk import split_document

# CLI
from kb.cli import main

__all__ = [
    # Domain
    "Document",
    "Chunk",
    # Storage
    "DocStore",
    "VectorStore",
    # Pipeline
    "ChunkingConfig",
    "Config",
    "clean_documents",
    "split_document",
    # CLI
    "main",
]
