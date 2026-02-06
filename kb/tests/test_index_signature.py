import sys
import types
import importlib.util
from pathlib import Path


def _load_config(fake_yaml):
    sys.modules["yaml"] = fake_yaml
    config_path = Path(__file__).resolve().parents[1] / "pipeline" / "config.py"
    spec = importlib.util.spec_from_file_location(
        "kb_pipeline_config_local", config_path
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.Config


def _load_signature_module():
    sig_path = Path(__file__).resolve().parents[1] / "pipeline" / "index_signature.py"
    spec = importlib.util.spec_from_file_location("kb_index_signature_local", sig_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_signature_changes_when_chunking_changes():
    fake_yaml = types.SimpleNamespace(safe_load=lambda _f: {})
    Config = _load_config(fake_yaml)

    cfg1 = Config.from_dict(
        {
            "embedding": {"provider": "gemini", "model": "models/text-embedding-004"},
            "chunking": {
                "chunk_size": 500,
                "chunk_overlap": 80,
                "max_section_chars": 2000,
            },
            "storage": {"database_url": "postgresql://x"},
        }
    )
    cfg2 = Config.from_dict(
        {
            "embedding": {"provider": "gemini", "model": "models/text-embedding-004"},
            "chunking": {
                "chunk_size": 700,
                "chunk_overlap": 80,
                "max_section_chars": 2000,
            },
            "storage": {"database_url": "postgresql://x"},
        }
    )

    sig_module = _load_signature_module()
    sig1 = sig_module.compute_signature(cfg1, embedding_dim=768)
    sig2 = sig_module.compute_signature(cfg2, embedding_dim=768)

    assert sig1 != sig2
