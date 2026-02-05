"""Pipeline configuration."""

from dataclasses import dataclass, field
from typing import Optional
import os
import re
import importlib


def _expand_env_var(value: str) -> str:
    """Expand environment variables in the form ${VAR:-default}.

    Args:
        value: String possibly containing ${VAR:-default}

    Returns:
        Expanded string with environment variable or default value
    """
    if not isinstance(value, str):
        return value

    # Match ${VAR:-default} or ${VAR-default}
    pattern = r'\$\{([^:}]+):-?([^}]*)\}'

    def replace_env(match):
        var_name = match.group(1)
        default_value = match.group(2)
        return os.environ.get(var_name, default_value)

    return re.sub(pattern, replace_env, value)


def _expand_env(value):
    """Recursively expand env vars in strings inside dicts/lists."""
    if isinstance(value, str):
        return _expand_env_var(value)
    if isinstance(value, dict):
        return {k: _expand_env(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_expand_env(v) for v in value]
    return value


@dataclass
class ChunkingConfig:
    """Chunking configuration."""

    max_section_chars: int = 2000
    chunk_size: int = 500
    chunk_overlap: int = 80


@dataclass
class Config:
    """Main configuration class."""

    chunking: ChunkingConfig = field(default_factory=ChunkingConfig)
    embedding_provider: str = "gemini"
    embedding_model: str = "BAAI/bge-m3"
    database_url: str = ""
    docs_dir: str = "docs"
    output_jsonl: str = "kb/data/cleaned/docs.jsonl"

    # Gemini API configuration
    gemini_api_key: str = ""
    vector_store_table_name: str = ""
    vector_store_batch_size: int = 32
    llm: dict = field(default_factory=dict)
    rag: dict = field(default_factory=dict)

    @classmethod
    def from_yaml(cls, path: str) -> "Config":
        """Load configuration from YAML file."""
        yaml = importlib.import_module("yaml")
        with open(path, "r") as f:
            data = yaml.safe_load(f) or {}
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        """Create config from dictionary."""
        data = _expand_env(data)

        chunking_data = data.get("chunking", {})
        chunking = ChunkingConfig(
            max_section_chars=chunking_data.get("max_section_chars", 2000),
            chunk_size=chunking_data.get("chunk_size", 500),
            chunk_overlap=chunking_data.get("chunk_overlap", 80),
        )

        embedding_data = data.get("embedding", {})
        storage_data = data.get("storage", {})
        gemini_data = data.get("gemini", {})
        vector_store_data = data.get("vector_store", {})
        llm_data = data.get("llm", {})
        rag_data = data.get("rag", {})

        # Expand environment variables in config values
        database_url = storage_data.get("database_url", "")
        if not database_url or "${" in str(database_url):
            database_url = os.environ.get("DATABASE_URL", "")

        gemini_api_key = gemini_data.get("api_key", "")
        if not gemini_api_key or "${" in str(gemini_api_key):
            gemini_api_key = os.environ.get("GEMINI_API_KEY", "")

        embedding_provider = embedding_data.get("provider", "gemini")
        if embedding_provider != "gemini":
            raise ValueError("Only Gemini embeddings are supported (provider must be 'gemini').")

        return cls(
            chunking=chunking,
            embedding_provider=embedding_provider,
            embedding_model=embedding_data.get("model", "models/embedding-001"),
            database_url=database_url,
            docs_dir=data.get("docs_dir", "docs"),
            output_jsonl=data.get("output_jsonl", "kb/data/cleaned/docs.jsonl"),
            gemini_api_key=gemini_api_key,
            vector_store_table_name=vector_store_data.get("table_name", ""),
            vector_store_batch_size=vector_store_data.get("batch_size", 32),
            llm=llm_data,
            rag=rag_data,
        )

    @classmethod
    def from_env(cls) -> "Config":
        """Load config from environment variables."""
        return cls(
            database_url=os.environ.get("DATABASE_URL", ""),
            embedding_provider="gemini",
            embedding_model=os.environ.get("EMBEDDING_MODEL", "models/embedding-001"),
            docs_dir=os.environ.get("DOCS_DIR", "docs"),
            output_jsonl=os.environ.get("OUTPUT_JSONL", "kb/data/cleaned/docs.jsonl"),
            gemini_api_key=os.environ.get("GEMINI_API_KEY", ""),
            vector_store_table_name=os.environ.get("VECTOR_TABLE_NAME", ""),
            vector_store_batch_size=int(os.environ.get("VECTOR_BATCH_SIZE", "32")),
        )
