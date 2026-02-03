# Offline KB Build (BGE-M3 + LangChain + PGVector) Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build an offline KB indexer that consumes cleaned JSONL documents and stores chunk embeddings in PGVector with incremental updates.

**Architecture:** Clean Architecture style: indexing use-case orchestrates chunking + embeddings + storage; adapters use LangChain PGVector and psycopg docstore.

**Tech Stack:** Python 3.11, LangChain (native splitters + PGVector), Postgres + pgvector, psycopg, BAAI/bge-m3 embeddings.

---

## Task 0: Plan File

**Files:**
- Create: `docs/plans/2026-02-03-kb-offline-build.md`

**Step 1: Write plan file**
- Add this document.

**Step 2: Commit**
```bash
git add docs/plans/2026-02-03-kb-offline-build.md
git commit -m "docs: add offline kb build plan"
```

---

## Task 1: Chunking + Stable IDs (TDD)

**Files:**
- Create: `kb/kb/indexing/chunking.py`
- Create: `kb/tests/test_chunking.py`
- Create: `kb/kb/__init__.py`

**Step 1: Write failing tests**
Create `kb/tests/test_chunking.py`:
```python
import unittest
from kb.indexing.chunking import split_document, build_chunk_id

class ChunkingTests(unittest.TestCase):
    def test_chunk_ids_stable(self):
        record = {
            "id": "docs:sample",
            "version": "latest",
            "content": "# Title\n\nHello world."
        }
        chunks_a = split_document(record, chunk_size=200, chunk_overlap=0)
        chunks_b = split_document(record, chunk_size=200, chunk_overlap=0)
        self.assertEqual([c["chunk_id"] for c in chunks_a], [c["chunk_id"] for c in chunks_b])

    def test_heading_path_present(self):
        record = {
            "id": "docs:sample",
            "version": "latest",
            "content": "# H1\n\n## H2\n\nText"
        }
        chunks = split_document(record, chunk_size=200, chunk_overlap=0)
        self.assertTrue(any(c["heading_path"] == ["H1", "H2"] for c in chunks))

if __name__ == "__main__":
    unittest.main()
```

**Step 2: Run test to confirm failure**
```bash
python -m unittest kb/tests/test_chunking.py -v
```
Expected: FAIL (module not found)

**Step 3: Implement chunking + IDs**
Create `kb/kb/indexing/chunking.py`:
```python
import hashlib
from langchain.text_splitter import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

HEADER_MAP = [('#', 'h1'), ('##', 'h2'), ('###', 'h3'), ('####', 'h4')]


def build_chunk_id(doc_id, version, heading_path, chunk_index, content):
    content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
    raw = f"{doc_id}|{version}|{heading_path}|{chunk_index}|{content_hash}"
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


def split_document(record, chunk_size=1500, chunk_overlap=200, max_section_chars=2000):
    doc_id = record["id"]
    version = record.get("version", "latest")
    content = record.get("content", "")

    header_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=HEADER_MAP, strip_headers=False)
    sections = header_splitter.split_text(content)

    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    chunks = []
    index = 0
    for section in sections:
        if len(section.page_content) > max_section_chars:
            subdocs = splitter.split_documents([section])
        else:
            subdocs = [section]

        for subdoc in subdocs:
            heading_path = [subdoc.metadata[k] for k in ["h1", "h2", "h3", "h4"] if subdoc.metadata.get(k)]
            chunk_id = build_chunk_id(doc_id, version, heading_path, index, subdoc.page_content)
            chunks.append({
                "chunk_id": chunk_id,
                "doc_id": doc_id,
                "chunk_index": index,
                "heading_path": heading_path,
                "content": subdoc.page_content,
            })
            index += 1
    return chunks
```

**Step 4: Run test to pass**
```bash
python -m unittest kb/tests/test_chunking.py -v
```
Expected: PASS

**Step 5: Commit**
```bash
git add kb/kb/__init__.py kb/kb/indexing/chunking.py kb/tests/test_chunking.py
git commit -m "feat: add chunking with stable ids"
```

---

## Task 2: Incremental Doc Logic (TDD)

**Files:**
- Create: `kb/kb/indexing/docstate.py`
- Create: `kb/tests/test_docstate.py`

**Step 1: Write failing tests**
Create `kb/tests/test_docstate.py`:
```python
import unittest
from kb.indexing.docstate import should_process

class DocStateTests(unittest.TestCase):
    def test_should_skip_when_checksum_same(self):
        self.assertFalse(should_process("abc", "abc"))

    def test_should_process_when_checksum_diff(self):
        self.assertTrue(should_process("abc", "def"))

if __name__ == "__main__":
    unittest.main()
```

**Step 2: Run test to confirm failure**
```bash
python -m unittest kb/tests/test_docstate.py -v
```
Expected: FAIL (module not found)

**Step 3: Implement**
Create `kb/kb/indexing/docstate.py`:
```python
def should_process(existing_checksum, new_checksum):
    return existing_checksum != new_checksum
```

**Step 4: Run test to pass**
```bash
python -m unittest kb/tests/test_docstate.py -v
```
Expected: PASS

**Step 5: Commit**
```bash
git add kb/kb/indexing/docstate.py kb/tests/test_docstate.py
git commit -m "feat: add checksum-based incremental logic"
```

---

## Task 3: DocStore + VectorStore Integration (TDD)

**Files:**
- Create: `kb/kb/storage/docstore.py`
- Create: `kb/kb/indexing/builder.py`
- Create: `kb/tests/test_builder.py`

**Step 1: Write failing tests**
Create `kb/tests/test_builder.py`:
```python
import unittest
from kb.indexing.builder import build_chunks_for_record

class BuilderTests(unittest.TestCase):
    def test_build_chunks_for_record_produces_metadata(self):
        record = {"id": "docs:one", "version": "latest", "title": "T", "path": "docs/x.mdx", "content": "# H1\n\nText"}
        chunks = build_chunks_for_record(record, chunk_size=200, chunk_overlap=0)
        self.assertTrue(all("doc_id" in c and "chunk_index" in c for c in chunks))

if __name__ == "__main__":
    unittest.main()
```

**Step 2: Run test to confirm failure**
```bash
python -m unittest kb/tests/test_builder.py -v
```
Expected: FAIL (module not found)

**Step 3: Implement builder + docstore**
Create `kb/kb/storage/docstore.py` with SQL helpers (create table, get checksum, upsert). Create `kb/kb/indexing/builder.py` with:
- `build_chunks_for_record(record, ...)`
- `index_documents(input_jsonl, db_url, collection_name, doc_table, embedding_model, ...)`
Use LangChain native:
- `HuggingFaceEmbeddings(model_name="BAAI/bge-m3")`
- `PGVector(...).add_texts(..., ids=chunk_ids)`
- Delete old chunks using stored `chunk_ids` from doc table.

**Step 4: Run test to pass**
```bash
python -m unittest kb/tests/test_builder.py -v
```
Expected: PASS

**Step 5: Commit**
```bash
git add kb/kb/indexing/builder.py kb/kb/storage/docstore.py kb/tests/test_builder.py
git commit -m "feat: add builder with langchain pgvector"
```

---

## Task 4: CLI + Config Defaults

**Files:**
- Create: `kb/kb/cli.py`
- Modify: `kb/config.example.yaml`
- Modify: `kb/pyproject.toml`

**Step 1: Write failing CLI test (smoke)**
Create `kb/tests/test_cli.py`:
```python
import unittest
from kb.cli import parse_args

class CliTests(unittest.TestCase):
    def test_parse_args_defaults(self):
        args = parse_args([])
        self.assertTrue(args.input)

if __name__ == "__main__":
    unittest.main()
```

**Step 2: Run test to confirm failure**
```bash
python -m unittest kb/tests/test_cli.py -v
```
Expected: FAIL (module not found)

**Step 3: Implement CLI**
- `kb/cli.py` with `argparse`, calling `index_documents`.
- Update `kb/config.example.yaml` to set embedding model `BAAI/bge-m3` and add vector store `collection_name` + doc table name.
- Update `kb/pyproject.toml` to add `langchain-text-splitters` if needed.

**Step 4: Run test to pass**
```bash
python -m unittest kb/tests/test_cli.py -v
```
Expected: PASS

**Step 5: Commit**
```bash
git add kb/kb/cli.py kb/config.example.yaml kb/pyproject.toml kb/tests/test_cli.py
git commit -m "feat: add kb index cli"
```

---

## Task 5: Verification

**Step 1: Run all tests**
```bash
python -m unittest discover -s kb/tests -v
```
Expected: PASS

**Step 2: Report**
Summarize outputs and readiness.
