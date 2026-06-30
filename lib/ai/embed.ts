import { GLM_EMBED_DIM, GLM_EMBED_MODEL } from "./provider";

// 直接调用 GLM embedding API，绕过 @ai-sdk/openai-compatible。
// SDK 的 embedding model 硬编码 encoding_format: 'float'，且 transformRequestBody
// 和 fetch 拦截器都无法可靠地影响 embedding 请求。直接用 fetch 调 API 最简单。
const GLM_BASE_URL =
  process.env.GLM_BASE_URL ?? "https://open.bigmodel.cn/api/paas/v4";
const GLM_API_KEY = process.env.GLM_API_KEY!;

// GLM embedding API 对单次输入有 token 上限（约 512 tokens ≈ 2000 chars）。
// 超长文本需要截断，否则会返回 1210 参数错误。
const MAX_INPUT_CHARS = 1800;

function truncate(text: string): string {
  if (text.length <= MAX_INPUT_CHARS) return text;
  return text.slice(0, MAX_INPUT_CHARS);
}

async function embedOne(text: string): Promise<number[]> {
  const payload = { model: GLM_EMBED_MODEL, input: truncate(text) };

  const resp = await fetch(`${GLM_BASE_URL}/embeddings`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${GLM_API_KEY}`,
    },
    body: JSON.stringify(payload),
  });

  if (!resp.ok) {
    const errorText = await resp.text();
    throw new Error(
      `GLM embedding API error (${resp.status}): ${errorText}\n` +
        `input length: ${text.length} chars (truncated to ${truncate(text).length})\n` +
        `input preview: ${text.slice(0, 100)}...`,
    );
  }

  const data = (await resp.json()) as {
    data: { embedding: number[] }[];
  };
  return data.data[0].embedding;
}

async function callGLMEmbed(values: string[]): Promise<number[][]> {
  const CONCURRENCY = 5;
  const results: number[][] = new Array(values.length);

  for (let i = 0; i < values.length; i += CONCURRENCY) {
    const batch = values.slice(i, i + CONCURRENCY);
    const responses = await Promise.all(
      batch.map(async (text, j) => {
        try {
          return await embedOne(text);
        } catch (e) {
          throw new Error(
            `Failed for input ${i + j} (${text.length} chars): ${(e as Error).message}`,
          );
        }
      }),
    );
    responses.forEach((emb, j) => {
      results[i + j] = emb;
    });
  }

  return results;
}

export async function embedText(text: string): Promise<number[]> {
  const embedding = await embedOne(text);
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
