"""
Document tracking utilities

Provides functions to track document processing status
"""

import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .models import Base, ProcessedDocument, ProcessingStatus


class DocumentTracker:
    """
    Manages document processing tracking using PostgreSQL

    Usage:
        tracker = DocumentTracker("postgresql://user:pass@localhost:5432/rag_metadata")
        tracker.init_db()  # Create tables

        # Mark document as processing
        doc = tracker.add_document("/path/to/file.pdf", doc_type="pdf")
        tracker.mark_processing(doc.id)

        # Mark as completed
        tracker.mark_completed(doc.id, chunks_created=5, archive_path="/archive/file.pdf")

        # Check if already processed
        if tracker.is_processed("/path/to/file.pdf"):
            print("Already processed!")
    """

    def __init__(self, db_url: str):
        """
        Initialize tracker with database connection

        Args:
            db_url: SQLAlchemy database URL
                    Example: "postgresql://airflow:airflow@localhost:5432/rag_metadata"
        """
        self.engine = create_engine(db_url)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def init_db(self):
        """Create all tables in the database"""
        Base.metadata.create_all(self.engine)

    def get_session(self) -> Session:
        """Get a new database session"""
        return self.SessionLocal()

    def _compute_hash(self, file_path: str) -> str:
        """Compute MD5 hash of file content"""
        md5_hash = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()

    def add_document(
        self,
        source_path: str,
        doc_type: str,
        compute_hash: bool = True,
        metadata: Optional[dict] = None
    ) -> ProcessedDocument:
        """
        Add a new document to tracking

        Args:
            source_path: Path to source file
            doc_type: Type of document (email, pdf, etc.)
            compute_hash: Whether to compute file hash
            metadata: Additional metadata

        Returns:
            ProcessedDocument instance
        """
        session = self.get_session()
        try:
            file_hash = None
            if compute_hash and Path(source_path).exists():
                file_hash = self._compute_hash(source_path)

            doc = ProcessedDocument(
                source_path=source_path,
                doc_type=doc_type,
                file_hash=file_hash,
                status=ProcessingStatus.PENDING,
                doc_metadata=metadata
            )
            session.add(doc)
            session.commit()
            session.refresh(doc)
            return doc
        finally:
            session.close()

    def get_document(self, doc_id: int) -> Optional[ProcessedDocument]:
        """Get document by ID"""
        session = self.get_session()
        try:
            return session.query(ProcessedDocument).filter_by(id=doc_id).first()
        finally:
            session.close()

    def get_by_path(self, source_path: str) -> Optional[ProcessedDocument]:
        """Get document by source path"""
        session = self.get_session()
        try:
            return session.query(ProcessedDocument).filter_by(source_path=source_path).first()
        finally:
            session.close()

    def is_processed(self, source_path: str) -> bool:
        """Check if document has been processed"""
        doc = self.get_by_path(source_path)
        return doc is not None and doc.status == ProcessingStatus.COMPLETED

    def mark_processing(self, doc_id: int):
        """Mark document as currently processing"""
        session = self.get_session()
        try:
            doc = session.query(ProcessedDocument).filter_by(id=doc_id).first()
            if doc:
                doc.status = ProcessingStatus.PROCESSING
                doc.updated_at = datetime.utcnow()
                session.commit()
        finally:
            session.close()

    def mark_completed(
        self,
        doc_id: int,
        chunks_created: int = 0,
        archive_path: Optional[str] = None
    ):
        """Mark document as successfully processed"""
        session = self.get_session()
        try:
            doc = session.query(ProcessedDocument).filter_by(id=doc_id).first()
            if doc:
                doc.status = ProcessingStatus.COMPLETED
                doc.chunks_created = chunks_created
                doc.archive_path = archive_path
                doc.processed_at = datetime.utcnow()
                doc.updated_at = datetime.utcnow()
                session.commit()
        finally:
            session.close()

    def mark_failed(self, doc_id: int, error_message: str):
        """Mark document as failed with error message"""
        session = self.get_session()
        try:
            doc = session.query(ProcessedDocument).filter_by(id=doc_id).first()
            if doc:
                doc.status = ProcessingStatus.FAILED
                doc.error_message = error_message
                doc.updated_at = datetime.utcnow()
                session.commit()
        finally:
            session.close()

    def get_pending_documents(self, limit: Optional[int] = None) -> List[ProcessedDocument]:
        """Get all pending documents"""
        session = self.get_session()
        try:
            query = session.query(ProcessedDocument).filter_by(status=ProcessingStatus.PENDING)
            if limit:
                query = query.limit(limit)
            return query.all()
        finally:
            session.close()

    def get_failed_documents(self) -> List[ProcessedDocument]:
        """Get all failed documents"""
        session = self.get_session()
        try:
            return session.query(ProcessedDocument).filter_by(status=ProcessingStatus.FAILED).all()
        finally:
            session.close()

    def get_stats(self) -> dict:
        """Get processing statistics"""
        session = self.get_session()
        try:
            total = session.query(ProcessedDocument).count()
            pending = session.query(ProcessedDocument).filter_by(status=ProcessingStatus.PENDING).count()
            processing = session.query(ProcessedDocument).filter_by(status=ProcessingStatus.PROCESSING).count()
            completed = session.query(ProcessedDocument).filter_by(status=ProcessingStatus.COMPLETED).count()
            failed = session.query(ProcessedDocument).filter_by(status=ProcessingStatus.FAILED).count()

            return {
                "total": total,
                "pending": pending,
                "processing": processing,
                "completed": completed,
                "failed": failed
            }
        finally:
            session.close()
