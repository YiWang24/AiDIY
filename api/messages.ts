// GET /api/messages?sessionId=xxx → { messages: UIMessage[] }
// Returns persisted UIMessages so useChat can hydrate via initialMessages.
import type { UIMessage } from "ai";
import { listMessages } from "../lib/db/queries";

export const config = { runtime: "edge" };

export default async function handler(req: Request): Promise<Response> {
  if (req.method !== "GET") {
    return new Response("Method Not Allowed", { status: 405 });
  }

  const url = new URL(req.url);
  const sessionId = url.searchParams.get("sessionId");
  if (!sessionId) {
    return new Response(JSON.stringify({ error: "?sessionId= required" }), {
      status: 400,
      headers: { "content-type": "application/json" },
    });
  }

  const rows = await listMessages(sessionId);
  const messages: UIMessage[] = rows.map((r) => ({
    id: r.id,
    role: r.role as UIMessage["role"],
    parts: r.parts,
    metadata: r.metadata ?? undefined,
  }));

  return Response.json({ messages });
}
