// Test Edge Function
export const config = {
  runtime: 'edge',
};

export default async function handler(req: Request) {
  const url = new URL(req.url);
  const method = req.method;
  const timestamp = new Date().toISOString();

  return new Response(
    JSON.stringify({
      message: 'Hello from Vercel Edge Function!',
      method,
      url: url.pathname,
      timestamp,
      headers: {
        'user-agent': req.headers.get('user-agent'),
        'referer': req.headers.get('referer'),
      },
    }),
    {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    }
  );
}
