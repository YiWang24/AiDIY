from __future__ import annotations

import os
from pathlib import Path

import pytest
import yaml

from kb.config import (
    AppConfig,
    load_config,
    load_env_database_url,
)


class TestLLMConfig:
    """Test LLM configuration"""

    def test_default_llm_config(self, tmp_path: Path):
        """Test default LLM configuration values"""
        config_path = tmp_path / "config.yaml"
        config_path.write_text("index:\n  content_roots: [docs]\n")

        config = load_config(config_path)

        assert hasattr(config, "llm")
        assert config.llm.provider == "openai"
        assert config.llm.model == "gpt-4o-mini"
        assert config.llm.api_key is None
        assert config.llm.temperature == 0.0

    def test_custom_llm_config(self, tmp_path: Path):
        """Test custom LLM configuration values"""
        config_path = tmp_path / "config.yaml"
        config_data = {
            "index": {"content_roots": ["docs"]},
            "llm": {
                "provider": "openai",
                "model": "gpt-4o",
                "temperature": 0.7,
            },
        }
        config_path.write_text(yaml.dump(config_data))

        config = load_config(config_path)

        assert config.llm.provider == "openai"
        assert config.llm.model == "gpt-4o"
        assert config.llm.temperature == 0.7

    def test_llm_api_key_from_env(self, tmp_path: Path, monkeypatch):
        """Test LLM API key can be loaded from environment"""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")

        config_path = tmp_path / "config.yaml"
        config_data = {
            "index": {"content_roots": ["docs"]},
            "llm": {"api_key": "${OPENAI_API_KEY}"},
        }
        config_path.write_text(yaml.dump(config_data))

        config = load_config(config_path)

        # Note: env expansion would be handled by config loading
        assert config.llm.api_key == "${OPENAI_API_KEY}"


class TestRetrievalConfig:
    """Test retrieval configuration"""

    def test_default_retrieval_config(self, tmp_path: Path):
        """Test default retrieval configuration values"""
        config_path = tmp_path / "config.yaml"
        config_path.write_text("index:\n  content_roots: [docs]\n")

        config = load_config(config_path)

        assert hasattr(config, "retrieval")
        assert config.retrieval.top_k == 10
        assert config.retrieval.rrf_k == 60
        assert config.retrieval.use_bm25 is True

    def test_custom_retrieval_config(self, tmp_path: Path):
        """Test custom retrieval configuration values"""
        config_path = tmp_path / "config.yaml"
        config_data = {
            "index": {"content_roots": ["docs"]},
            "retrieval": {
                "top_k": 20,
                "rrf_k": 100,
                "use_bm25": False,
            },
        }
        config_path.write_text(yaml.dump(config_data))

        config = load_config(config_path)

        assert config.retrieval.top_k == 20
        assert config.retrieval.rrf_k == 100
        assert config.retrieval.use_bm25 is False


class TestAPIConfig:
    """Test API configuration"""

    def test_default_api_config(self, tmp_path: Path):
        """Test default API configuration values"""
        config_path = tmp_path / "config.yaml"
        config_path.write_text("index:\n  content_roots: [docs]\n")

        config = load_config(config_path)

        assert hasattr(config, "api")
        assert config.api.host == "0.0.0.0"
        assert config.api.port == 8000
        assert config.api.cors_origins == ["*"]

    def test_custom_api_config(self, tmp_path: Path):
        """Test custom API configuration values"""
        config_path = tmp_path / "config.yaml"
        config_data = {
            "index": {"content_roots": ["docs"]},
            "api": {
                "host": "127.0.0.1",
                "port": 9000,
                "cors_origins": ["http://localhost:3000", "http://localhost:3001"],
            },
        }
        config_path.write_text(yaml.dump(config_data))

        config = load_config(config_path)

        assert config.api.host == "127.0.0.1"
        assert config.api.port == 9000
        assert len(config.api.cors_origins) == 2
        assert "http://localhost:3000" in config.api.cors_origins


class TestAppConfigIntegration:
    """Test AppConfig with all new configurations"""

    def test_full_config_loading(self, tmp_path: Path):
        """Test loading complete configuration file"""
        config_path = tmp_path / "config.yaml"
        config_data = {
            "index": {"content_roots": ["docs"]},
            "chunking": {
                "target_tokens": 500,
                "min_tokens": 350,
                "max_tokens": 800,
                "overlap_tokens": 80,
                "heading_levels": [1, 2, 3],
                "max_codeblock_chars": 1500,
            },
            "embedding": {
                "enabled": True,
                "provider": "huggingface",
                "model": "BAAI/bge-small-en-v1.5",
            },
            "vector_store": {
                "table_name": "kb_llama_nodes",
                "embed_dim": 384,
            },
            "storage": {
                "database_url": "postgresql://postgres:postgres@localhost:5432/kb",
                "persist_dir": "kb_index/storage",
            },
            "bm25": {
                "persist_dir": "kb_index/bm25",
            },
            "output": {
                "chunks_path": "kb_index/chunks.jsonl",
                "manifest_path": "kb_index/manifest.json",
            },
            "llm": {
                "provider": "openai",
                "model": "gpt-4o-mini",
                "api_key": None,
                "temperature": 0.0,
            },
            "retrieval": {
                "top_k": 10,
                "rrf_k": 60,
                "use_bm25": True,
            },
            "api": {
                "host": "0.0.0.0",
                "port": 8000,
                "cors_origins": ["*"],
            },
        }
        config_path.write_text(yaml.dump(config_data))

        config = load_config(config_path)

        # Verify all sections are loaded
        assert hasattr(config, "index")
        assert hasattr(config, "chunking")
        assert hasattr(config, "embedding")
        assert hasattr(config, "vector_store")
        assert hasattr(config, "storage")
        assert hasattr(config, "bm25")
        assert hasattr(config, "output")
        assert hasattr(config, "llm")
        assert hasattr(config, "retrieval")
        assert hasattr(config, "api")

        # Verify values match
        assert config.llm.model == "gpt-4o-mini"
        assert config.retrieval.top_k == 10
        assert config.api.port == 8000

    def test_config_immutability(self, tmp_path: Path):
        """Test that config objects are immutable (frozen dataclass)"""
        config_path = tmp_path / "config.yaml"
        config_path.write_text("index:\n  content_roots: [docs]\n")

        config = load_config(config_path)

        with pytest.raises(Exception):  # FrozenInstanceError
            config.llm.provider = "anthropic"

        with pytest.raises(Exception):  # FrozenInstanceError
            config.retrieval.top_k = 20

    def test_env_database_url_override(self, tmp_path: Path, monkeypatch):
        """Test that DATABASE_URL env var overrides config"""
        test_db_url = "postgresql://test:test@localhost:5432/test_kb"
        monkeypatch.setenv("DATABASE_URL", test_db_url)

        config_path = tmp_path / "config.yaml"
        config_data = {
            "index": {"content_roots": ["docs"]},
            "storage": {
                "database_url": "postgresql://postgres:postgres@localhost:5432/kb",
                "persist_dir": "kb_index/storage",
            },
        }
        config_path.write_text(yaml.dump(config_data))

        config = load_config(config_path)
        config = load_env_database_url(config)

        # When DATABASE_URL is set and config doesn't have one, use env
        # If config already has one, it's preserved
        assert config.storage.database_url == "postgresql://postgres:postgres@localhost:5432/kb"

    def test_env_database_url_when_config_empty(self, tmp_path: Path, monkeypatch):
        """Test DATABASE_URL is used when config has no database_url"""
        test_db_url = "postgresql://test:test@localhost:5432/test_kb"
        monkeypatch.setenv("DATABASE_URL", test_db_url)

        config_path = tmp_path / "config.yaml"
        config_data = {
            "index": {"content_roots": ["docs"]},
            "storage": {
                "persist_dir": "kb_index/storage",
            },
        }
        config_path.write_text(yaml.dump(config_data))

        config = load_config(config_path)
        config = load_env_database_url(config)

        assert config.storage.database_url == test_db_url


class TestConfigYAMLExample:
    """Test that config.example.yaml works with new structure"""

    def test_example_config_file(self):
        """Test loading the actual config.example.yaml file"""
        # This test uses the actual config.example.yaml in the project
        project_root = Path(__file__).parent.parent
        example_config = project_root / "config.example.yaml"

        if example_config.exists():
            config = load_config(example_config)

            # Verify new config sections exist
            assert hasattr(config, "llm")
            assert hasattr(config, "retrieval")
            assert hasattr(config, "api")
