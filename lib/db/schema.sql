-- AiDIY Neon schema. Run once via `npm run db:migrate` against $DATABASE_URL.
-- Idempotent: safe to re-run.

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE TABLE IF NOT EXISTS kb_documents (
  id          TEXT PRIMARY KEY,
  path        TEXT NOT NULL,
  title       TEXT,
  checksum    TEXT NOT NULL,
  version     TEXT NOT NULL DEFAULT 'latest',
  frontmatter JSONB,
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS kb_chunks_glm (
  chunk_id     TEXT PRIMARY KEY,
  doc_id       TEXT NOT NULL REFERENCES kb_documents(id) ON DELETE CASCADE,
  chunk_index  INT  NOT NULL,
  heading_path TEXT[] NOT NULL DEFAULT '{}',
  content      TEXT NOT NULL,
  -- halfvec (16-bit float) supports HNSW up to 4000 dims, vs vector() cap of 2000.
  -- Quality loss vs full-precision is negligible for cosine similarity.
  embedding    halfvec(2048) NOT NULL,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS kb_chunks_glm_doc_idx
  ON kb_chunks_glm (doc_id);

CREATE INDEX IF NOT EXISTS kb_chunks_glm_embedding_idx
  ON kb_chunks_glm USING hnsw (embedding halfvec_cosine_ops);

CREATE INDEX IF NOT EXISTS kb_chunks_glm_content_trgm
  ON kb_chunks_glm USING gin (content gin_trgm_ops);

CREATE TABLE IF NOT EXISTS chat_sessions (
  id         TEXT PRIMARY KEY,
  title      TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS chat_messages (
  id         TEXT PRIMARY KEY,
  session_id TEXT NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
  role       TEXT NOT NULL CHECK (role IN ('user','assistant','system','tool')),
  parts      JSONB NOT NULL,
  metadata   JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS chat_messages_session_idx
  ON chat_messages (session_id, created_at);
