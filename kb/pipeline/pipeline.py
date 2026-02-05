"""Complete offline KB pipeline orchestrator."""

from tqdm import tqdm

from kb.domain.document import Document
from kb.pipeline.clean import clean_documents
from kb.pipeline.config import Config
from kb.pipeline.chunk import ChunkingConfig
from kb.pipeline.index import IndexBuilder


class OfflineKBPipeline:
    """Complete offline KB pipeline orchestrator."""

    def __init__(
        self,
        config: Config | None = None,
        database_url: str = "",
        embedding_model: str = "embedding-3",
        chunking_config: ChunkingConfig | None = None,
    ):
        """Initialize pipeline.

        Args:
            config: Full pipeline configuration (recommended)
            database_url: Database URL (used if config not provided)
            embedding_model: Embedding model name (used if config not provided)
            chunking_config: Chunking configuration (used if config not provided)
        """
        if config:
            self._config = config
        else:
            # Create config from individual parameters
            from kb.pipeline.config import Config as ConfigClass
            self._config = ConfigClass.from_env()
            if database_url:
                self._config.database_url = database_url
            if embedding_model:
                self._config.embedding_model = embedding_model
            if chunking_config:
                self._config.chunking = chunking_config

    def clean_documents(self, input_dir: str, output_path: str, noise_filter: bool = False) -> dict:
        """Clean MDX documents using JS tool."""
        return clean_documents(input_dir, output_path, noise_filter)

    def build_index(
        self,
        input_jsonl: str,
        force_rebuild: bool = False,
    ) -> dict:
        """Build vector index from JSONL file."""
        builder = IndexBuilder(config=self._config)

        try:
            builder.initialize()
            stats = builder.build_from_jsonl(input_jsonl, force_rebuild)
        finally:
            builder.close()

        return stats


def run_full_pipeline(
    config: Config | None = None,
    input_dir: str = "",
    output_jsonl: str = "",
    database_url: str = "",
    force_rebuild: bool = False,
    embedding_model: str = "embedding-3",
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
    overall_stats = {
        "cleaning": {},
        "indexing": {},
    }

    # Use config or create from parameters
    if config:
        pipeline_config = config
    else:
        from kb.pipeline.config import Config as ConfigClass
        pipeline_config = ConfigClass.from_env()
        if database_url:
            pipeline_config.database_url = database_url
        if embedding_model:
            pipeline_config.embedding_model = embedding_model

    # Override paths if provided
    docs_dir = input_dir or pipeline_config.docs_dir
    output_path = output_jsonl or pipeline_config.output_jsonl

    # Stage 1: Clean documents
    print("Stage 1: Cleaning MDX documents (using JS mdx-clean tool)...")
    pipeline = OfflineKBPipeline(config=pipeline_config)

    cleaning_stats = pipeline.clean_documents(
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
    indexing_stats = pipeline.build_index(
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
