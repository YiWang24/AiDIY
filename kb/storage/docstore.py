"""Document metadata storage using psycopg3."""

import json
from dataclasses import dataclass
from psycopg import Connection
from psycopg_pool import ConnectionPool


@dataclass
class DocumentRow:
    """Row from kb_documents table."""

    doc_id: str
    path: str
    title: str
    checksum: str
    chunk_ids: list[str]


class DocStore:
    """Document metadata storage adapter.

    Manages document metadata, checksums, and chunk ID tracking
    using PostgreSQL with psycopg3 connection pooling.
    """

    def __init__(self, database_url: str):
        """Initialize DocStore.

        Args:
            database_url: PostgreSQL connection URL
        """
        self._database_url = database_url
        self._pool: ConnectionPool | None = None

    def initialize(self) -> None:
        """Initialize connection pool and create table if needed."""
        self._pool = ConnectionPool(
            conninfo=self._database_url,
            min_size=1,
            max_size=10,
            open=False,
        )

        self._pool.open()

        # Create table if not exists
        with self._pool.connection() as conn:
            self._create_table(conn)
            self._create_meta_table(conn)

    def _create_table(self, conn: Connection) -> None:
        """Create kb_documents table if it doesn't exist."""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS kb_documents (
                doc_id VARCHAR(255) PRIMARY KEY,
                path VARCHAR(1024) NOT NULL,
                title VARCHAR(512) NOT NULL,
                version VARCHAR(64) NOT NULL DEFAULT 'latest',
                checksum VARCHAR(64) NOT NULL,
                chunk_ids JSONB NOT NULL DEFAULT '[]',
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)

    def _create_meta_table(self, conn: Connection) -> None:
        """Create kb_index_meta table if it doesn't exist."""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS kb_index_meta (
                key VARCHAR(64) PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)

    def close(self) -> None:
        """Close connection pool."""
        if self._pool:
            self._pool.close()

    def get_checksum(self, doc_id: str) -> str | None:
        """Get checksum for a document.

        Args:
            doc_id: Document identifier

        Returns:
            Checksum string or None if not found
        """
        if not self._pool:
            raise RuntimeError("DocStore not initialized")

        with self._pool.connection() as conn:
            cursor = conn.execute(
                "SELECT checksum FROM kb_documents WHERE doc_id = %s",
                (doc_id,),
            )
            row = cursor.fetchone()

            return row[0] if row else None

    def get_chunk_ids(self, doc_id: str) -> list[str]:
        """Get chunk IDs for a document.

        Args:
            doc_id: Document identifier

        Returns:
            List of chunk IDs (empty if not found)
        """
        if not self._pool:
            raise RuntimeError("DocStore not initialized")

        with self._pool.connection() as conn:
            cursor = conn.execute(
                "SELECT chunk_ids FROM kb_documents WHERE doc_id = %s",
                (doc_id,),
            )
            row = cursor.fetchone()

            return row[0] if row else []

    def upsert_document(
        self,
        doc_id: str,
        path: str,
        title: str,
        checksum: str,
        chunk_ids: list[str],
        version: str = "latest",
    ) -> None:
        """Insert or update a document.

        Args:
            doc_id: Document identifier
            path: File path
            title: Document title
            checksum: Content checksum
            chunk_ids: List of chunk IDs
            version: Document version (default: "latest")
        """
        if not self._pool:
            raise RuntimeError("DocStore not initialized")

        with self._pool.connection() as conn:
            conn.execute(
                """
                INSERT INTO kb_documents (doc_id, path, title, version, checksum, chunk_ids)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (doc_id) DO UPDATE SET
                    path = EXCLUDED.path,
                    title = EXCLUDED.title,
                    version = EXCLUDED.version,
                    checksum = EXCLUDED.checksum,
                    chunk_ids = EXCLUDED.chunk_ids,
                    updated_at = NOW()
            """,
                (doc_id, path, title, version, checksum, json.dumps(chunk_ids)),
            )

    def delete_chunks(self, doc_id: str) -> None:
        """Delete chunk IDs from a document.

        Args:
            doc_id: Document identifier
        """
        if not self._pool:
            raise RuntimeError("DocStore not initialized")

        with self._pool.connection() as conn:
            conn.execute(
                "UPDATE kb_documents SET chunk_ids = '[]' WHERE doc_id = %s",
                (doc_id,),
            )

    def delete_document(self, doc_id: str) -> None:
        """Delete a document.

        Args:
            doc_id: Document identifier
        """
        if not self._pool:
            raise RuntimeError("DocStore not initialized")

        with self._pool.connection() as conn:
            conn.execute(
                "DELETE FROM kb_documents WHERE doc_id = %s",
                (doc_id,),
            )

    def list_documents(self) -> list[dict]:
        """List all documents.

        Returns:
            List of document dicts
        """
        if not self._pool:
            raise RuntimeError("DocStore not initialized")

        with self._pool.connection() as conn:
            cursor = conn.execute("""
                SELECT doc_id, path, title, checksum, chunk_ids
                FROM kb_documents
                ORDER BY created_at DESC
            """)

            return [
                {
                    "doc_id": row[0],
                    "path": row[1],
                    "title": row[2],
                    "checksum": row[3],
                    "chunk_ids": row[4],
                }
                for row in cursor.fetchall()
            ]

    def get_index_signature(self) -> str | None:
        """Get the current index signature if present."""
        if not self._pool:
            raise RuntimeError("DocStore not initialized")

        with self._pool.connection() as conn:
            cursor = conn.execute(
                "SELECT value FROM kb_index_meta WHERE key = %s",
                ("index_signature",),
            )
            row = cursor.fetchone()
            return row[0] if row else None

    def set_index_signature(self, signature: str) -> None:
        """Set or update the index signature."""
        if not self._pool:
            raise RuntimeError("DocStore not initialized")

        with self._pool.connection() as conn:
            conn.execute(
                """
                INSERT INTO kb_index_meta (key, value)
                VALUES (%s, %s)
                ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
            """,
                ("index_signature", signature),
            )

    def clear_documents(self) -> None:
        """Remove all documents metadata (used for rebuilds)."""
        if not self._pool:
            raise RuntimeError("DocStore not initialized")

        with self._pool.connection() as conn:
            conn.execute("TRUNCATE TABLE kb_documents")
