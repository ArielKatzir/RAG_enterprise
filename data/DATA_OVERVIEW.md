# RAG Enterprise Dataset Overview

## Scenario: TechCorp Infrastructure Operations

This dataset simulates a realistic mid-size SaaS company (300 employees, 42 engineers) facing operational challenges with incident response and infrastructure reliability.

## The Core Problem

**Context:** TechCorp uses a distributed, team-based incident response model where each product team owns their services end-to-end. This worked well initially but is breaking down as the company scales.

**Key Issues:**
1. **Incident volume growing 23% quarter-over-quarter**
2. **Payment team drowning** - 17 incidents in Q3 (38% of total) with only 3 engineers
3. **Knowledge silos** - Teams solving the same problems repeatedly (e.g., INC-2024-089 was identical to INC-2024-021 from 6 months prior)
4. **Tool fragmentation** - 5 different monitoring systems causing coordination delays
5. **Burnout** - On-call rotations as frequent as every 10 days for some teams

**The Decision:** Should they centralize incident response (create SRE team) or enhance the current distributed model?

---

## Dataset Structure

```
data/
├── documents/              # 3 PDFs (markdown source)
│   ├── incident_response_process.md
│   ├── incident_postmortem_2024_q3.md
│   └── quarterly_planning_2024_q4.md
├── structured/             # 2 CSV files
│   ├── incident_log.csv
│   └── resource_allocation.csv
└── conversations/          # 1 Slack export
    └── slack_ops_channel_export.txt
```

---

## Document Details

### 1. Incident Response Process (`incident_response_process.md`)

**Type:** Formal process documentation
**Date:** August 15, 2024
**Last Updated:** Before the major Q3 incident

**Contents:**
- Current team-based ownership model philosophy
- Incident severity levels (SEV-1 through SEV-4)
- Response workflow and escalation paths
- Known challenges with current approach
- Tools in use (DataDog, New Relic, Prometheus, Sentry, PingDom)
- Metrics tracked (MTTD, MTTA, MTTR)

**Key Points:**
- Documents the *existing* distributed model
- Acknowledges known issues (uneven load, knowledge silos, tool sprawl)
- Mentions that changes are "under discussion" for 2025
- Benefits of current approach: domain expertise, ownership culture
- Challenges: burnout, inconsistent practices, escalation confusion

**RAG Testing Opportunities:**
- What is the current incident response model?
- What are the tools used for monitoring?
- What are the known challenges with the current process?

---

### 2. Incident Postmortem (`incident_postmortem_2024_q3.md`)

**Type:** Detailed incident analysis
**Incident ID:** INC-2024-089
**Date:** September 12, 2024
**Severity:** SEV-1
**Duration:** 3 hours 47 minutes
**Impact:** $127K revenue loss

**Contents:**
- Complete timeline of the incident (minute-by-minute)
- Root cause: Database connection pool exhaustion from async code bug
- **Organizational finding:** Same issue was solved 6 months ago (INC-2024-021) by different team, but knowledge wasn't shared
- Action items (immediate, short-term, long-term strategic)
- Explicit recommendations to evaluate centralized SRE model

**Key Points:**
- **Technical root cause:** Connection leak in error handling paths
- **Organizational root cause:** Knowledge silos, no incident commander, tool fragmentation
- Took 1 hour 53 minutes to find engineer who'd solved this before
- 7 engineers involved but unclear decision-making
- Sparked the Q4 planning discussion about structural changes

**RAG Testing Opportunities:**
- What went wrong in INC-2024-089?
- What was the revenue impact?
- What organizational issues did this incident reveal?
- What are the connections to previous incidents?

---

### 3. Quarterly Planning Document (`quarterly_planning_2024_q4.md`)

**Type:** Strategic planning proposal
**Date:** October 3, 2024
**Status:** Draft under review

**Contents:**
- Three strategic options for Q4/2025:
  - **Option A:** Full centralized SRE team (6 people, $750K)
  - **Option B:** Enhanced distributed model (2 platform engineers, $270K)
  - **Option C:** Hybrid model (3-person IR team, $450K) - **RECOMMENDED**
- Tool consolidation plan (DataDog)
- Detailed cost-benefit analysis for each option
- Pros, cons, risks for each approach
- References to incident data, postmortem findings, and Slack discussions

**Key Points:**
- Budget approved: $450K (fits Option C perfectly)
- Option C recommended as pragmatic middle ground
- Includes stakeholder feedback from Slack
- Tool consolidation recommended regardless of org structure choice
- Timeline: Decision by October 20, implementation starts Q4

**Conflicting Perspectives:**
- Lisa Wong (Platform): Strongly favors centralization
- Tom Chen (DevOps): Skeptical, worried about losing ownership
- Dev Patel (Payment): Desperate for relief, supports centralization
- Hybrid model (Option C) emerging as consensus

**RAG Testing Opportunities:**
- Should we centralize incident response?
- What are the pros and cons of each option?
- What is the recommended approach and why?
- What are the budget constraints?
- What do different team members think?

---

## Structured Data

### 4. Incident Log (`incident_log.csv`)

**42 incidents** from Q2-Q3 2024 (with some historical references)

**Key Columns:**
- `incident_id`: Unique identifier (e.g., INC-2024-089)
- `date`, `severity`, `service`, `team`
- `duration_minutes`, `mttr_minutes`
- `cross_team`: Boolean - did it require multiple teams?
- `repeat_incident`: Boolean - was this a repeat of a past issue?
- `related_incidents`: References to similar past incidents
- `estimated_revenue_impact`: Dollar value

**Key Patterns in Data:**
- **Payment team: 17 incidents in Q3** (38% of all incidents)
- **Cross-team incidents: 22 incidents** (49% of total) - these took 2.3x longer to resolve
- **Repeat incidents: 18 incidents** - knowledge not being retained
- **INC-2024-089:** Highest impact, 227-minute duration, $127K loss
- **Connection-related incidents:** INC-2024-021, INC-2024-053, INC-2024-089, INC-2023-142 (pattern!)

**RAG Testing Opportunities:**
- Which team has the most incidents?
- What percentage of incidents require cross-team coordination?
- What patterns exist in repeat incidents?
- How much revenue was lost to incidents in Q3?
- Filter by severity, team, or time period

---

### 5. Resource Allocation (`resource_allocation.csv`)

**9 engineering teams** with budget and staffing details

**Key Columns:**
- `team`, `team_lead`, `headcount`
- `on_call_engineers`, `on_call_rotation_days`
- `avg_incidents_per_month`
- `annual_budget_usd`, `tooling_costs_usd`, `on_call_comp_annual_usd`
- `ops_load_pct`: Percentage of time spent on ops vs features
- `feature_velocity_pts_per_sprint`: Proxy for productivity

**Key Insights:**
- **Payment team:** 3 engineers, on-call every 10 days (!), 65% ops load, 17 incidents/month
- **Platform team:** 5 engineers, 45% ops load, handles cross-team escalations
- **Product teams:** 8-15% ops load (much healthier)
- **Total tooling cost:** ~$240K across all teams
- **Total on-call compensation:** $640K/year

**RAG Testing Opportunities:**
- Which teams are most burdened by on-call?
- What's the correlation between ops load and feature velocity?
- How much do we spend on tooling?
- Compare team sizes vs incident volume

---

## Conversational Data

### 6. Slack Export (`slack_ops_channel_export.txt`)

**78 messages across 6 threads** (Sept 12 - Oct 5, 2024)

**Threads:**
1. **Payment Gateway Incident (Sep 12)** - Real-time incident response during INC-2024-089
2. **Do we need centralized SRE?** - Debate with conflicting opinions
3. **Payment Team Burnout** - Dev Patel expresses burnout, gets on-call relief
4. **Tool Consolidation** - Discussion of monitoring tool sprawl
5. **Incident Commander Role** - Proposal for IC rotation
6. **Q4 Planning Follow-up** - Rough consensus forming around Option C

**Conflicting Information Examples:**

| Topic | Pro-Centralization View | Anti-Centralization View |
|-------|------------------------|--------------------------|
| **Ownership** | Lisa: "Platform team spends 40-50% on incidents, need to focus on roadmap" | Tom: "Creates 'throw it over wall' mentality, teams stop caring" |
| **Context** | Dev: "I'm burned out, would love specialists" | Anna: "When I'm on-call for billing, I KNOW the system" |
| **Velocity** | Lisa: "Dedicated SRE lets us build features" | Rachel: "Will SRE become a bottleneck? Don't want to wait in queue" |
| **Solution** | Dev: "Centralized SRE would give most relief" | Tom: "Better processes and 2 more people, don't need restructuring" |

**Informal Knowledge (not in formal docs):**
- Dev Patel updating resume due to burnout
- Jake Martinez left in Q3, cited "constant firefighting" as reason
- Tool consolidation trial was successful (notification-service to DataDog)
- Sarah Chen gave Dev a month off on-call rotation
- Rough consensus forming around Option C (hybrid model)

**RAG Testing Opportunities:**
- What do team members think about centralization?
- Who is in favor and who is opposed?
- What are the concerns about creating an SRE team?
- What informal context exists beyond formal documents?
- Surface disagreements between formal docs and informal discussions

---

## Cross-Document Connections

### The Connection Web

```
Incident Response Process
    ↓ (mentions upcoming changes)
    ↓
INC-2024-089 Postmortem
    ↓ (recommends evaluating centralization)
    ↓ (references incident_log.csv data)
    ↓
Quarterly Planning Document
    ↓ (references postmortem findings)
    ↓ (references incident metrics)
    ↓ (references resource allocation)
    ↓ (references Slack stakeholder input)
    ↓
Slack Conversations
    ↓ (debate findings and recommendations)
    ↓ (express conflicting opinions)
    ↓ (reveal informal context)
```

### Example Cross-Document Queries

**Query 1: "Should we centralize incident response?"**

*Expected RAG behavior:*
- **Planning doc** says Option C (hybrid) is recommended based on cost, risk, pragmatism
- **Postmortem** recommends evaluating centralization due to coordination failures
- **Slack** shows conflicting opinions:
  - Lisa, Dev favor centralization (burnout, focus)
  - Tom opposes (ownership culture)
  - Rough consensus on hybrid Option C
- **Incident log** shows 49% cross-team incidents (supports need for coordination)
- **Resource allocation** shows payment team unsustainable (supports need for change)

*Decision-ready output should:*
- Present Option C as recommended approach
- List pros/cons from planning doc
- Surface disagreement (Tom's ownership concerns)
- Cite evidence (incident metrics, cost analysis)
- Note confidence level (high - multiple sources align on Option C)

---

**Query 2: "Why did INC-2024-089 take so long to resolve?"**

*Expected RAG behavior:*
- **Postmortem** provides detailed timeline and root cause analysis
  - Took 1h 53min to find Anna who'd solved it before
  - No incident commander → chaotic coordination
  - Tool fragmentation → time wasted searching
- **Incident log** shows it's related to INC-2024-021 (6 months prior, same pattern)
- **Slack** shows real-time confusion during incident
  - "Can't find the postmortem in Confluence"
  - Multiple false leads (network, deployment)
- **Process doc** mentions known issue: "Knowledge silos - solutions don't propagate"

*Decision-ready output should:*
- Technical root cause: Connection leak in async error handlers
- Organizational root cause: Knowledge silos, no IC, tool fragmentation
- Evidence: Took nearly 2 hours to find person who'd solved this before
- Sources: Postmortem timeline, Slack #infrastructure-ops thread

---

**Query 3: "What's the incident load on the payment team?"**

*Expected RAG behavior:*
- **Incident log CSV**: 17 incidents in Q3 (filter by team='payment')
- **Resource allocation CSV**: 3 engineers, on-call every 10 days, 65% ops load
- **Planning doc**: "Payment team carries 38% of incidents despite being 15% of engineering"
- **Postmortem**: Dev Patel as primary responder on major incident
- **Slack**: Dev expresses burnout, says "Every 10 days I'm back on-call and we average 5-6 incidents per week"

*Decision-ready output should:*
- 17 incidents in Q3 (38% of total)
- 3-person team with 10-day rotation (unsustainable)
- 65% time on ops vs 15% for product teams
- Primary responder expressing burnout
- Sources: incident_log.csv, resource_allocation.csv, Slack conversations

---

## Intentional Conflicts & Challenges

### 1. Conflicting Opinions (Slack vs Planning Doc)

**Challenge:** Slack shows Tom Chen opposing centralization, but planning doc recommends hybrid model

**Expected behavior:**
- RAG should surface the disagreement
- Explain that Option C (hybrid) is a compromise that addresses Tom's ownership concerns
- Cite that rough consensus formed around Option C despite initial disagreement

### 2. Time-Sensitive Information

**Challenge:** Process doc is dated Aug 15, postmortem is Sept 12, planning doc is Oct 3

**Expected behavior:**
- Prioritize more recent information (planning doc) for strategic questions
- Use process doc for "current state" questions
- Recognize that planning doc reflects learnings from postmortem

### 3. Partial Data (Failure Case)

**Query:** "Should we migrate to Kubernetes?"

**Expected behavior:**
- No evidence in dataset about Kubernetes migration
- RAG should say: "Insufficient evidence in available documents"
- Suggest what data would be needed: "Infrastructure roadmap, container adoption data, cost analysis"

### 4. Multi-Document Reasoning

**Query:** "What's the ROI of Option C vs Option A?"

**Expected behavior:**
- Extract cost/benefit data from planning doc (Option C: $449K, Option A: $750K)
- Reference incident metrics from incident log (MTTR, repeat incidents)
- Reference burnout context from Slack and postmortem
- Calculate payback periods (Option C: 2.3 years, Option A: 3 years)
- Recommend Option C based on budget fit ($450K approved) and lower risk

### 5. Contradictory Metrics

**Challenge:** Planning doc says "23% increase in incidents" but incident log shows 37 → 45 incidents (21.6%)

**Expected behavior:**
- Note the discrepancy
- Recognize 21.6% rounds to ~23% (acceptable variance)
- Or surface as potential data quality issue

---

## Test Queries (Organized by Difficulty)

### Easy (Single Document, Direct Lookup)

1. "What is the current incident response process?"
   - Source: incident_response_process.md
   - Straightforward retrieval

2. "What tools are used for monitoring?"
   - Source: incident_response_process.md, planning doc
   - List retrieval

3. "How many engineers are on the payment team?"
   - Source: resource_allocation.csv
   - Simple filter

### Medium (Multi-Document, Some Reasoning)

4. "What caused the payment gateway incident in September?"
   - Sources: Postmortem + incident log + Slack
   - Technical + organizational causes

5. "Which teams have the highest incident load?"
   - Sources: Incident log (count) + resource allocation (team size)
   - Aggregation + comparison

6. "What are the pros and cons of centralized SRE?"
   - Source: Planning doc
   - Structured extraction

### Hard (Decision-Support, Conflicting Info)

7. "Should we centralize incident response or keep team-based ownership?"
   - Sources: ALL documents
   - Conflicting opinions, cost analysis, evidence synthesis
   - Must produce recommendation with confidence level

8. "Why are repeat incidents increasing?"
   - Sources: Incident log (pattern) + postmortem (knowledge silos) + process doc (challenges) + Slack (context)
   - Pattern recognition + root cause analysis

9. "What immediate actions should we take to reduce payment team burnout?"
   - Sources: Resource allocation (load data) + Slack (burnout signals) + planning doc (options) + postmortem (action items)
   - Prioritization + decision-making

### Failure Cases (Intentional)

10. "Should we adopt microservices architecture?"
    - No evidence in dataset
    - Should refuse to speculate

11. "What's the average salary of an SRE?"
    - Planning doc mentions $160K for Option A, but generic question has insufficient data
    - Should clarify if asking about TechCorp's plan vs industry average

---

## Success Criteria

Your RAG system should be able to:

✅ **Answer grounded in evidence**
- Every claim cites specific document + section/page

✅ **Compare options with pros/cons**
- Extract structured comparisons (e.g., Option A vs B vs C)

✅ **Surface conflicts**
- Identify when Slack disagrees with formal docs
- Present both perspectives

✅ **Aggregate across data types**
- Combine CSV metrics + PDF analysis + Slack context

✅ **Handle time-sensitive queries**
- Prefer newer docs for strategic questions
- Use older docs for "what was the process in August?"

✅ **Refuse gracefully**
- Say "insufficient evidence" when data doesn't exist
- Suggest what additional data would help

✅ **Produce structured output**
- JSON schema with decision_summary, options, risks, recommendation, sources

---

## Dataset Statistics

**Total Size:** ~40 pages equivalent

| File | Type | Size | Sections | Records |
|------|------|------|----------|---------|
| incident_response_process.md | PDF | ~6 pages | 10 + appendix | - |
| incident_postmortem_2024_q3.md | PDF | ~12 pages | 11 + appendices | - |
| quarterly_planning_2024_q4.md | PDF | ~18 pages | 11 sections | - |
| incident_log.csv | CSV | 42 rows | - | 42 incidents |
| resource_allocation.csv | CSV | 9 rows | - | 9 teams |
| slack_ops_channel_export.txt | Text | ~4 pages | 6 threads | 78 messages |

**People mentioned:** 12 named engineers + executives
**Time span:** March 2024 - October 2024 (with Nov 2023 historical reference)
**Key dates:**
- Aug 15: Process doc updated
- Sept 12: Major incident (INC-2024-089)
- Sept 18: Postmortem review
- Oct 3: Planning doc drafted
- Oct 20: Decision deadline

---

## Using This Dataset

### Step 1: Document Chunking Strategy

**Recommendation:**
- **PDFs:** Chunk by section (headers are clear delimiters)
- **CSV:** Each row is a chunk, preserve column headers as metadata
- **Slack:** Each message or thread as chunk, preserve timestamp and author

**Metadata to preserve:**
- Document type (process, postmortem, planning, incident_log, resource, slack)
- Date/timestamp
- Section/thread title
- Author (for Slack)
- Related incident IDs

### Step 2: Embedding Strategy

**Recommendation:**
- Use cheap embeddings (OpenAI text-embedding-3-small or local)
- Embed once, store in vector DB
- Consider hybrid search (semantic + keyword) for incident IDs and names

### Step 3: Retrieval Strategy

**Basic:** Top-k similarity search (k=5-10)

**Better:** Metadata filtering + similarity
- Filter by document type for specific queries
- Filter by date range for time-sensitive queries
- Filter by team for team-specific queries

**Best:** Two-stage retrieval
1. Initial retrieval (k=20)
2. Re-rank by relevance to specific decision question
3. Take top 5-7 for context

### Step 4: LLM Prompting

Use function calling / structured output for decision-support queries.

**Schema example:**
```json
{
  "decision_summary": "string",
  "options": [
    {
      "option": "string",
      "pros": ["string"],
      "cons": ["string"],
      "risks": ["string"],
      "cost": "string"
    }
  ],
  "recommendation": "string",
  "confidence_level": "high|medium|low",
  "reasoning": "string",
  "evidence": [
    {
      "claim": "string",
      "source": "document name",
      "location": "section or page"
    }
  ],
  "conflicts_or_gaps": ["string"]
}
```

### Step 5: Evaluation

**Test Queries:**
- Easy: 90%+ accuracy expected
- Medium: 70-80% accuracy expected
- Hard: 50-70% accuracy (this is genuinely difficult)
- Failure cases: Should refuse, not hallucinate

**Key metrics:**
- Source citation accuracy (are sources real and relevant?)
- Conflict detection (does it surface disagreements?)
- Structured output compliance (valid JSON schema?)
- Refusal rate on out-of-scope queries

---

## Intentional "Gotchas" for Testing

1. **INC-2024-089 appears TWICE in incident_log.csv**
   - Once in chronological order (Sept 12)
   - Once out of order (later in file) because it's the detailed entry
   - RAG should deduplicate

2. **Incident counts don't exactly match**
   - Planning doc: "45 incidents in Q3"
   - Incident log: 42 total records (but some are Q2 or historical)
   - RAG should handle approximate matching or explain discrepancy

3. **Tool costs vary by source**
   - Planning doc: $178K total
   - Resource allocation CSV: Sum of tooling_costs_usd = $240K (includes team-specific tools)
   - RAG should recognize these are different scopes (company-wide vs team-level)

4. **Consensus isn't unanimous**
   - Planning doc recommends Option C
   - Slack shows Tom still prefers Option B
   - RAG should surface this nuance

5. **Action items are time-sensitive**
   - Some marked as complete (✅)
   - Some marked as incomplete (☐)
   - Postmortem is dated Sept 12, but read in October - some items should be complete by now
   - RAG should handle temporal reasoning

---

## Next Steps for Your RAG System

1. **Chunk and embed these documents**
2. **Store in vector DB with metadata**
3. **Test with the provided queries**
4. **Iterate on retrieval strategy based on failures**
5. **Implement structured output with source attribution**
6. **Create one intentional failure case** (e.g., ask about something not in the data)

Good luck! This dataset is designed to be challenging but realistic. Real-world RAG systems face exactly these issues: conflicting sources, time-sensitive data, multi-document reasoning, and the need to produce actionable recommendations rather than just answers.
