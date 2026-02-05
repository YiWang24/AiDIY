"""Incremental indexing with checksum comparison."""

from typing import List

from kb.domain.document import Document
from kb.domain.chunk import Chunk
from kb.storage.docstore import DocStore
from kb.storage.vectorstore import VectorStore


class IncrementalIndexer:
    """Incremental indexing with checksum-based change detection."""

    def __init__(self, docstore: DocStore, vectorstore: VectorStore):
        """Initialize incremental indexer."""
        self._docstore = docstore
        self._vectorstore = vectorstore

    def index_document(self, document: Document, chunks: List[Chunk]) -> dict:
        """Index a document with incremental logic."""
        existing_checksum = self._docstore.get_checksum(document.id)

        if existing_checksum == document.checksum:
            return {
                "doc_id": document.id,
                "status": "skipped",
                "chunks_added": 0,
                "chunks_deleted": 0,
            }

        old_chunk_ids = self._docstore.get_chunk_ids(document.id)
        if old_chunk_ids:
            self._vectorstore.delete_chunks(old_chunk_ids)

        if chunks:
            self._vectorstore.add_chunks(chunks)

        chunk_ids = [chunk.chunk_id for chunk in chunks]
        self._docstore.upsert_document(
            doc_id=document.id,
            path=document.path,
            title=document.title,
            checksum=document.checksum,
            chunk_ids=chunk_ids,
            version=document.version,
        )

        return {
            "doc_id": document.id,
            "status": "indexed",
            "chunks_added": len(chunks),
            "chunks_deleted": len(old_chunk_ids),
        }

    def delete_document(self, doc_id: str) -> None:
        """Delete a document from the index."""
        chunk_ids = self._docstore.get_chunk_ids(doc_id)
        if chunk_ids:
            self._vectorstore.delete_chunks(chunk_ids)
        self._docstore.delete_document(doc_id)
