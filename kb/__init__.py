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
from kb.pipeline.chunk import ChunkingStrategy
from kb.pipeline.incremental import IncrementalIndexer
from kb.pipeline.index import IndexBuilder
from kb.pipeline.pipeline import OfflineKBPipeline, run_full_pipeline

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
    "ChunkingStrategy",
    "IncrementalIndexer",
    "IndexBuilder",
    "OfflineKBPipeline",
    "run_full_pipeline",
    # CLI
    "main",
]
