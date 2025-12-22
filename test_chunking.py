# Update test.py
from src.chunking.loader import load_markdown, load_csv, load_slack
from src.chunking.chunker import chunk_all

# Load
md_chunks = load_markdown("data/documents/incident_postmortem_2024_q3.md")
csv_chunks = load_csv("data/structured/incident_log.csv")
slack_chunks = load_slack("data/conversations/slack_ops_channel_export.txt")

all_raw = md_chunks + csv_chunks + slack_chunks
print(f"Loaded {len(all_raw)} raw chunks")

# Chunk
processed = chunk_all(all_raw)
print(f"Processed into {len(processed)} chunks")

# Inspect
print("\n=== Incident chunk example ===")
incident_chunk = [c for c in processed if c["metadata"]["doc_type"] == "incident_log"][0]
print(incident_chunk["text"])
print(f"Chunk ID: {incident_chunk['metadata']['chunk_id']}")

