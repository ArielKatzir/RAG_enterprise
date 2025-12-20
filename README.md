# 🧠 Advanced LLM Systems Challenge

### *“Internal Operations Intelligence Copilot”*

## 🎯 Objective

Build an **AI copilot for an operations team** that can:

1. Answer questions grounded in internal documents
2. Compare options and highlight risks
3. Produce **structured, decision-ready outputs**
4. Cite sources
5. Work on **messy, heterogeneous data**

No fine-tuning. No expensive infra.

---

## 🏗️ Scenario

You’ve joined a mid-size company (~300 employees).

The **Operations division** struggles with:

* Scattered documentation (PDFs, spreadsheets, notes)
* Repeated questions
* Inconsistent weekly reports
* Decisions based on partial context

Your task is to build an **internal AI system** that helps ops managers make decisions faster and with evidence.

---

## 📦 Provided Data (you create this)

You’ll create a **mini but realistic corpus**:

### 1️⃣ Documents (required)

Create:

* **3 PDFs** (or markdown → PDF):

  * Ops process doc
  * Incident postmortem
  * Quarterly planning notes

* **2 CSV or Excel files**

  * Incident log
  * Resource allocation table

* **1 Slack-style text export**

  * Simulated conversations with conflicting info

Total size can be small (20–40 pages equivalent).

---

## 🧩 Core System Requirements

### 1️⃣ Retrieval-Augmented Generation (mandatory)

* Chunk documents intelligently
* Embed them
* Store in a vector DB (FAISS, Chroma, SQLite-based)
* Retrieve top-k with metadata filtering

No fine-tuning allowed.

---

### 2️⃣ Decision-Support Output (not just answers)

For queries like:

> *“Should we centralise incident response or keep team-based ownership?”*

Your system must return:

* Summary of relevant evidence
* Pros / cons
* Risks
* Recommendation
* Sources (doc + section)

This is **hard** — that’s intentional.

---

### 3️⃣ Structured Outputs (mandatory)

Outputs must conform to a schema, e.g.:

```json
{
  "decision_summary": "",
  "options": [
    {
      "option": "",
      "pros": [],
      "cons": [],
      "risks": []
    }
  ],
  "recommendation": "",
  "confidence_level": ""
}
```

Use function calling / JSON schema enforcement.

---

### 4️⃣ Source Attribution (mandatory)

Every factual claim must reference:

* Document name
* Chunk ID or page range

No “trust me bro” answers.

---

### 5️⃣ Failure Handling

If evidence is insufficient:

* The model must say so
* Suggest what data is missing

---

## ⚙️ Constraints (important)

* 💸 **Cost:**

  * Use small / cheap models
  * OpenAI GPT-4o-mini / GPT-4.1-mini or local (Ollama + Mistral)
  * Embeddings once only

* ❌ No LangChain magic chains required

* ✅ Plain Python is preferred

* ❌ No web search

* ❌ No fine-tuning

---

## 🛠️ Suggested Tech Stack (you may vary)

* Python
* FAISS or Chroma
* OpenAI / Anthropic / local LLM
* Pydantic for schema validation
* Simple CLI or Streamlit UI

---

## 🧪 Evaluation Tasks (you must test these)

Your system must handle:

1. **Conflicting documents**

   * Two docs disagree → surface conflict

2. **Multi-document reasoning**

   * Answer requires CSV + PDF + Slack text

3. **Partial data**

   * Missing info → refuse to over-speculate

4. **Time filtering**

   * Prefer newer docs over outdated ones

---

## 📈 Stretch Goals (pick 1–2)

* Re-ranking step
* Self-critique pass
* Confidence scoring
* Chunk quality evaluation
* Automatic doc freshness detection
* Cost tracking per query

---

## 📄 Deliverables

1. **Repo or folder**
2. README explaining:

   * Architecture
   * Trade-offs
   * Why you *didn’t* fine-tune
3. Example queries + outputs
4. One “failure case” you intentionally designed

---

## 🧠 What this tests (implicitly)

* Real-world LLM system design
* Restraint (not over-engineering)
* RAG quality
* Decision-support thinking
* Senior-level judgment

This is **interview-grade** work.

---

## 🧩 Bonus Interview Question (answer for yourself)

> “Why is this safer and cheaper than training a model on company data?”

If you can answer that clearly, you’re already ahead of many “AI leads”.

---

If you want:

* I can **break this into daily milestones**
* I can **review your architecture**
* I can act as **a stakeholder giving changing requirements**
* I can give you **grading criteria like a hiring panel**

Tell me how you want to run it.
