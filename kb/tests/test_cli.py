"""Tests for CLI commands."""

from __future__ import annotations

from unittest.mock import MagicMock, patch
from click.testing import CliRunner

import pytest


class TestValidateCommand:
    """Test CLI validate command."""

    def test_validate_valid_config(self, tmp_path):
        """Test validate with valid configuration."""
        from kb.cli import cli

        # Create a valid config file
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text("""
index:
  content_roots:
    - tests/fixtures/content
  file_extensions:
    - .md
    - .mdx

chunking:
  target_tokens: 500
  min_tokens: 350
  max_tokens: 800
  overlap_tokens: 80
  heading_levels: [1, 2, 3]
  max_codeblock_chars: 1500

embedding:
  enabled: true
  provider: huggingface
  model: BAAI/bge-small-en-v1.5

vector_store:
  table_name: kb_llama_nodes
  embed_dim: 384

storage:
  database_url: null
  persist_dir: storage_test

bm25:
  persist_dir: kb_index/bm25

output:
  chunks_path: kb_index/chunks.jsonl
  manifest_path: kb_index/manifest.json

llm:
  provider: openai
  model: gpt-4o-mini
  api_key: null
  temperature: 0.0

retrieval:
  top_k: 10
  rrf_k: 60
  use_bm25: true

api:
  host: 0.0.0.0
  port: 8000
  cors_origins:
    - "*"
""")

        runner = CliRunner()
        result = runner.invoke(cli, ['validate', '-c', str(config_file)])

        assert result.exit_code == 0
        assert '✓' in result.output or 'valid' in result.output.lower()

    def test_validate_invalid_config(self, tmp_path):
        """Test validate with invalid configuration."""
        from kb.cli import cli

        # Create an invalid config file (malformed YAML)
        config_file = tmp_path / "invalid_config.yaml"
        config_file.write_text("""
index:
  content_roots:
    - docs
  invalid_key: [unclosed list
""")

        runner = CliRunner()
        result = runner.invoke(cli, ['validate', '-c', str(config_file)])

        # Should fail due to malformed YAML
        assert result.exit_code != 0


class TestBuildCommand:
    """Test CLI build command."""

    def test_build_with_mock_pipeline(self, tmp_path):
        """Test build command with mocked pipeline."""
        from kb.cli import cli

        # Create a valid config file
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text("""
index:
  content_roots:
    - tests/fixtures/content
  file_extensions:
    - .md
    - .mdx

chunking:
  target_tokens: 500
  min_tokens: 350
  max_tokens: 800
  overlap_tokens: 80
  heading_levels: [1, 2, 3]
  max_codeblock_chars: 1500

embedding:
  enabled: true
  provider: huggingface
  model: BAAI/bge-small-en-v1.5

vector_store:
  table_name: kb_llama_nodes
  embed_dim: 384

storage:
  database_url: null
  persist_dir: storage_test

bm25:
  persist_dir: kb_index/bm25

output:
  chunks_path: kb_index/chunks.jsonl
  manifest_path: kb_index/manifest.json

llm:
  provider: openai
  model: gpt-4o-mini
  api_key: null
  temperature: 0.0

retrieval:
  top_k: 10
  rrf_k: 60
  use_bm25: true

api:
  host: 0.0.0.0
  port: 8000
  cors_origins:
    - "*"
""")

        # Mock the build_index function
        with patch('kb.indexing.pipeline.build_index') as mock_build:
            mock_index = MagicMock()
            mock_build.return_value = mock_index

            runner = CliRunner()
            result = runner.invoke(cli, ['build', '-c', str(config_file)])

            # Verify command succeeded
            assert result.exit_code == 0

            # Verify build_index was called
            mock_build.assert_called_once()

            # Verify output contains expected messages
            assert 'Building index' in result.output or 'building' in result.output.lower()

    def test_build_with_verify(self, tmp_path):
        """Test build command with verify flag."""
        from kb.cli import cli

        config_file = tmp_path / "test_config.yaml"
        config_file.write_text("""
index:
  content_roots: []
  file_extensions:
    - .md

chunking:
  target_tokens: 500
  min_tokens: 350
  max_tokens: 800
  overlap_tokens: 80
  heading_levels: [1, 2, 3]
  max_codeblock_chars: 1500

embedding:
  enabled: true
  provider: huggingface
  model: BAAI/bge-small-en-v1.5

vector_store:
  table_name: test
  embed_dim: 384

storage:
  database_url: null
  persist_dir: storage_test

bm25:
  persist_dir: kb_index/bm25

output:
  chunks_path: kb_index/chunks.jsonl
  manifest_path: kb_index/manifest.json

llm:
  provider: openai
  model: gpt-4o-mini
  api_key: null
  temperature: 0.0

retrieval:
  top_k: 10
  rrf_k: 60
  use_bm25: true

api:
  host: 0.0.0.0
  port: 8000
  cors_origins:
    - "*"
""")

        with patch('kb.indexing.pipeline.build_index'):
            runner = CliRunner()
            result = runner.invoke(cli, ['build', '-c', str(config_file), '--verify'])

            # Check that verify message was printed
            assert 'verifying' in result.output.lower() or 'verify' in result.output.lower()


class TestCLI:
    """Test CLI group."""

    def test_cli_group_exists(self):
        """Test that CLI group is created."""
        from kb.cli import cli

        assert cli is not None
        assert cli.name == "cli"

    def test_cli_has_commands(self):
        """Test that CLI has expected commands."""
        from kb.cli import cli

        commands = list(cli.commands.keys())
        assert "build" in commands
        assert "validate" in commands
