"""Vector embeddings storage using langchain-postgres PGVector."""

from typing import List

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector

from kb.domain.chunk import Chunk


class VectorStore:
    """Vector embeddings storage using langchain PGVector.

    Uses langchain for storage (add/delete) but provides minimal SQL wrapper
    for embedding-based search (required by hybrid search systems).
    """

    EMBEDDING_DIM = 1024  # Will be updated based on model

    def __init__(
        self,
        database_url: str,
        embedding_model: str = "models/gemini-embedding-001",
        gemini_api_key: str = "",
        table_name: str = "",
        batch_size: int = 32,
    ):
        """Initialize VectorStore.

        Args:
            database_url: PostgreSQL connection URL
            embedding_model: Model name (default: models/gemini-embedding-001)
            gemini_api_key: Google API key (required)
            table_name: Optional table name override
            batch_size: Default embedding batch size
        """
        self._database_url = database_url
        self._embedding_model = embedding_model
        self._gemini_api_key = gemini_api_key
        self._table_name = table_name or self._default_table_name()
        self._batch_size = batch_size

        self._embeddings: GoogleGenerativeAIEmbeddings | None = None
        self._vectorstore: PGVector | None = None

    def _default_table_name(self) -> str:
        """Generate default table name from embedding model."""
        model_safe = self._embedding_model.replace("/", "_").replace("-", "_")
        return f"kb_chunks_{model_safe}"

    def initialize(self) -> None:
        """Initialize embeddings model and PGVector store."""
        if not self._gemini_api_key:
            raise ValueError("Gemini API key is required for embeddings")

        # Use langchain's GoogleGenerativeAIEmbeddings
        self._embeddings = GoogleGenerativeAIEmbeddings(
            model=self._embedding_model,
            google_api_key=self._gemini_api_key,
        )

        # Infer embedding dimension from model
        self.EMBEDDING_DIM = _infer_embedding_dim(self._embedding_model)

        # Use langchain's PGVector for storage
        self._vectorstore = PGVector(
            embeddings=self._embeddings,
            collection_name=self._table_name,
            connection=self._database_url,
            use_jsonb=True,
        )

        # Create table and indexes using langchain
        self._vectorstore.create_tables_if_not_exists()

    def close(self) -> None:
        """Close connections (handled by langchain)."""
        pass

    def reset_table(self) -> None:
        """Drop and recreate the embeddings table."""
        if not self._vectorstore:
            raise RuntimeError("VectorStore not initialized")

        # Use langchain's drop_tables
        self._vectorstore.drop_tables()
        self._vectorstore.create_tables_if_not_exists()

    def add_chunks(self, chunks: List[Chunk], batch_size: int | None = None) -> None:
        """Add chunks with embeddings using langchain PGVector.

        Args:
            chunks: List of chunks to embed and store
            batch_size: Number of chunks to embed at once (default: 32)
        """
        if not self._vectorstore:
            raise RuntimeError("VectorStore not initialized")

        # Prepare texts and metadata for langchain
        texts = [chunk.content for chunk in chunks]
        metadatas = [
            {
                "chunk_id": chunk.chunk_id,
                "doc_id": chunk.doc_id,
                "heading_path": chunk.heading_path,
                "chunk_index": chunk.chunk_index,
            }
            for chunk in chunks
        ]
        ids = [chunk.chunk_id for chunk in chunks]

        # Use langchain's add_texts
        self._vectorstore.add_texts(
            texts=texts,
            metadatas=metadatas,
            ids=ids,
        )

    def delete_chunks(self, chunk_ids: List[str]) -> None:
        """Delete chunks by chunk_id using langchain PGVector.

        Args:
            chunk_ids: List of chunk IDs to delete
        """
        if not self._vectorstore:
            raise RuntimeError("VectorStore not initialized")

        # Use langchain's delete by filter
        for chunk_id in chunk_ids:
            self._vectorstore.delete(filter={"chunk_id": chunk_id})

    def search_by_text(
        self,
        query_text: str,
        top_k: int = 10,
        score_threshold: float | None = None,
    ) -> List[dict]:
        """Search by query text using langchain PGVector.

        Args:
            query_text: Query text (will be embedded by PGVector)
            top_k: Number of results to return
            score_threshold: Minimum similarity score (0-1)

        Returns:
            List of dicts with chunk_id, doc_id, content, heading_path, score
        """
        if not self._vectorstore:
            raise RuntimeError("VectorStore not initialized")

        # Use langchain's similarity_search_with_score
        docs_with_scores = self._vectorstore.similarity_search_with_score(
            query=query_text,
            k=top_k,
            score_threshold=score_threshold,
        )

        # Convert to our format
        return [
            {
                "chunk_id": doc.metadata.get("chunk_id", ""),
                "doc_id": doc.metadata.get("doc_id", ""),
                "content": doc.page_content,
                "heading_path": doc.metadata.get("heading_path", []),
                "chunk_index": doc.metadata.get("chunk_index", 0),
                "score": float(score),
            }
            for doc, score in docs_with_scores
        ]

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        score_threshold: float | None = None,
    ) -> List[dict]:
        """Search by pre-computed embedding (minimal SQL wrapper).

        Note: PGVector handles embeddings internally. This method exists for
        hybrid search systems that need to search with pre-computed embeddings.

        Args:
            query_embedding: Query vector embedding
            top_k: Number of results to return
            score_threshold: Minimum similarity score (0-1)

        Returns:
            List of dicts with chunk_id, doc_id, content, heading_path, score
        """
        if not self._vectorstore:
            raise RuntimeError("VectorStore not initialized")

        # Use langchain's connection for minimal SQL
        connection = self._vectorstore.connection

        # Build minimal SQL for cosine similarity search
        embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"
        table_name = self._vectorstore.collection_name

        sql = f"""
            SELECT
                chunk_id,
                doc_id,
                content,
                heading_path,
                chunk_index,
                1 - (embedding <=> %s::vector) AS score
            FROM {table_name}
        """

        if score_threshold is not None:
            sql += f" WHERE 1 - (embedding <=> %s::vector) >= {score_threshold}"

        sql += f" ORDER BY embedding <=> %s::vector LIMIT {top_k}"

        results = connection.execute(sql, [embedding_str, embedding_str]).fetchall()

        return [
            {
                "chunk_id": row[0],
                "doc_id": row[1],
                "content": row[2],
                "heading_path": row[3] if row[3] else [],
                "chunk_index": row[4],
                "score": row[5],
            }
            for row in results
        ]

    def get_chunk_count(self) -> int:
        """Get total number of chunks in the store."""
        if not self._vectorstore:
            raise RuntimeError("VectorStore not initialized")

        connection = self._vectorstore.connection
        result = connection.execute(
            f"SELECT COUNT(*) FROM {self._vectorstore.collection_name}"
        ).fetchone()
        return result[0] if result else 0


def _infer_embedding_dim(model: str) -> int:
    """Infer embedding dimension from model name.

    Args:
        model: Model name (e.g., "models/gemini-embedding-001")

    Returns:
        Embedding dimension
    """
    if "gemini-embedding-001" in model:
        return 768
    elif "text-embedding-004" in model:
        return 768
    else:
        return 1024
