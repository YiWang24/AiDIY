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


def test_parse_vector_dim_from_pgvector_format():
    module = _load_vectorstore_module()
    assert module._parse_vector_dim("vector(768)") == 768
    assert module._parse_vector_dim("vector(1024)") == 1024
