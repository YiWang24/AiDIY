"""Tests for DocStore adapter."""

import os
import pytest

from kb.storage.docstore import DocStore


@pytest.fixture
def test_db_url():
    """Get test database URL from environment."""
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL not set")
    return url


@pytest.fixture
def docstore(test_db_url):
    """Create a DocStore instance for testing."""
    ds = DocStore(test_db_url)
    ds.initialize()

    # Clean up before tests
    with ds._pool.connection() as conn:
        conn.execute("DROP TABLE IF EXISTS kb_documents")
        ds._create_table(conn)

    yield ds

    # Clean up after tests
    with ds._pool.connection() as conn:
        conn.execute("DROP TABLE IF EXISTS kb_documents")

    ds.close()


class TestDocStore:
    """Test DocStore CRUD operations."""

    def test_initialize_creates_table(self, docstore):
        """Test that initialize creates the kb_documents table."""
        with docstore._pool.connection() as conn:
            # Check table exists
            cursor = conn.execute(
                "SELECT COUNT(*) FROM information_schema.tables "
                "WHERE table_name = 'kb_documents'"
            )
            count = cursor.fetchone()[0]
            assert count == 1

    def test_upsert_document_insert(self, docstore):
        """Test inserting a new document."""
        docstore.upsert_document(
            doc_id="doc1",
            path="docs/test.md",
            title="Test Document",
            checksum="abc123",
            chunk_ids=["chunk1", "chunk2"],
        )

        checksum = docstore.get_checksum("doc1")
        assert checksum == "abc123"

    def test_upsert_document_update(self, docstore):
        """Test updating an existing document."""
        # Insert
        docstore.upsert_document(
            doc_id="doc1",
            path="docs/test.md",
            title="Test Document",
            checksum="abc123",
            chunk_ids=["chunk1"],
        )

        # Update
        docstore.upsert_document(
            doc_id="doc1",
            path="docs/test.md",
            title="Test Document",
            checksum="new456",
            chunk_ids=["chunk1", "chunk2", "chunk3"],
        )

        checksum = docstore.get_checksum("doc1")
        assert checksum == "new456"

    def test_get_checksum_not_found(self, docstore):
        """Test getting checksum for non-existent document."""
        checksum = docstore.get_checksum("nonexistent")
        assert checksum is None

    def test_get_chunk_ids(self, docstore):
        """Test getting chunk IDs for a document."""
        docstore.upsert_document(
            doc_id="doc1",
            path="docs/test.md",
            title="Test Document",
            checksum="abc123",
            chunk_ids=["chunk1", "chunk2", "chunk3"],
        )

        chunk_ids = docstore.get_chunk_ids("doc1")
        assert chunk_ids == ["chunk1", "chunk2", "chunk3"]

    def test_get_chunk_ids_not_found(self, docstore):
        """Test getting chunk IDs for non-existent document."""
        chunk_ids = docstore.get_chunk_ids("nonexistent")
        assert chunk_ids == []

    def test_delete_chunks(self, docstore):
        """Test deleting chunks from a document."""
        docstore.upsert_document(
            doc_id="doc1",
            path="docs/test.md",
            title="Test Document",
            checksum="abc123",
            chunk_ids=["chunk1", "chunk2"],
        )

        docstore.delete_chunks("doc1")

        chunk_ids = docstore.get_chunk_ids("doc1")
        assert chunk_ids == []

    def test_delete_document(self, docstore):
        """Test deleting a document."""
        docstore.upsert_document(
            doc_id="doc1",
            path="docs/test.md",
            title="Test Document",
            checksum="abc123",
            chunk_ids=["chunk1"],
        )

        docstore.delete_document("doc1")

        checksum = docstore.get_checksum("doc1")
        assert checksum is None

    def test_list_documents(self, docstore):
        """Test listing all documents."""
        docstore.upsert_document(
            doc_id="doc1",
            path="docs/test1.md",
            title="Doc 1",
            checksum="abc123",
            chunk_ids=["chunk1"],
        )
        docstore.upsert_document(
            doc_id="doc2",
            path="docs/test2.md",
            title="Doc 2",
            checksum="def456",
            chunk_ids=["chunk2"],
        )

        docs = docstore.list_documents()
        assert len(docs) == 2
        assert docs[0]["doc_id"] in ["doc1", "doc2"]
        assert docs[1]["doc_id"] in ["doc1", "doc2"]
