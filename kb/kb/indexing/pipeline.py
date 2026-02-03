from __future__ import annotations

from pathlib import Path

from kb.config import AppConfig
from kb.indexing.llama_pipeline import build_nodes
from kb.indexing.storage import create_storage_context


def build_index(config: AppConfig, base_dir: Path | None = None):
    """Build and persist a vector index from markdown files.

    Args:
        config: Application configuration
        base_dir: Base directory for content root resolution

    Returns:
        VectorStoreIndex: The built index
    """
    base_dir = base_dir or Path.cwd()

    # 1. Collect file paths
    paths = []
    for root in config.index.content_roots:
        root_path = (base_dir / root).resolve()
        if not root_path.exists():
            continue
        for ext in config.index.file_extensions:
            paths.extend(sorted(root_path.rglob(f"*{ext}")))

    # 2. Build nodes from documents
    nodes = build_nodes(paths, config, base_dir=base_dir)

    # 3. Create storage context with PGVectorStore
    storage_context = create_storage_context(config)

    # 4. Create embedding model
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding

    embed_model = HuggingFaceEmbedding(model_name=config.embedding.model)

    # 5. Build and persist index
    from llama_index.core import VectorStoreIndex

    index = VectorStoreIndex(
        nodes=nodes,
        storage_context=storage_context,
        embed_model=embed_model,
        show_progress=True,
    )

    # 6. Persist to disk
    persist_dir = Path(config.storage.persist_dir)
    persist_dir.mkdir(parents=True, exist_ok=True)
    storage_context.persist(persist_dir=str(persist_dir))

    return index
