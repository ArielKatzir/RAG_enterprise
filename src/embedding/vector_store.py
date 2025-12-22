"""
Vector Store: FAISS-based storage and retrieval of embeddings
"""
import os
import pickle
import numpy as np
import faiss
from typing import List, Dict, Optional


class VectorStore:
    """
    FAISS-based vector store for chunk embeddings

    Why FAISS:
    - Fast: Optimized C++ implementation
    - Simple: No external dependencies (unlike Pinecone/Weaviate)
    - Free: Runs locally
    - Scalable: Can handle millions of vectors

    Why IndexFlatL2:
    - Exact search (not approximate)
    - Good for <100K vectors
    - L2 distance ≈ cosine similarity for normalized vectors (OpenAI embeddings are normalized)
    """

    def __init__(self, dimension: int = 1536):
        """
        Initialize vector store

        Args:
            dimension: Embedding dimension
                - text-embedding-3-small: 1536
                - text-embedding-3-large: 3072
        """
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)  # L2 distance index
        self.chunks = []  # Store chunk metadata alongside vectors

    def add_chunks(self, chunks: List[Dict]):
        """
        Add chunks with embeddings to the index

        Args:
            chunks: List of chunks with 'embedding' field

        Process:
        1. Extract embeddings as numpy array
        2. Convert to float32 (FAISS requirement)
        3. Add to FAISS index
        4. Store chunk metadata separately
        """
        if not chunks:
            print("Warning: No chunks to add")
            return

        print(f"Adding {len(chunks)} chunks to vector store...")

        # Extract embeddings
        embeddings = np.array([chunk["embedding"] for chunk in chunks]).astype('float32')

        # Verify shape
        expected_shape = (len(chunks), self.dimension)
        if embeddings.shape != expected_shape:
            raise ValueError(f"Expected shape {expected_shape}, got {embeddings.shape}")

        # Add to FAISS index
        self.index.add(embeddings)

        # Store chunks (without embeddings to save space)
        for chunk in chunks:
            chunk_copy = chunk.copy()
            # Remove embedding from stored chunk (we have it in FAISS)
            if "embedding" in chunk_copy:
                del chunk_copy["embedding"]
            self.chunks.append(chunk_copy)

        print(f"✓ Vector store now contains {self.index.ntotal} vectors")

    def search(self, query_embedding: np.ndarray, k: int = 10) -> List[Dict]:
        """
        Find k nearest neighbors to query embedding

        Args:
            query_embedding: Query vector (1536-dim)
            k: Number of results to return

        Returns:
            List of chunks sorted by similarity (closest first)
        """
        if self.index.ntotal == 0:
            print("Warning: Vector store is empty")
            return []

        # Ensure query is float32 and correct shape
        query_embedding = np.array(query_embedding).astype('float32')
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)

        # Search FAISS index
        # D = distances (lower = more similar)
        # I = indices of nearest neighbors
        k = min(k, self.index.ntotal)  # Don't request more than available
        distances, indices = self.index.search(query_embedding, k)

        # Retrieve chunks
        results = []
        for i, (idx, distance) in enumerate(zip(indices[0], distances[0])):
            chunk = self.chunks[idx].copy()
            chunk["_distance"] = float(distance)  # Add distance for debugging
            chunk["_rank"] = i + 1
            results.append(chunk)

        return results

    def save(self, path: str):
        """
        Persist vector store to disk

        Saves two files:
        - faiss.index: Binary FAISS index
        - chunks.pkl: Chunk metadata
        """
        os.makedirs(path, exist_ok=True)

        # Save FAISS index
        index_path = os.path.join(path, "faiss.index")
        faiss.write_index(self.index, index_path)

        # Save chunk metadata
        chunks_path = os.path.join(path, "chunks.pkl")
        with open(chunks_path, "wb") as f:
            pickle.dump(self.chunks, f)

        print(f"✓ Saved vector store to {path}/")
        print(f"  - {self.index.ntotal} vectors")
        print(f"  - {len(self.chunks)} chunks")

    def load(self, path: str):
        """
        Load vector store from disk

        Args:
            path: Directory containing faiss.index and chunks.pkl
        """
        # Load FAISS index
        index_path = os.path.join(path, "faiss.index")
        if not os.path.exists(index_path):
            raise FileNotFoundError(f"FAISS index not found at {index_path}")

        self.index = faiss.read_index(index_path)

        # Load chunk metadata
        chunks_path = os.path.join(path, "chunks.pkl")
        if not os.path.exists(chunks_path):
            raise FileNotFoundError(f"Chunks file not found at {chunks_path}")

        with open(chunks_path, "rb") as f:
            self.chunks = pickle.load(f)

        # Update dimension from loaded index
        self.dimension = self.index.d

        print(f"✓ Loaded vector store from {path}/")
        print(f"  - {self.index.ntotal} vectors")
        print(f"  - {len(self.chunks)} chunks")

    def stats(self) -> Dict:
        """
        Get statistics about the vector store

        Returns:
            Dict with counts and metadata info
        """
        if not self.chunks:
            return {
                "total_chunks": 0,
                "dimension": self.dimension,
                "index_size": 0
            }

        # Count by document type
        doc_types = {}
        sources = {}

        for chunk in self.chunks:
            doc_type = chunk["metadata"].get("doc_type", "unknown")
            source = chunk["metadata"].get("source", "unknown")

            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
            sources[source] = sources.get(source, 0) + 1

        return {
            "total_chunks": len(self.chunks),
            "dimension": self.dimension,
            "index_size": self.index.ntotal,
            "doc_types": doc_types,
            "sources": sources
        }
