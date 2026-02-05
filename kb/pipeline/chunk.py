"""Document chunking strategy."""

import hashlib
from typing import List
from dataclasses import dataclass, field

from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

from kb.domain.document import Document
from kb.domain.chunk import Chunk


@dataclass
class ChunkingConfig:
    """Configuration for chunking strategy."""

    max_section_chars: int = 2000
    chunk_size: int = 500
    chunk_overlap: int = 80


class ChunkingStrategy:
    """Structure-first chunking using MarkdownHeaderTextSplitter."""

    def __init__(self, config: ChunkingConfig | None = None):
        """Initialize chunking strategy."""
        self._config = config or ChunkingConfig()

        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
            ("####", "Header 4"),
        ]
        self._markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on,
        )

        self._recursive_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self._config.chunk_size,
            chunk_overlap=self._config.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""],
        )

    def split(self, document: Document) -> List[Chunk]:
        """Split a document into chunks."""
        if not document.content:
            return []

        sections = self._markdown_splitter.split_text(document.content)
        chunks = []
        chunk_index = 0

        for section in sections:
            heading_path = self._extract_heading_path(section.metadata)
            section_text = section.page_content

            if len(section_text) > self._config.max_section_chars:
                sub_chunks = self._recursive_splitter.split_text(section_text)
                for sub_chunk in sub_chunks:
                    chunks.append(self._create_chunk(
                        document, sub_chunk, heading_path, chunk_index
                    ))
                    chunk_index += 1
            else:
                chunks.append(self._create_chunk(
                    document, section_text, heading_path, chunk_index
                ))
                chunk_index += 1

        return chunks

    def _extract_heading_path(self, metadata: dict) -> List[str]:
        """Extract heading path from section metadata."""
        heading_path = []
        for level in ["Header 1", "Header 2", "Header 3", "Header 4"]:
            if level in metadata and metadata[level]:
                heading_path.append(metadata[level])
        return heading_path

    def _create_chunk(
        self, document: Document, content: str,
        heading_path: List[str], chunk_index: int
    ) -> Chunk:
        """Create a chunk with stable ID."""
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        chunk_id_input = (
            f"{document.id}:{document.version}:"
            f"{':'.join(heading_path)}:{chunk_index}:{content_hash}"
        )
        chunk_id = hashlib.sha256(chunk_id_input.encode()).hexdigest()

        return Chunk(
            chunk_id=chunk_id,
            doc_id=document.id,
            content=content,
            heading_path=heading_path,
            chunk_index=chunk_index,
        )
