"""Index building - simple functional approach."""

import json
from typing import Iterator
from tqdm import tqdm

from kb.domain.document import Document
from kb.pipeline.chunk import split_document
from kb.pipeline.config import Config
from kb.storage.docstore import DocStore
from kb.storage.vectorstore import VectorStore


def build_index(
    config: Config,
    input_jsonl: str,
    force_rebuild: bool = False,
) -> dict:
    """Build vector index from JSONL file.

    Args:
        config: Pipeline configuration
        input_jsonl: Path to JSONL file
        force_rebuild: Force rebuild all documents

    Returns:
        Statistics dict with indexing results
    """
    # Initialize storage
    docstore = DocStore(config.get_database_url())
    vectorstore = VectorStore(
        database_url=config.get_database_url(),
        embedding_model=config.embedding_model,
        gemini_api_key=config.gemini_api_key,
        table_name=config.vector_store_table_name,
        batch_size=config.vector_store_batch_size,
    )

    try:
        docstore.initialize()
        vectorstore.initialize()

        # Process documents
        stats = {
            "total": 0,
            "indexed": 0,
            "skipped": 0,
            "chunks_added": 0,
            "errors": [],
        }

        for doc_dict in tqdm(_load_jsonl(input_jsonl), desc="Indexing"):
            stats["total"] += 1
            try:
                document = Document.from_dict(doc_dict)

                # Check if already indexed
                existing_chunks = docstore.get_chunk_ids(document.id)
                if existing_chunks and not force_rebuild:
                    stats["skipped"] += 1
                    continue

                # Delete old chunks if rebuilding
                if force_rebuild and existing_chunks:
                    vectorstore.delete_chunks(existing_chunks)

                # Split document into chunks
                chunks = split_document(
                    document,
                    chunk_size=config.chunking.chunk_size,
                    chunk_overlap=config.chunking.chunk_overlap,
                    max_section_chars=config.chunking.max_section_chars,
                )

                # Add chunks to vector store
                if chunks:
                    vectorstore.add_chunks(chunks)
                    docstore.upsert_document(
                        doc_id=document.id,
                        path=document.path,
                        title=document.title,
                        checksum=document.checksum,
                        chunk_ids=[c.chunk_id for c in chunks],
                        version=document.version,
                    )
                    stats["indexed"] += 1
                    stats["chunks_added"] += len(chunks)

            except Exception as e:
                stats["errors"].append({
                    "doc_id": doc_dict.get("id", "unknown"),
                    "error": str(e),
                })

        return stats

    finally:
        docstore.close()
        vectorstore.close()


def _load_jsonl(path: str) -> Iterator[dict]:
    """Load documents from JSONL file."""
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)
