import { GLM_EMBED_DIM, GLM_EMBED_MODEL } from "./provider";

// 直接调用 GLM embedding API，绕过 @ai-sdk/openai-compatible。
// SDK 的 embedding model 硬编码 encoding_format: 'float'，且 transformRequestBody
// 和 fetch 拦截器都无法可靠地影响 embedding 请求。直接用 fetch 调 API 最简单。
const GLM_BASE_URL =
  process.env.GLM_BASE_URL ?? "https://open.bigmodel.cn/api/paas/v4";
const GLM_API_KEY = process.env.GLM_API_KEY!;

async function callGLMEmbed(values: string[]): Promise<number[][]> {
  const resp = await fetch(`${GLM_BASE_URL}/embeddings`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${GLM_API_KEY}`,
    },
    body: JSON.stringify({
      model: GLM_EMBED_MODEL,
      input: values,
    }),
  });

  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(
      `GLM embedding API error (${resp.status}): ${text}`,
    );
  }

  const data = (await resp.json()) as {
    data: { embedding: number[] }[];
  };

  return data.data.map((d) => d.embedding);
}

export async function embedText(text: string): Promise<number[]> {
  const [embedding] = await callGLMEmbed([text]);
  assertDim(embedding);
  return embedding;
}

export async function embedBatch(texts: string[]): Promise<number[][]> {
  if (texts.length === 0) return [];
  const embeddings = await callGLMEmbed(texts);
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
