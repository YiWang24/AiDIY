// Vercel Edge Function to proxy requests to Python backend with Cloudflare Access authentication
// https://vercel.com/docs/functions/edge-functions

export const config = {
  runtime: 'edge',
};

export default async function handler(req: Request) {
  // Only allow POST requests
  if (req.method !== 'POST') {
    return new Response('Method not allowed', { status: 405 });
  }

  // Get environment variables
  const BACKEND_API_URL = process.env.BACKEND_URL || 'http://localhost:8000';
  const CF_CLIENT_ID = process.env.CF_CLIENT_ID;
  const CF_CLIENT_SECRET = process.env.CF_CLIENT_SECRET;

  try {
    // Prepare request headers
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    // Add Cloudflare Access Service Authentication
    // https://developers.cloudflare.com/cloudflare-one/identity/authorization-cookie/advanced-service-auth/
    if (CF_CLIENT_ID && CF_CLIENT_SECRET) {
      // Method 1: Combined JSON format (recommended)
      headers['CF-Access-Client-Id'] = `${CF_CLIENT_ID}:${CF_CLIENT_SECRET}`;

      // Method 2: Separate headers (alternative, uncomment to use)
      // headers['CF-Access-Client-Id'] = CF_CLIENT_ID;
      // headers['CF-Access-Client-Secret'] = CF_CLIENT_SECRET;
    }

    // Forward request to backend
    const response = await fetch(`${BACKEND_API_URL}/stream`, {
      method: 'POST',
      headers,
      body: await req.text(),
    });

    if (!response.ok) {
      const errorText = await response.text();
      return new Response(
        JSON.stringify({
          error: `Backend error: ${response.status}`,
          detail: errorText,
        }),
        {
          status: response.status,
          headers: { 'Content-Type': 'application/json' },
        }
      );
    }

    // Return streaming response
    return new Response(response.body, {
      status: response.status,
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      },
    });
  } catch (error) {
    console.error('Edge Function error:', error);
    return new Response(
      JSON.stringify({
        error: 'Proxy error',
        detail: error instanceof Error ? error.message : 'Unknown error',
      }),
      {
        status: 500,
        headers: { 'Content-Type': 'application/json' },
      }
    );
  }
}
