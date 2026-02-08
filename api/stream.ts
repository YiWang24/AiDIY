// Vercel Edge Function to proxy requests to Python backend with Cloudflare Access authentication
// https://vercel.com/docs/functions/edge-functions

export const config = {
  runtime: "edge",
};

export default async function handler(req: Request) {
  // Only allow POST requests
  if (req.method !== "POST") {
    return new Response("Method not allowed", { status: 405 });
  }

  // Get environment variables
  const BACKEND_API_URL = process.env.BACKEND_URL || "http://localhost:8000";
  const CF_CLIENT_ID = process.env.CF_CLIENT_ID;
  const CF_CLIENT_SECRET = process.env.CF_CLIENT_SECRET;

  try {
    // Prepare request headers
    const headers: HeadersInit = {
      "Content-Type": "application/json",
    };

    // Forward client IP headers so backend per-IP rate limiting works
    for (const name of ["x-forwarded-for", "x-real-ip", "cf-connecting-ip"]) {
      const value = req.headers.get(name);
      if (value) headers[name] = value;
    }

    // Add Cloudflare Access Service Authentication
    // https://developers.cloudflare.com/cloudflare-one/identity/authorization-cookie/advanced-service-auth/
    if (CF_CLIENT_ID && CF_CLIENT_SECRET) {
      // Standard Cloudflare Access service auth headers
      headers["CF-Access-Client-Id"] = CF_CLIENT_ID;
      headers["CF-Access-Client-Secret"] = CF_CLIENT_SECRET;
    }

    // Forward request to backend
    const response = await fetch(`${BACKEND_API_URL}/stream`, {
      method: "POST",
      headers,
      body: await req.text(),
    });

    if (!response.ok) {
      const errorText = await response.text();

      // Preserve backend 429 payload + rate limit headers so the client can
      // surface accurate retry timing.
      if (response.status === 429) {
        const passthroughHeaders = new Headers(response.headers);
        if (!passthroughHeaders.get("Content-Type")) {
          passthroughHeaders.set("Content-Type", "application/json");
        }
        return new Response(errorText, {
          status: response.status,
          headers: passthroughHeaders,
        });
      }

      return new Response(
        JSON.stringify({
          error: `Backend error: ${response.status}`,
          detail: errorText,
        }),
        {
          status: response.status,
          headers: { "Content-Type": "application/json" },
        },
      );
    }

    // Return streaming response
    const streamHeaders = new Headers(response.headers);
    streamHeaders.set("Content-Type", "text/event-stream");
    streamHeaders.set("Cache-Control", "no-cache");
    streamHeaders.set("Connection", "keep-alive");

    return new Response(response.body, {
      status: response.status,
      headers: streamHeaders,
    });
  } catch (error) {
    console.error("Edge Function error:", error);
    return new Response(
      JSON.stringify({
        error: "Proxy error",
        detail: error instanceof Error ? error.message : "Unknown error",
      }),
      {
        status: 500,
        headers: { "Content-Type": "application/json" },
      },
    );
  }
}
