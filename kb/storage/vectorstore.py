"""Vector embeddings storage using PGVector (Gemini-only)."""

from typing import List
import json
import httpx
import re

from psycopg_pool import ConnectionPool

from kb.domain.chunk import Chunk


class VectorStore:
    """Vector embeddings storage adapter (Gemini-only)."""

    TABLE_NAME = "kb_chunks_embedding_3"
    EMBEDDING_DIM = 1024

    def __init__(
        self,
        database_url: str,
        embedding_model: str = "embedding-3",
        gemini_api_key: str = "",
        table_name: str = "",
        batch_size: int = 32,
    ):
        """Initialize VectorStore.

        Args:
            database_url: PostgreSQL connection URL
            embedding_model: Model name (e.g., "embedding-3" for GLM, "models/embedding-001" for Gemini)
            gemini_api_key: Google API key (required)
            table_name: Optional table name override
            batch_size: Default embedding batch size
        """
        self._database_url = database_url
        self._embedding_model = embedding_model
        self._gemini_api_key = gemini_api_key
        self._table_name = table_name
        self._batch_size = batch_size
        self._embeddings: object | None = None
        self._pool: ConnectionPool | None = None

    def initialize(self) -> None:
        """Initialize embeddings model and vector store."""
        if not self._gemini_api_key:
            raise ValueError("Gemini API key is required when using Gemini embeddings")

        self._embeddings = GeminiEmbeddings(
            model=self._embedding_model,
            api_key=self._gemini_api_key,
        )

        # Detect embedding dimension
        test_embedding = self._embeddings.embed_query("test")
        self.EMBEDDING_DIM = len(test_embedding)

        if self._table_name:
            self.TABLE_NAME = self._table_name
        else:
            model_safe = self._embedding_model.replace("/", "_").replace("-", "_")
            self.TABLE_NAME = f"kb_chunks_{model_safe}"

        # Initialize connection pool
        self._pool = ConnectionPool(
            conninfo=self._database_url,
            min_size=1,
            max_size=10,
            open=False,
            kwargs={"autocommit": True},  # Enable autocommit for all connections
        )
        self._pool.open()

        # Create table if not exists
        with self._pool.connection() as conn:
            conn.autocommit = True  # Enable autocommit for this connection
            self._create_table(conn)

    def _create_table(self, conn) -> None:
        """Create vector store table if it doesn't exist."""
        # Enable pgvector extension
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector")

        # Check if table exists and get its vector dimension
        check_table = conn.execute(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = '{self.TABLE_NAME}'
            )
        """).fetchone()[0]

        if check_table:
            # Table exists, check if dimension matches
            try:
                result = conn.execute(f"""
                    SELECT pg_catalog.format_type(atttypid, atttypmod)
                    FROM pg_attribute
                    WHERE attrelid = '{self.TABLE_NAME}'::regclass
                    AND attname = 'embedding'
                """).fetchone()

                if result:
                    existing_dim = _parse_vector_dim(result[0])
                    if existing_dim != self.EMBEDDING_DIM:
                        print(f"Warning: Table {self.TABLE_NAME} has dimension {existing_dim}, "
                              f"but model requires {self.EMBEDDING_DIM}. Recreating table...")
                        conn.execute(f"DROP TABLE {self.TABLE_NAME} CASCADE")
                        check_table = False
            except Exception as e:
                print(f"Warning: Could not check table dimension: {e}")

        # Create table
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.TABLE_NAME} (
                id SERIAL PRIMARY KEY,
                chunk_id VARCHAR(64) UNIQUE NOT NULL,
                doc_id VARCHAR(255) NOT NULL,
                content TEXT NOT NULL,
                heading_path JSONB DEFAULT '[]',
                chunk_index INTEGER DEFAULT 0,
                embedding vector({self.EMBEDDING_DIM}),
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)

        # Create index for similarity search (only if <= 2000 dimensions for ivfflat)
        if self.EMBEDDING_DIM <= 2000:
            try:
                conn.execute(f"""
                    CREATE INDEX IF NOT EXISTS {self.TABLE_NAME}_embedding_idx
                    ON {self.TABLE_NAME}
                    USING ivfflat (embedding vector_cosine_ops)
                    WITH (lists = 100)
                """)
            except Exception:
                pass  # Index may already exist with different parameters
        else:
            # For high-dimensional vectors, use HNSW index if available, or skip index
            try:
                conn.execute(f"""
                    CREATE INDEX IF NOT EXISTS {self.TABLE_NAME}_embedding_idx
                    ON {self.TABLE_NAME}
                    USING hnsw (embedding vector_cosine_ops)
                    WITH (m = 16, ef_construction = 64)
                """)
            except Exception:
                # HNSW not available, skip vector index (still works without index, just slower)
                pass

        # Create index for doc_id lookups
        try:
            conn.execute(f"""
                CREATE INDEX IF NOT EXISTS {self.TABLE_NAME}_doc_id_idx
                ON {self.TABLE_NAME}(doc_id)
            """)
        except Exception:
            pass  # Index may already exist

    def close(self) -> None:
        """Close connections."""
        if self._pool:
            self._pool.close()

    def reset_table(self) -> None:
        """Drop and recreate the embeddings table."""
        if not self._pool:
            raise RuntimeError("VectorStore not initialized")

        with self._pool.connection() as conn:
            conn.autocommit = True  # Enable autocommit for this connection
            conn.execute(f"DROP TABLE IF EXISTS {self.TABLE_NAME} CASCADE")
            self._create_table(conn)

    def add_chunks(self, chunks: List[Chunk], batch_size: int | None = None) -> None:
        """Add chunks with embeddings to vector store.

        Args:
            chunks: List of chunks to embed and store
            batch_size: Number of chunks to embed at once (default: 32)
        """
        if not self._pool or not self._embeddings:
            raise RuntimeError("VectorStore not initialized")

        # Generate embeddings in batches
        effective_batch_size = batch_size or self._batch_size

        for i in range(0, len(chunks), effective_batch_size):
            batch = chunks[i : i + effective_batch_size]
            texts = [chunk.content for chunk in batch]

            # Get embeddings
            embeddings = self._embeddings.embed_documents(texts)

            # Insert batch
            with self._pool.connection() as conn:
                for chunk, embedding in zip(batch, embeddings):
                    conn.execute(f"""
                        INSERT INTO {self.TABLE_NAME}
                        (chunk_id, doc_id, content, heading_path, chunk_index, embedding)
                        VALUES (%s, %s, %s, %s, %s, %s::vector)
                        ON CONFLICT (chunk_id) DO UPDATE SET
                            content = EXCLUDED.content,
                            embedding = EXCLUDED.embedding,
                            heading_path = EXCLUDED.heading_path,
                            chunk_index = EXCLUDED.chunk_index
                    """, (
                        chunk.chunk_id,
                        chunk.doc_id,
                        chunk.content,
                        json.dumps(chunk.heading_path),
                        chunk.chunk_index,
                        "[" + ",".join(str(x) for x in embedding) + "]",
                    ))
                conn.execute("COMMIT")

    def delete_chunks(self, chunk_ids: List[str]) -> None:
        """Delete chunks by chunk_id.

        Args:
            chunk_ids: List of chunk IDs to delete
        """
        if not self._pool:
            raise RuntimeError("VectorStore not initialized")

        with self._pool.connection() as conn:
            for chunk_id in chunk_ids:
                conn.execute(
                    f"DELETE FROM {self.TABLE_NAME} WHERE chunk_id = %s",
                    (chunk_id,),
                )
            conn.execute("COMMIT")

    def delete_by_doc_id(self, doc_id: str) -> None:
        """Delete all chunks for a document.

        Args:
            doc_id: Document ID
        """
        if not self._pool:
            raise RuntimeError("VectorStore not initialized")

        with self._pool.connection() as conn:
            conn.execute(
                f"DELETE FROM {self.TABLE_NAME} WHERE doc_id = %s",
                (doc_id,),
            )
            conn.execute("COMMIT")

    def search(
        self,
        query: str,
        k: int = 10,
        filter_doc_id: str | None = None,
    ) -> List[dict]:
        """Search for similar chunks.

        Args:
            query: Search query text
            k: Number of results to return (default: 10)
            filter_doc_id: Optional filter by document ID

        Returns:
            List of search results with metadata
        """
        if not self._pool or not self._embeddings:
            raise RuntimeError("VectorStore not initialized")

        # Embed query
        query_embedding = self._embeddings.embed_query(query)
        embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

        # Build query
        sql = f"""
            SELECT
                chunk_id,
                doc_id,
                content,
                heading_path,
                chunk_index,
                1 - (embedding <=> %s::vector) as score
            FROM {self.TABLE_NAME}
        """

        params = [embedding_str]

        if filter_doc_id:
            sql += " WHERE doc_id = %s"
            params.append(filter_doc_id)

        sql += f" ORDER BY embedding <=> %s::vector LIMIT {k}"
        params.append(embedding_str)

        with self._pool.connection() as conn:
            conn.autocommit = True  # Enable autocommit for this connection
            cursor = conn.execute(sql, params)
            results = cursor.fetchall()

        return [
            {
                "chunk_id": row[0],
                "doc_id": row[1],
                "content": row[2],
                "heading_path": row[3],
                "chunk_index": row[4],
                "score": float(row[5]),
            }
            for row in results
        ]


def _parse_vector_dim(type_str: str) -> int | None:
    """Parse pgvector type like 'vector(768)' to dimension."""
    match = re.match(r"vector\((\d+)\)", type_str)
    if not match:
        return None
    return int(match.group(1))


class GeminiEmbeddings:
    """Google Gemini embeddings adapter for LangChain.

    Uses the Gemini embedding API via httpx.
    """

    def __init__(
        self,
        model: str = "models/embedding-001",
        api_key: str = "",
        timeout: float = 60.0,
    ):
        """Initialize Gemini embeddings.

        Args:
            model: Model name (models/embedding-001 or models/text-embedding-004)
            api_key: Google API key
            timeout: Request timeout in seconds
        """
        self._model = model
        self._api_key = api_key
        self._timeout = timeout

        if not self._api_key:
            raise ValueError("Google API key is required")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents.

        Args:
            texts: List of text strings

        Returns:
            List of embedding vectors
        """
        return self._embed_batch(texts)

    def embed_query(self, text: str) -> List[float]:
        """Embed a query text.

        Args:
            text: Query text

        Returns:
            Embedding vector
        """
        return self._embed_batch([text])[0]

    def _embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed a batch of texts.

        Args:
            texts: List of text strings

        Returns:
            List of embedding vectors
        """
        url = f"https://generativelanguage.googleapis.com/v1beta/{self._model}:batchEmbedContents?key={self._api_key}"

        headers = {
            "Content-Type": "application/json",
        }

        # Gemini API format
        requests = []
        for text in texts:
            requests.append({
                "model": self._model,
                "content": {
                    "parts": [{"text": text}]
                }
            })

        data = {"requests": requests}

        with httpx.Client(timeout=self._timeout) as client:
            response = client.post(url, json=data, headers=headers)
            response.raise_for_status()
            result = response.json()

        if "embeddings" not in result:
            raise RuntimeError(f"Gemini API returned unexpected response: {result}")

        return [embedding["values"] for embedding in result["embeddings"]]
