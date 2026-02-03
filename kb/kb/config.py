from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import json
import os

import yaml


@dataclass(frozen=True)
class IndexConfig:
    content_roots: list[str] = field(default_factory=lambda: ["docs"])
    file_extensions: list[str] = field(default_factory=lambda: [".md", ".mdx"])


@dataclass(frozen=True)
class ChunkingConfig:
    target_tokens: int = 500
    min_tokens: int = 350
    max_tokens: int = 800
    overlap_tokens: int = 80
    heading_levels: list[int] = field(default_factory=lambda: [1, 2, 3])
    max_codeblock_chars: int = 1500


@dataclass(frozen=True)
class EmbeddingConfig:
    enabled: bool = True
    provider: str = "sentence-transformers"
    model: str = "BAAI/bge-small-en-v1.5"


@dataclass(frozen=True)
class VectorStoreConfig:
    table_name: str = "kb_llama_nodes"
    embed_dim: int = 384


@dataclass(frozen=True)
class StorageConfig:
    database_url: str | None = None
    persist_dir: str = "kb_index/storage"


@dataclass(frozen=True)
class BM25Config:
    persist_dir: str = "kb_index/bm25"


@dataclass(frozen=True)
class OutputConfig:
    chunks_path: str = "kb_index/chunks.jsonl"
    manifest_path: str = "kb_index/manifest.json"


@dataclass(frozen=True)
class LLMConfig:
    provider: str = "openai"
    model: str = "gpt-4o-mini"
    api_key: str | None = None
    temperature: float = 0.0


@dataclass(frozen=True)
class RetrievalConfig:
    top_k: int = 10
    rrf_k: int = 60
    use_bm25: bool = True


@dataclass(frozen=True)
class APIConfig:
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list[str] = field(default_factory=lambda: ["*"])


@dataclass(frozen=True)
class AppConfig:
    index: IndexConfig = field(default_factory=IndexConfig)
    chunking: ChunkingConfig = field(default_factory=ChunkingConfig)
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    vector_store: VectorStoreConfig = field(default_factory=VectorStoreConfig)
    bm25: BM25Config = field(default_factory=BM25Config)
    output: OutputConfig = field(default_factory=OutputConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    retrieval: RetrievalConfig = field(default_factory=RetrievalConfig)
    api: APIConfig = field(default_factory=APIConfig)


def _coalesce(base: dict[str, Any], updates: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _coalesce(merged[key], value)
        else:
            merged[key] = value
    return merged


def _from_dict(data: dict[str, Any]) -> AppConfig:
    index_data = data.get("index", {})
    if not index_data:
        index_data = data.get("content", {})
    return AppConfig(
        index=IndexConfig(**index_data),
        chunking=ChunkingConfig(**data.get("chunking", {})),
        embedding=EmbeddingConfig(**data.get("embedding", {})),
        storage=StorageConfig(**data.get("storage", {})),
        vector_store=VectorStoreConfig(**data.get("vector_store", {})),
        bm25=BM25Config(**data.get("bm25", {})),
        output=OutputConfig(**data.get("output", {})),
        llm=LLMConfig(**data.get("llm", {})),
        retrieval=RetrievalConfig(**data.get("retrieval", {})),
        api=APIConfig(**data.get("api", {})),
    )


def load_config(path: str | Path | None) -> AppConfig:
    if path is None:
        return AppConfig()

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")

    raw = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".json"}:
        data = json.loads(raw)
    else:
        data = yaml.safe_load(raw) or {}

    if "content_roots" in data or "file_extensions" in data:
        index_data = data.get("index", {})
        if "content_roots" in data:
            index_data["content_roots"] = data["content_roots"]
        if "file_extensions" in data:
            index_data["file_extensions"] = data["file_extensions"]
        data["index"] = index_data

    defaults = AppConfig()
    default_dict = {
        "index": defaults.index.__dict__,
        "chunking": defaults.chunking.__dict__,
        "embedding": defaults.embedding.__dict__,
        "storage": defaults.storage.__dict__,
        "vector_store": defaults.vector_store.__dict__,
        "bm25": defaults.bm25.__dict__,
        "output": defaults.output.__dict__,
        "llm": defaults.llm.__dict__,
        "retrieval": defaults.retrieval.__dict__,
        "api": defaults.api.__dict__,
    }
    merged = _coalesce(default_dict, data)
    return _from_dict(merged)


def load_env_database_url(config: AppConfig) -> AppConfig:
    env_url = os.getenv("DATABASE_URL")
    if env_url and not config.storage.database_url:
        return AppConfig(
            index=config.index,
            chunking=config.chunking,
            embedding=config.embedding,
            storage=StorageConfig(database_url=env_url, persist_dir=config.storage.persist_dir),
            vector_store=config.vector_store,
            bm25=config.bm25,
            output=config.output,
            llm=config.llm,
            retrieval=config.retrieval,
            api=config.api,
        )
    return config


def resolve_path(value: str, base: Path | None = None) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    base = base or Path.cwd()
    return (base / path).resolve()
