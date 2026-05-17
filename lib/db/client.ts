import { neon, neonConfig, Pool } from "@neondatabase/serverless";

neonConfig.fetchConnectionCache = true;

function requireDatabaseUrl(): string {
  const url = process.env.DATABASE_URL;
  if (!url) {
    throw new Error(
      "DATABASE_URL is not set. Configure it via the Vercel Neon integration " +
        "or copy it into .env.local for local development.",
    );
  }
  return url;
}

// HTTP-based driver — one round-trip per query, ideal for serverless functions.
export const sql = neon(requireDatabaseUrl());

// Pool — only use for ingest/migration scripts that need transactions or
// many sequential queries on one connection. Caller is responsible for `.end()`.
export function createPool(): Pool {
  return new Pool({ connectionString: requireDatabaseUrl() });
}
