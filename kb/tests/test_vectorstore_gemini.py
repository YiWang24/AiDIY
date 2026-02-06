import sys
import types
import importlib.util
from pathlib import Path


def _load_vectorstore_module():
    sys.modules.setdefault("psycopg_pool", types.SimpleNamespace(ConnectionPool=object))
    vectorstore_path = (
        Path(__file__).resolve().parents[1] / "storage" / "vectorstore.py"
    )
    spec = importlib.util.spec_from_file_location(
        "kb_vectorstore_local", vectorstore_path
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_vectorstore_requires_gemini_key():
    module = _load_vectorstore_module()
    VectorStore = module.VectorStore

    try:
        vs = VectorStore(
            database_url="postgresql://x",
            embedding_model="models/embedding-001",
            gemini_api_key="",
        )
        vs.initialize()
    except ValueError as e:
        assert "gemini api key" in str(e).lower()
    else:
        assert False, "expected ValueError when gemini key missing"
