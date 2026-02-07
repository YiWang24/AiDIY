#!/usr/bin/env python3
"""
KB Pipeline - Build knowledge base from MDX documents.

Usage:
    kb-build                        # Run all stages (uses kb/config.yaml)
    kb-build --stage clean          # Run stage 1 only (clean MDX)
    kb-build --stage build          # Run stage 2 only (build index)
    kb-build --force-rebuild        # Force full rebuild of index
    kb-build --config custom.yaml   # Use custom config file

Configuration:
    Config file: kb/config.yaml (default)
    Environment variables are used as fallback if config file not found
    Set DATABASE_URL and GLM_API_KEY environment variables for production
"""

import argparse
import os
import sys
from pathlib import Path

# Add project root to Python path (kb -> project root)
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from kb.pipeline.pipeline import run_full_pipeline, build_index  # noqa: E402
from kb.pipeline.clean import clean_documents  # noqa: E402
from kb.pipeline.config import Config  # noqa: E402


def get_default_config_path() -> str:
    """Get default config path relative to project root."""
    return str(PROJECT_ROOT / "kb" / "config.yaml")


def load_config(config_path: str | None = None) -> Config:
    """Load config from YAML file or environment variables.

    Args:
        config_path: Path to YAML config file. If None, uses default path.

    Returns:
        Config object
    """
    if config_path is None:
        config_path = get_default_config_path()

    # Try YAML config first
    if os.path.exists(config_path):
        print(f"Loading config from: {config_path}")
        return Config.from_yaml(config_path)

    # Fallback to environment variables
    print(f"Config file not found: {config_path}")
    print("Loading from environment variables...")
    return Config.from_env()


def print_header(text: str):
    """Print section header."""
    print(f"\n{'=' * 50}\n{text}\n{'=' * 50}\n")


def stage1_clean(
    docs_dir: str, output_path: str, noise_filter: bool = False
) -> dict:
    """Stage 1: Clean MDX documents using JS tool."""
    print_header("Stage 1: Cleaning MDX documents")

    stats = clean_documents(
        input_dir=docs_dir,
        output_path=output_path,
        noise_filter=noise_filter,
    )

    print(f"✓ Cleaned: {stats['cleaned']}/{stats['total']} documents")
    if stats["errors"]:
        print(f"  Errors: {len(stats['errors'])}")

    return stats


def stage2_build(
    config: Config,
    input_jsonl: str,
    force_rebuild: bool = False,
) -> dict:
    """Stage 2: Build vector index from JSONL."""
    print_header("Stage 2: Building vector index")

    if not os.path.exists(input_jsonl):
        print(f"✗ Error: Cleaned documents not found: {input_jsonl}")
        print("  Run stage 1 first with --stage clean")
        sys.exit(1)

    stats = build_index(
        config=config,
        input_jsonl=input_jsonl,
        force_rebuild=force_rebuild,
    )

    print(f"✓ Indexed: {stats['indexed']}/{stats['total']} documents")
    print(f"  Skipped: {stats['skipped']}")
    print(f"  Chunks added: {stats['chunks_added']}")

    if stats["errors"]:
        print(f"  Errors: {len(stats['errors'])}")

    return stats


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="KB Pipeline - Build knowledge base from MDX documents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--stage",
        choices=["clean", "build"],
        help="Run specific stage only (clean or build)",
    )
    parser.add_argument(
        "--config",
        help="Path to config YAML file (default: kb/config.yaml)",
    )
    parser.add_argument(
        "--force-rebuild",
        action="store_true",
        help="Force rebuild all documents (ignore existing checksums)",
    )
    parser.add_argument(
        "--noise-filter",
        action="store_true",
        help="Enable noise filtering in stage 1 (remove navigation text)",
    )

    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)

    # Determine paths
    docs_dir = str(PROJECT_ROOT / config.docs_dir)
    output_jsonl = str(PROJECT_ROOT / config.output_jsonl)

    # Run pipeline
    if args.stage == "clean":
        stage1_clean(docs_dir, output_jsonl, args.noise_filter)

    elif args.stage == "build":
        stage2_build(config, output_jsonl, args.force_rebuild)

    else:
        # Run full pipeline
        print_header("KB Pipeline - Full Run")

        stats = run_full_pipeline(
            config=config,
            input_dir=docs_dir,
            output_jsonl=output_jsonl,
            force_rebuild=args.force_rebuild,
            noise_filter=args.noise_filter,
        )

        print_header("Pipeline Complete")
        print(f"Cleaning: {stats['cleaning']['cleaned']}/{stats['cleaning']['total']}")
        print(f"Indexing: {stats['indexing']['indexed']}/{stats['indexing']['total']}")
        print(f"Chunks added: {stats['indexing']['chunks_added']}")


if __name__ == "__main__":
    main()
