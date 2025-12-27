"""
Gmail email processor: Loader + Chunker

Handles emails from n8n Gmail integration (metadata.json + body.txt)
"""

import json
from pathlib import Path
from typing import List, Dict
from .base import BaseLoader, BaseChunker


class GmailLoader(BaseLoader):
    """
    Load Gmail emails from n8n staging format

    Expected directory structure:
        email_dir/
            metadata.json  - email metadata (from, to, subject, etc.)
            body.txt       - email body text
    """

    def load(self, source_path: str) -> List[Dict]:
        """
        Load email from directory

        Args:
            source_path: Path to email directory

        Returns:
            List with single dict containing email content and metadata
        """
        email_path = Path(source_path)

        # Load metadata
        metadata_path = email_path / "metadata.json"
        if not metadata_path.exists():
            raise FileNotFoundError(f"metadata.json not found in {source_path}")

        with open(metadata_path, 'r') as f:
            email_metadata = json.load(f)

        # Load body
        body_path = email_path / "body.txt"
        body_text = ""
        if body_path.exists():
            with open(body_path, 'r') as f:
                body_text = f.read()

        # Extract sender info
        from_email = email_metadata.get('from', 'unknown')
        if isinstance(from_email, dict):
            from_email = from_email.get('address', 'unknown')

        return [{
            "content": body_text,
            "metadata": {
                "source": f"email_{email_metadata.get('id', 'unknown')}",
                "doc_type": "email",
                "from": from_email,
                "subject": email_metadata.get('subject', ''),
                "date": email_metadata.get('date', ''),
                "message_id": email_metadata.get('message_id', ''),
                "thread_id": email_metadata.get('thread_id', ''),
                "labels": email_metadata.get('labels', []),
            }
        }]


class GmailChunker(BaseChunker):
    """
    Chunk Gmail emails for embedding

    Emails are kept as single chunks (not split) since they're typically
    conversational and benefit from full context.
    """

    def chunk(self, doc: Dict) -> List[Dict]:
        """
        Convert email into embeddable chunk

        Args:
            doc: Document from GmailLoader

        Returns:
            List with single chunk (emails not split)
        """
        meta = doc["metadata"]
        content = doc["content"]

        # Format email text with headers
        text = f"From: {meta.get('from', 'unknown')}\n"
        text += f"Subject: {meta.get('subject', '(no subject)')}\n"
        text += f"Date: {meta.get('date', 'unknown')}\n\n"
        text += content

        # Generate chunk ID from message_id
        chunk_id = self.generate_chunk_id(
            meta['source'],
            meta.get('message_id', 'unknown')
        )

        return [{
            "text": text.strip(),
            "metadata": {
                **meta,
                "chunk_id": chunk_id
            }
        }]
