from __future__ import annotations

import pickle
from pathlib import Path

from kb.config import AppConfig


class BM25Retriever:
    """BM25 retrieval using spaCy tokenization."""

    def __init__(self, config: AppConfig, persist_dir: str):
        """Initialize BM25 retriever.

        Args:
            config: Application configuration
            persist_dir: Base directory for persistence
        """
        self.config = config
        self.persist_dir = Path(persist_dir)
        self._nlp = None
        self._bm25 = None
        self._nodes = None

        # Lazy load spaCy
        try:
            import spacy

            self._nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
        except OSError:
            # Model not downloaded, will load on first use
            self._nlp = None

    def _load_spacy(self):
        """Load spaCy model if not already loaded."""
        if self._nlp is None:
            import spacy

            try:
                self._nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
            except OSError:
                # Download model if not present
                from spacy.cli import download

                download("en_core_web_sm")
                self._nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])

    def _tokenize(self, text: str) -> list[str]:
        """Use spaCy for tokenization with stopword and punctuation removal.

        Args:
            text: Input text to tokenize

        Returns:
            List of tokens (lowercased, no stopwords/punctuation/spaces)
        """
        if self._nlp is None:
            self._load_spacy()

        doc = self._nlp(text.lower())
        return [
            t.text for t in doc
            if not t.is_stop and not t.is_punct and not t.is_space
        ]

    def _load_nodes_from_storage(self):
        """Load nodes from storage (placeholder for now).

        In production, this would load from the same storage as VectorRetriever.
        For now, we assume nodes are set externally.
        """
        if self._nodes is None:
            raise RuntimeError(
                "Nodes not loaded. Call set_nodes() or implement _load_nodes_from_storage()"
            )
        return self._nodes

    def set_nodes(self, nodes: list):
        """Set nodes for BM25 indexing.

        Args:
            nodes: List of nodes to index
        """
        self._nodes = nodes

    def build_index(self):
        """Build BM25 index from nodes.

        Tokenizes all nodes and creates BM25 index.
        Persists the index to disk.
        """
        nodes = self._load_nodes_from_storage()

        corpus = [
            self._tokenize(node.get_content())
            for node in nodes
        ]

        from rank_bm25 import BM25Okapi

        self._bm25 = BM25Okapi(corpus)

        # Persist to disk
        self._persist_index()

    def _persist_index(self):
        """Persist BM25 index and nodes to disk."""
        persist_path = self.persist_dir / self.config.bm25.persist_dir
        persist_path.mkdir(parents=True, exist_ok=True)

        with open(persist_path / "bm25_index.pkl", 'wb') as f:
            pickle.dump(self._bm25, f)

        # Also persist nodes for retrieval
        with open(persist_path / "bm25_nodes.pkl", 'wb') as f:
            pickle.dump(self._nodes, f)

    def _load_or_build_index(self):
        """Load index from disk or build if not exists."""
        persist_path = self.persist_dir / self.config.bm25.persist_dir
        index_file = persist_path / "bm25_index.pkl"
        nodes_file = persist_path / "bm25_nodes.pkl"

        if index_file.exists() and nodes_file.exists():
            # Load from disk
            with open(index_file, 'rb') as f:
                self._bm25 = pickle.load(f)
            with open(nodes_file, 'rb') as f:
                self._nodes = pickle.load(f)
        else:
            self.build_index()

    def retrieve(self, query: str, top_k: int = 10):
        """BM25 retrieval.

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of (node, score) tuples
        """
        import numpy as np

        if self._bm25 is None:
            self._load_or_build_index()

        tokenized = self._tokenize(query)
        scores = self._bm25.get_scores(tokenized)
        top_indices = np.argsort(scores)[::-1][:top_k]

        return [(self._nodes[i], float(scores[i])) for i in top_indices]
