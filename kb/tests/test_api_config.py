import sys
import types
import importlib.util
from pathlib import Path


def _load_dependencies_module(fake_config):
    # Stub package structure to avoid importing kb/__init__.py
    kb_pkg = types.ModuleType("kb")
    kb_pkg.__path__ = [str(Path(__file__).resolve().parents[1])]
    sys.modules["kb"] = kb_pkg

    sys.modules["kb.pipeline"] = types.ModuleType("kb.pipeline")
    sys.modules["kb.pipeline.config"] = types.SimpleNamespace(Config=fake_config)

    sys.modules["kb.storage"] = types.ModuleType("kb.storage")
    sys.modules["kb.storage.docstore"] = types.SimpleNamespace(DocStore=object)
    sys.modules["kb.storage.vectorstore"] = types.SimpleNamespace(VectorStore=object)

    sys.modules["fastapi"] = types.SimpleNamespace(Depends=lambda x: x)

    deps_path = Path(__file__).resolve().parents[1] / "api" / "dependencies.py"
    spec = importlib.util.spec_from_file_location(
        "kb_api_dependencies_local", deps_path
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_dependencies_use_config_from_yaml(tmp_path):
    class FakeConfig:
        called = False

        @classmethod
        def from_yaml(cls, path):
            cls.called = True
            return types.SimpleNamespace(
                database_url="postgresql://x",
                embedding_provider="gemini",
                embedding_model="models/text-embedding-004",
                gemini_api_key="key",
                vector_store_table_name="",
                vector_store_batch_size=32,
                rag={},
                llm={},
            )

    deps = _load_dependencies_module(FakeConfig)

    cfg = deps.get_config()

    assert FakeConfig.called is True
    assert cfg.database_url == "postgresql://x"
