from kb.indexing.llama_pipeline import build_nodes
from kb.config import AppConfig


def test_deterministic_node_ids(tmp_path):
    doc = tmp_path / "sample.md"
    doc.write_text("# Title\n\nHello world.", encoding="utf-8")
    cfg = AppConfig()
    nodes_a = build_nodes([doc], cfg)
    nodes_b = build_nodes([doc], cfg)
    assert [n.node_id for n in nodes_a] == [n.node_id for n in nodes_b]
