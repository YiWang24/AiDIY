import { createOpenAICompatible } from "@ai-sdk/openai-compatible";

function required(name: string): string {
  const value = process.env[name];
  if (!value) {
    throw new Error(`${name} is required (configure in Vercel env vars)`);
  }
  return value;
}

export const GLM_CHAT_MODEL = process.env.GLM_CHAT_MODEL ?? "glm-4.7";
export const GLM_EMBED_MODEL = process.env.GLM_EMBED_MODEL ?? "embedding-3";
export const GLM_EMBED_DIM = Number(process.env.GLM_EMBED_DIM ?? "2048");

// 智谱 API 不支持 embedding 请求中的 encoding_format / dimensions / user 参数。
// SDK 的 transformRequestBody 只对 chat model 生效，embedding model 硬编码了
// encoding_format: 'float'。需要用 fetch 拦截器在请求层面剥离这些参数。
const GLM_EMBED_STRIP_KEYS = new Set([
  "encoding_format",
  "dimensions",
  "user",
]);

const glmFetch: typeof fetch = async (input, init) => {
  if (init?.body && typeof init.body === "string") {
    try {
      const parsed = JSON.parse(init.body);
      if (
        typeof parsed === "object" &&
        parsed !== null &&
        typeof parsed.model === "string" &&
        typeof parsed.input !== "undefined" // embedding request
      ) {
        GLM_EMBED_STRIP_KEYS.forEach((key) => {
          delete parsed[key];
        });
        init = { ...init, body: JSON.stringify(parsed) };
      }
    } catch {
      // not JSON, pass through
    }
  }
  return fetch(input, init);
};

export const glm = createOpenAICompatible({
  name: "glm",
  apiKey: required("GLM_API_KEY"),
  baseURL: process.env.GLM_BASE_URL ?? "https://open.bigmodel.cn/api/paas/v4",
  // transformRequestBody 仍保留给 chat model（SDK 只对 chat 生效）
  transformRequestBody: (body: Record<string, unknown>) => {
    const { encoding_format, user, ...rest } = body;
    return rest;
  },
  fetch: glmFetch,
});
