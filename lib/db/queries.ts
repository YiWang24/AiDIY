import type { UIMessage } from "ai";
import { sql } from "./client";
import { embedText, toPgVector } from "../ai/embed";

export interface ChunkHit {
  chunk_id: string;
  doc_id: string;
  chunk_index: number;
  heading_path: string[];
  content: string;
  title: string | null;
  path: string;
  score: number; // 0..1, higher = more similar
}

export async function searchChunks(
  query: string,
  topK: number = 8,
): Promise<ChunkHit[]> {
  const queryVec = await embedText(query);
  const pgVec = toPgVector(queryVec);

  // Cosine distance: smaller is better. Convert to similarity 1 - dist.
  const rows = (await sql`
    SELECT
      c.chunk_id,
      c.doc_id,
      c.chunk_index,
      c.heading_path,
      c.content,
      d.title,
      d.path,
      1 - (c.embedding <=> ${pgVec}::halfvec) AS score
    FROM kb_chunks_glm c
    JOIN kb_documents d ON d.id = c.doc_id
    ORDER BY c.embedding <=> ${pgVec}::halfvec
    LIMIT ${topK}
  `) as ChunkHit[];

  return rows;
}

// ---------- Documents / Chunks (ingestion) ----------

export interface DocumentInput {
  id: string;
  path: string;
  title: string | null;
  checksum: string;
  version: string;
  frontmatter: Record<string, unknown> | null;
}

export async function getDocumentChecksum(id: string): Promise<string | null> {
  const rows = (await sql`
    SELECT checksum FROM kb_documents WHERE id = ${id}
  `) as Array<{ checksum: string }>;
  return rows[0]?.checksum ?? null;
}

export async function upsertDocument(doc: DocumentInput): Promise<void> {
  await sql`
    INSERT INTO kb_documents (id, path, title, checksum, version, frontmatter, updated_at)
    VALUES (${doc.id}, ${doc.path}, ${doc.title}, ${doc.checksum}, ${doc.version},
            ${doc.frontmatter ? JSON.stringify(doc.frontmatter) : null}::jsonb, now())
    ON CONFLICT (id) DO UPDATE
    SET path = EXCLUDED.path,
        title = EXCLUDED.title,
        checksum = EXCLUDED.checksum,
        version = EXCLUDED.version,
        frontmatter = EXCLUDED.frontmatter,
        updated_at = now()
  `;
}

export async function deleteChunksForDoc(docId: string): Promise<void> {
  await sql`DELETE FROM kb_chunks_glm WHERE doc_id = ${docId}`;
}

export interface ChunkRecord {
  chunk_id: string;
  doc_id: string;
  chunk_index: number;
  heading_path: string[];
  content: string;
  embedding: number[];
}

export async function insertChunk(chunk: ChunkRecord): Promise<void> {
  await sql`
    INSERT INTO kb_chunks_glm (chunk_id, doc_id, chunk_index, heading_path, content, embedding)
    VALUES (${chunk.chunk_id}, ${chunk.doc_id}, ${chunk.chunk_index},
            ${chunk.heading_path}, ${chunk.content}, ${toPgVector(chunk.embedding)}::halfvec)
    ON CONFLICT (chunk_id) DO UPDATE
    SET chunk_index = EXCLUDED.chunk_index,
        heading_path = EXCLUDED.heading_path,
        content = EXCLUDED.content,
        embedding = EXCLUDED.embedding
  `;
}

export async function listDocumentIds(): Promise<string[]> {
  const rows = (await sql`SELECT id FROM kb_documents`) as Array<{ id: string }>;
  return rows.map((r) => r.id);
}

export async function deleteDocument(id: string): Promise<void> {
  await sql`DELETE FROM kb_documents WHERE id = ${id}`;
}

// ---------- Chat sessions / messages ----------

export interface SessionRow {
  id: string;
  title: string | null;
  created_at: string;
  updated_at: string;
}

export async function ensureSession(
  id: string,
  title?: string,
): Promise<void> {
  await sql`
    INSERT INTO chat_sessions (id, title)
    VALUES (${id}, ${title ?? null})
    ON CONFLICT (id) DO UPDATE SET updated_at = now()
  `;
}

export async function listSessions(): Promise<SessionRow[]> {
  return (await sql`
    SELECT id, title, created_at, updated_at
    FROM chat_sessions
    ORDER BY updated_at DESC
    LIMIT 50
  `) as SessionRow[];
}

export async function deleteSession(id: string): Promise<void> {
  await sql`DELETE FROM chat_sessions WHERE id = ${id}`;
}

export interface PersistedMessage {
  id: string;
  session_id: string;
  role: "user" | "assistant" | "system" | "tool";
  parts: UIMessage["parts"];
  metadata: Record<string, unknown> | null;
  created_at: string;
}

export async function listMessages(
  sessionId: string,
): Promise<PersistedMessage[]> {
  return (await sql`
    SELECT id, session_id, role, parts, metadata, created_at
    FROM chat_messages
    WHERE session_id = ${sessionId}
    ORDER BY created_at ASC
  `) as PersistedMessage[];
}

export async function saveMessages(
  sessionId: string,
  messages: UIMessage[],
): Promise<void> {
  if (messages.length === 0) return;
  for (const m of messages) {
    await sql`
      INSERT INTO chat_messages (id, session_id, role, parts, metadata)
      VALUES (${m.id}, ${sessionId}, ${m.role},
              ${JSON.stringify(m.parts)}::jsonb,
              ${m.metadata ? JSON.stringify(m.metadata) : null}::jsonb)
      ON CONFLICT (id) DO UPDATE
      SET parts = EXCLUDED.parts,
          metadata = EXCLUDED.metadata
    `;
  }
  await sql`UPDATE chat_sessions SET updated_at = now() WHERE id = ${sessionId}`;
}
