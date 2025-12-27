"""
PDF document processor: Loader + Chunker

Handles PDF files with configurable page-based chunking
"""

from pathlib import Path
from typing import List, Dict
from .base import BaseLoader, BaseChunker


class PDFLoader(BaseLoader):
    """
    Load PDF files and extract text

    Requires: pypdf library (pip install pypdf)
    """

    def __init__(self, chunk_pages: int = 1):
        """
        Initialize PDF loader

        Args:
            chunk_pages: Number of pages to combine per chunk
        """
        self.chunk_pages = chunk_pages

    def load(self, source_path: str) -> List[Dict]:
        """
        Load PDF and extract text by pages

        Args:
            source_path: Path to PDF file

        Returns:
            List of dicts, one per chunk (group of pages)
        """
        try:
            from pypdf import PdfReader
        except ImportError:
            raise ImportError("pypdf is required for PDF loading. Install with: pip install pypdf")

        pdf_path = Path(source_path)
        reader = PdfReader(source_path)

        docs = []
        page_buffer = []

        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            page_buffer.append((page_num + 1, text))

            # Create document when buffer reaches chunk_pages
            if len(page_buffer) >= self.chunk_pages:
                page_numbers = [p[0] for p in page_buffer]
                combined_text = "\n\n".join([p[1] for p in page_buffer])

                docs.append({
                    "content": combined_text,
                    "metadata": {
                        "source": pdf_path.name,
                        "doc_type": "pdf",
                        "pages": page_numbers,
                        "page_range": f"{page_numbers[0]}-{page_numbers[-1]}" if len(page_numbers) > 1 else str(page_numbers[0]),
                        "total_pages": len(reader.pages),
                    }
                })
                page_buffer = []

        # Handle remaining pages
        if page_buffer:
            page_numbers = [p[0] for p in page_buffer]
            combined_text = "\n\n".join([p[1] for p in page_buffer])

            docs.append({
                "content": combined_text,
                "metadata": {
                    "source": pdf_path.name,
                    "doc_type": "pdf",
                    "pages": page_numbers,
                    "page_range": f"{page_numbers[0]}-{page_numbers[-1]}" if len(page_numbers) > 1 else str(page_numbers[0]),
                    "total_pages": len(reader.pages),
                }
            })

        return docs


class PDFChunker(BaseChunker):
    """
    Chunk PDF documents for embedding

    PDFs are already chunked by pages in the loader, so this just adds chunk_id
    and formats the text
    """

    def chunk(self, doc: Dict) -> List[Dict]:
        """
        Convert PDF page group into embeddable chunk

        Args:
            doc: Document from PDFLoader

        Returns:
            List with single chunk (already chunked by loader)
        """
        meta = doc["metadata"]
        content = doc["content"]

        # Add page header
        text = f"[PDF: {meta['source']} | Pages: {meta['page_range']}]\n\n"
        text += content

        # Generate chunk ID from source + page range
        chunk_id = self.generate_chunk_id(
            meta['source'],
            f"pages_{meta['page_range']}"
        )

        return [{
            "text": text.strip(),
            "metadata": {
                **meta,
                "chunk_id": chunk_id
            }
        }]
