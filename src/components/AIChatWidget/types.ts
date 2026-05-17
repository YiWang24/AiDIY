// Shared widget types — kept thin to stay aligned with AI SDK v5 UIMessage parts.

export interface RetrievedChunk {
  chunk_id: string;
  doc_id: string;
  title: string | null;
  path: string;
  heading_path: string[];
  content: string;
  score: number;
}

export interface RetrievalToolOutput {
  chunks: RetrievedChunk[];
  retrieval_time_ms: number;
}

export interface SessionSummary {
  id: string;
  title: string | null;
  updated_at: string;
}
