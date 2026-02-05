"""Pipeline configuration."""

from dataclasses import dataclass, field
from typing import Optional
import os
import re

import yaml


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
    embedding_model: str = "BAAI/bge-m3"
    database_url: str = ""
    docs_dir: str = "docs"
    output_jsonl: str = "kb/data/cleaned/docs.jsonl"

    # GLM API configuration
    glm_api_key: str = ""
    glm_api_base: str = "https://open.bigmodel.cn/api/paas/v4"

    # Gemini API configuration
    gemini_api_key: str = ""

    @classmethod
    def from_yaml(cls, path: str) -> "Config":
        """Load configuration from YAML file."""
        with open(path, "r") as f:
            data = yaml.safe_load(f) or {}
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        """Create config from dictionary."""
        chunking_data = data.get("chunking", {})
        chunking = ChunkingConfig(
            max_section_chars=chunking_data.get("max_section_chars", 2000),
            chunk_size=chunking_data.get("chunk_size", 500),
            chunk_overlap=chunking_data.get("chunk_overlap", 80),
        )

        embedding_data = data.get("embedding", {})
        storage_data = data.get("storage", {})
        glm_data = data.get("glm", {})
        gemini_data = data.get("gemini", {})

        # Expand environment variables in config values
        database_url = _expand_env_var(storage_data.get("database_url", ""))
        if not database_url or "${" in database_url:
            # Fallback to direct env var if expansion failed or not set
            database_url = os.environ.get("DATABASE_URL", "")

        glm_api_key = _expand_env_var(glm_data.get("api_key", ""))
        if not glm_api_key or "${" in glm_api_key:
            glm_api_key = os.environ.get("GLM_API_KEY", "")

        glm_api_base = _expand_env_var(glm_data.get("api_base", "https://open.bigmodel.cn/api/paas/v4"))

        gemini_api_key = _expand_env_var(gemini_data.get("api_key", ""))
        if not gemini_api_key or "${" in gemini_api_key:
            gemini_api_key = os.environ.get("GEMINI_API_KEY", "")

        return cls(
            chunking=chunking,
            embedding_model=embedding_data.get("model", "models/embedding-001"),
            database_url=database_url,
            docs_dir=data.get("docs_dir", "docs"),
            output_jsonl=data.get("output_jsonl", "kb/data/cleaned/docs.jsonl"),
            glm_api_key=glm_api_key,
            glm_api_base=glm_api_base,
            gemini_api_key=gemini_api_key,
        )

    @classmethod
    def from_env(cls) -> "Config":
        """Load config from environment variables."""
        return cls(
            database_url=os.environ.get("DATABASE_URL", ""),
            embedding_model=os.environ.get("EMBEDDING_MODEL", "models/embedding-001"),
            docs_dir=os.environ.get("DOCS_DIR", "docs"),
            output_jsonl=os.environ.get("OUTPUT_JSONL", "kb/data/cleaned/docs.jsonl"),
            glm_api_key=os.environ.get("GLM_API_KEY", ""),
            glm_api_base=os.environ.get("GLM_API_BASE", "https://open.bigmodel.cn/api/paas/v4"),
            gemini_api_key=os.environ.get("GEMINI_API_KEY", ""),
        )
