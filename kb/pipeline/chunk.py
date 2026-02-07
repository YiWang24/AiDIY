"""Document chunking using langchain splitters."""

import hashlib
from typing import List

from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

from kb.domain.document import Document
from kb.domain.chunk import Chunk


def split_document(
    document: Document,
    chunk_size: int = 500,
    chunk_overlap: int = 80,
    max_section_chars: int = 2000,
) -> List[Chunk]:
    """Split document into chunks using langchain splitters.

    Uses MarkdownHeaderTextSplitter for structure-aware splitting,
    then RecursiveCharacterTextSplitter for large sections.

    Args:
        document: Document to split
        chunk_size: Target chunk size for recursive splitting
        chunk_overlap: Overlap between chunks
        max_section_chars: Max section size before recursive split

    Returns:
        List of chunks with stable IDs and metadata
    """
    if not document.content:
        return []

    # Initialize splitters (using langchain defaults)
    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
            ("####", "Header 4"),
        ]
    )

    recursive_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""],
    )

    # Split by markdown headers first
    sections = markdown_splitter.split_text(document.content)

    chunks = []
    chunk_index = 0

    for section in sections:
        # Extract heading path from langchain metadata
        heading_path = _extract_heading_path(section.metadata)
        section_text = section.page_content

        # Apply recursive splitting if section is too large
        if len(section_text) > max_section_chars:
            sub_chunks = recursive_splitter.split_text(section_text)
            for sub_chunk in sub_chunks:
                chunks.append(
                    _create_chunk(
                        document=document,
                        content=sub_chunk,
                        heading_path=heading_path,
                        chunk_index=chunk_index,
                    )
                )
                chunk_index += 1
        else:
            chunks.append(
                _create_chunk(
                    document=document,
                    content=section_text,
                    heading_path=heading_path,
                    chunk_index=chunk_index,
                )
            )
            chunk_index += 1

    return chunks


def _extract_heading_path(metadata: dict) -> List[str]:
    """Extract heading path from langchain section metadata."""
    heading_path = []
    for level in ["Header 1", "Header 2", "Header 3", "Header 4"]:
        if level in metadata and metadata[level]:
            heading_path.append(metadata[level])
    return heading_path


def _create_chunk(
    document: Document,
    content: str,
    heading_path: List[str],
    chunk_index: int,
) -> Chunk:
    """Create chunk with stable ID using content hash."""
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

