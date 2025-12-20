# RAG Enterprise - Decision-Support Copilot

## What I'm Building

An **internal operations AI system** that produces structured, decision-ready outputs from heterogeneous data sources. Not a chatbot—a decision support tool.

**Core challenge**: Multi-document reasoning + conflicting sources + structured outputs + source attribution.

---

## Requirements

✅ **RAG pipeline**: Chunk → Embed → Vector DB → Retrieve top-k
✅ **Decision outputs**: Pros/cons, risks, recommendations (not just answers)
✅ **Structured JSON**: Schema-validated responses
✅ **Source attribution**: Every claim cites document + section
✅ **Failure handling**: Refuse when evidence insufficient

**Constraints**: No fine-tuning. Cheap models only (GPT-4o-mini / local).

---

## Dataset

**Scenario**: TechCorp (300 employees) debating whether to centralize incident response

| Type | Files | Purpose |
|------|-------|---------|
| **Documents** | 3 markdown (→PDF) | Process docs, postmortem, strategic planning |
| **Structured** | 2 CSV files | Incident log (42 records), resource allocation (9 teams) |
| **Conversations** | 1 Slack export | 78 messages with conflicting opinions |

**Key feature**: All data is contextually coherent—references same incidents, teams, decisions.

---

## Example Decision Query

**Q**: *"Should we centralize incident response or keep team-based ownership?"*

**Expected output**:
```json
{
  "decision_summary": "...",
  "options": [
    {"option": "Centralized SRE", "pros": [...], "cons": [...], "cost": "$750K"},
    {"option": "Status quo+", "pros": [...], "cons": [...], "cost": "$270K"},
    {"option": "Hybrid model", "pros": [...], "cons": [...], "cost": "$450K"}
  ],
  "recommendation": "Option C (Hybrid) - fits budget, addresses coordination gaps, lower risk",
  "confidence_level": "high",
  "evidence": [
    {"claim": "...", "source": "quarterly_planning_2024_q4.md", "location": "Section 3"},
    {"claim": "...", "source": "incident_log.csv", "location": "Q3 data"}
  ],
  "conflicts": ["Slack: Tom Chen opposes centralization (ownership concerns)"]
}
```

---

## Testing Challenges

- **Conflicting sources**: Slack disagrees with formal docs
- **Multi-doc reasoning**: Answer requires CSV + PDF + Slack synthesis
- **Time-sensitive**: Prioritize newer docs for strategic questions
- **Failure case**: Refuse queries with insufficient evidence

---

## Files

```
data/
├── documents/              # 3 markdown files (convert to PDF)
│   ├── incident_response_process.md
│   ├── incident_postmortem_2024_q3.md
│   └── quarterly_planning_2024_q4.md
├── structured/
│   ├── incident_log.csv
│   └── resource_allocation.csv
└── conversations/
    └── slack_ops_channel_export.txt
```

See [data/DATA_OVERVIEW.md](data/DATA_OVERVIEW.md) for detailed dataset guide.

---

## Tech Stack 

- **Vector DB**: FAISS or Chroma
- **LLM**: GPT-4o-mini / GPT-4.1-mini / Ollama+Mistral
- **Embeddings**: text-embedding-3-small (cheap)
- **Schema validation**: Pydantic
- **Interface**: CLI or Streamlit

No LangChain required.
