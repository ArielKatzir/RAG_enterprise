"""
Retriever: Clean interface for query -> relevant chunks

Wraps embedder + vector store into single retrieve() call
"""
from typing import List, Dict, Optional
from embedding.embedder import Embedder
from embedding.vector_store import VectorStore


class Retriever:
    """
    High-level retrieval interface

    Why this exists:
    - Clean API: retrieve(query, k) instead of embed -> search
    - Could add filters, re-ranking, hybrid search later
    - Single place to tune retrieval behavior
    """

    def __init__(self, vector_store: VectorStore, embedder: Embedder):
        """
        Initialize retriever

        Args:
            vector_store: Loaded VectorStore instance
            embedder: Embedder instance
        """
        self.vector_store = vector_store
        self.embedder = embedder

    def retrieve(self,
                 query: str,
                 k: int = 10,
                 filters: Optional[Dict] = None) -> List[Dict]:
        """
        Retrieve top-k relevant chunks for a query

        Args:
            query: User's question
            k: Number of chunks to retrieve
            filters: Optional filters (e.g., {"doc_type": "markdown"})
                    Not implemented yet, placeholder for future

        Returns:
            List of chunk dicts with text, metadata, _distance
        """
        # Embed query
        query_embedding = self.embedder.embed_query(query)

        # Search vector store
        results = self.vector_store.search(query_embedding, k=k)

        # Apply filters if provided
        if filters:
            results = self._apply_filters(results, filters)

        return results

    def _apply_filters(self, chunks: List[Dict], filters: Dict) -> List[Dict]:
        """
        Apply metadata filters to retrieved chunks

        Example filters:
        - {"doc_type": "markdown"}
        - {"source": "incident_postmortem_2024_q3.md"}
        - {"team": "Payment"}

        This is post-retrieval filtering (FAISS filters are complex).
        For large-scale systems, use pre-filtering or hybrid approaches.
        """
        filtered = []
        for chunk in chunks:
            meta = chunk["metadata"]
            matches = True

            for key, value in filters.items():
                if key not in meta or meta[key] != value:
                    matches = False
                    break

            if matches:
                filtered.append(chunk)

        return filtered

    def stats(self) -> Dict:
        """
        Get retrieval system statistics

        Returns:
            Dict with vector store stats
        """
        return self.vector_store.stats()


# Convenience function for one-off retrieval
def retrieve_chunks(query: str,
                   vector_store_path: str = "vector_store",
                   k: int = 10,
                   filters: Optional[Dict] = None) -> List[Dict]:
    """
    Retrieve chunks (convenience function)

    Args:
        query: User question
        vector_store_path: Path to saved vector store
        k: Number of chunks
        filters: Optional metadata filters

    Returns:
        List of retrieved chunks
    """
    # Load vector store
    vs = VectorStore()
    vs.load(vector_store_path)

    # Initialize embedder
    embedder = Embedder()

    # Create retriever and retrieve
    retriever = Retriever(vs, embedder)
    return retriever.retrieve(query, k=k, filters=filters)
