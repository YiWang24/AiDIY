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

from kb.pipeline.pipeline import OfflineKBPipeline, run_full_pipeline  # noqa: E402
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
    config: Config, docs_dir: str, output_path: str, noise_filter: bool = False
) -> dict:
    """Stage 1: Clean MDX documents using JS tool."""
    print_header("Stage 1: Cleaning MDX documents")

    pipeline = OfflineKBPipeline(
        database_url="",  # Not needed for cleaning
        chunking_config=config.chunking,
    )

    stats = pipeline.clean_documents(
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

    pipeline = OfflineKBPipeline(config=config)

    stats = pipeline.build_index(
        input_jsonl=input_jsonl,
        force_rebuild=force_rebuild,
    )

    print(f"✓ Indexed: {stats['indexed']}/{stats['total']} documents")
    print(f"  Skipped: {stats['skipped']}")
    print(f"  Chunks added: {stats['chunks_added']}")
    print(f"  Chunks deleted: {stats['chunks_deleted']}")

    if stats["errors"]:
        print(f"  Errors: {len(stats['errors'])}")
        for err in stats["errors"][:5]:
            print(f"    - {err['doc_id']}: {err['error']}")

    return stats


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="KB Pipeline - Build knowledge base from MDX documents"
    )
    parser.add_argument(
        "--config",
        default=None,
        help=f"Path to config YAML file (default: {get_default_config_path()})",
    )
    parser.add_argument(
        "--stage",
        choices=["clean", "build", "all"],
        default="all",
        help="Pipeline stage to run (default: all)",
    )
    parser.add_argument(
        "--docs-dir",
        default=None,
        help="Input docs directory (overrides config)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output JSONL path (overrides config)",
    )
    parser.add_argument(
        "--force-rebuild",
        action="store_true",
        help="Force full rebuild of index",
    )
    parser.add_argument(
        "--noise-filter",
        action="store_true",
        help="Enable noise filtering in stage 1",
    )

    args = parser.parse_args()

    print_header("KB Pipeline Build")

    # Load config
    config = load_config(args.config)

    # Override config with command-line arguments
    docs_dir = args.docs_dir or config.docs_dir
    output_jsonl = args.output or config.output_jsonl

    # Validate database URL for stage 2
    if args.stage in ["build", "all"] and not config.database_url:
        print("✗ Error: DATABASE_URL not set in config or environment")
        print("  Set database_url in config.yaml or DATABASE_URL env var")
        sys.exit(1)

    try:
        # Run requested stage(s)
        if args.stage == "clean":
            stage1_clean(config, docs_dir, output_jsonl, args.noise_filter)
        elif args.stage == "build":
            stage2_build(config, output_jsonl, args.force_rebuild)
        else:  # all
            overall_stats = run_full_pipeline(
                config=config,
                input_dir=docs_dir,
                output_jsonl=output_jsonl,
                force_rebuild=args.force_rebuild,
                noise_filter=args.noise_filter,
            )

            print_header("Pipeline Statistics")
            print("Stage 1 - Cleaning:")
            print(
                f"  Cleaned: {overall_stats['cleaning']['cleaned']}/{overall_stats['cleaning']['total']}"
            )
            print("\nStage 2 - Indexing:")
            print(
                f"  Indexed: {overall_stats['indexing']['indexed']}/{overall_stats['indexing']['total']}"
            )
            print(f"  Skipped: {overall_stats['indexing']['skipped']}")
            print(f"  Chunks added: {overall_stats['indexing']['chunks_added']}")

        print_header("✓ Pipeline Complete")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
