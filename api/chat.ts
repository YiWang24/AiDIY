import {
  convertToModelMessages,
  stepCountIs,
  streamText,
  tool,
  type UIMessage,
} from "ai";
import { z } from "zod";
import { waitUntil } from "@vercel/functions";
import { glm, GLM_CHAT_MODEL } from "../lib/ai/provider";
import { retrieve } from "../lib/rag/retrieve";
import { ensureSession, saveMessages } from "../lib/db/queries";

export const config = { runtime: "edge" };

const SYSTEM_PROMPT = `You are the AiDIY documentation assistant.

You answer questions about computer science, AI engineering, backend/frontend
engineering, and case studies hosted on this site. Always call the kb_search
tool first to ground your answer in the docs. Cite specific sources by their
path when you use them. If the knowledge base lacks the answer, say so plainly
instead of inventing facts.`;

interface ChatRequestBody {
  id: string;
  messages: UIMessage[];
}

export default async function handler(req: Request): Promise<Response> {
  if (req.method !== "POST") {
    return new Response("Method Not Allowed", { status: 405 });
  }

  let body: ChatRequestBody;
  try {
    body = (await req.json()) as ChatRequestBody;
  } catch {
    return new Response(JSON.stringify({ error: "Invalid JSON body" }), {
      status: 400,
      headers: { "content-type": "application/json" },
    });
  }

  // Prefer the persistent session id from the AiDIY widget header; fall back
  // to body.id for any non-widget caller (e.g. curl smoke tests).
  const sessionId =
    req.headers.get("x-aidiy-session") || (body.id as string);
  const { messages } = body;
  if (!sessionId || !Array.isArray(messages)) {
    return new Response(
      JSON.stringify({
        error: "Request must include a session id (header x-aidiy-session or body.id) and messages",
      }),
      { status: 400, headers: { "content-type": "application/json" } },
    );
  }

  const firstUserText = messages
    .find((m) => m.role === "user")
    ?.parts?.find((p) => p.type === "text") as
    | { type: "text"; text: string }
    | undefined;
  await ensureSession(sessionId, firstUserText?.text?.slice(0, 60));

  const result = streamText({
    model: glm.chatModel(GLM_CHAT_MODEL),
    system: SYSTEM_PROMPT,
    messages: convertToModelMessages(messages),
    // Allow up to 6 steps so the model has room for several refinement
    // searches plus a final text answer (each tool call eats one step).
    stopWhen: stepCountIs(6),
    // GLM-4.x reasoning models (e.g. glm-4.7) otherwise emit the final answer
    // as `reasoning_content`, leaving `content` empty — the assistant bubble
    // would render blank. Disable thinking for this docs Q&A bot.
    providerOptions: {
      glm: { thinking: { type: "disabled" } },
    },
    tools: {
      kb_search: tool({
        description:
          "Search the AiDIY documentation knowledge base via semantic vector search. Always call this before answering substantive questions.",
        inputSchema: z.object({
          query: z.string().describe("Search query in the user's language"),
          top_k: z
            .number()
            .int()
            .min(1)
            .max(15)
            .optional()
            .describe("Number of chunks to return (default 8)"),
        }),
        execute: async ({ query, top_k }) => retrieve(query, top_k ?? 8),
      }),
    },
  });

  return result.toUIMessageStreamResponse({
    originalMessages: messages,
    onFinish: ({ messages: full }) => {
      // Edge/Fluid runtimes terminate the function once the response body has
      // been flushed. waitUntil keeps it alive so the Neon HTTP writes in
      // saveMessages actually reach the database.
      waitUntil(
        saveMessages(sessionId, full).catch((err) => {
          console.error(
            `[api/chat] persistence failed: ${(err as Error).message ?? err}`,
          );
        }),
      );
    },
  });
}
