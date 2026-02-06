"""Tests for document cleaner and full pipeline."""

import json
import tempfile
from pathlib import Path

import pytest

from kb.pipeline.pipeline import OfflineKBPipeline


@pytest.fixture
def sample_mdx_content():
    """Sample MDX content for testing."""
    return """---
title: Test Document
author: Test Author
tags: [test, example]
---

# Introduction

This is the introduction.

## Code Example

```python
def hello():
    print("Hello, world!")
```

## More Content

This is more content.
"""


@pytest.fixture
def temp_mdx_file(sample_mdx_content):
    """Create a temporary MDX file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".mdx", delete=False) as f:
        f.write(sample_mdx_content)
        temp_path = f.name

    yield temp_path

    # Cleanup
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def temp_mdx_directory():
    """Create a temporary directory with MDX files."""
    import tempfile
    import shutil

    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir)

    # Create sample files
    (temp_path / "doc1.md").write_text("""---
title: Document 1
---

# Doc 1

Content 1.
""")

    (temp_path / "doc2.mdx").write_text("""---
title: Document 2
---

# Doc 2

Content 2.
""")

    (temp_path / "subdir").mkdir()
    (temp_path / "subdir" / "doc3.md").write_text("""# Doc 3

Content 3.
""")

    yield str(temp_dir)

    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


class TestOfflineKBPipeline:
    """Test offline KB pipeline."""

    @pytest.fixture
    def test_db_url(self):
        """Get test database URL."""
        import os

        url = os.environ.get("TEST_DATABASE_URL")
        if not url:
            pytest.skip("TEST_DATABASE_URL not set")
        return url

    @pytest.fixture
    def test_jsonl(self, temp_mdx_directory):
        """Create test JSONL file."""
        import hashlib
        from pathlib import Path as Pathlib

        output_file = tempfile.mktemp(suffix=".jsonl")

        # Manually create JSONL with test documents
        docs = [
            {
                "id": "doc1",
                "path": "doc1.md",
                "title": "Document 1",
                "checksum": hashlib.sha256(b"Content 1.").hexdigest(),
                "content": "# Doc 1\n\nContent 1.",
                "frontmatter": {"title": "Document 1"},
            },
            {
                "id": "doc2",
                "path": "doc2.mdx",
                "title": "Document 2",
                "checksum": hashlib.sha256(b"Content 2.").hexdigest(),
                "content": "# Doc 2\n\nContent 2.",
                "frontmatter": {"title": "Document 2"},
            },
            {
                "id": "subdir_doc3",
                "path": "subdir/doc3.md",
                "title": "Doc 3",
                "checksum": hashlib.sha256(b"Content 3.").hexdigest(),
                "content": "# Doc 3\n\nContent 3.",
                "frontmatter": {},
            },
        ]

        with open(output_file, "w") as f:
            for doc in docs:
                f.write(json.dumps(doc) + "\n")

        yield output_file

        # Cleanup
        Pathlib(output_file).unlink(missing_ok=True)

    def test_incremental_build(self, test_db_url, test_jsonl):
        """Test incremental build mode."""
        pipeline = OfflineKBPipeline(database_url=test_db_url)

        # First run - should index all
        stats1 = pipeline.build_index(test_jsonl, force_rebuild=False)

        assert stats1["total"] == 3
        assert stats1["indexed"] == 3
        assert stats1["skipped"] == 0

        # Second run - should skip all (incremental)
        stats2 = pipeline.build_index(test_jsonl, force_rebuild=False)

        assert stats2["total"] == 3
        assert stats2["indexed"] == 0
        assert stats2["skipped"] == 3

    def test_full_rebuild(self, test_db_url, test_jsonl):
        """Test full rebuild mode."""
        pipeline = OfflineKBPipeline(database_url=test_db_url)

        # First run
        stats1 = pipeline.build_index(test_jsonl, force_rebuild=True)

        assert stats1["total"] == 3
        assert stats1["indexed"] == 3

        # Second run with force_rebuild - should reindex all
        stats2 = pipeline.build_index(test_jsonl, force_rebuild=True)

        assert stats2["total"] == 3
        assert stats2["indexed"] == 3  # Reindexed, not skipped
        assert stats2["skipped"] == 0
