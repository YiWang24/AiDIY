import unittest
from kb.indexing.chunking import split_document, build_chunk_id


class ChunkingTests(unittest.TestCase):
    def test_chunk_ids_stable(self):
        record = {
            "id": "docs:sample",
            "version": "latest",
            "content": "# Title\n\nHello world.",
        }
        chunks_a = split_document(record, chunk_size=200, chunk_overlap=0)
        chunks_b = split_document(record, chunk_size=200, chunk_overlap=0)
        self.assertEqual(
            [c["chunk_id"] for c in chunks_a], [c["chunk_id"] for c in chunks_b]
        )

    def test_heading_path_present(self):
        record = {
            "id": "docs:sample",
            "version": "latest",
            "content": "# H1\n\n## H2\n\nText",
        }
        chunks = split_document(record, chunk_size=200, chunk_overlap=0)
        self.assertTrue(any(c["heading_path"] == ["H1", "H2"] for c in chunks))


if __name__ == "__main__":
    unittest.main()
