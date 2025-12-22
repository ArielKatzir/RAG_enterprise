import pandas as pd

def load_markdown(file_path: str) -> dict:
    """
    Load markdown file with metadata
    Chunk by ## titles
    """
    with open(file_path, 'r') as f:
        content = f.read()
    
    chunks = []
    for chunk in content.split("\n## "):
        chunks.append({
                "content": chunk.strip(),
                "metadata": {
                    "source": file_path.split('/')[-1],
                    "doc_type": f"document: {file_path.split('/')[-1]}",  # or "process", "postmortem", "planning"
                    # Add: date, title, etc.
                }
            }
        )
    return chunks   
 

def load_csv(file_path: str) -> list[dict]:
    """
    Load CSV, each row becomes a chunk
    """
    df = pd.read_csv(file_path)

    rows = []
    for _, row in df.iterrows():
        # Convert row to readable text
        rows.append({
            "content": row.to_dict(),  # Original structured data
            "metadata": {
                "source": file_path.split('/')[-1],
                "doc_type": "incident_log" if "incident" in file_path else "resource",
                **row.to_dict()  # All columns become searchable metadata
            }
        })

    return rows

def load_slack(file_path: str) -> list[dict]:
    """
    Parse Slack export into individual messages

    Format:
    ==================================================
    Thread: <title>
    Started: <timestamp> by <author>
    ==================================================

    [HH:MM:SS] author: message text
    """
    import re

    with open(file_path, 'r') as f:
        content = f.read()

    messages = []

    # Split by thread separators
    threads = content.split('=' * 50)

    current_thread_title = None
    current_thread_date = None

    for section in threads:
        section = section.strip()
        if not section:
            continue

        lines = section.split('\n')

        # Check if this is a thread header
        for line in lines:
            if line.startswith('Thread:'):
                current_thread_title = line.replace('Thread:', '').strip()
            elif line.startswith('Started:'):
                # Extract date from "Started: 2024-09-12 14:20:11 by author"
                match = re.search(r'(\d{4}-\d{2}-\d{2})', line)
                if match:
                    current_thread_date = match.group(1)

        # Parse messages in format [HH:MM:SS] author: message
        message_pattern = r'\[(\d{2}:\d{2}:\d{2})\]\s+([a-z.]+):\s+(.+)'

        for line in lines:
            match = re.match(message_pattern, line)
            if match:
                timestamp, author, text = match.groups()

                messages.append({
                    "content": text.strip(),
                    "metadata": {
                        "source": file_path.split('/')[-1],
                        "doc_type": "slack",
                        "thread_title": current_thread_title or "Unknown",
                        "thread_date": current_thread_date or "Unknown",
                        "author": author,
                        "timestamp": timestamp,
                        "full_timestamp": f"{current_thread_date} {timestamp}" if current_thread_date else timestamp
                    }
                })

    return messages 



