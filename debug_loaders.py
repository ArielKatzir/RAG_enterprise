"""
Debug script to test loaders without API calls

Run this to verify loaders work before building index
"""
import sys
sys.path.insert(0, 'src')

from chunking.loader import load_markdown, load_csv, load_slack
from chunking.chunker import chunk_all
from glob import glob

print("Testing loaders...\n", flush=True)

# Test markdown
print("1. Testing markdown loader...", flush=True)
md_files = glob("data/documents/*.md")
print(f"   Found {len(md_files)} files", flush=True)
for f in md_files:
    chunks = load_markdown(f)
    print(f"   {f}: {len(chunks)} chunks", flush=True)

# Test CSV
print("\n2. Testing CSV loader...", flush=True)
csv_files = glob("data/structured/*.csv")
print(f"   Found {len(csv_files)} files", flush=True)
for f in csv_files:
    chunks = load_csv(f)
    print(f"   {f}: {len(chunks)} rows", flush=True)

# Test Slack
print("\n3. Testing Slack loader...", flush=True)
slack_files = glob("data/conversations/*.txt")
print(f"   Found {len(slack_files)} files", flush=True)
for f in slack_files:
    chunks = load_slack(f)
    print(f"   {f}: {len(chunks)} messages", flush=True)

# Test chunker
print("\n4. Testing chunker...", flush=True)
all_chunks = []
for f in md_files:
    all_chunks.extend(load_markdown(f))
for f in csv_files:
    all_chunks.extend(load_csv(f))
for f in slack_files:
    all_chunks.extend(load_slack(f))

print(f"   Total raw chunks: {len(all_chunks)}", flush=True)

processed = chunk_all(all_chunks)
print(f"   Processed chunks: {len(processed)}", flush=True)

# Show sample
print("\n5. Sample processed chunk:", flush=True)
sample = processed[0]
print(f"   Text preview: {sample['text'][:100]}...", flush=True)
print(f"   Metadata: {sample['metadata']}", flush=True)

print("\n✓ All loaders working!", flush=True)
