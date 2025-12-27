# RAG Enterprise - Automated Document Intelligence Pipeline

Production-ready RAG system with automated ingestion pipeline for heterogeneous data sources (emails, PDFs, documents). Combines n8n workflow automation with Airflow orchestration for continuous document processing and vector indexing to allow users to interact with LLMs regarding their own documents. 

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Data Sources                                │
├─────────────────────────────────────────────────────────────────────┤
│  Gmail API  │  Web Content  │  File Uploads  │  Database Exports   │
└──────┬──────────────┬─────────────────┬──────────────────┬──────────┘
       │              │                 │                  │
       └──────────────┴─────────────────┴──────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │   n8n Workflows    │ ← Fetch & stage raw data
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │  data/staging/     │ ← Raw files await processing
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │  Airflow DAGs      │ ← Orchestrate processing
                    │  • Load & Parse    │
                    │  • Chunk Text      │
                    │  • Embed (OpenAI)  │
                    │  • Index (FAISS)   │
                    │  • Track Metadata  │
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │  Vector Store      │ ← Searchable embeddings
                    │  PostgreSQL        │ ← Document tracking
                    │  data/archive/     │ ← Processed files
                    └────────────────────┘
```

## Components

### 1. **Data Ingestion** (n8n)
- Gmail integration: Auto-fetch emails via Gmail API
- Web scraping: Schedule URL content extraction
- File monitoring: Watch folders for new documents

### 2. **Processing Pipeline** (Airflow)
- **Loaders**: Gmail, PDF, Markdown, CSV, Slack
- **Chunkers**: Semantic chunking with overlap
- **Embedder**: OpenAI text-embedding-3-small
- **Vector Store**: FAISS for similarity search
- **Tracking**: PostgreSQL for document status/lineage

### 3. **Retrieval & Query**
- Embed user queries
- FAISS similarity search
- Return top-k relevant chunks with metadata

## Quick Start

### Prerequisites
```bash
# Install Docker
brew install docker docker-compose

# Clone repo
git clone <repo-url>
cd rag_enterprise
```

### 1. Setup Secrets
Create `.secrets.json`:
```json
{
  "OPENAI_API_KEY": "sk-proj-...",
  "GMAIL_CLIENT_ID": "...",
  "GMAIL_CLIENT_SECRET": "..."
}
```

### 2. Start Services
```bash
# Start Airflow
cd airflow
docker-compose up -d

# Start n8n (separate terminal)
cd n8n
npm install n8n -g
n8n start
```

### 3. Configure Workflows
1. Import n8n workflow from `n8n/workflows/gmail_fetcher.json`
2. Configure Gmail OAuth credentials
3. Activate workflow

### 4. Verify Pipeline
```bash
# Check Airflow UI
open http://localhost:8080  # user: airflow, pass: airflow

# Trigger DAG manually or wait for schedule
# Monitor: staging → processing → archive

# Query vector store
python test_query_vector_store.py
```

## Testing

```bash
# Query vector store
python test_query_vector_store.py

# Test retrieval system
python tests/test_retrieval.py
```


