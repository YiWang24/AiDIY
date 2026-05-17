import { searchChunks, type ChunkHit } from "../db/queries";

export interface RetrievalResult {
  chunks: Array<{
    chunk_id: string;
    doc_id: string;
    title: string | null;
    path: string;
    heading_path: string[];
    content: string;
    score: number;
  }>;
  retrieval_time_ms: number;
}

export async function retrieve(
  query: string,
  topK: number = 8,
): Promise<RetrievalResult> {
  const start = Date.now();
  const hits: ChunkHit[] = await searchChunks(query, topK);
  return {
    chunks: hits.map((h) => ({
      chunk_id: h.chunk_id,
      doc_id: h.doc_id,
      title: h.title,
      path: h.path,
      heading_path: h.heading_path ?? [],
      content: h.content,
      score: h.score,
    })),
    retrieval_time_ms: Date.now() - start,
  };
}
