import sys
import types
import importlib.util
from pathlib import Path


def _load_config_with_yaml(fake_yaml):
    sys.modules["yaml"] = fake_yaml
    config_path = Path(__file__).resolve().parents[1] / "pipeline" / "config.py"
    spec = importlib.util.spec_from_file_location("kb_pipeline_config_local", config_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.Config


def test_config_from_dict_expands_env_vars(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@h:5432/db")
    monkeypatch.setenv("GEMINI_API_KEY", "gkey")

    fake_yaml = types.SimpleNamespace(safe_load=lambda _f: {})
    Config = _load_config_with_yaml(fake_yaml)

    data = {
        "storage": {"database_url": "${DATABASE_URL:-}"},
        "gemini": {"api_key": "${GEMINI_API_KEY:-}"},
        "embedding": {"provider": "gemini", "model": "models/embedding-001"},
    }

    cfg = Config.from_dict(data)

    assert cfg.database_url == "postgresql://u:p@h:5432/db"
    assert cfg.gemini_api_key == "gkey"
    assert cfg.embedding_provider == "gemini"


def test_config_from_yaml_uses_yaml_loader(tmp_path):
    fake_yaml = types.SimpleNamespace(safe_load=lambda _f: {
        "embedding": {"provider": "gemini", "model": "models/embedding-001"},
        "storage": {"database_url": "postgresql://x"},
    })
    Config = _load_config_with_yaml(fake_yaml)

    path = tmp_path / "config.yaml"
    path.write_text("fake: yaml")

    cfg = Config.from_yaml(str(path))
    assert cfg.embedding_provider == "gemini"
    assert cfg.database_url == "postgresql://x"


def test_config_rejects_non_gemini_provider():
    fake_yaml = types.SimpleNamespace(safe_load=lambda _f: {})
    Config = _load_config_with_yaml(fake_yaml)

    data = {
        "embedding": {"provider": "glm", "model": "embedding-3"},
        "storage": {"database_url": "postgresql://x"},
    }
    try:
        Config.from_dict(data)
    except ValueError as e:
        assert "gemini" in str(e).lower()
    else:
        assert False, "expected ValueError for non-gemini provider"
