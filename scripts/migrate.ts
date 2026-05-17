// Apply lib/db/schema.sql to $DATABASE_URL. Idempotent.
import fs from "node:fs/promises";
import path from "node:path";
import { createPool } from "../lib/db/client";

async function main(): Promise<void> {
  const schemaPath = path.resolve(__dirname, "..", "lib", "db", "schema.sql");
  const sqlText = await fs.readFile(schemaPath, "utf8");

  const pool = createPool();
  try {
    process.stderr.write(`Applying schema from ${schemaPath}...\n`);
    await pool.query(sqlText);
    process.stderr.write("Schema applied successfully.\n");
  } finally {
    await pool.end();
  }
}

main().catch((err) => {
  process.stderr.write(`Migration failed: ${err?.message ?? err}\n`);
  process.exit(1);
});
