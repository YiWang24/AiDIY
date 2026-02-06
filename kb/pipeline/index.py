"""Index building - orchestrates chunking and incremental indexing."""

import json
from typing import Iterator
from tqdm import tqdm

from kb.domain.document import Document
from kb.pipeline.chunk import ChunkingStrategy
from kb.pipeline.config import Config
from kb.pipeline.index_signature import compute_signature
from kb.pipeline.incremental import IncrementalIndexer
from kb.storage.docstore import DocStore
from kb.storage.vectorstore import VectorStore


class IndexBuilder:
    """Main index builder orchestrator."""

    def __init__(
        self,
        config: Config,
    ):
        """Initialize index builder.

        Args:
            config: Pipeline configuration
        """
        self._config = config
        self._chunking_config = config.chunking

        # Initialize storage
        self._docstore = DocStore(config.database_url)
        self._vectorstore = VectorStore(
            database_url=config.database_url,
            embedding_model=config.embedding_model,
            gemini_api_key=config.gemini_api_key,
            table_name=config.vector_store_table_name,
            batch_size=config.vector_store_batch_size,
        )

        # Initialize components
        self._chunker = ChunkingStrategy(self._chunking_config)
        self._incremental = IncrementalIndexer(self._docstore, self._vectorstore)
        self._force_rebuild_override = False

    def initialize(self) -> None:
        """Initialize storage connections."""
        self._docstore.initialize()
        self._vectorstore.initialize()

        signature = compute_signature(self._config, self._vectorstore.EMBEDDING_DIM)
        stored_signature = self._docstore.get_index_signature()
        if stored_signature and stored_signature != signature:
            # Config changed: clear existing data and force rebuild.
            self._vectorstore.reset_table()
            self._docstore.clear_documents()
            self._force_rebuild_override = True

        self._docstore.set_index_signature(signature)

    def close(self) -> None:
        """Close storage connections."""
        self._docstore.close()
        self._vectorstore.close()

    def build_from_jsonl(
        self,
        input_path: str,
        force_rebuild: bool = False,
    ) -> dict:
        """Build index from JSONL file.

        Args:
            input_path: Path to JSONL file
            force_rebuild: Force rebuild all documents

        Returns:
            Build statistics dict
        """
        stats = {
            "total": 0,
            "indexed": 0,
            "skipped": 0,
            "chunks_added": 0,
            "chunks_deleted": 0,
            "errors": [],
        }

        effective_force_rebuild = force_rebuild or self._force_rebuild_override

        # Process each document (streaming)
        for doc_dict in tqdm(self._load_jsonl(input_path), desc="Indexing"):
            stats["total"] += 1
            try:
                document = Document.from_dict(doc_dict)

                # Force rebuild: delete existing chunks first
                if effective_force_rebuild:
                    old_chunk_ids = self._docstore.get_chunk_ids(document.id)
                    if old_chunk_ids:
                        self._vectorstore.delete_chunks(old_chunk_ids)

                # Chunk document
                chunks = self._chunker.split(document)

                # Index with incremental logic
                result = self._incremental.index_document(document, chunks)

                # Update stats
                if result["status"] == "indexed":
                    stats["indexed"] += 1
                    stats["chunks_added"] += result["chunks_added"]
                    stats["chunks_deleted"] += result["chunks_deleted"]
                else:
                    stats["skipped"] += 1

            except Exception as e:
                stats["errors"].append({
                    "doc_id": doc_dict.get("id", "unknown"),
                    "error": str(e),
                })

        return stats

    def _load_jsonl(self, path: str) -> Iterator[dict]:
        """Load documents from JSONL file."""
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    yield json.loads(line)
