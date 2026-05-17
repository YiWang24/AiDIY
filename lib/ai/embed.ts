import { embed, embedMany } from "ai";
import { glm, GLM_EMBED_DIM, GLM_EMBED_MODEL } from "./provider";

const embeddingModel = glm.textEmbeddingModel(GLM_EMBED_MODEL);

export async function embedText(text: string): Promise<number[]> {
  const { embedding } = await embed({ model: embeddingModel, value: text });
  assertDim(embedding);
  return embedding;
}

export async function embedBatch(texts: string[]): Promise<number[][]> {
  if (texts.length === 0) return [];
  const { embeddings } = await embedMany({
    model: embeddingModel,
    values: texts,
  });
  embeddings.forEach(assertDim);
  return embeddings;
}

function assertDim(vec: number[]): void {
  if (vec.length !== GLM_EMBED_DIM) {
    throw new Error(
      `Embedding dim mismatch: expected ${GLM_EMBED_DIM}, got ${vec.length}. ` +
        `Either update schema vector(${vec.length}) or set GLM_EMBED_DIM accordingly.`,
    );
  }
}

// pgvector wire format: '[0.1,0.2,...]'
export function toPgVector(vec: number[]): string {
  return `[${vec.join(",")}]`;
}
