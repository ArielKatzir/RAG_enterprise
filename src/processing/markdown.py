"""
Markdown document processor: Loader + Chunker

Handles markdown files, chunking by ## section headers
"""

from typing import List, Dict
from .base import BaseLoader, BaseChunker


class MarkdownLoader(BaseLoader):
    """
    Load markdown files and split by ## headers
    """

    def load(self, source_path: str) -> List[Dict]:
        """
        Load markdown file and split into sections

        Args:
            source_path: Path to markdown file

        Returns:
            List of dicts, one per section
        """
        with open(source_path, 'r') as f:
            content = f.read()

        chunks = []
        for chunk in content.split("\n## "):
            chunks.append({
                "content": chunk.strip(),
                "metadata": {
                    "source": source_path.split('/')[-1],
                    "doc_type": f"document: {source_path.split('/')[-1]}",
                }
            })
        return chunks


class MarkdownChunker(BaseChunker):
    """
    Chunk markdown sections for embedding

    Extracts section title and cleans up formatting
    """

    def chunk(self, doc: Dict) -> List[Dict]:
        """
        Process markdown section into embeddable chunk

        Args:
            doc: Document from MarkdownLoader

        Returns:
            List with single chunk (or empty list if section is empty)
        """
        content = doc["content"]

        if not content.strip():
            return []

        lines = content.split('\n')

        # Extract section title (first non-empty line)
        section_title = "Introduction"
        clean_lines = []

        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped:
                continue

            # First non-empty line is the section title
            if i == 0 or (i < 3 and stripped.startswith('#')):
                section_title = stripped.lstrip('#').strip()
            else:
                clean_lines.append(line)

        # Reconstruct content without title
        text = '\n'.join(clean_lines).strip()

        if not text:
            return []

        chunk_id = self.generate_chunk_id(
            doc["metadata"]["source"],
            section_title
        )

        return [{
            "text": text,
            "metadata": {
                **doc["metadata"],
                "section": section_title,
                "chunk_id": chunk_id
            }
        }]
