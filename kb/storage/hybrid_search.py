"""Hybrid semantic + keyword search using Reciprocal Rank Fusion (RRF).

Combines vector similarity search with PostgreSQL full-text search
for better precision on keyword-heavy queries.
"""

from typing import List, Dict


class HybridSearcher:
    """Hybrid searcher combining semantic and keyword search.

    Uses Reciprocal Rank Fusion (RRF) to combine results from:
    - Semantic search (vector similarity)
    - Keyword search (PostgreSQL full-text search)

    RRF formula: score = alpha / (k + rank_semantic) + (1 - alpha) / (k + rank_keyword)
    where k is a constant (default 60) and alpha controls semantic vs keyword weight.
    """

    def __init__(
        self,
        vector_store,
        doc_store,
        alpha: float = 0.7,
        rrf_k: int = 60,
    ):
        """Initialize HybridSearcher.

        Args:
            vector_store: Vector store for semantic search
            doc_store: Document store for keyword search
            alpha: Semantic search weight (0.0 = keyword only, 1.0 = semantic only)
            rrf_k: RRF constant (higher = more rank fusion, default 60)
        """
        self._vector_store = vector_store
        self._doc_store = doc_store
        self.alpha = alpha
        self.rrf_k = rrf_k

        # Initialize full-text search index if needed
        self._ensure_fts_index()

    def _ensure_fts_index(self) -> None:
        """Ensure full-text search GIN index exists on the chunks table."""
        # This requires database access - we'll do this on first search
        pass

    def _keyword_search(self, query: str, k: int) -> List[dict]:
        """Perform full-text keyword search.

        Args:
            query: Search query
            k: Number of results

        Returns:
            List of results with ts_rank scores
        """
        # Get the table name from vector store
        table_name = self._vector_store.TABLE_NAME

        # Check if full-text search is available
        # First try: if there's a content_tsv column, use it
        # Otherwise, fall back to simple LIKE queries

        if not hasattr(self._vector_store, "_pool") or self._vector_store._pool is None:
            return []

        try:
            with self._vector_store._pool.connection() as conn:
                conn.autocommit = True

                # Check for content_tsv column (tsvector for full-text search)
                check_column = conn.execute(f"""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = '{table_name}'
                        AND column_name = 'content_tsv'
                    )
                """).fetchone()[0]

                if check_column:
                    # Use full-text search with ts_rank
                    sql = f"""
                        SELECT
                            chunk_id,
                            doc_id,
                            content,
                            heading_path,
                            chunk_index,
                            ts_rank(content_tsv, to_tsquery('english', $1)) as score
                        FROM {table_name}
                        WHERE content_tsv @@ to_tsquery('english', $1)
                        ORDER BY score DESC
                        LIMIT $2
                    """
                    cursor = conn.execute(sql, (self._query_to_tsquery(query), k))
                    results = cursor.fetchall()

                    return [
                        {
                            "chunk_id": row[0],
                            "doc_id": row[1],
                            "content": row[2],
                            "heading_path": row[3],
                            "chunk_index": row[4],
                            "score": float(row[5]) if row[5] else 0.0,
                        }
                        for row in results
                    ]
                else:
                    # Fallback: simple ILIKE search (less accurate but works)
                    # Search for query terms in content
                    search_terms = query.split()
                    where_clauses = []
                    params = []

                    for term in search_terms[:5]:  # Limit to 5 terms
                        where_clauses.append("content ILIKE %s")
                        params.append(f"%{term}%")

                    sql = f"""
                        SELECT
                            chunk_id,
                            doc_id,
                            content,
                            heading_path,
                            chunk_index
                        FROM {table_name}
                        WHERE {" OR ".join(where_clauses)}
                        LIMIT {k}
                    """

                    cursor = conn.execute(sql, params)
                    results = cursor.fetchall()

                    # Score based on term frequency (simple heuristic)
                    scored_results = []
                    for row in results:
                        content_lower = row[2].lower()
                        term_count = sum(
                            1 for term in search_terms if term.lower() in content_lower
                        )
                        score = term_count / len(
                            search_terms
                        )  # Normalize by number of terms

                        scored_results.append(
                            {
                                "chunk_id": row[0],
                                "doc_id": row[1],
                                "content": row[2],
                                "heading_path": row[3],
                                "chunk_index": row[4],
                                "score": score,
                            }
                        )

                    # Sort by score
                    scored_results.sort(key=lambda x: x["score"], reverse=True)
                    return scored_results[:k]

        except Exception as e:
            # If full-text search fails, return empty results
            print(f"Warning: Keyword search failed: {e}")
            return []

    def _query_to_tsquery(self, query: str) -> str:
        """Convert natural language query to tsquery format.

        Args:
            query: Natural language query

        Returns:
            tsquery string (e.g., "search & query")
        """
        # Simple conversion: join terms with & (AND)
        # Remove common stop words
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
        }

        terms = query.lower().split()
        filtered_terms = [t for t in terms if t not in stop_words and len(t) > 2]

        if not filtered_terms:
            # Fallback to original query if all words filtered
            return query.replace(" ", " & ")

        return " & ".join(filtered_terms)

    def search(self, query: str, k: int = 10) -> List[dict]:
        """Perform hybrid search combining semantic and keyword results.

        Args:
            query: Search query
            k: Number of results to return

        Returns:
            List of search results with hybrid scores
        """
        # 1. Perform semantic search
        semantic_results = self._vector_store.search(query=query, k=k)

        # 2. Perform keyword search
        keyword_results = self._keyword_search(query=query, k=k)

        # 3. Apply Reciprocal Rank Fusion
        return self._reciprocal_rank_fusion(
            semantic_results,
            keyword_results,
            k=k,
        )

    def _reciprocal_rank_fusion(
        self,
        semantic_results: List[dict],
        keyword_results: List[dict],
        k: int = 10,
    ) -> List[dict]:
        """Combine ranked lists using Reciprocal Rank Fusion.

        RRF formula: score = alpha / (rrf_k + rank_semantic) + (1 - alpha) / (rrf_k + rank_keyword)

        Args:
            semantic_results: Results from semantic search, ranked by score
            keyword_results: Results from keyword search, ranked by score
            k: Number of final results to return

        Returns:
            Fused and ranked results
        """
        # Create mappings: chunk_id -> rank (1-indexed)
        semantic_ranks: Dict[str, int] = {
            r["chunk_id"]: i + 1 for i, r in enumerate(semantic_results)
        }
        keyword_ranks: Dict[str, int] = {
            r["chunk_id"]: i + 1 for i, r in enumerate(keyword_results)
        }

        # Collect all unique chunk_ids
        all_chunk_ids = set(semantic_ranks.keys()) | set(keyword_ranks.keys())

        # Calculate RRF scores
        rrf_scores: Dict[str, float] = {}
        for chunk_id in all_chunk_ids:
            semantic_rank = semantic_ranks.get(chunk_id)
            keyword_rank = keyword_ranks.get(chunk_id)

            # RRF: 1 / (k + rank)
            if semantic_rank is not None and keyword_rank is not None:
                # Both results present
                semantic_score = 1.0 / (self.rrf_k + semantic_rank)
                keyword_score = 1.0 / (self.rrf_k + keyword_rank)
                rrf_scores[chunk_id] = (
                    self.alpha * semantic_score + (1 - self.alpha) * keyword_score
                )
            elif semantic_rank is not None:
                # Only in semantic results
                rrf_scores[chunk_id] = self.alpha / (self.rrf_k + semantic_rank)
            elif keyword_rank is not None:
                # Only in keyword results
                rrf_scores[chunk_id] = (1 - self.alpha) / (self.rrf_k + keyword_rank)

        # Create result list with original metadata from semantic results (preferred)
        # Fall back to keyword results if not in semantic
        result_map = {r["chunk_id"]: r for r in semantic_results}
        for r in keyword_results:
            if r["chunk_id"] not in result_map:
                result_map[r["chunk_id"]] = r

        # Attach RRF scores and sort
        final_results = []
        for chunk_id, rrf_score in sorted(
            rrf_scores.items(), key=lambda x: x[1], reverse=True
        ):
            result = result_map[chunk_id].copy()
            result["score"] = rrf_score
            final_results.append(result)

            if len(final_results) >= k:
                break

        return final_results
