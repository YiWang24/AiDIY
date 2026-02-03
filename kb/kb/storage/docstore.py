import json


def ensure_doc_table(conn, table_name):
    with conn.cursor() as cur:
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                doc_id TEXT PRIMARY KEY,
                path TEXT,
                title TEXT,
                version TEXT,
                checksum TEXT,
                chunk_ids JSONB,
                updated_at TIMESTAMPTZ DEFAULT NOW()
            )
            """
        )
    conn.commit()


def get_doc_state(conn, table_name, doc_id):
    with conn.cursor() as cur:
        cur.execute(
            f"SELECT checksum, chunk_ids FROM {table_name} WHERE doc_id = %s",
            (doc_id,),
        )
        row = cur.fetchone()
    if not row:
        return None
    checksum, chunk_ids = row
    return {
        "checksum": checksum,
        "chunk_ids": chunk_ids or [],
    }


def upsert_doc_state(conn, table_name, doc, chunk_ids):
    payload = json.dumps(chunk_ids)
    with conn.cursor() as cur:
        cur.execute(
            f"""
            INSERT INTO {table_name} (doc_id, path, title, version, checksum, chunk_ids, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s::jsonb, NOW())
            ON CONFLICT (doc_id) DO UPDATE SET
                path = EXCLUDED.path,
                title = EXCLUDED.title,
                version = EXCLUDED.version,
                checksum = EXCLUDED.checksum,
                chunk_ids = EXCLUDED.chunk_ids,
                updated_at = NOW()
            """,
            (
                doc.get("doc_id"),
                doc.get("path"),
                doc.get("title"),
                doc.get("version"),
                doc.get("checksum"),
                payload,
            ),
        )
    conn.commit()
