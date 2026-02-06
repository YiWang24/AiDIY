"""Heuristic re-ranking for RAG results.

Implements fast, deterministic re-ranking to improve:
- Exact query match relevance
- Heading match boosting
- Document diversity
"""

import re
from typing import List, Dict
from collections import Counter


class ReRanker:
    """Heuristic re-ranker for retrieved chunks.

    Boosts results based on:
    1. Exact query term matches in content
    2. Query terms in headings
    3. Document diversity (penalize same-doc chunks)
    4. Term frequency scoring

    This is a lightweight, deterministic approach with no LLM calls.
    """

    def __init__(
        self,
        exact_match_boost: float = 0.15,
        heading_boost: float = 0.10,
        diversity_penalty: float = 0.05,
        term_freq_weight: float = 0.05,
    ):
        """Initialize ReRanker.

        Args:
            exact_match_boost: Score boost for exact query matches
            heading_boost: Score boost for query terms in headings
            diversity_penalty: Penalty for additional chunks from same doc
            term_freq_weight: Weight for term frequency scoring
        """
        self.exact_match_boost = exact_match_boost
        self.heading_boost = heading_boost
        self.diversity_penalty = diversity_penalty
        self.term_freq_weight = term_freq_weight

    def rerank(
        self,
        results: List[dict],
        query: str,
    ) -> List[dict]:
        """Re-rank search results using heuristics.

        Args:
            results: List of search results with 'content', 'heading_path', 'score', 'doc_id'
            query: Original search query

        Returns:
            Re-ranked results with adjusted scores
        """
        if not results:
            return []

        # Normalize query
        query_lower = query.lower()
        query_terms = self._extract_terms(query)

        # Track documents for diversity penalty
        doc_occurrences: Dict[str, int] = Counter()

        # Calculate boosts and penalties
        reranked = []
        for result in results:
            # Copy result to avoid mutation
            rerank_result = result.copy()
            base_score = result.get("score", 0.0)

            # Initialize boost/penalty accumulator
            score_adjustment = 0.0

            content = result.get("content", "").lower()
            heading_path = result.get("heading_path", [])
            doc_id = result.get("doc_id", "")

            # 1. Exact match boost
            exact_matches = self._count_exact_matches(query_lower, content)
            if exact_matches > 0:
                score_adjustment += self.exact_match_boost * min(exact_matches, 3) / 3

            # 2. Heading boost
            heading_boost_score = self._calculate_heading_boost(
                query_terms, heading_path
            )
            score_adjustment += heading_boost_score

            # 3. Term frequency scoring
            term_freq_score = self._calculate_term_frequency(query_terms, content)
            score_adjustment += term_freq_score * self.term_freq_weight

            # 4. Diversity penalty (track for later)
            doc_occurrences[doc_id] += 1

            # Apply score adjustment (clamped to [0, 1])
            new_score = max(0.0, min(1.0, base_score + score_adjustment))
            rerank_result["score"] = new_score

            # Store for diversity penalty pass
            rerank_result["_doc_id"] = doc_id
            reranked.append(rerank_result)

        # Apply diversity penalty (second pass)
        for result in reranked:
            doc_id = result.get("_doc_id", "")
            occurrence_count = doc_occurrences.get(doc_id, 1)

            if occurrence_count > 1:
                # Penalize subsequent chunks from same doc
                penalty = self.diversity_penalty * (occurrence_count - 1)
                result["score"] = max(0.0, result["score"] - penalty)

            # Clean up temporary field
            result.pop("_doc_id", None)

        # Sort by adjusted score
        reranked.sort(key=lambda x: x.get("score", 0.0), reverse=True)

        return reranked

    def _extract_terms(self, query: str) -> List[str]:
        """Extract meaningful terms from query.

        Args:
            query: Search query

        Returns:
            List of query terms (lowercase, no stop words)
        """
        # Simple tokenization
        terms = re.findall(r"\b\w+\b", query.lower())

        # Filter stop words
        stop_words = {
            "a",
            "an",
            "the",
            "and",
            "or",
            "but",
            "is",
            "are",
            "was",
            "were",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "from",
            "as",
            "how",
            "what",
            "where",
            "when",
            "why",
            "who",
            "which",
            "that",
        }

        return [t for t in terms if t not in stop_words and len(t) > 2]

    def _count_exact_matches(self, query: str, content: str) -> int:
        """Count exact query matches in content.

        Args:
            query: Query string (lowercase)
            content: Content string (lowercase)

        Returns:
            Number of exact matches
        """
        # Count occurrences of full query
        return content.count(query)

    def _calculate_heading_boost(
        self,
        query_terms: List[str],
        heading_path: List[str],
    ) -> float:
        """Calculate heading match boost.

        Args:
            query_terms: Query terms
            heading_path: List of heading strings

        Returns:
            Heading boost score
        """
        if not heading_path:
            return 0.0

        # Flatten heading path to single string
        heading_text = " ".join(heading_path).lower()

        # Count query term matches in headings
        matches = sum(1 for term in query_terms if term in heading_text)

        if matches == 0:
            return 0.0

        # Boost increases with number of matches (capped at heading_boost)
        return self.heading_boost * min(matches / len(query_terms), 1.0)

    def _calculate_term_frequency(
        self,
        query_terms: List[str],
        content: str,
    ) -> float:
        """Calculate term frequency score.

        Args:
            query_terms: Query terms
            content: Content string

        Returns:
            Term frequency score (normalized to [0, 1])
        """
        if not query_terms:
            return 0.0

        # Count term occurrences
        term_counts: Dict[str, int] = {}
        for term in query_terms:
            term_counts[term] = content.count(term)

        # Calculate score as fraction of terms found
        terms_found = sum(1 for count in term_counts.values() if count > 0)

        if terms_found == 0:
            return 0.0

        # Bonus for multiple occurrences
        total_occurrences = sum(term_counts.values())
        occurrence_bonus = min(total_occurrences / (len(query_terms) * 2), 0.5)

        return (terms_found / len(query_terms)) * 0.5 + occurrence_bonus * 0.5
