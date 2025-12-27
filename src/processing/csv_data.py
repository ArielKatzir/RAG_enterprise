"""
CSV data processor: Loader + Chunker

Handles CSV files (incident logs, resource allocation, etc.)
Each row becomes a chunk
"""

import pandas as pd
import math
from typing import List, Dict
from .base import BaseLoader, BaseChunker


class CSVLoader(BaseLoader):
    """
    Load CSV files, each row becomes a document
    """

    def load(self, source_path: str) -> List[Dict]:
        """
        Load CSV file

        Args:
            source_path: Path to CSV file

        Returns:
            List of dicts, one per row
        """
        df = pd.read_csv(source_path)

        rows = []
        for _, row in df.iterrows():
            rows.append({
                "content": row.to_dict(),  # Original structured data
                "metadata": {
                    "source": source_path.split('/')[-1],
                    "doc_type": "incident_log" if "incident" in source_path else "resource",
                    **row.to_dict()  # All columns become searchable metadata
                }
            })

        return rows


class CSVChunker(BaseChunker):
    """
    Chunk CSV rows for embedding

    Converts structured data to natural language text
    """

    def chunk(self, doc: Dict) -> List[Dict]:
        """
        Convert CSV row into natural language text

        Args:
            doc: Document from CSVLoader

        Returns:
            List with single chunk containing formatted text
        """
        row = doc["content"]
        doc_type = doc["metadata"]["doc_type"]

        if doc_type == "incident_log":
            text = self._format_incident(row)
            chunk_id = row.get('incident_id', self.generate_chunk_id(
                doc["metadata"]["source"], str(row)
            ))
        else:  # resource
            text = self._format_resource(row)
            team_name = row.get('team', 'unknown')
            chunk_id = self.generate_chunk_id(
                doc["metadata"]["source"], team_name
            )

        return [{
            "text": text.strip(),
            "metadata": {
                **doc["metadata"],
                "chunk_id": chunk_id
            }
        }]

    def _format_incident(self, row: dict) -> str:
        """Format incident log row as natural language"""
        parts = []

        # Key fields
        if self._notna(row.get('incident_id')):
            parts.append(f"Incident {row['incident_id']}")
        if self._notna(row.get('date')):
            parts.append(f"occurred on {row['date']}")
        if self._notna(row.get('severity')):
            parts.append(f"with severity {row['severity']}")

        # Service and team
        details = []
        if self._notna(row.get('service')):
            details.append(f"Service: {row['service']}")
        if self._notna(row.get('team')):
            details.append(f"Team: {row['team']}")
        if self._notna(row.get('duration_minutes')):
            details.append(f"Duration: {row['duration_minutes']} minutes")
        if self._notna(row.get('customer_impact')):
            details.append(f"Customer impact: {row['customer_impact']}")
        if self._notna(row.get('root_cause_category')):
            details.append(f"Root cause: {row['root_cause_category']}")

        # Build text
        summary = ' '.join(parts) + '.'
        detail_text = '\n'.join(details)
        text = f"{summary}\n{detail_text}"

        # Additional context
        if self._notna(row.get('cross_team')) and row['cross_team']:
            text += "\nThis incident required cross-team coordination."
        if self._notna(row.get('repeat_incident')) and row['repeat_incident']:
            text += "\nThis is a repeat incident."
            if self._notna(row.get('related_incidents')):
                text += f" Related to: {row['related_incidents']}"
        if self._notna(row.get('estimated_revenue_impact')) and row['estimated_revenue_impact'] > 0:
            text += f"\nEstimated revenue impact: ${row['estimated_revenue_impact']}"

        return text

    def _format_resource(self, row: dict) -> str:
        """Format resource allocation row as natural language"""
        parts = []

        # Team info
        if self._notna(row.get('team')):
            parts.append(f"Team: {row['team']}")
        if self._notna(row.get('team_lead')):
            parts.append(f"Lead: {row['team_lead']}")

        # Headcount
        if self._notna(row.get('headcount')):
            parts.append(f"Headcount: {row['headcount']} engineers")
        if self._notna(row.get('on_call_engineers')):
            parts.append(f"On-call engineers: {row['on_call_engineers']}")
        if self._notna(row.get('on_call_rotation_days')):
            parts.append(f"On-call rotation: every {row['on_call_rotation_days']} days")

        # Incident load
        if self._notna(row.get('avg_incidents_per_month')):
            parts.append(f"Average incidents per month: {row['avg_incidents_per_month']}")

        # Budget
        if self._notna(row.get('annual_budget_usd')):
            parts.append(f"Annual budget: ${row['annual_budget_usd']:,.0f}")
        if self._notna(row.get('on_call_comp_annual_usd')):
            parts.append(f"On-call compensation: ${row['on_call_comp_annual_usd']:,.0f}/year")

        # Workload
        if self._notna(row.get('ops_load_pct')):
            parts.append(f"Operational load: {row['ops_load_pct']}% of time")
        if self._notna(row.get('feature_velocity_pts_per_sprint')):
            parts.append(f"Feature velocity: {row['feature_velocity_pts_per_sprint']} points/sprint")

        return '\n'.join(parts)

    @staticmethod
    def _notna(value) -> bool:
        """Check if value is not NaN/None"""
        if value is None:
            return False
        if isinstance(value, float) and math.isnan(value):
            return False
        return True
