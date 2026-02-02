# KB Agent LlamaIndex + LangChain Rewrite Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 用 LlamaIndex 重写文档索引/检索，用 LangChain 负责轻量 Agent 决策，同时保留现有 `/search` `/ask` `/doc` API 与严格引用对齐。
**Architecture:** 离线索引由 LlamaIndex Reader→NodeParser→Embedding→PGVectorStore 完成；在线查询用 LlamaIndex Retriever 做混合召回，LangChain 负责工具调用与回答生成，引用对齐仍用自有规则。
**Tech Stack:** Python 3.11, LlamaIndex, LangChain, FastAPI, Postgres + pgvector, HuggingFace Embeddings, (可选) OpenAI LLM.

---

## Public API / Interface Changes

- **Config**：新增 LlamaIndex 相关配置
  - `storage.persist_dir`（索引持久化路径）
  - `vector_store.table_name` / `vector_store.embed_dim`
  - `bm25.persist_dir`（可选，持久化节点语料）
- **Env**：
  - `KB_CONFIG`（配置文件路径）
  - `OPENAI_API_KEY` / `KB_LLM_MODEL`（可选 LLM）
- **DB**：新增 LlamaIndex PGVectorStore 表结构（自定义 `table_name`）
- **Behavior**：/ask 回答由 LangChain Agent 输出；引用对齐仍严格。

---

## Task 0: Worktree + Plan File (准备阶段)
**Files:**
- Create: `docs/plans/2026-02-02-kb-llamaindex-langchain.md`

**Step 1: Create worktree**
Run: `git worktree add .worktrees/kb-llamaindex -b codex/kb-llamaindex`

**Step 2: Create plan file**
Write this plan into `docs/plans/2026-02-02-kb-llamaindex-langchain.md`

**Step 3: Commit plan**
Run:
```bash
git add docs/plans/2026-02-02-kb-llamaindex-langchain.md
git commit -m "docs: add llamaindex+langchain rewrite plan"
```

---

## Task 1: Dependencies & Config Schema
**Files:**
- Modify: `kb/pyproject.toml`
- Modify: `kb/config.example.yaml`
- Modify: `kb/kb/config.py`
- Test: `kb/tests/test_config.py`

**Step 1: Write failing config test**
Create `kb/tests/test_config.py`:
```python
from kb.config import load_config

def test_llamaindex_config_load(tmp_path):
    cfg = tmp_path / "cfg.yaml"
    cfg.write_text(
        """\nindex:\n  content_roots: [docs]\nvector_store:\n  table_name: kb_llama_nodes\n  embed_dim: 384\nstorage:\n  persist_dir: kb_index/storage\n""", 
        encoding="utf-8"
    )
    config = load_config(cfg)
    assert config.vector_store.table_name == "kb_llama_nodes"
    assert config.storage.persist_dir == "kb_index/storage"
```

**Step 2: Run test to confirm failure**
Run: `pytest kb/tests/test_config.py -v`
Expected: FAIL (attributes missing)

**Step 3: Implement config dataclasses**
Update `kb/kb/config.py` with new dataclasses:
```python
@dataclass(frozen=True)
class VectorStoreConfig:
    table_name: str = "kb_llama_nodes"
    embed_dim: int = 384

@dataclass(frozen=True)
class StorageConfig:
    database_url: str | None = None
    persist_dir: str = "kb_index/storage"

@dataclass(frozen=True)
class AppConfig:
    ...
    vector_store: VectorStoreConfig = field(default_factory=VectorStoreConfig)
```
Update `_from_dict` and `load_config` merging.

**Step 4: Run test to pass**
Run: `pytest kb/tests/test_config.py -v`
Expected: PASS

**Step 5: Commit**
```bash
git add kb/pyproject.toml kb/config.example.yaml kb/kb/config.py kb/tests/test_config.py
git commit -m "feat: add llamaindex config schema"
```

---

## Task 2: LlamaIndex Ingestion & Node Pipeline
**Files:**
- Create: `kb/kb/indexing/llama_pipeline.py`
- Modify: `kb/kb/indexing/pipeline.py`
- Modify: `kb/kb/indexing/parser.py` (if reused for slugify)
- Test: `kb/tests/test_llama_nodes.py`

**Step 1: Write failing deterministic ID test**
Create `kb/tests/test_llama_nodes.py`:
```python
from kb.indexing.llama_pipeline import build_nodes
from kb.config import AppConfig

def test_deterministic_node_ids(tmp_path):
    doc = tmp_path / "sample.md"
    doc.write_text("# Title\n\nHello world.", encoding="utf-8")
    cfg = AppConfig()
    nodes_a = build_nodes([doc], cfg)
    nodes_b = build_nodes([doc], cfg)
    assert [n.node_id for n in nodes_a] == [n.node_id for n in nodes_b]
```

**Step 2: Run test to confirm failure**
Run: `pytest kb/tests/test_llama_nodes.py -v`
Expected: FAIL (missing build_nodes)

**Step 3: Implement LlamaIndex pipeline**
Create `kb/kb/indexing/llama_pipeline.py`:
```python
from llama_index.readers.file import SimpleDirectoryReader, MarkdownReader
from llama_index.core.node_parser import MarkdownNodeParser, SentenceSplitter
from llama_index.core.schema import TextNode
from kb.utils import slugify, sha1_text

def build_nodes(paths, config):
    reader = SimpleDirectoryReader(
        input_files=sorted([str(p) for p in paths]),
        file_extractor={".md": MarkdownReader(), ".mdx": MarkdownReader()},
    )
    docs = reader.load_data()
    parser = MarkdownNodeParser()
    nodes = parser.get_nodes_from_documents(docs)
    splitter = SentenceSplitter(chunk_size=config.chunking.max_tokens, chunk_overlap=config.chunking.overlap_tokens)

    final_nodes = []
    for doc in docs:
        doc_id = doc.metadata.get("doc_id") or sha1_text(doc.metadata.get("file_path", ""))
        # ... split nodes, apply deterministic node_id, metadata ...
    return final_nodes
```
Ensure each `TextNode` has:
- `node_id` deterministic
- metadata: `doc_id, path, title, heading_path, anchor, chunk_index, content_hash`

**Step 4: Run test to pass**
Run: `pytest kb/tests/test_llama_nodes.py -v`
Expected: PASS

**Step 5: Commit**
```bash
git add kb/kb/indexing/llama_pipeline.py kb/tests/test_llama_nodes.py kb/kb/indexing/pipeline.py
git commit -m "feat: add llamaindex node pipeline"
```

---

## Task 3: LlamaIndex Vector Store + Persisted Index
**Files:**
- Modify: `kb/kb/indexing/pipeline.py`
- Modify: `kb/kb/cli.py`
- Modify: `kb/migrations/001_init.sql` (or add `002_llamaindex_pgvector.sql`)
- Test: `kb/tests/test_index_persist.py`

**Step 1: Write failing persistence test**
```python
from kb.indexing.pipeline import build_index
from kb.config import AppConfig

def test_index_persist(tmp_path):
    cfg = AppConfig()
    cfg = cfg.__class__(**{**cfg.__dict__, "storage": cfg.storage.__class__(database_url=None, persist_dir=str(tmp_path))})
    build_index(cfg)
    assert (tmp_path / "docstore.json").exists()
```

**Step 2: Run test to confirm failure**
Run: `pytest kb/tests/test_index_persist.py -v`
Expected: FAIL

**Step 3: Implement LlamaIndex storage**
In `kb/kb/indexing/pipeline.py`:
- Build `StorageContext` with `PGVectorStore` (table_name from config)
- Use `VectorStoreIndex.from_nodes(nodes, storage_context=...)`
- `storage_context.persist(persist_dir)`
- Still write `chunks.jsonl` + `manifest.json` for deterministic check

**Step 4: Migration SQL**
Add `kb/migrations/002_llamaindex_pgvector.sql`:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE IF NOT EXISTS kb_llama_nodes (
    id BIGSERIAL PRIMARY KEY,
    node_id TEXT NOT NULL,
    text TEXT NOT NULL,
    metadata JSONB,
    embedding VECTOR(384)
);
CREATE INDEX IF NOT EXISTS kb_llama_nodes_node_id_idx ON kb_llama_nodes(node_id);
```

**Step 5: Run test to pass**
Run: `pytest kb/tests/test_index_persist.py -v`
Expected: PASS

**Step 6: Commit**
```bash
git add kb/kb/indexing/pipeline.py kb/kb/cli.py kb/migrations/002_llamaindex_pgvector.sql kb/tests/test_index_persist.py
git commit -m "feat: persist llamaindex vector index"
```

---

## Task 4: Hybrid Retrieval (LlamaIndex + BM25)
**Files:**
- Modify: `kb/kb/retrieval/hybrid.py`
- Create: `kb/kb/retrieval/llama_retriever.py`
- Test: `kb/tests/test_hybrid_merge.py`

**Step 1: Write failing hybrid merge test**
```python
from kb.retrieval.hybrid import hybrid_merge

def test_hybrid_merge_stable():
    merged = hybrid_merge([("a", 0.8)], [("a", 0.2)], alpha=0.7)
    assert merged[0][0] == "a"
```

**Step 2: Run test to confirm failure**
Run: `pytest kb/tests/test_hybrid_merge.py -v`
Expected: FAIL

**Step 3: Implement LlamaIndex retrievers**
- Create `llama_retriever.py` to wrap `VectorIndexRetriever` + `BM25Retriever`
- Expose `search(query, k, doc_id)` returning `NodeWithScore`
- Reuse `hybrid_merge` for scoring

**Step 4: Run test to pass**
Run: `pytest kb/tests/test_hybrid_merge.py -v`
Expected: PASS

**Step 5: Commit**
```bash
git add kb/kb/retrieval/hybrid.py kb/kb/retrieval/llama_retriever.py kb/tests/test_hybrid_merge.py
git commit -m "feat: llamaindex hybrid retrieval"
```

---

## Task 5: API Rewrite (LlamaIndex + LangChain Agent)
**Files:**
- Modify: `kb/kb/api/app.py`
- Modify: `kb/kb/api/schemas.py`
- Test: `kb/tests/test_api_search.py`

**Step 1: Write failing API test**
```python
from fastapi.testclient import TestClient
from kb.api.app import create_app

def test_search_returns_results(monkeypatch):
    app = create_app()
    client = TestClient(app)
    resp = client.post("/search", json={"query": "vector db", "k": 2})
    assert resp.status_code in (200, 404)
```

**Step 2: Run test to confirm failure**
Run: `pytest kb/tests/test_api_search.py -v`

**Step 3: Implement LlamaIndex-based API**
- Load storage context from `persist_dir`
- Build retriever from `llama_retriever`
- Implement `/search` using NodeWithScore metadata
- Implement `/ask` with LangChain tool-calling, max 1 tool call:
```python
tool = StructuredTool.from_function(kb_search)
agent = create_tool_calling_agent(llm, [tool], prompt)
executor = AgentExecutor(agent=agent, tools=[tool], max_iterations=1)
```
- Fallback when no LLM key: return first two sentences of context

**Step 4: Run test to pass**
Run: `pytest kb/tests/test_api_search.py -v`

**Step 5: Commit**
```bash
git add kb/kb/api/app.py kb/kb/api/schemas.py kb/tests/test_api_search.py
git commit -m "feat: llamaindex api + langchain agent"
```

---

## Task 6: Strict Citations over LlamaIndex Source Nodes
**Files:**
- Modify: `kb/kb/citations/aligner.py`
- Test: `kb/tests/test_citations.py`

**Step 1: Write failing citation test**
```python
from kb.citations.aligner import align_citations

def test_citations_strict():
    result = align_citations("Hello world.", sources=[])
    assert result.status == "insufficient_evidence"
```

**Step 2: Run test to confirm failure**
Run: `pytest kb/tests/test_citations.py -v`

**Step 3: Implement source_nodes adapter**
- Accept LlamaIndex `NodeWithScore`/`TextNode`
- Map to `ChunkMetadata` with `doc_id/path/anchor`
- Keep strict rules: unsupported sentences removed

**Step 4: Run test to pass**
Run: `pytest kb/tests/test_citations.py -v`

**Step 5: Commit**
```bash
git add kb/kb/citations/aligner.py kb/tests/test_citations.py
git commit -m "feat: strict citations with llamaindex sources"
```

---

## Task 7: Update OpenSpec Design + Tasks
**Files:**
- Modify: `openspec/changes/kb-agent-mvp/design.md`
- Modify: `openspec/changes/kb-agent-mvp/tasks.md`
- (Optional) Modify: `openspec/changes/kb-agent-mvp/proposal.md`

**Steps:**
- Update design decisions to mention LlamaIndex + LangChain split
- Reopen or adjust tasks to reflect rewrite steps
- Commit with `docs:` prefix

---

## Verification / Acceptance
- `kb-index-build --config kb/config.example.yaml --verify`
- Smoke test: `/search`, `/doc`, `/ask` with known queries
- Ensure citations never reference unknown sources

---

## Assumptions / Defaults
- LlamaIndex version pinned to latest stable compatible with Python 3.11 (adjust in `pyproject.toml` if needed)
- Embeddings default to HuggingFace BGE
- BM25 rebuilt at startup from persisted nodes (no separate BM25 binary dump)
- /ask uses LangChain tool-calling with max 1 retrieval call
