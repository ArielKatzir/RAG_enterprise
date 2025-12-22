"""
Embedder: Convert text chunks into vector embeddings using OpenAI
"""
import os
import json
from typing import List, Dict
from openai import OpenAI


def load_api_key() -> str:
    """
    Load OpenAI API key from secrets.json

    Tries:
    1. /Users/arielkatzir/Library/CloudStorage/GoogleDrive-ari.katzir@gmail.com/My Drive/.secrets.json
    2. OPENAI_API_KEY environment variable
    """
    secrets_path = "/Users/arielkatzir/Library/CloudStorage/GoogleDrive-ari.katzir@gmail.com/My Drive/.secrets.json"

    # Try loading from secrets.json
    if os.path.exists(secrets_path):
        with open(secrets_path, 'r') as f:
            secrets = json.load(f)
            return secrets["OPENAI_API_KEY"]

    # Fallback to environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return api_key

    raise ValueError(
        "OpenAI API key not found. Please either:\n"
        f"1. Create {secrets_path} with {{'OPENAI_API_KEY': 'sk-...'}}\n"
        "2. Set OPENAI_API_KEY environment variable"
    )


class Embedder:
    """
    Handles embedding generation using OpenAI API

    OpenAI embeddings:
    - High quality semantic search
    - cheap $0.02 per 1M tokens
    - 1536 dimensions (good balance)
    """

    def __init__(self, model: str = "text-embedding-3-small"):
        """
        Initialize embedder

        Args:
            model: OpenAI embedding model
                - text-embedding-3-small: $0.02/1M tokens, 1536 dims
                - text-embedding-3-large: $0.13/1M tokens, 3072 dims (overkill)
        """
        api_key = load_api_key()
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def embed_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """
        Add embeddings to chunks

        Args:
            chunks: List of chunk dicts with 'text' field

        Returns:
            Same chunks with 'embedding' field added

        Process:
        1. Extract all text
        2. Batch embed (up to 2048 texts per call)
        3. Attach embeddings back to chunks
        """
        print(f"Embedding {len(chunks)} chunks...", flush=True)

        # Extract text from chunks
        texts = [chunk["text"] for chunk in chunks]
        print(f"  Extracted {len(texts)} text items", flush=True)

        # Batch embed (OpenAI allows up to 2048 texts per call)
        batch_size = 100  # Conservative batch size
        all_embeddings = []
        total_batches = (len(texts) - 1) // batch_size + 1

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            batch_num = i // batch_size + 1
            print(f"  Embedding batch {batch_num}/{total_batches} ({len(batch)} items)...", flush=True)

            try:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=batch
                )

                # Extract embeddings from response
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
                print(f"    ✓ Batch {batch_num} complete", flush=True)

            except Exception as e:
                print(f"    ✗ Error in batch {batch_num}: {e}", flush=True)
                raise

        # Attach embeddings to chunks
        print(f"  Attaching embeddings to chunks...", flush=True)
        for chunk, embedding in zip(chunks, all_embeddings):
            chunk["embedding"] = embedding

        print(f"✓ Embedded {len(chunks)} chunks", flush=True)
        return chunks

    def embed_query(self, query: str) -> List[float]:
        """
        Embed a single query string

        Used during retrieval to convert user questions to vectors

        Args:
            query: User's question

        Returns:
            1536-dimensional embedding vector
        """
        response = self.client.embeddings.create(
            model=self.model,
            input=[query]
        )

        return response.data[0].embedding


def embed_chunks(chunks: List[Dict], model: str = "text-embedding-3-small") -> List[Dict]:
    """
    Convenience function for one-off embedding

    Args:
        chunks: List of chunk dicts
        model: OpenAI embedding model

    Returns:
        Chunks with embeddings added
    """
    embedder = Embedder(model=model)
    return embedder.embed_chunks(chunks)
