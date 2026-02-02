from kb.config import load_config


def test_llamaindex_config_load(tmp_path):
    cfg = tmp_path / "cfg.yaml"
    cfg.write_text(
        """
index:
  content_roots: [docs]
vector_store:
  table_name: kb_llama_nodes
  embed_dim: 384
storage:
  persist_dir: kb_index/storage
""",
        encoding="utf-8",
    )
    config = load_config(cfg)
    assert config.vector_store.table_name == "kb_llama_nodes"
    assert config.storage.persist_dir == "kb_index/storage"
