"""
Test document processing with new OOP structure

Demonstrates loading and chunking with the new processing module
"""
import sys
sys.path.insert(0, "/Users/arielkatzir/Library/CloudStorage/GoogleDrive-ari.katzir@gmail.com/My Drive/Colab Notebooks/rag_enterprise")

from src.processing import (
    MarkdownLoader, MarkdownChunker,
    CSVLoader, CSVChunker,
    SlackLoader, SlackChunker
)

# Initialize loaders and chunkers
md_loader = MarkdownLoader()
md_chunker = MarkdownChunker()

csv_loader = CSVLoader()
csv_chunker = CSVChunker()

slack_loader = SlackLoader()
slack_chunker = SlackChunker()

# Load and chunk documents
all_chunks = []

# Process markdown
md_docs = md_loader.load("data/documents/incident_postmortem_2024_q3.md")
for doc in md_docs:
    chunks = md_chunker.chunk(doc)
    all_chunks.extend(chunks)

# Process CSV
csv_docs = csv_loader.load("data/structured/incident_log.csv")
for doc in csv_docs:
    chunks = csv_chunker.chunk(doc)
    all_chunks.extend(chunks)

# Process Slack
slack_docs = slack_loader.load("data/conversations/slack_ops_channel_export.txt")
for doc in slack_docs:
    chunks = slack_chunker.chunk(doc)
    all_chunks.extend(chunks)

print(f"Processed {len(all_chunks)} total chunks")

# Inspect
print("\n=== Incident chunk example ===")
incident_chunk = [c for c in all_chunks if c["metadata"]["doc_type"] == "incident_log"][0]
print(incident_chunk["text"])
print(f"Chunk ID: {incident_chunk['metadata']['chunk_id']}")

