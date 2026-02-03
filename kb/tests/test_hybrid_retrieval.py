from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from kb.config import AppConfig, RetrievalConfig


class TestReciprocalRankFusion:
    """Test Reciprocal Rank Fusion (RRF) algorithm"""

    def test_rrf_basic(self):
        """Test basic RRF fusion with two result lists"""
        from kb.retrieval.hybrid import reciprocal_rank_fusion

        # Create two lists of results
        # List 1: items A, B, C with scores 0.9, 0.8, 0.7
        item_a = MagicMock()
        item_b = MagicMock()
        item_c = MagicMock()

        results1 = [(item_a, 0.9), (item_b, 0.8), (item_c, 0.7)]

        # List 2: items B, A, D with scores 0.95, 0.85, 0.6
        item_d = MagicMock()
        results2 = [(item_b, 0.95), (item_a, 0.85), (item_d, 0.6)]

        # Fuse with k=60
        fused = reciprocal_rank_fusion([results1, results2], k=60)

        # Expected scores:
        # A: rank 0 in list1, rank 1 in list2
        #    score = 1/(60+0+1) + 1/(60+1+1) = 1/61 + 1/62 ≈ 0.0325
        # B: rank 1 in list1, rank 0 in list2
        #    score = 1/(60+1+1) + 1/(60+0+1) = 1/62 + 1/61 ≈ 0.0325
        # C: rank 2 in list1, not in list2
        #    score = 1/(60+2+1) = 1/63 ≈ 0.0159
        # D: not in list1, rank 2 in list2
        #    score = 1/(60+2+1) = 1/63 ≈ 0.0159

        assert len(fused) == 4
        # A and B should have highest scores (tied or nearly tied)
        assert fused[0][0] in [item_a, item_b]
        assert fused[1][0] in [item_a, item_b]

    def test_rrf_with_different_k(self):
        """Test RRF with different k values"""
        from kb.retrieval.hybrid import reciprocal_rank_fusion

        item_a = MagicMock()
        item_b = MagicMock()

        results1 = [(item_a, 0.9)]
        results2 = [(item_b, 0.8)]

        # With k=10, smaller k emphasizes rank more
        fused_k10 = reciprocal_rank_fusion([results1, results2], k=10)
        # With k=100, larger k smooths scores
        fused_k100 = reciprocal_rank_fusion([results1, results2], k=100)

        # Both should have same items
        assert len(fused_k10) == 2
        assert len(fused_k100) == 2

        # k=10 should give more differentiated scores
        assert fused_k10[0][1] > fused_k100[0][1]

    def test_rrf_single_list(self):
        """Test RRF with a single result list"""
        from kb.retrieval.hybrid import reciprocal_rank_fusion

        item_a = MagicMock()
        item_b = MagicMock()

        results = [(item_a, 0.9), (item_b, 0.8)]

        fused = reciprocal_rank_fusion([results], k=60)

        assert len(fused) == 2
        assert fused[0][0] is item_a
        assert fused[1][0] is item_b

    def test_rrf_empty_lists(self):
        """Test RRF with empty result lists"""
        from kb.retrieval.hybrid import reciprocal_rank_fusion

        fused = reciprocal_rank_fusion([], k=60)

        assert len(fused) == 0

    def test_rrf_handles_duplicate_items(self):
        """Test that RRF properly handles items appearing in multiple lists"""
        from kb.retrieval.hybrid import reciprocal_rank_fusion

        item = MagicMock()
        results1 = [(item, 0.9)]
        results2 = [(item, 0.8)]
        results3 = [(item, 0.7)]

        fused = reciprocal_rank_fusion([results1, results2, results3], k=60)

        # Should only have one item with combined score
        assert len(fused) == 1
        assert fused[0][0] is item
        # Score should be sum of contributions from all 3 lists
        # Each at rank 0: 3 * (1/(60+0+1)) = 3/61 ≈ 0.049
        assert fused[0][1] > 0.04


class TestHybridRetriever:
    """Test HybridRetriever class"""

    def test_init(self):
        """Test HybridRetriever initialization"""
        import sys
        from unittest.mock import MagicMock

        # Mock modules
        sys.modules["spacy"] = MagicMock()
        sys.modules["llama_index.core"] = MagicMock()
        sys.modules["llama_index.embeddings.huggingface"] = MagicMock()

        from kb.retrieval.hybrid import HybridRetriever
        from kb.retrieval.vector_retriever import VectorRetriever
        from kb.retrieval.bm25_retriever import BM25Retriever

        config = AppConfig()

        mock_vector = MagicMock(spec=VectorRetriever)
        mock_bm25 = MagicMock(spec=BM25Retriever)

        retriever = HybridRetriever(mock_vector, mock_bm25, config)

        assert retriever.vector is mock_vector
        assert retriever.bm25 is mock_bm25
        assert retriever.config is config

        # Cleanup
        del sys.modules["spacy"]
        del sys.modules["llama_index.core"]
        del sys.modules["llama_index.embeddings.huggingface"]

    def test_retrieve_calls_both_retrievers(self):
        """Test that retrieve calls both vector and BM25 retrievers"""
        import sys
        from unittest.mock import MagicMock

        sys.modules["spacy"] = MagicMock()
        sys.modules["llama_index.core"] = MagicMock()
        sys.modules["llama_index.embeddings.huggingface"] = MagicMock()

        from kb.retrieval.hybrid import HybridRetriever
        from kb.retrieval.vector_retriever import VectorRetriever
        from kb.retrieval.bm25_retriever import BM25Retriever

        config = AppConfig(retrieval=RetrievalConfig(rrf_k=60))

        mock_vector = MagicMock(spec=VectorRetriever)
        mock_bm25 = MagicMock(spec=BM25Retriever)

        # Create mock nodes
        mock_node1 = MagicMock()
        mock_node1.node_id = "node1"
        mock_node2 = MagicMock()
        mock_node2.node_id = "node2"

        # Setup vector retriever to return nodes with score attribute
        mock_result1 = MagicMock()
        mock_result1.node = mock_node1
        mock_result1.score = 0.9
        mock_result2 = MagicMock()
        mock_result2.node = mock_node2
        mock_result2.score = 0.8

        mock_vector.retrieve.return_value = [mock_result1, mock_result2]

        # Setup BM25 retriever to return tuples
        mock_bm25.retrieve.return_value = [(mock_node2, 0.95), (mock_node1, 0.85)]

        retriever = HybridRetriever(mock_vector, mock_bm25, config)
        results = retriever.retrieve("test query", top_k=5)

        # Verify both retrievers were called with recall_k = top_k * 2
        mock_vector.retrieve.assert_called_once_with("test query", top_k=10)
        mock_bm25.retrieve.assert_called_once_with("test query", top_k=10)

        # Verify we get results back
        assert len(results) > 0

        # Cleanup
        del sys.modules["spacy"]
        del sys.modules["llama_index.core"]
        del sys.modules["llama_index.embeddings.huggingface"]

    def test_retrieve_limits_results(self):
        """Test that retrieve respects top_k parameter"""
        import sys
        from unittest.mock import MagicMock

        sys.modules["spacy"] = MagicMock()
        sys.modules["llama_index.core"] = MagicMock()
        sys.modules["llama_index.embeddings.huggingface"] = MagicMock()

        from kb.retrieval.hybrid import HybridRetriever
        from kb.retrieval.vector_retriever import VectorRetriever
        from kb.retrieval.bm25_retriever import BM25Retriever

        config = AppConfig(retrieval=RetrievalConfig(rrf_k=60))

        mock_vector = MagicMock(spec=VectorRetriever)
        mock_bm25 = MagicMock(spec=BM25Retriever)

        # Create mock nodes
        mock_nodes = [MagicMock(node_id=f"node{i}") for i in range(20)]

        # Setup retrievers to return many results
        vector_results = []
        for node in mock_nodes[:20]:
            mr = MagicMock()
            mr.node = node
            mr.score = 0.9
            vector_results.append(mr)

        bm25_results = [(node, 0.8) for node in mock_nodes[:20]]

        mock_vector.retrieve.return_value = vector_results
        mock_bm25.retrieve.return_value = bm25_results

        retriever = HybridRetriever(mock_vector, mock_bm25, config)
        results = retriever.retrieve("test query", top_k=5)

        # Should only return top_k results
        assert len(results) == 5

        # Cleanup
        del sys.modules["spacy"]
        del sys.modules["llama_index.core"]
        del sys.modules["llama_index.embeddings.huggingface"]
