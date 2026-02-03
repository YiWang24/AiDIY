from __future__ import annotations

from kb.config import AppConfig


def reciprocal_rank_fusion(
    results_list: list[list[tuple[object, float]]],
    k: int = 60
) -> list[tuple[object, float]]:
    """Reciprocal Rank Fusion (RRF) algorithm.

    RRF combines multiple ranked lists into a single ranked list.
    It is score-agnostic, meaning it works regardless of the scale
    of scores in individual result lists.

    Formula: score(item) = sum(1 / (k + rank + 1)) for each list

    Args:
        results_list: List of result lists, where each result list
                     contains (item, score) tuples
        k: RRF constant (default 60 is commonly used)

    Returns:
        List of (item, fused_score) tuples sorted by fused score descending
    """
    scores = {}

    for results in results_list:
        for rank, (item, _) in enumerate(results):
            if item not in scores:
                scores[item] = 0.0
            scores[item] += 1.0 / (k + rank + 1)

    # Sort by score descending
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)


class HybridRetriever:
    """Hybrid retrieval combining Vector and BM25 using RRF."""

    def __init__(self, vector, bm25, config: AppConfig):
        """Initialize hybrid retriever.

        Args:
            vector: VectorRetriever instance
            bm25: BM25Retriever instance
            config: Application configuration
        """
        self.vector = vector
        self.bm25 = bm25
        self.config = config

    def retrieve(self, query: str, top_k: int = 10):
        """Retrieve using hybrid search with RRF fusion.

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of (node, fused_score) tuples
        """
        # Recall more results from each retriever for better fusion
        # Using 2x recall is a common practice
        recall_k = top_k * 2

        # Get results from both retrievers
        vector_results = self.vector.retrieve(query, top_k=recall_k)

        # Convert vector results to (node, score) tuples
        vector_tuples = [
            (result.node, result.score)
            for result in vector_results
        ]

        # Get BM25 results (already in tuple format)
        bm25_results = self.bm25.retrieve(query, top_k=recall_k)

        # Use RRF to fuse results
        fused = reciprocal_rank_fusion(
            [vector_tuples, bm25_results],
            k=self.config.retrieval.rrf_k
        )

        # Return top_k results
        return fused[:top_k]
