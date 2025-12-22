"""
Chunker: Convert loaded documents into embeddable chunks with metadata
"""
import re
from typing import List, Dict
import hashlib


def chunk_all(raw_docs: List[Dict]) -> List[Dict]:
    """
    Process all documents and return unified chunks

    Args:
        raw_docs: List of document dicts from loaders

    Returns:
        List of chunks ready for embedding
    """
    chunks = []

    for doc in raw_docs:
        doc_type = doc["metadata"]["doc_type"]

        if "document:" in doc_type:  # Markdown documents
            chunk = chunk_markdown(doc)
            if chunk:  # Only add non-empty chunks
                chunks.append(chunk)

        elif doc_type == "incident_log":
            chunk = chunk_incident_row(doc)
            chunks.append(chunk)

        elif doc_type == "resource":
            chunk = chunk_resource_row(doc)
            chunks.append(chunk)

        elif doc_type == "slack":
            chunk = chunk_slack_message(doc)
            chunks.append(chunk)

    return chunks


def chunk_markdown(doc: Dict) -> Dict:
    """
    Process markdown chunk: extract section title and clean up

    Markdown chunks are already split by ## headers from loader
    """
    content = doc["content"]

    if not content.strip():
        return None

    lines = content.split('\n')

    # Extract section title (first non-empty line, usually starts with #)
    section_title = "Introduction"  # Default
    clean_lines = []

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue

        # First non-empty line is likely the section title
        if i == 0 or (i < 3 and stripped.startswith('#')):
            section_title = stripped.lstrip('#').strip()
        else:
            clean_lines.append(line)

    # Reconstruct content without the title (it's in metadata)
    text = '\n'.join(clean_lines).strip()

    if not text:
        return None

    # Generate chunk ID
    chunk_id = generate_chunk_id(doc["metadata"]["source"], section_title)

    return {
        "text": text,
        "metadata": {
            **doc["metadata"],
            "section": section_title,
            "chunk_id": chunk_id
        }
    }


def chunk_incident_row(doc: Dict) -> Dict:
    """
    Convert incident log CSV row to natural language text

    Structure: incident_id, date, severity, service, team, etc.
    """
    row = doc["content"]  # This is a dict from pandas

    # Convert to readable text, skipping NaN values
    parts = []

    # Key fields first
    if pd_notna(row.get('incident_id')):
        parts.append(f"Incident {row['incident_id']}")

    if pd_notna(row.get('date')):
        parts.append(f"occurred on {row['date']}")

    if pd_notna(row.get('severity')):
        parts.append(f"with severity {row['severity']}")

    # Service and team
    details = []
    if pd_notna(row.get('service')):
        details.append(f"Service: {row['service']}")
    if pd_notna(row.get('team')):
        details.append(f"Team: {row['team']}")
    if pd_notna(row.get('duration_minutes')):
        details.append(f"Duration: {row['duration_minutes']} minutes")
    if pd_notna(row.get('customer_impact')):
        details.append(f"Customer impact: {row['customer_impact']}")
    if pd_notna(row.get('root_cause_category')):
        details.append(f"Root cause: {row['root_cause_category']}")

    # Build full text
    summary = ' '.join(parts) + '.'
    detail_text = '\n'.join(details)
    text = f"{summary}\n{detail_text}"

    # Additional context
    if pd_notna(row.get('cross_team')) and row['cross_team']:
        text += "\nThis incident required cross-team coordination."

    if pd_notna(row.get('repeat_incident')) and row['repeat_incident']:
        text += "\nThis is a repeat incident."
        if pd_notna(row.get('related_incidents')):
            text += f" Related to: {row['related_incidents']}"

    if pd_notna(row.get('estimated_revenue_impact')) and row['estimated_revenue_impact'] > 0:
        text += f"\nEstimated revenue impact: ${row['estimated_revenue_impact']}"

    chunk_id = row.get('incident_id', generate_chunk_id(doc["metadata"]["source"], str(row)))

    return {
        "text": text.strip(),
        "metadata": {
            **doc["metadata"],
            "chunk_id": chunk_id
        }
    }


def chunk_resource_row(doc: Dict) -> Dict:
    """
    Convert resource allocation CSV row to natural language text

    Structure: team, headcount, on_call_rotation, budget, etc.
    """
    row = doc["content"]

    parts = []

    # Team info
    if pd_notna(row.get('team')):
        parts.append(f"Team: {row['team']}")
        team_name = row['team']
    else:
        team_name = "unknown"

    if pd_notna(row.get('team_lead')):
        parts.append(f"Lead: {row['team_lead']}")

    # Headcount and on-call
    if pd_notna(row.get('headcount')):
        parts.append(f"Headcount: {row['headcount']} engineers")

    if pd_notna(row.get('on_call_engineers')):
        parts.append(f"On-call engineers: {row['on_call_engineers']}")

    if pd_notna(row.get('on_call_rotation_days')):
        parts.append(f"On-call rotation: every {row['on_call_rotation_days']} days")

    # Incident load
    if pd_notna(row.get('avg_incidents_per_month')):
        parts.append(f"Average incidents per month: {row['avg_incidents_per_month']}")

    # Budget
    if pd_notna(row.get('annual_budget_usd')):
        parts.append(f"Annual budget: ${row['annual_budget_usd']:,.0f}")

    if pd_notna(row.get('on_call_comp_annual_usd')):
        parts.append(f"On-call compensation: ${row['on_call_comp_annual_usd']:,.0f}/year")

    # Workload metrics
    if pd_notna(row.get('ops_load_pct')):
        parts.append(f"Operational load: {row['ops_load_pct']}% of time")

    if pd_notna(row.get('feature_velocity_pts_per_sprint')):
        parts.append(f"Feature velocity: {row['feature_velocity_pts_per_sprint']} points/sprint")

    text = '\n'.join(parts)

    chunk_id = generate_chunk_id(doc["metadata"]["source"], team_name)

    return {
        "text": text.strip(),
        "metadata": {
            **doc["metadata"],
            "chunk_id": chunk_id
        }
    }


def chunk_slack_message(doc: Dict) -> Dict:
    """
    Process Slack message - already well-structured from loader

    Just add chunk_id and format text nicely
    """
    meta = doc["metadata"]

    # Format: [Thread: title] Author (timestamp): message
    text = f"[Thread: {meta['thread_title']}]\n"
    text += f"{meta['author']} ({meta['timestamp']}): {doc['content']}"

    chunk_id = generate_chunk_id(
        meta['source'],
        f"{meta['thread_title']}_{meta['author']}_{meta['timestamp']}"
    )

    return {
        "text": text,
        "metadata": {
            **meta,
            "chunk_id": chunk_id
        }
    }


def generate_chunk_id(source: str, identifier: str) -> str:
    """
    Generate unique, deterministic chunk ID

    Uses hash to keep IDs short but unique
    """
    combined = f"{source}::{identifier}"
    hash_obj = hashlib.md5(combined.encode())
    return hash_obj.hexdigest()[:12]  # First 12 chars of hash


def pd_notna(value) -> bool:
    """
    Check if pandas value is not NaN

    Handles both pandas NaN and regular None
    """
    import math
    if value is None:
        return False
    if isinstance(value, float) and math.isnan(value):
        return False
    return True
