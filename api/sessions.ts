import { deleteSession, listSessions } from "../lib/db/queries";

export const config = { runtime: "nodejs" };

export default async function handler(req: Request): Promise<Response> {
  if (req.method === "GET") {
    const sessions = await listSessions();
    return Response.json({ sessions });
  }

  if (req.method === "DELETE") {
    const url = new URL(req.url);
    const id = url.searchParams.get("id");
    if (!id) {
      return new Response(JSON.stringify({ error: "?id= required" }), {
        status: 400,
        headers: { "content-type": "application/json" },
      });
    }
    await deleteSession(id);
    return new Response(null, { status: 204 });
  }

  return new Response("Method Not Allowed", { status: 405 });
}
