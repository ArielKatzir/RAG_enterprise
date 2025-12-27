"""
Base classes for document loaders and chunkers

Provides abstract interfaces that all source-specific implementations must follow
"""

from abc import ABC, abstractmethod
from typing import List, Dict
import hashlib


class BaseLoader(ABC):
    """
    Abstract base class for document loaders

    Loaders are responsible for reading raw files and extracting content + metadata
    """

    @abstractmethod
    def load(self, source_path: str) -> List[Dict]:
        """
        Load document from source path

        Args:
            source_path: Path to document (file or directory)

        Returns:
            List of dicts with structure:
                {
                    "content": <raw content>,
                    "metadata": {
                        "source": <source identifier>,
                        "doc_type": <document type>,
                        ... other metadata ...
                    }
                }
        """
        pass


class BaseChunker(ABC):
    """
    Abstract base class for document chunkers

    Chunkers convert loaded documents into embeddable chunks with standardized format
    """

    @abstractmethod
    def chunk(self, doc: Dict) -> List[Dict]:
        """
        Convert loaded document into embeddable chunks

        Args:
            doc: Document dict from loader with "content" and "metadata" keys

        Returns:
            List of chunk dicts with structure:
                {
                    "text": <processed text ready for embedding>,
                    "metadata": {
                        "chunk_id": <unique identifier>,
                        "source": <source identifier>,
                        "doc_type": <document type>,
                        ... other metadata from loader ...
                    }
                }
        """
        pass

    @staticmethod
    def generate_chunk_id(source: str, identifier: str) -> str:
        """
        Generate unique, deterministic chunk ID

        Args:
            source: Source file/document name
            identifier: Unique identifier within source (page num, section, etc.)

        Returns:
            12-character hash ID
        """
        combined = f"{source}::{identifier}"
        hash_obj = hashlib.md5(combined.encode())
        return hash_obj.hexdigest()[:12]
