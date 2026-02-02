from __future__ import annotations

from pathlib import Path

from kb.config import AppConfig
from kb.indexing.llama_pipeline import build_nodes


def build_index(config: AppConfig, base_dir: Path | None = None):
    base_dir = base_dir or Path.cwd()
    paths = []
    for root in config.index.content_roots:
        root_path = (base_dir / root).resolve()
        if not root_path.exists():
            continue
        for ext in config.index.file_extensions:
            paths.extend(sorted(root_path.rglob(f"*{ext}")))
    return build_nodes(paths, config, base_dir=base_dir)
