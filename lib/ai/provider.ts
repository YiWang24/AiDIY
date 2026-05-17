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

export const glm = createOpenAICompatible({
  name: "glm",
  apiKey: required("GLM_API_KEY"),
  baseURL: process.env.GLM_BASE_URL ?? "https://open.bigmodel.cn/api/paas/v4",
});
