# RAG Enterprise - Operations Intelligence Copilot

Internal decision-support AI that retrieves from heterogeneous sources (docs, CSVs, Slack) and generates structured JSON responses with source citations.

**Challenge**: Multi-document reasoning + conflicting sources + structured outputs + no fine-tuning.

---

## How It Works

```
Query → Embed → FAISS Search → Top-k Chunks → GPT-4o-mini → Structured JSON
```

**Pipeline**:
1. **Chunk & Index** (one-time): Parse markdown/CSV/Slack → chunk → embed → FAISS
2. **Retrieve**: Embed query → search FAISS → get top-k relevant chunks
3. **Generate**: Send query + chunks to GPT-4o-mini with schema → get validated DecisionResponse

**Output Schema**:
```json
{
  "decision_summary": "...",
  "options": [{"option": "...", "pros": [], "cons": [], "risks": [], "cost": "..."}],
  "recommendation": "...",
  "confidence_level": "high|medium|low",
  "reasoning": "...",
  "evidence": [{"claim": "...", "source": "...", "location": "..."}],
  "conflicts_or_gaps": []
}
```

---

## Setup

### 1. Install Dependencies
```bash
pip install openai faiss-cpu numpy pandas pydantic
```

### 2. Configure API Key

Create `/Users/arielkatzir/Library/CloudStorage/GoogleDrive-ari.katzir@gmail.com/My Drive/.secrets.json`:
```json
{
  "OPENAI_API_KEY": "sk-..."
}
```

Or set environment variable:
```bash
export OPENAI_API_KEY="sk-..."
```

### 3. Build Vector Store (one-time)

```bash
python -u scripts/build_index.py
```

This will:
- Load all data files (markdown, CSV, Slack)
- Chunk into 198 pieces
- Embed using OpenAI text-embedding-3-small
- Save FAISS index to `vector_store/`

Expected time: 30-60 seconds

---

## Usage

```bash
python -u src/main.py
```

Then ask questions:
```
> Should we centralize incident response?
> What caused the payment gateway incident?
> Which team has the most incidents?
> What do people think about centralization?
```

**Commands**:
- `examples` - Show example queries
- `stats` - Show indexed document stats
- `quit` - Exit

---

## Testing

```bash
# Test loaders (no API calls, <1 second)
python -u debug_loaders.py

# Test retrieval (requires vector_store/, ~2 seconds)
python -u test_retrieval.py

# Test generation (requires API key, ~20 seconds)
python -u test_generation.py
```

---

## Dataset

**Scenario**: TechCorp (300 employees) debating centralized vs distributed incident response

| Type | Files | Content |
|------|-------|---------|
| Documents | 3 markdown | Process docs, postmortem (INC-2024-089), Q4 planning with 3 options |
| Structured | 2 CSV | 42 incidents (Q2-Q3), 9 team resource allocations |
| Conversations | 1 Slack export | 107 messages across 6 threads with conflicting opinions |

