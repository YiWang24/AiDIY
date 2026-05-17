// AiDIY ingestion: clean MDX -> chunk -> embed (GLM embedding-3) -> Neon pgvector.
// Run: `npm run ingest` (uses tsx). Requires DATABASE_URL + GLM_API_KEY in env.
//
// Incremental: skips documents whose checksum is unchanged. Orphaned docs
// (present in DB but no longer on disk) are deleted along with their chunks.

import path from "node:path";
import { chunkMarkdown, type Chunk } from "../lib/rag/chunk";
import { embedBatch } from "../lib/ai/embed";
import {
  deleteChunksForDoc,
  deleteDocument,
  getDocumentChecksum,
  insertChunk,
  listDocumentIds,
  upsertDocument,
  type DocumentInput,
} from "../lib/db/queries";

interface CleanedRecord {
  id: string;
  path: string;
  title: string;
  version: string;
  frontmatter: Record<string, unknown>;
  content: string;
  checksum: string;
}

const EMBED_BATCH_SIZE = 16;

async function main(): Promise<void> {
  const repoRoot = path.resolve(__dirname, "..");
  const log = (msg: string) => process.stderr.write(`${msg}\n`);

  log("[ingest] cleaning MDX...");
  // Dynamic import: cleaner.js is ESM, ingest.ts is loaded as CJS by tsx.
  const cleanerMod = (await import(
    path.join(repoRoot, "kb/tools/mdx-clean/src/cleaner.js")
  )) as { cleanDocuments: (opts: unknown) => Promise<CleanedRecord[]> };
  const records = (await cleanerMod.cleanDocuments({
    roots: [
      { dir: "docs", prefix: "docs" },
      { dir: "blog", prefix: "blog" },
    ],
    include: [".md", ".mdx"],
    exclude: [
      "docs/plans/**",
      "build/**",
      "node_modules/**",
      "kb/**",
      ".docusaurus/**",
    ],
    repoRoot,
    noiseFilter: true,
  })) as CleanedRecord[];
  log(`[ingest] cleaned ${records.length} documents`);

  const seenIds = new Set<string>();
  let upserted = 0;
  let skipped = 0;

  for (const rec of records) {
    seenIds.add(rec.id);
    const existing = await getDocumentChecksum(rec.id);
    if (existing === rec.checksum) {
      skipped += 1;
      continue;
    }

    const docInput: DocumentInput = {
      id: rec.id,
      path: rec.path,
      title: rec.title,
      checksum: rec.checksum,
      version: rec.version,
      frontmatter: rec.frontmatter ?? null,
    };

    const chunks = chunkMarkdown(rec.id, rec.content);
    if (chunks.length === 0) {
      log(`[ingest] skip ${rec.id}: no chunkable content`);
      continue;
    }

    log(`[ingest] ${existing ? "update" : "insert"} ${rec.id} (${chunks.length} chunks)`);

    const embeddedChunks = await embedAllChunks(chunks);

    await deleteChunksForDoc(rec.id);
    await upsertDocument(docInput);
    for (const c of embeddedChunks) {
      await insertChunk({ ...c, doc_id: rec.id });
    }
    upserted += 1;
  }

  // Garbage-collect orphans
  const existingIds = await listDocumentIds();
  const orphans = existingIds.filter((id) => !seenIds.has(id));
  for (const id of orphans) {
    log(`[ingest] delete orphan ${id}`);
    await deleteDocument(id);
  }

  log(
    `[ingest] done — upserted=${upserted} skipped=${skipped} orphans_deleted=${orphans.length}`,
  );
}

async function embedAllChunks(
  chunks: Chunk[],
): Promise<Array<Chunk & { embedding: number[] }>> {
  const out: Array<Chunk & { embedding: number[] }> = [];
  for (let i = 0; i < chunks.length; i += EMBED_BATCH_SIZE) {
    const batch = chunks.slice(i, i + EMBED_BATCH_SIZE);
    const vectors = await embedBatch(batch.map((c) => c.content));
    batch.forEach((c, j) => out.push({ ...c, embedding: vectors[j] }));
  }
  return out;
}

main().catch((err) => {
  process.stderr.write(`[ingest] failed: ${err?.message ?? err}\n`);
  if (err?.stack) process.stderr.write(err.stack + "\n");
  process.exit(1);
});
