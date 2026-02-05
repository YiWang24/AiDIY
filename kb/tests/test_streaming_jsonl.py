import sys
import types
import importlib.util
from pathlib import Path


def _load_config_module():
    sys.modules["yaml"] = types.SimpleNamespace(safe_load=lambda _f: {})
    config_path = Path(__file__).resolve().parents[1] / "pipeline" / "config.py"
    spec = importlib.util.spec_from_file_location("kb_pipeline_config_local", config_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _load_document_module():
    doc_path = Path(__file__).resolve().parents[1] / "domain" / "document.py"
    spec = importlib.util.spec_from_file_location("kb_domain_document_local", doc_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _load_index_module(config_module, document_module):
    kb_pkg = types.ModuleType("kb")
    kb_pkg.__path__ = [str(Path(__file__).resolve().parents[1])]
    sys.modules["kb"] = kb_pkg

    sys.modules["kb.domain"] = types.ModuleType("kb.domain")
    sys.modules["kb.domain.document"] = document_module

    class DummyChunkingConfig:
        def __init__(self, max_section_chars=2000, chunk_size=500, chunk_overlap=80):
            self.max_section_chars = max_section_chars
            self.chunk_size = chunk_size
            self.chunk_overlap = chunk_overlap

    class DummyChunker:
        def __init__(self, *_args, **_kwargs):
            pass

        def split(self, _document):
            return []

    sys.modules["kb.pipeline"] = types.ModuleType("kb.pipeline")
    sys.modules["kb.pipeline.config"] = config_module
    sys.modules["kb.pipeline.chunk"] = types.SimpleNamespace(
        ChunkingStrategy=DummyChunker,
        ChunkingConfig=DummyChunkingConfig,
    )

    class DummyDocStore:
        def __init__(self, *_args, **_kwargs):
            pass

        def initialize(self):
            pass

        def close(self):
            pass

    class DummyVectorStore:
        def __init__(self, *_args, **_kwargs):
            pass

        def initialize(self):
            pass

        def close(self):
            pass

    class DummyIncremental:
        def __init__(self, *_args, **_kwargs):
            pass

        def index_document(self, *_args, **_kwargs):
            return {"status": "indexed", "chunks_added": 0, "chunks_deleted": 0}

    sys.modules["kb.storage"] = types.ModuleType("kb.storage")
    sys.modules["kb.storage.docstore"] = types.SimpleNamespace(DocStore=DummyDocStore)
    sys.modules["kb.storage.vectorstore"] = types.SimpleNamespace(VectorStore=DummyVectorStore)
    sys.modules["kb.pipeline.incremental"] = types.SimpleNamespace(IncrementalIndexer=DummyIncremental)

    index_path = Path(__file__).resolve().parents[1] / "pipeline" / "index.py"
    spec = importlib.util.spec_from_file_location("kb_pipeline_index_local", index_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_build_from_jsonl_counts_without_preloading(tmp_path):
    config_module = _load_config_module()
    document_module = _load_document_module()
    index_module = _load_index_module(config_module, document_module)

    jsonl_path = tmp_path / "docs.jsonl"
    jsonl_path.write_text('{"id":"a","path":"a","title":"a","checksum":"x","content":"c"}\n')

    cfg = config_module.Config.from_dict({
        "embedding": {"provider": "gemini", "model": "models/embedding-001"},
        "storage": {"database_url": "postgresql://x"},
    })

    builder = index_module.IndexBuilder(config=cfg)

    def _forbid_list(*_args, **_kwargs):
        raise AssertionError("list() should not be used for JSONL loading")

    index_module.list = _forbid_list

    stats = builder.build_from_jsonl(str(jsonl_path))
    assert stats["total"] == 1
