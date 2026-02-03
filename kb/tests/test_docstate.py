import unittest
from kb.indexing.docstate import should_process


class DocStateTests(unittest.TestCase):
    def test_should_skip_when_checksum_same(self):
        self.assertFalse(should_process("abc", "abc"))

    def test_should_process_when_checksum_diff(self):
        self.assertTrue(should_process("abc", "def"))


if __name__ == "__main__":
    unittest.main()
