"""
SQLAlchemy models for document tracking
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, Text, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ProcessingStatus(str, Enum):
    """Document processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


class ProcessedDocument(Base):
    """
    Tracks documents processed through the RAG pipeline

    Attributes:
        id: Primary key
        source_path: Original file path in staging
        doc_type: Type of document (email, pdf, markdown, etc.)
        file_hash: MD5 hash of file content (to detect duplicates)
        status: Current processing status
        chunks_created: Number of chunks created from this document
        archive_path: Path in archive after processing
        error_message: Error details if processing failed
        doc_metadata: Additional metadata (JSON)
        created_at: When record was created
        processed_at: When processing completed
        updated_at: Last update timestamp
    """
    __tablename__ = 'processed_documents'

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_path = Column(String(500), nullable=False, unique=True, index=True)
    doc_type = Column(String(50), nullable=False, index=True)
    file_hash = Column(String(32), nullable=True, index=True)  # MD5 hash
    status = Column(SQLEnum(ProcessingStatus), default=ProcessingStatus.PENDING, nullable=False, index=True)
    chunks_created = Column(Integer, default=0)
    archive_path = Column(String(500), nullable=True)
    error_message = Column(Text, nullable=True)
    doc_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<ProcessedDocument(id={self.id}, path='{self.source_path}', status='{self.status}')>"
