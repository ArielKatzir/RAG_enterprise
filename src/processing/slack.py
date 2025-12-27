"""
Slack export processor: Loader + Chunker

Handles Slack channel exports, each message becomes a chunk
"""

import re
from typing import List, Dict
from .base import BaseLoader, BaseChunker


class SlackLoader(BaseLoader):
    """
    Load Slack channel export and parse messages

    Expected format:
        ==================================================
        Thread: <title>
        Started: <timestamp> by <author>
        ==================================================

        [HH:MM:SS] author: message text
    """

    def load(self, source_path: str) -> List[Dict]:
        """
        Load Slack export file

        Args:
            source_path: Path to Slack export text file

        Returns:
            List of dicts, one per message
        """
        with open(source_path, 'r') as f:
            content = f.read()

        messages = []
        threads = content.split('=' * 50)

        current_thread_title = None
        current_thread_date = None

        for section in threads:
            section = section.strip()
            if not section:
                continue

            lines = section.split('\n')

            # Parse thread header
            for line in lines:
                if line.startswith('Thread:'):
                    current_thread_title = line.replace('Thread:', '').strip()
                elif line.startswith('Started:'):
                    # Extract date from "Started: 2024-09-12 14:20:11 by author"
                    match = re.search(r'(\d{4}-\d{2}-\d{2})', line)
                    if match:
                        current_thread_date = match.group(1)

            # Parse messages: [HH:MM:SS] author: message
            message_pattern = r'\[(\d{2}:\d{2}:\d{2})\]\s+([a-z.]+):\s+(.+)'

            for line in lines:
                match = re.match(message_pattern, line)
                if match:
                    timestamp, author, text = match.groups()

                    messages.append({
                        "content": text.strip(),
                        "metadata": {
                            "source": source_path.split('/')[-1],
                            "doc_type": "slack",
                            "thread_title": current_thread_title or "Unknown",
                            "thread_date": current_thread_date or "Unknown",
                            "author": author,
                            "timestamp": timestamp,
                            "full_timestamp": f"{current_thread_date} {timestamp}" if current_thread_date else timestamp
                        }
                    })

        return messages


class SlackChunker(BaseChunker):
    """
    Chunk Slack messages for embedding

    Each message is already a chunk, just format with context
    """

    def chunk(self, doc: Dict) -> List[Dict]:
        """
        Format Slack message as embeddable chunk

        Args:
            doc: Document from SlackLoader

        Returns:
            List with single chunk
        """
        meta = doc["metadata"]

        # Format: [Thread: title] Author (timestamp): message
        text = f"[Thread: {meta['thread_title']}]\n"
        text += f"{meta['author']} ({meta['timestamp']}): {doc['content']}"

        chunk_id = self.generate_chunk_id(
            meta['source'],
            f"{meta['thread_title']}_{meta['author']}_{meta['timestamp']}"
        )

        return [{
            "text": text,
            "metadata": {
                **meta,
                "chunk_id": chunk_id
            }
        }]
