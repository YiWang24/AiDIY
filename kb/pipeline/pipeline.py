"""Complete offline KB pipeline - simple functional approach."""

from kb.pipeline.clean import clean_documents
from kb.pipeline.config import Config
from kb.pipeline.index import build_index


def run_full_pipeline(
    config: Config | None = None,
    input_dir: str = "",
    output_jsonl: str = "",
    database_url: str = "",
    force_rebuild: bool = False,
    embedding_model: str = "models/gemini-embedding-001",
    noise_filter: bool = False,
) -> dict:
    """Run complete pipeline from MDX to vector database.

    Args:
        config: Pipeline configuration (recommended)
        input_dir: Input directory with MDX files (overrides config)
        output_jsonl: Output JSONL path (overrides config)
        database_url: Database URL (overrides config)
        force_rebuild: Force rebuild all documents
        embedding_model: Embedding model name (overrides config)
        noise_filter: Enable noise filtering in stage 1

    Returns:
        Overall statistics dict with cleaning and indexing stats
    """
    # Use config or create from environment
    if config:
        pipeline_config = config
    else:
        from kb.pipeline.config import Config as ConfigClass
        pipeline_config = ConfigClass.from_env()

    # Override with explicit parameters if provided
    if database_url:
        pipeline_config.database_url = database_url
        # Clear postgres_* params so database_url takes precedence
        pipeline_config.postgres_host = ""
    if embedding_model:
        pipeline_config.embedding_model = embedding_model

    # Override paths if provided
    docs_dir = input_dir or pipeline_config.docs_dir
    output_path = output_jsonl or pipeline_config.output_jsonl

    overall_stats = {
        "cleaning": {},
        "indexing": {},
    }

    # Stage 1: Clean documents
    print("Stage 1: Cleaning MDX documents (using JS mdx-clean tool)...")
    cleaning_stats = clean_documents(
        input_dir=docs_dir,
        output_path=output_path,
        noise_filter=noise_filter,
    )
    overall_stats["cleaning"] = cleaning_stats

    print(f"Cleaned: {cleaning_stats['cleaned']}/{cleaning_stats['total']} documents")
    if cleaning_stats["errors"]:
        print(f"Errors: {len(cleaning_stats['errors'])}")

    # Stage 2: Build index
    print("\nStage 2: Building vector index...")
    indexing_stats = build_index(
        config=pipeline_config,
        input_jsonl=output_path,
        force_rebuild=force_rebuild,
    )
    overall_stats["indexing"] = indexing_stats

    print(f"Indexed: {indexing_stats['indexed']}/{indexing_stats['total']} documents")
    print(f"Skipped: {indexing_stats['skipped']}")
    print(f"Chunks added: {indexing_stats['chunks_added']}")

    if indexing_stats["errors"]:
        print(f"Errors: {len(indexing_stats['errors'])}")

    return overall_stats


