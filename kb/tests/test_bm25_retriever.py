from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from kb.config import AppConfig, BM25Config, StorageConfig


class TestBM25Retriever:
    """Test BM25Retriever class"""

    def test_init(self):
        """Test BM25Retriever initialization"""
        import sys
        from unittest.mock import MagicMock

        # Mock spaCy
        mock_spacy = MagicMock()
        sys.modules["spacy"] = mock_spacy

        from kb.retrieval.bm25_retriever import BM25Retriever

        config = AppConfig(
            bm25=BM25Config(persist_dir="test_bm25"),
        )

        retriever = BM25Retriever(config, "test_storage")

        assert retriever.config is config
        assert retriever.persist_dir == Path("test_storage")
        assert retriever._bm25 is None
        assert retriever._nodes is None

        # Cleanup
        del sys.modules["spacy"]

    def test_tokenize_removes_stopwords_and_punctuation(self):
        """Test that tokenization removes stopwords and punctuation"""
        import sys
        from unittest.mock import MagicMock, Mock

        # Mock spaCy
        mock_spacy = MagicMock()
        mock_nlp = MagicMock()

        # Create mock tokens
        mock_token1 = Mock()
        mock_token1.text = "valid"
        mock_token1.is_stop = False
        mock_token1.is_punct = False
        mock_token1.is_space = False

        mock_token2 = Mock()
        mock_token2.text = "the"
        mock_token2.is_stop = True
        mock_token2.is_punct = False
        mock_token2.is_space = False

        mock_token3 = Mock()
        mock_token3.text = "."
        mock_token3.is_stop = False
        mock_token3.is_punct = True
        mock_token3.is_space = False

        mock_token4 = Mock()
        mock_token4.text = " "
        mock_token4.is_stop = False
        mock_token4.is_punct = False
        mock_token4.is_space = True

        mock_doc = MagicMock()
        mock_doc.__iter__ = lambda self: iter([mock_token1, mock_token2, mock_token3, mock_token4])

        mock_nlp.return_value = mock_doc
        mock_nlp.__call__ = lambda x: mock_doc

        # Setup the spacy load mock
        mock_spacy.load.return_value = mock_nlp

        sys.modules["spacy"] = mock_spacy

        from kb.retrieval.bm25_retriever import BM25Retriever

        config = AppConfig(bm25=BM25Config(persist_dir="test_bm25"))
        retriever = BM25Retriever(config, "test_storage")

        tokens = retriever._tokenize("Valid the . ")

        assert tokens == ["valid"]

        # Cleanup
        del sys.modules["spacy"]

    def test_build_index_creates_bm25(self):
        """Test that build_index() creates BM25 index"""
        import sys
        import tempfile
        from unittest.mock import MagicMock, patch

        # Mock spaCy and rank_bm25
        mock_spacy = MagicMock()
        mock_rank_bm25 = MagicMock()

        # Mock the actual BM25Okapi class
        mock_bm25_instance = MagicMock()
        mock_rank_bm25.BM25Okapi = MagicMock(return_value=mock_bm25_instance)

        sys.modules["spacy"] = mock_spacy
        sys.modules["rank_bm25"] = mock_rank_bm25

        from kb.retrieval.bm25_retriever import BM25Retriever

        with tempfile.TemporaryDirectory() as tmpdir:
            config = AppConfig(bm25=BM25Config(persist_dir=tmpdir))

            # Mock nodes
            mock_node = MagicMock()
            mock_node.get_content.return_value = "test content"

            retriever = BM25Retriever(config, tmpdir)
            retriever._nodes = [mock_node]
            retriever._tokenize = lambda x: ["test", "content"]

            # Mock _persist_index to avoid pickling issues
            with patch.object(retriever, '_persist_index'):
                retriever.build_index()

                # Verify BM25Okapi was called
                mock_rank_bm25.BM25Okapi.assert_called_once()

        # Cleanup
        del sys.modules["spacy"]
        del sys.modules["rank_bm25"]

    def test_retrieve_returns_top_nodes(self):
        """Test that retrieve() returns top K nodes"""
        import sys
        from unittest.mock import MagicMock, patch
        import numpy as np

        mock_spacy = MagicMock()

        sys.modules["spacy"] = mock_spacy

        from kb.retrieval.bm25_retriever import BM25Retriever

        config = AppConfig(bm25=BM25Config(persist_dir="test_bm25"))

        # Create mock nodes
        mock_node1 = MagicMock()
        mock_node1.node_id = "node1"
        mock_node1.get_content.return_value = "content 1"

        mock_node2 = MagicMock()
        mock_node2.node_id = "node2"
        mock_node2.get_content.return_value = "content 2"

        mock_node3 = MagicMock()
        mock_node3.node_id = "node3"
        mock_node3.get_content.return_value = "content 3"

        nodes = [mock_node1, mock_node2, mock_node3]

        mock_bm25_instance = MagicMock()
        mock_bm25_instance.get_scores.return_value = np.array([0.9, 0.5, 0.3])

        retriever = BM25Retriever(config, "test_storage")
        retriever._nodes = nodes
        retriever._bm25 = mock_bm25_instance
        retriever._tokenize = lambda x: ["test", "query"]

        # Mock numpy.argsort to return sorted indices (ascending order)
        # The implementation then reverses with [::-1] to get descending
        with patch("numpy.argsort", return_value=np.array([0, 1, 2])):
            results = retriever.retrieve("test query", top_k=2)

        assert len(results) == 2
        # After reversing [0, 1, 2] we get [2, 1], so node3, node2
        assert results[0][0].node_id == "node3"
        assert results[1][0].node_id == "node2"

        # Cleanup
        del sys.modules["spacy"]

    def test_persists_bm25_index(self):
        """Test that BM25 index is persisted to disk"""
        import sys
        import tempfile
        from unittest.mock import MagicMock, patch

        mock_spacy = MagicMock()
        mock_rank_bm25 = MagicMock()

        mock_bm25_instance = MagicMock()
        mock_bm25_class = MagicMock()
        mock_bm25_class.BM25Okapi.return_value = mock_bm25_instance

        sys.modules["spacy"] = mock_spacy
        sys.modules["rank_bm25"] = mock_rank_bm25

        from kb.retrieval.bm25_retriever import BM25Retriever

        with tempfile.TemporaryDirectory() as tmpdir:
            config = AppConfig(bm25=BM25Config(persist_dir=tmpdir))

            mock_node = MagicMock()
            mock_node.get_content.return_value = "test"

            retriever = BM25Retriever(config, tmpdir)
            retriever._nodes = [mock_node]
            retriever._tokenize = lambda x: ["test"]

            # Mock pickle.dump to avoid pickling MagicMock
            with patch("kb.retrieval.bm25_retriever.pickle.dump") as mock_dump:
                retriever.build_index()

                # Verify pickle.dump was called twice (index and nodes)
                assert mock_dump.call_count == 2

        # Cleanup
        del sys.modules["spacy"]
        del sys.modules["rank_bm25"]
