"""
Build vector store from raw data

Run once to process all documents and create FAISS index:
    python scripts/build_index.py

This will:
1. Load all documents (markdown, CSV, Slack)
2. Chunk them into embeddable pieces
3. Generate embeddings using OpenAI
4. Store in FAISS vector database
5. Save to disk at vector_store/

Cost: ~$0.002 for this dataset
"""
import sys
import os
from glob import glob

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from chunking.loader import load_markdown, load_csv, load_slack
from chunking.chunker import chunk_all
from embedding.embedder import Embedder
from embedding.vector_store import VectorStore


def main():
    print("=" * 60, flush=True)
    print("Building Vector Store", flush=True)
    print("=" * 60, flush=True)

    # Step 1: Load all documents
    print("\n📂 Step 1: Loading documents...", flush=True)

    all_raw_chunks = []

    # Load markdown documents
    md_files = glob("data/documents/*.md")
    print(f"  Found {len(md_files)} markdown files", flush=True)
    for md_file in md_files:
        print(f"  Loading {md_file}...", flush=True)
        chunks = load_markdown(md_file)
        print(f"    → {len(chunks)} chunks", flush=True)
        all_raw_chunks.extend(chunks)

    # Load CSV files
    csv_files = glob("data/structured/*.csv")
    print(f"  Found {len(csv_files)} CSV files", flush=True)
    for csv_file in csv_files:
        print(f"  Loading {csv_file}...", flush=True)
        chunks = load_csv(csv_file)
        print(f"    → {len(chunks)} rows", flush=True)
        all_raw_chunks.extend(chunks)

    # Load Slack export
    slack_files = glob("data/conversations/*.txt")
    print(f"  Found {len(slack_files)} conversation files", flush=True)
    for slack_file in slack_files:
        print(f"  Loading {slack_file}...", flush=True)
        chunks = load_slack(slack_file)
        print(f"    → {len(chunks)} messages", flush=True)
        all_raw_chunks.extend(chunks)

    print(f"\n✓ Loaded {len(all_raw_chunks)} raw chunks", flush=True)

    # Step 2: Chunk documents
    print("\n✂️  Step 2: Processing chunks...", flush=True)
    processed_chunks = chunk_all(all_raw_chunks)
    print(f"✓ Processed {len(processed_chunks)} chunks", flush=True)

    # Show distribution
    from collections import Counter
    doc_types = Counter(c["metadata"]["doc_type"] for c in processed_chunks)
    print("\nChunk distribution:")
    for doc_type, count in doc_types.items():
        print(f"  - {doc_type}: {count}")

    # Step 3: Generate embeddings
    print("\n🔢 Step 3: Generating embeddings...")
    print("(This will cost ~$0.002 using OpenAI API)")

    embedder = Embedder()
    chunks_with_embeddings = embedder.embed_chunks(processed_chunks)

    # Verify
    sample = chunks_with_embeddings[0]
    print(f"\nSample embedding shape: {len(sample['embedding'])} dimensions")
    print(f"First 5 values: {sample['embedding'][:5]}")

    # Step 4: Build vector store
    print("\n📦 Step 4: Building vector store...")
    vector_store = VectorStore(dimension=1536)
    vector_store.add_chunks(chunks_with_embeddings)

    # Step 5: Save to disk
    print("\n💾 Step 5: Saving to disk...")
    vector_store.save("vector_store")

    # Show stats
    print("\n" + "=" * 60)
    print("✓ Build Complete!")
    print("=" * 60)

    stats = vector_store.stats()
    print(f"\nVector store statistics:")
    print(f"  Total chunks: {stats['total_chunks']}")
    print(f"  Dimension: {stats['dimension']}")
    print(f"\nBy document type:")
    for doc_type, count in stats['doc_types'].items():
        print(f"  - {doc_type}: {count}")

    print(f"\n💡 Next step: Run queries using src/main.py")
    print(f"   or test with: python test_retrieval.py")


if __name__ == "__main__":
    main()
