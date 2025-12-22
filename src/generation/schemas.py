"""
Response schemas for structured LLM outputs

Uses Pydantic for validation and OpenAI structured output enforcement
"""
from pydantic import BaseModel, Field
from typing import List, Literal, Optional


class Evidence(BaseModel):
    """
    Source citation for a factual claim

    Why: Challenge requires source attribution for every claim
    """
    claim: str = Field(
        description="The specific factual claim being made"
    )
    source: str = Field(
        description="Source document name (e.g., 'incident_postmortem_2024_q3.md', 'slack_ops_channel_export.txt')"
    )
    location: str = Field(
        description="Section, page, or row identifier for precise attribution"
    )


class Option(BaseModel):
    """
    A decision option with structured trade-offs

    Why: Challenge requires comparing options with pros/cons/risks
    """
    option: str = Field(
        description="Name of this option (e.g., 'Centralized SRE', 'Hybrid model')"
    )
    pros: List[str] = Field(
        description="Benefits and advantages of this option",
        default_factory=list
    )
    cons: List[str] = Field(
        description="Drawbacks and disadvantages of this option",
        default_factory=list
    )
    risks: List[str] = Field(
        description="Implementation risks and potential failure modes",
        default_factory=list
    )
    cost: str = Field(
        default="",
        description="Cost estimate if available in the context"
    )


class DecisionResponse(BaseModel):
    """
    Complete decision-support response

    Why: Maps to challenge requirements - decision-ready output with evidence
    """
    decision_summary: str = Field(
        description="High-level summary of the decision to be made or question to be answered"
    )

    options: List[Option] = Field(
        default_factory=list,
        description="Available options if this is a comparison/decision query. Empty list if not applicable."
    )

    recommendation: str = Field(
        description="Recommended course of action based on evidence, or direct answer to the question"
    )

    confidence_level: Literal["high", "medium", "low"] = Field(
        description="Confidence in this response based on evidence quality and completeness"
    )

    reasoning: str = Field(
        description="Explanation of why this recommendation was made, referencing specific evidence"
    )

    evidence: List[Evidence] = Field(
        description="Source citations for all factual claims made in the response"
    )

    conflicts_or_gaps: List[str] = Field(
        default_factory=list,
        description="Conflicting information found across sources, or gaps in available data"
    )


# Example of how to use this schema:
# response = openai.beta.chat.completions.parse(
#     model="gpt-4o-mini",
#     messages=[...],
#     response_format=DecisionResponse
# )
# result = response.choices[0].message.parsed  # Guaranteed valid DecisionResponse object
