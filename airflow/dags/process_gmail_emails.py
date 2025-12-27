"""
Airflow DAG: Process Gmail emails from n8n staging

This DAG:
1. Scans staging directory for new emails
2. Loads and chunks emails using GmailLoader/GmailChunker
3. Embeds chunks using OpenAI
4. Adds to FAISS vector store
5. Moves processed files to archive
6. Updates tracking database

Schedule: Runs every 15 minutes
"""

from datetime import datetime, timedelta
from pathlib import Path
import shutil
import os
import sys

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

# Add project root to path so we can import from src/
# Inside Docker container, project is mounted at /opt/airflow/rag_enterprise
PROJECT_ROOT = "/opt/airflow/rag_enterprise"
sys.path.insert(0, PROJECT_ROOT)

from src.processing import GmailLoader, GmailChunker
from src.embedding.embedder import Embedder
from src.embedding.vector_store import VectorStore
from src.tracking import DocumentTracker, ProcessingStatus


# Configuration
STAGING_DIR = Path(PROJECT_ROOT) / "data" / "staging" / "gmail"
ARCHIVE_DIR = Path(PROJECT_ROOT) / "data" / "archive" / "gmail"
VECTOR_STORE_PATH = Path(PROJECT_ROOT) / "vector_store"
DB_URL = "postgresql://airflow:airflow@postgres:5432/rag_metadata"


def scan_staging(**context):
    """
    Task 1: Scan staging directory for unprocessed emails

    Returns list of email directory paths to process
    """
    print(f"Scanning staging directory: {STAGING_DIR}")

    if not STAGING_DIR.exists():
        print(f"Staging directory does not exist: {STAGING_DIR}")
        return []

    # Find all email directories (format: YYYY-MM-DD_<email_id>)
    email_dirs = [
        str(d) for d in STAGING_DIR.iterdir()
        if d.is_dir() and (d / "metadata.json").exists()
    ]

    print(f"Found {len(email_dirs)} email directories")

    # Filter out already processed emails using tracker
    tracker = DocumentTracker(DB_URL)
    tracker.init_db()  # Ensure tables exist

    unprocessed = []
    for email_dir in email_dirs:
        if not tracker.is_processed(email_dir):
            unprocessed.append(email_dir)
            # Add to tracking as pending
            try:
                tracker.add_document(
                    source_path=email_dir,
                    doc_type="email",
                    compute_hash=False,
                    metadata={"stage": "pending"}
                )
            except Exception as e:
                # Might already exist from previous run
                print(f"Document {email_dir} already in tracking: {e}")

    print(f"Found {len(unprocessed)} unprocessed emails")
    for email_dir in unprocessed:
        print(f"  - {email_dir}")

    # Push to XCom for next task
    context['task_instance'].xcom_push(key='email_dirs', value=unprocessed)
    return unprocessed


def process_and_embed(**context):
    """
    Task 2: Load, chunk, and embed emails

    Processes emails found in previous task
    """
    # Get email directories from previous task
    email_dirs = context['task_instance'].xcom_pull(
        task_ids='scan_staging',
        key='email_dirs'
    )

    if not email_dirs:
        print("No emails to process")
        return

    print(f"Processing {len(email_dirs)} emails")

    # Initialize loader, chunker, embedder
    loader = GmailLoader()
    chunker = GmailChunker()
    embedder = Embedder()
    tracker = DocumentTracker(DB_URL)

    all_chunks = []
    processed_docs = []

    for email_dir in email_dirs:
        try:
            print(f"\nProcessing: {email_dir}")

            # Get document ID from tracker
            doc = tracker.get_by_path(email_dir)
            if not doc:
                print(f"  Warning: Document not in tracking, skipping")
                continue

            # Mark as processing
            tracker.mark_processing(doc.id)

            # Load email
            docs = loader.load(email_dir)
            print(f"  Loaded {len(docs)} documents")

            # Chunk
            for doc_data in docs:
                chunks = chunker.chunk(doc_data)
                all_chunks.extend(chunks)
                print(f"  Created {len(chunks)} chunks")

            processed_docs.append((doc.id, len(chunks)))

        except Exception as e:
            print(f"  Error processing {email_dir}: {e}")
            # Mark as failed
            if doc:
                tracker.mark_failed(doc.id, str(e))

    if not all_chunks:
        print("No chunks created")
        return

    print(f"\nTotal chunks to embed: {len(all_chunks)}")

    # Embed all chunks
    try:
        all_chunks = embedder.embed_chunks(all_chunks)
        print(f"Successfully embedded {len(all_chunks)} chunks")
    except Exception as e:
        print(f"Error embedding chunks: {e}")
        # Mark all as failed
        for doc_id, _ in processed_docs:
            tracker.mark_failed(doc_id, f"Embedding failed: {e}")
        raise

    # Store for next task
    context['task_instance'].xcom_push(key='chunks', value=all_chunks)
    context['task_instance'].xcom_push(key='processed_docs', value=processed_docs)


def add_to_vector_store(**context):
    """
    Task 3: Add embedded chunks to FAISS vector store
    """
    chunks = context['task_instance'].xcom_pull(
        task_ids='process_and_embed',
        key='chunks'
    )

    if not chunks:
        print("No chunks to add to vector store")
        return

    print(f"Adding {len(chunks)} chunks to vector store")

    # Load or create vector store
    vector_store = VectorStore(dimension=1536)

    if VECTOR_STORE_PATH.exists():
        try:
            vector_store.load(str(VECTOR_STORE_PATH))
            print("Loaded existing vector store")
        except Exception as e:
            print(f"Error loading vector store, creating new one: {e}")

    # Add chunks
    vector_store.add_chunks(chunks)

    # Save vector store
    VECTOR_STORE_PATH.mkdir(parents=True, exist_ok=True)
    vector_store.save(str(VECTOR_STORE_PATH))

    # Print stats
    stats = vector_store.stats()
    print(f"\nVector store statistics:")
    print(f"  Total chunks: {stats['total_chunks']}")
    print(f"  Document types: {stats['doc_types']}")


def archive_and_update_tracking(**context):
    """
    Task 4: Move processed emails to archive and update tracking
    """
    email_dirs = context['task_instance'].xcom_pull(
        task_ids='scan_staging',
        key='email_dirs'
    )
    processed_docs = context['task_instance'].xcom_pull(
        task_ids='process_and_embed',
        key='processed_docs'
    )

    if not email_dirs or not processed_docs:
        print("No emails to archive")
        return

    print(f"Archiving {len(email_dirs)} emails")

    tracker = DocumentTracker(DB_URL)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    # Create doc_id to chunks mapping
    doc_chunks = {doc_id: chunks_count for doc_id, chunks_count in processed_docs}

    for email_dir in email_dirs:
        try:
            email_path = Path(email_dir)
            doc = tracker.get_by_path(email_dir)

            if not doc or doc.id not in doc_chunks:
                print(f"  Skipping {email_dir} (not successfully processed)")
                continue

            # Move to archive
            archive_path = ARCHIVE_DIR / email_path.name
            shutil.move(str(email_path), str(archive_path))
            print(f"  Archived: {email_path.name} -> {archive_path}")

            # Update tracking
            tracker.mark_completed(
                doc.id,
                chunks_created=doc_chunks[doc.id],
                archive_path=str(archive_path)
            )
            print(f"  Updated tracking: {doc.id} marked as completed")

        except Exception as e:
            print(f"  Error archiving {email_dir}: {e}")
            if doc:
                tracker.mark_failed(doc.id, f"Archive failed: {e}")

    print(f"\nArchive complete. Check {ARCHIVE_DIR} for processed emails")


# Define DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'process_gmail_emails',
    default_args=default_args,
    description='Process Gmail emails from n8n staging into vector store',
    schedule_interval=timedelta(minutes=5),  # Run every 5 minutes
    start_date=days_ago(1),
    catchup=False,
    max_active_runs=1,  # Prevent concurrent runs to avoid file locking issues
    tags=['rag', 'gmail', 'processing'],
) as dag:

    # Task 1: Scan staging directory
    scan_task = PythonOperator(
        task_id='scan_staging',
        python_callable=scan_staging,
    )

    # Task 2: Process and embed
    process_task = PythonOperator(
        task_id='process_and_embed',
        python_callable=process_and_embed,
    )

    # Task 3: Add to vector store
    vectorize_task = PythonOperator(
        task_id='add_to_vector_store',
        python_callable=add_to_vector_store,
    )

    # Task 4: Archive and update tracking
    archive_task = PythonOperator(
        task_id='archive_and_update',
        python_callable=archive_and_update_tracking,
    )

    # Define task dependencies
    scan_task >> process_task >> vectorize_task >> archive_task
