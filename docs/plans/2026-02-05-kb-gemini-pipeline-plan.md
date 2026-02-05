# KB Gemini Pipeline Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Unify pipeline/API config via `Config.from_yaml`, make Gemini the only embedding provider, and fix correctness issues (index signature, vector dims, streaming JSONL).

**Architecture:** Centralize configuration in `kb/pipeline/config.py`, remove GLM/HF paths, compute a deterministic index signature (embedding + chunking), and enforce rebuilds on signature mismatch. Vector store uses Gemini embeddings only.

**Tech Stack:** Python 3.11+, FastAPI, psycopg3, pgvector, httpx, PyYAML, pytest.

---

### Task 1: Config Env Expansion Tests (TDD)

**Files:**
- Create: `kb/tests/test_config_unified.py`
- Modify: `kb/pipeline/config.py`

**Step 1: Write the failing test**

```python
import os
import types
import sys

from kb.pipeline.config import Config


def test_config_from_dict_expands_env_vars(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@h:5432/db")
    monkeypatch.setenv("GEMINI_API_KEY", "gkey")

    data = {
        "storage": {"database_url": "${DATABASE_URL:-}"},
        "gemini": {"api_key": "${GEMINI_API_KEY:-}"},
        "embedding": {"provider": "gemini", "model": "models/embedding-001"},
    }

    cfg = Config.from_dict(data)

    assert cfg.database_url == "postgresql://u:p@h:5432/db"
    assert cfg.gemini_api_key == "gkey"
    assert cfg.embedding_provider == "gemini"


def test_config_from_yaml_uses_yaml_loader(monkeypatch, tmp_path):
    # stub yaml.safe_load so we don't need PyYAML in the test environment
    fake_yaml = types.SimpleNamespace(safe_load=lambda _f: {
        "embedding": {"provider": "gemini", "model": "models/embedding-001"},
        "storage": {"database_url": "postgresql://x"},
    })
    sys.modules["yaml"] = fake_yaml

    path = tmp_path / "config.yaml"
    path.write_text("fake: yaml")

    cfg = Config.from_yaml(str(path))
    assert cfg.embedding_provider == "gemini"
    assert cfg.database_url == "postgresql://x"
```

**Step 2: Run test to verify it fails**

Run: `PYTHONPATH=. pytest kb/tests/test_config_unified.py -q`
Expected: FAIL (missing `embedding_provider` or config parsing behavior).

**Step 3: Write minimal implementation**
- Add `embedding_provider` to `Config`.
- Implement recursive env expansion for all string fields.
- Ensure `Config.from_yaml` loads via yaml (import inside function).

**Step 4: Run test to verify it passes**

Run: `PYTHONPATH=. pytest kb/tests/test_config_unified.py -q`
Expected: PASS

---

### Task 2: Gemini-only Config & API/CLI Unification (TDD)

**Files:**
- Modify: `kb/api/dependencies.py`
- Modify: `kb/cli.py`
- Modify: `kb/config.yaml`
- Modify: `kb/pipeline/config.py`

**Step 1: Write the failing test**

```python
from kb.pipeline.config import Config


def test_config_rejects_non_gemini_provider():
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
```

**Step 2: Run test to verify it fails**

Run: `PYTHONPATH=. pytest kb/tests/test_config_unified.py::test_config_rejects_non_gemini_provider -q`
Expected: FAIL

**Step 3: Write minimal implementation**
- `Config.from_dict` enforces `embedding_provider == "gemini"`.
- Update API dependencies to build stores from `Config.from_yaml`.
- Update CLI to load `Config.from_yaml` and use config fields only (no model inference).
- Update `kb/config.yaml` to Gemini-only schema (no glm fields).

**Step 4: Run test to verify it passes**

Run: `PYTHONPATH=. pytest kb/tests/test_config_unified.py::test_config_rejects_non_gemini_provider -q`
Expected: PASS

---

### Task 3: Remove GLM / HF Dependencies (TDD)

**Files:**
- Modify: `kb/storage/vectorstore.py`
- Modify: `kb/pipeline/index.py`
- Modify: `kb/pyproject.toml`

**Step 1: Write the failing test**

```python
from kb.storage.vectorstore import VectorStore


def test_vectorstore_requires_gemini_key():
    try:
        vs = VectorStore(database_url="postgresql://x", embedding_model="models/embedding-001", gemini_api_key="")
        vs.initialize()
    except ValueError as e:
        assert "gemini api key" in str(e).lower()
    else:
        assert False, "expected ValueError when gemini key missing"
```

**Step 2: Run test to verify it fails**

Run: `PYTHONPATH=. pytest kb/tests/test_vectorstore_gemini.py -q`
Expected: FAIL (test file missing, VectorStore not Gemini-only).

**Step 3: Write minimal implementation**
- Remove GLM/HF classes and logic from `VectorStore`.
- Keep only `GeminiEmbeddings` and enforce key check.
- Update `IndexBuilder` to remove provider inference.
- Remove GLM dependencies from `kb/pyproject.toml`.

**Step 4: Run test to verify it passes**

Run: `PYTHONPATH=. pytest kb/tests/test_vectorstore_gemini.py -q`
Expected: PASS

---

### Task 4: Index Signature and Auto Rebuild (TDD)

**Files:**
- Create: `kb/pipeline/index_signature.py`
- Modify: `kb/storage/docstore.py`
- Modify: `kb/pipeline/index.py`

**Step 1: Write the failing test**

```python
from kb.pipeline.index_signature import compute_signature
from kb.pipeline.config import Config


def test_signature_changes_when_chunking_changes():
    cfg1 = Config.from_dict({
        "embedding": {"provider": "gemini", "model": "models/embedding-001"},
        "chunking": {"chunk_size": 500, "chunk_overlap": 80, "max_section_chars": 2000},
        "storage": {"database_url": "postgresql://x"},
    })
    cfg2 = Config.from_dict({
        "embedding": {"provider": "gemini", "model": "models/embedding-001"},
        "chunking": {"chunk_size": 700, "chunk_overlap": 80, "max_section_chars": 2000},
        "storage": {"database_url": "postgresql://x"},
    })

    sig1 = compute_signature(cfg1, embedding_dim=768)
    sig2 = compute_signature(cfg2, embedding_dim=768)

    assert sig1 != sig2
```

**Step 2: Run test to verify it fails**

Run: `PYTHONPATH=. pytest kb/tests/test_index_signature.py -q`
Expected: FAIL

**Step 3: Write minimal implementation**
- Add `compute_signature` (hash of embedding model + dim + chunking params).
- Add `kb_index_meta` table + `get_index_signature` / `set_index_signature` methods in `DocStore`.
- In `IndexBuilder.initialize()`, compare stored signature and trigger rebuild when changed.

**Step 4: Run test to verify it passes**

Run: `PYTHONPATH=. pytest kb/tests/test_index_signature.py -q`
Expected: PASS

---

### Task 5: Vector Dimension Detection (TDD)

**Files:**
- Modify: `kb/storage/vectorstore.py`

**Step 1: Write the failing test**

```python
from kb.storage.vectorstore import _parse_vector_dim


def test_parse_vector_dim_from_pgvector_format():
    assert _parse_vector_dim("vector(768)") == 768
    assert _parse_vector_dim("vector(1024)") == 1024
```

**Step 2: Run test to verify it fails**

Run: `PYTHONPATH=. pytest kb/tests/test_vector_dim.py -q`
Expected: FAIL (helper missing)

**Step 3: Write minimal implementation**
- Add `_parse_vector_dim` helper.
- Update `_create_table` to use `pg_catalog.format_type` (or `vector_dims` if available) and parse dimensions reliably.

**Step 4: Run test to verify it passes**

Run: `PYTHONPATH=. pytest kb/tests/test_vector_dim.py -q`
Expected: PASS

---

### Task 6: Streaming JSONL (TDD)

**Files:**
- Modify: `kb/pipeline/index.py`

**Step 1: Write the failing test**

```python
from kb.pipeline.index import IndexBuilder
from kb.pipeline.config import Config


def test_build_from_jsonl_counts_without_preloading(monkeypatch, tmp_path):
    # Build a tiny JSONL file
    p = tmp_path / "docs.jsonl"
    p.write_text('{"id":"a","path":"a","title":"a","checksum":"x","content":"c"}\n')

    cfg = Config.from_dict({
        "embedding": {"provider": "gemini", "model": "models/embedding-001"},
        "storage": {"database_url": "postgresql://x"},
    })

    builder = IndexBuilder(config=cfg)

    # Monkeypatch to avoid DB/embeddings
    builder._docstore = type("D", (), {"initialize": lambda *_: None, "close": lambda *_: None})()
    builder._vectorstore = type("V", (), {"initialize": lambda *_: None, "close": lambda *_: None})()
    builder._incremental = type("I", (), {"index_document": lambda *_: {"status": "indexed", "chunks_added": 0, "chunks_deleted": 0}})()
    builder._chunker = type("C", (), {"split": lambda *_: []})()

    stats = builder.build_from_jsonl(str(p))
    assert stats["total"] == 1
```

**Step 2: Run test to verify it fails**

Run: `PYTHONPATH=. pytest kb/tests/test_streaming_jsonl.py -q`
Expected: FAIL

**Step 3: Write minimal implementation**
- Update `build_from_jsonl` to iterate documents without `list(...)`.

**Step 4: Run test to verify it passes**

Run: `PYTHONPATH=. pytest kb/tests/test_streaming_jsonl.py -q`
Expected: PASS

---

### Task 7: Consolidated Test Run

**Step 1: Run targeted test suite**

Run: `PYTHONPATH=. pytest kb/tests/test_config_unified.py kb/tests/test_vectorstore_gemini.py kb/tests/test_index_signature.py kb/tests/test_vector_dim.py kb/tests/test_streaming_jsonl.py -q`

**Step 2: Fix any failures**

---

### Task 8: Commit

**Step 1: Git status and review**

Run: `git status --short`

**Step 2: Commit**

```bash
git add kb/pipeline/config.py kb/api/dependencies.py kb/cli.py kb/config.yaml kb/storage/vectorstore.py kb/pipeline/index.py kb/storage/docstore.py kb/pipeline/index_signature.py kb/pyproject.toml kb/tests/test_config_unified.py kb/tests/test_vectorstore_gemini.py kb/tests/test_index_signature.py kb/tests/test_vector_dim.py kb/tests/test_streaming_jsonl.py
git commit -m "feat(kb): unify config and gemini-only pipeline"
```
