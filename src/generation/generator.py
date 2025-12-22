"""
Generator: Convert retrieved chunks + query into structured decision-support responses
"""
import os
import json
from typing import List, Dict, Type
from pydantic import BaseModel
from openai import OpenAI


def load_api_key() -> str:
    """Load OpenAI API key from secrets.json"""
    secrets_path = "/Users/arielkatzir/Library/CloudStorage/GoogleDrive-ari.katzir@gmail.com/My Drive/.secrets.json"

    if os.path.exists(secrets_path):
        with open(secrets_path, 'r') as f:
            secrets = json.load(f)
            return secrets["OPENAI_API_KEY"]

    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return api_key

    raise ValueError("OpenAI API key not found")


class Generator:
    """
    Generates structured responses from query + retrieved chunks

    Why GPT-4o-mini:
    - Cheap: $0.15/1M input, $0.60/1M output tokens
    - Smart enough for multi-document reasoning
    - Supports structured output (JSON schema enforcement)
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        """
        Initialize generator

        Args:
            model: OpenAI model
                - gpt-4o-mini: Cheap, good quality
                - gpt-4o: Better but 10x more expensive
        """
        api_key = load_api_key()
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate(self,
                 query: str,
                 retrieved_chunks: List[Dict],
                 response_schema: Type[BaseModel]) -> BaseModel:
        """
        Generate structured response from query + context

        Args:
            query: User's question
            retrieved_chunks: Top-k chunks from retriever (with metadata)
            response_schema: Pydantic model (usually DecisionResponse)

        Returns:
            Parsed Pydantic object (guaranteed valid schema)
        """
        # Build context from chunks
        context = self._build_context(retrieved_chunks)

        # System prompt (defines behavior)
        system_prompt = self._get_system_prompt()

        # User prompt (specific to this query)
        user_prompt = f"""Query: {query}

Retrieved context:
{context}

Analyze the retrieved documents and provide a comprehensive decision-ready response.

Instructions:
- If this is a comparison/decision query (e.g., "Should we...?"), extract all options with structured pros/cons/risks/costs
- Every factual claim MUST cite the source document and location
- If sources conflict (e.g., Slack conversations disagree with formal docs), explicitly list this in conflicts_or_gaps
- If evidence is insufficient, set confidence_level to "low" and explain what's missing
- Use exact document names from the context (shown in [Source N: filename])
- Be specific: include costs, timelines, metrics from the context
"""

        print(f"Generating response for: {query[:60]}...", flush=True)

        # Call OpenAI with structured output
        response = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format=response_schema
        )

        print(f"✓ Generated structured response", flush=True)
        return response.choices[0].message.parsed

    def _get_system_prompt(self) -> str:
        """
        System prompt defining the AI's behavior

        Why this matters:
        - Generic prompts → generic answers ("consider the trade-offs")
        - Specific prompts → actionable outputs ("Option C costs $450K, fits budget")
        """
        return """You are a decision-support AI for operations teams.

Your job is to:
1. Analyze retrieved documents (formal process docs, incident postmortems, CSV data, Slack conversations)
2. Synthesize evidence from multiple sources
3. Surface conflicting information explicitly
4. Produce structured, actionable recommendations

CRITICAL RULES:
- Every factual claim MUST cite source document + location (section/page/row)
- If sources conflict (e.g., Slack disagrees with formal docs), explicitly mention it in conflicts_or_gaps
- If evidence is insufficient, say so (confidence_level: "low") and suggest what's missing
- Prioritize newer documents for strategic questions (check dates in metadata)
- Use exact document names from the context (as shown in [Source N: filename - section])
- For decision queries, extract and structure ALL options with pros/cons/risks/costs
- Be specific: use exact numbers, costs, timelines from the context
- Do not make up information not present in the retrieved context

Context structure:
Each retrieved chunk is labeled [Source N: filename - section/metadata].
Only cite sources from the provided context - do not reference external knowledge.

Your responses must be:
- Evidence-based (cite specific sources)
- Decision-ready (clear recommendation with reasoning)
- Honest about uncertainty (flag conflicts and gaps)
- Actionable (specific, not generic advice)
"""

    def _build_context(self, chunks: List[Dict]) -> str:
        """
        Format retrieved chunks into readable context for LLM

        Why this format:
        - Clear source labels → LLM knows what to cite
        - Metadata included → Section names, dates, authors help LLM prioritize
        - Separators → Chunk boundaries clear
        """
        if not chunks:
            return "(No relevant context retrieved)"

        context_parts = []
        for i, chunk in enumerate(chunks):
            meta = chunk["metadata"]
            source_label = f"Source {i+1}: {meta['source']}"

            # Add additional context from metadata
            metadata_info = []

            if "section" in meta and meta["section"]:
                metadata_info.append(f"Section: {meta['section']}")

            if "thread_title" in meta:
                metadata_info.append(f"Thread: {meta['thread_title']}")

            if "author" in meta:
                metadata_info.append(f"Author: {meta['author']}")

            if "thread_date" in meta and meta["thread_date"] != "Unknown":
                metadata_info.append(f"Date: {meta['thread_date']}")

            if "date" in meta:
                metadata_info.append(f"Date: {meta['date']}")

            # Build source header
            if metadata_info:
                source_label += f" ({', '.join(metadata_info)})"

            # Add distance for transparency (lower = more relevant)
            if "_distance" in chunk:
                source_label += f" [Relevance: {1 / (1 + chunk['_distance']):.2f}]"

            context_parts.append(
                f"[{source_label}]\n{chunk['text']}\n"
            )

        return "\n" + ("=" * 60) + "\n".join(context_parts)


# Convenience function for one-off generation
def generate_response(query: str,
                     retrieved_chunks: List[Dict],
                     response_schema: Type[BaseModel] = None,
                     model: str = "gpt-4o-mini") -> BaseModel:
    """
    Generate a response (convenience function)

    Args:
        query: User question
        retrieved_chunks: Top-k chunks from retriever
        response_schema: Pydantic model (imports DecisionResponse if None)
        model: OpenAI model name

    Returns:
        Parsed response object
    """
    if response_schema is None:
        from .schemas import DecisionResponse
        response_schema = DecisionResponse

    generator = Generator(model=model)
    return generator.generate(query, retrieved_chunks, response_schema)
