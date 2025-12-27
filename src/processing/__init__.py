"""
Document processing module

Provides Loaders and Chunkers for different document types.

Usage:
    from src.processing import GmailLoader, GmailChunker

    # Load email
    loader = GmailLoader()
    docs = loader.load("/path/to/email_dir")

    # Chunk for embedding
    chunker = GmailChunker()
    for doc in docs:
        chunks = chunker.chunk(doc)
        # Now chunks are ready for embedding
"""

from .base import BaseLoader, BaseChunker
from .gmail import GmailLoader, GmailChunker
from .pdf import PDFLoader, PDFChunker
from .markdown import MarkdownLoader, MarkdownChunker
from .csv_data import CSVLoader, CSVChunker
from .slack import SlackLoader, SlackChunker

__all__ = [
    # Base classes
    'BaseLoader',
    'BaseChunker',

    # Gmail
    'GmailLoader',
    'GmailChunker',

    # PDF
    'PDFLoader',
    'PDFChunker',

    # Markdown
    'MarkdownLoader',
    'MarkdownChunker',

    # CSV
    'CSVLoader',
    'CSVChunker',

    # Slack
    'SlackLoader',
    'SlackChunker',
]
