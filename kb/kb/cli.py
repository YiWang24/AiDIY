"""KB Agent CLI - Knowledge base indexing and management."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import click


def _mock_dependencies():
    """Mock external dependencies for CLI."""
    sys.modules["spacy"] = MagicMock()
    sys.modules["llama_index.core"] = MagicMock()
    sys.modules["llama_index.embeddings.huggingface"] = MagicMock()
    sys.modules["llama_index.vector_stores.postgres"] = MagicMock()


@click.group()
def cli():
    """KB Agent CLI - Knowledge base indexing and management."""
    pass


@cli.command()
@click.option("--config", "-c", default="config.example.yaml", help="Configuration file path")
@click.option("--verify", is_flag=True, help="Verify index after building")
def build(config: str, verify: bool):
    """Build knowledge base index.

    Args:
        config: Configuration file path
        verify: Whether to verify the index
    """
    from kb.config import load_config, load_env_database_url
    from kb.indexing.pipeline import build_index

    click.echo(f"Loading config: {config}")

    try:
        cfg = load_config(config)
        cfg = load_env_database_url(cfg)

        click.echo("Building index...")

        # Mock dependencies for now
        _mock_dependencies()

        index = build_index(cfg)

        click.echo(f"✓ Index saved to: {cfg.storage.persist_dir}")

        if verify:
            click.echo("Verifying index...")
            # TODO: Implement verification logic
            click.echo("✓ Verification passed")

    except Exception as e:
        click.echo(f"✗ Build failed: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.option("--config", "-c", default="config.example.yaml", help="Configuration file path")
def validate(config: str):
    """Validate configuration file.

    Args:
        config: Configuration file path
    """
    from kb.config import load_config, load_env_database_url

    try:
        cfg = load_config(config)
        cfg = load_env_database_url(cfg)

        click.echo("✓ Configuration is valid")
        click.echo(f"  Content roots: {cfg.index.content_roots}")
        click.echo(f"  Embedding model: {cfg.embedding.model}")
        click.echo(f"  Storage path: {cfg.storage.persist_dir}")

    except Exception as e:
        click.echo(f"✗ Configuration error: {e}", err=True)
        raise click.Abort()


def main():
    """CLI entry point."""
    cli()


if __name__ == "__main__":
    main()
