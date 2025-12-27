"""
Example usage of the document tracking system

This script demonstrates how to use DocumentTracker to track
document processing in the RAG pipeline.
"""

from tracker import DocumentTracker
from models import ProcessingStatus


def example_usage():
    """Example workflow with the tracker"""

    # Initialize tracker with PostgreSQL connection
    # Using the same Postgres instance as Airflow, but different database
    db_url = "postgresql://airflow:airflow@localhost:5432/rag_metadata"
    tracker = DocumentTracker(db_url)

    # Create tables (run once)
    tracker.init_db()
    print("✓ Database initialized")

    # Example 1: Track a new email
    email_path = "/tmp/n8n_staging/2025-12-25_19b57310bb6f15e5"

    # Check if already processed
    if tracker.is_processed(email_path):
        print(f"Email {email_path} already processed, skipping")
    else:
        # Add to tracking
        doc = tracker.add_document(
            source_path=email_path,
            doc_type="email",
            compute_hash=False,  # Don't hash directories
            metadata={"source": "gmail"}
        )
        print(f"✓ Added document: {doc.id}")

        # Mark as processing
        tracker.mark_processing(doc.id)
        print(f"✓ Marked as processing")

        # Simulate processing...
        # (load with load_gmail, chunk, embed, index)

        # Mark as completed
        tracker.mark_completed(
            doc.id,
            chunks_created=3,
            archive_path="/path/to/archive/email_123"
        )
        print(f"✓ Marked as completed")

    # Example 2: Track a PDF file
    pdf_path = "/tmp/n8n_staging/research_paper.pdf"

    try:
        doc = tracker.add_document(
            source_path=pdf_path,
            doc_type="pdf",
            compute_hash=True,  # Compute hash for PDFs
            metadata={"source": "web_fetch"}
        )
        tracker.mark_processing(doc.id)

        # Simulate processing that fails
        raise ValueError("Invalid PDF format")

    except Exception as e:
        tracker.mark_failed(doc.id, str(e))
        print(f"✗ Processing failed: {e}")

    # Get statistics
    stats = tracker.get_stats()
    print("\n📊 Processing Statistics:")
    print(f"  Total: {stats['total']}")
    print(f"  Pending: {stats['pending']}")
    print(f"  Processing: {stats['processing']}")
    print(f"  Completed: {stats['completed']}")
    print(f"  Failed: {stats['failed']}")

    # Get pending documents for batch processing
    pending = tracker.get_pending_documents(limit=10)
    print(f"\n📋 Found {len(pending)} pending documents")
    for doc in pending:
        print(f"  - {doc.source_path} ({doc.doc_type})")


if __name__ == "__main__":
    example_usage()
