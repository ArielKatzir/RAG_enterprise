"""
Test querying the vector store to verify emails were processed

This script:
1. Loads the vector store
2. Embeds a query using OpenAI
3. Searches for relevant chunks
4. Displays results
"""
import sys
sys.path.insert(0, "/Users/arielkatzir/Library/CloudStorage/GoogleDrive-ari.katzir@gmail.com/My Drive/Colab Notebooks/rag_enterprise")

from src.embedding.embedder import Embedder
from src.embedding.vector_store import VectorStore

def test_query(query: str, top_k: int = 5):
    """
    Query the vector store

    Args:
        query: Question to ask
        top_k: Number of results to return
    """
    print(f"Query: {query}\n")

    # Load vector store
    print("Loading vector store...")
    vector_store = VectorStore(dimension=1536)

    try:
        vector_store.load("vector_store")
        print(f"✓ Loaded vector store with {vector_store.index.ntotal} vectors\n")
    except FileNotFoundError:
        print("✗ Vector store not found. Run the Airflow DAG first!")
        return

    # Show stats
    stats = vector_store.stats()
    print("Vector Store Stats:")
    print(f"  Total chunks: {stats['total_chunks']}")
    print(f"  Document types: {stats['doc_types']}")
    print(f"  Sources: {list(stats['sources'].keys())[:5]}")  # Show first 5
    print()

    # Embed query
    print("Embedding query...")
    embedder = Embedder()
    query_embedding = embedder.embed_query(query)
    print("✓ Query embedded\n")

    # Search
    print(f"Searching for top {top_k} results...")
    results = vector_store.search(query_embedding, k=top_k)
    print(f"✓ Found {len(results)} results\n")

    # Display results
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)

    for i, chunk in enumerate(results, 1):
        print(f"\n[{i}] Rank #{chunk['_rank']} | Distance: {chunk['_distance']:.4f}")
        print(f"Source: {chunk['metadata'].get('source', 'unknown')}")
        print(f"Type: {chunk['metadata'].get('doc_type', 'unknown')}")

        # Show email-specific metadata
        if chunk['metadata'].get('doc_type') == 'email':
            print(f"From: {chunk['metadata'].get('from', 'unknown')}")
            print(f"Subject: {chunk['metadata'].get('subject', 'no subject')}")
            print(f"Date: {chunk['metadata'].get('date', 'unknown')}")

        print(f"\nContent Preview:")
        content = chunk.get('text', '')
        preview = content[:300] + "..." if len(content) > 300 else content
        print(preview)
        print("-" * 80)


if __name__ == "__main__":
    # Test queries
    queries = [
        "what was my latest email?",
        "show me recent emails",
        "what emails did I receive?",
    ]

    # Run first query
    test_query(queries[0], top_k=3)

    # Uncomment to try other queries:
    # for query in queries:
    #     test_query(query, top_k=3)
    #     print("\n\n")
