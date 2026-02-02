from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from kb.config import AppConfig
from kb.utils import sha1_text, slugify


@dataclass(frozen=True)
class SimpleNode:
    node_id: str
    text: str
    metadata: dict


def build_nodes(paths: Sequence[Path], config: AppConfig, base_dir: Path | None = None) -> list[object]:
    base_dir = base_dir or Path.cwd()
    sorted_paths = sorted(paths, key=lambda p: str(p))
    try:
        return _build_nodes_llama(sorted_paths, config, base_dir)
    except ImportError:
        return _build_nodes_fallback(sorted_paths, config, base_dir)


def _build_nodes_llama(paths: Sequence[Path], config: AppConfig, base_dir: Path) -> list[object]:
    from llama_index.core.node_parser import MarkdownNodeParser, SentenceSplitter
    from llama_index.core.schema import TextNode
    try:
        from llama_index.readers.file import SimpleDirectoryReader, MarkdownReader
    except ImportError:  # pragma: no cover - depends on llama_index version
        from llama_index.core import SimpleDirectoryReader
        from llama_index.readers.file import MarkdownReader

    reader = SimpleDirectoryReader(
        input_files=[str(path) for path in paths],
        file_extractor={".md": MarkdownReader(), ".mdx": MarkdownReader()},
    )
    docs = reader.load_data()
    parser = MarkdownNodeParser()
    nodes = parser.get_nodes_from_documents(docs)
    splitter = SentenceSplitter(
        chunk_size=config.chunking.max_tokens,
        chunk_overlap=config.chunking.overlap_tokens,
    )

    final_nodes: list[TextNode] = []
    for node in nodes:
        chunks = splitter.split_text(node.get_content())
        for chunk_index, chunk_text in enumerate(chunks):
            metadata = dict(node.metadata or {})
            path = _resolve_path(metadata, base_dir)
            doc_id = _resolve_doc_id(metadata, path)
            heading_path = _resolve_heading_path(metadata)
            anchor = slugify(heading_path[-1]) if heading_path else None
            title = metadata.get("title") or metadata.get("file_name")
            content_hash = sha1_text(chunk_text)
            node_id = _build_node_id(doc_id, heading_path, chunk_index, content_hash)
            metadata.update(
                {
                    "doc_id": doc_id,
                    "path": path,
                    "title": title,
                    "heading_path": heading_path,
                    "anchor": anchor,
                    "chunk_index": chunk_index,
                    "content_hash": content_hash,
                }
            )
            text_node = TextNode(text=chunk_text, metadata=metadata)
            try:
                text_node.node_id = node_id
            except AttributeError:
                pass
            final_nodes.append(text_node)

    return _sort_nodes(final_nodes)


def _build_nodes_fallback(paths: Sequence[Path], config: AppConfig, base_dir: Path) -> list[SimpleNode]:
    nodes: list[SimpleNode] = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        if path.is_absolute():
            try:
                rel_path = str(path.relative_to(base_dir))
            except ValueError:
                rel_path = str(path)
        else:
            rel_path = str(path)
        doc_id = sha1_text(rel_path)
        content_hash = sha1_text(text)
        node_id = _build_node_id(doc_id, [], 0, content_hash)
        nodes.append(
            SimpleNode(
                node_id=node_id,
                text=text,
                metadata={
                    "doc_id": doc_id,
                    "path": rel_path,
                    "title": None,
                    "heading_path": [],
                    "anchor": None,
                    "chunk_index": 0,
                    "content_hash": content_hash,
                },
            )
        )
    return nodes


def _build_node_id(doc_id: str, heading_path: list[str], chunk_index: int, content_hash: str) -> str:
    heading = "|".join(heading_path)
    return sha1_text(f"{doc_id}:{heading}:{chunk_index}:{content_hash}")


def _resolve_path(metadata: dict, base_dir: Path) -> str:
    raw = metadata.get("file_path") or metadata.get("file_name") or ""
    try:
        path = Path(raw)
        if path.is_absolute():
            return str(path.relative_to(base_dir))
    except (TypeError, ValueError):
        return str(raw)
    return str(raw)


def _resolve_doc_id(metadata: dict, path: str) -> str:
    for key in ("doc_id", "id", "slug"):
        value = metadata.get(key)
        if value:
            return str(value).lstrip("/")
    return sha1_text(path or "")


def _resolve_heading_path(metadata: dict) -> list[str]:
    value = metadata.get("header_path") or metadata.get("heading_path")
    if isinstance(value, list):
        return [str(item) for item in value if item]
    if isinstance(value, str) and value.strip():
        return [part.strip() for part in value.split("/") if part.strip()]
    header = metadata.get("header")
    if header:
        return [str(header)]
    return []


def _sort_nodes(nodes: Iterable[object]) -> list[object]:
    def _key(node: object) -> tuple[str, str, int]:
        metadata = getattr(node, "metadata", {}) or {}
        path = metadata.get("path", "")
        heading = "|".join(metadata.get("heading_path", []) or [])
        chunk_index = int(metadata.get("chunk_index", 0) or 0)
        return (path, heading, chunk_index)

    return sorted(nodes, key=_key)
