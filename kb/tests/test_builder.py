import unittest
from kb.indexing.builder import build_chunks_for_record


class BuilderTests(unittest.TestCase):
    def test_build_chunks_for_record_produces_metadata(self):
        record = {
            "id": "docs:one",
            "version": "latest",
            "title": "T",
            "path": "docs/x.mdx",
            "content": "# H1\n\nText",
        }
        chunks = build_chunks_for_record(record, chunk_size=200, chunk_overlap=0)
        self.assertTrue(all("doc_id" in c and "chunk_index" in c for c in chunks))


if __name__ == "__main__":
    unittest.main()
