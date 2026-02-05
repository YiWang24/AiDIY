# KB Gemini Pipeline Unification - Design

**Date:** 2026-02-05

## Goal
Unify the offline KB pipeline and API on a single configuration system, remove GLM/HF logic in favor of Gemini-only embeddings, and fix correctness issues in chunking/indexing/embedding while keeping the pipeline maintainable and deterministic.

## Scope
- **In:** Config unification (API + CLI), Gemini-only embeddings, reliable vector dimension handling, index signature with auto rebuild, streaming JSONL, clean error reporting, tests.
- **Out:** New features beyond current pipeline (search API changes, RAG prompt changes, UI changes).

## Key Decisions
1. **Single config source:** All runtime configuration uses `Config.from_yaml` with recursive env expansion. No direct `yaml.safe_load` in API/CLI.
2. **Gemini-only embeddings:** Remove GLM and HuggingFace providers, dependencies, and config fields. The pipeline and API always use Gemini embeddings.
3. **Index signature for rebuilds:** Track an index signature derived from `embedding_model`, `embedding_dim`, and chunking params. When it changes, trigger full rebuild and clear existing vector data.
4. **Streaming JSONL load:** Process JSONL iteratively to avoid high memory use.
5. **Vector dimension correctness:** Determine embedding dimensions from a test embedding and store or verify them reliably; no fragile `atttypmod` math.

## Configuration Model
`Config` will include:
- `docs_dir`, `output_jsonl`
- `chunking`: `max_section_chars`, `chunk_size`, `chunk_overlap`
- `embedding`: `provider` (fixed `gemini`), `model`
- `gemini`: `api_key`
- `storage`: `database_url`
- `vector_store`: `table_name`, `batch_size`
- `llm`: provider/model/key/temperature/max_tokens
- `rag`: retrieval/context/generation settings

`Config.from_yaml` performs recursive env expansion for all string values using `${VAR:-default}` syntax.

## Index Signature
Introduce a lightweight `kb_index_meta` table with:
- `key`: `index_signature`
- `value`: computed hash of embedding model + embedding dimension + chunking config

On initialization:
- If signature missing, store it.
- If signature differs, trigger full rebuild (delete existing embeddings table rows or recreate table) and update signature.

## Vector Store Behavior
- Gemini-only `GeminiEmbeddings`.
- Table name comes from `vector_store.table_name` (default to sanitized model name).
- Dimension mismatch triggers a table rebuild (safe + explicit).

## Chunking
Chunking strategy remains header-first with recursive split; no behavioral change in this phase.

## Testing Strategy
Add/extend tests to cover:
- Config env expansion and API/CLI unified behavior.
- Gemini-only initialization and missing API key errors.
- Index signature change triggers rebuild.
- Vector dimension detection and table rebuild logic (mocked).
- JSONL streaming (no full list loading).

## Migration Notes
- Remove GLM dependencies (`zhipuai`, GLM embedding classes).
- Update `kb/config.yaml` to Gemini-only.
- Existing vector tables may be rebuilt on first run due to new signature or dimension enforcement.
