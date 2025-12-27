"""
Test retrieval after building vector store

Run after: python scripts/build_index.py

Tests:
1. Load vector store
2. Embed a test query
3. Retrieve similar chunks
4. Verify results make sense
"""
import sys
sys.path.insert(0, "/Users/arielkatzir/Library/CloudStorage/GoogleDrive-ari.katzir@gmail.com/My Drive/Colab Notebooks/rag_enterprise")


from src.embedding.vector_store import VectorStore
from src.embedding.embedder import Embedder


def main():
    print("Loading vector store...")
    vs = VectorStore()
    vs.load("vector_store")

    print(f"\n✓ Loaded {vs.index.ntotal} vectors")

    # Initialize embedder
    embedder = Embedder()

    # Test queries
    test_queries = [
        "What caused the payment gateway incident?",
        "Which team has the most incidents?",
        "What do people think about centralization?",
        "What are the monitoring tools used?",
    ]

    for query in test_queries:
        print("\n" + "=" * 60)
        print(f"Query: {query}")
        print("=" * 60)

        # Embed query
        query_embedding = embedder.embed_query(query)

        # Search
        results = vs.search(query_embedding, k=5)

        # Display results
        for i, chunk in enumerate(results, 1):
            meta = chunk["metadata"]
            text_preview = chunk["text"][:150] + "..." if len(chunk["text"]) > 150 else chunk["text"]

            print(f"\n[{i}] Source: {meta['source']}")
            print(f"    Type: {meta['doc_type']}")
            if "section" in meta:
                print(f"    Section: {meta['section']}")
            if "thread_title" in meta:
                print(f"    Thread: {meta['thread_title']}")
            if "author" in meta:
                print(f"    Author: {meta['author']}")
            print(f"    Distance: {chunk['_distance']:.4f}")
            print(f"    Preview: {text_preview}")

    print("\n" + "=" * 60)
    print("✓ Retrieval test complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
