"""
Internal Operations Intelligence Copilot
End-to-end RAG system for decision support

Usage:
    python -u src/main.py

Features:
- Loads vector store once (fast subsequent queries)
- Retrieves relevant chunks via semantic search
- Generates structured decision-ready responses
- Interactive CLI with command history
"""
import sys
import json
from typing import Optional

from embedding.vector_store import VectorStore
from embedding.embedder import Embedder
from retrieval.retriever import Retriever
from generation.generator import Generator
from generation.schemas import DecisionResponse


class OperationsCopilot:
    """
    Main RAG system for operations decision support

    Architecture:
    1. Query -> Embedder -> query vector
    2. Query vector -> VectorStore -> top-k chunks
    3. Query + chunks -> Generator -> structured response
    """

    def __init__(self,
                 vector_store_path: str = "vector_store",
                 model: str = "gpt-4o-mini",
                 default_k: int = 15):
        """
        Initialize the copilot system

        Args:
            vector_store_path: Path to FAISS index + chunks
            model: OpenAI model for generation
            default_k: Default number of chunks to retrieve
        """
        print("=" * 60, flush=True)
        print("Internal Operations Intelligence Copilot", flush=True)
        print("=" * 60, flush=True)

        print("\nInitializing system...", flush=True)

        # Load vector store
        print(f"Loading vector store from {vector_store_path}...", flush=True)
        self.vector_store = VectorStore()
        self.vector_store.load(vector_store_path)
        print(f"✓ Loaded {self.vector_store.index.ntotal} vectors", flush=True)

        # Initialize components
        print("Initializing embedder...", flush=True)
        self.embedder = Embedder()
        print("✓ Embedder ready", flush=True)

        print(f"Initializing generator ({model})...", flush=True)
        self.generator = Generator(model=model)
        print("✓ Generator ready", flush=True)

        # Create retriever
        self.retriever = Retriever(self.vector_store, self.embedder)
        self.default_k = default_k

        # Show stats
        stats = self.vector_store.stats()
        print(f"\nIndexed documents:", flush=True)
        for doc_type, count in stats["by_doc_type"].items():
            print(f"  - {doc_type}: {count} chunks", flush=True)

        print("\n✓ System ready!", flush=True)
        print("=" * 60, flush=True)

    def query(self,
              question: str,
              k: Optional[int] = None,
              show_sources: bool = True,
              show_context: bool = False) -> DecisionResponse:
        """
        Ask a question and get structured response

        Args:
            question: User's query
            k: Number of chunks to retrieve (None = use default)
            show_sources: Print retrieved sources
            show_context: Print full context (verbose)

        Returns:
            DecisionResponse object
        """
        k = k or self.default_k

        print(f"\n{'=' * 60}", flush=True)
        print(f"Query: {question}", flush=True)
        print(f"{'=' * 60}", flush=True)

        # Retrieve
        print(f"\nRetrieving top {k} chunks...", flush=True)
        chunks = self.retriever.retrieve(question, k=k)
        print(f"✓ Retrieved {len(chunks)} chunks", flush=True)

        # Show sources if requested
        if show_sources:
            print("\nRetrieved sources:", flush=True)
            sources_shown = set()
            for chunk in chunks[:10]:  # Show up to 10
                source = chunk["metadata"]["source"]
                distance = chunk["_distance"]
                if source not in sources_shown:
                    print(f"  - {source} (distance: {distance:.3f})", flush=True)
                    sources_shown.add(source)
            if len(chunks) > 10:
                print(f"  ... and {len(chunks) - 10} more chunks", flush=True)

        # Show full context if requested (verbose)
        if show_context:
            print("\n" + "=" * 60, flush=True)
            print("RETRIEVED CONTEXT", flush=True)
            print("=" * 60, flush=True)
            for i, chunk in enumerate(chunks, 1):
                meta = chunk["metadata"]
                print(f"\n[{i}] {meta['source']}", flush=True)
                print(f"Distance: {chunk['_distance']:.4f}", flush=True)
                print(chunk["text"][:300] + "...", flush=True)

        # Generate
        print("\nGenerating response...", flush=True)
        response = self.generator.generate(
            query=question,
            retrieved_chunks=chunks,
            response_schema=DecisionResponse
        )

        return response

    def display_response(self, response: DecisionResponse):
        """
        Pretty-print structured response

        Args:
            response: DecisionResponse object
        """
        print("\n" + "=" * 60, flush=True)
        print("RESPONSE", flush=True)
        print("=" * 60, flush=True)

        print(f"\n📋 Summary:", flush=True)
        print(f"{response.decision_summary}\n", flush=True)

        if response.options:
            print(f"🔍 Options ({len(response.options)}):", flush=True)
            for i, option in enumerate(response.options, 1):
                print(f"\n  {i}. {option.option}", flush=True)
                if option.cost:
                    print(f"     Cost: {option.cost}", flush=True)
                if option.pros:
                    print(f"     Pros:", flush=True)
                    for pro in option.pros[:3]:  # Show top 3
                        print(f"       + {pro}", flush=True)
                if option.cons:
                    print(f"     Cons:", flush=True)
                    for con in option.cons[:3]:  # Show top 3
                        print(f"       - {con}", flush=True)
                if option.risks:
                    print(f"     Risks:", flush=True)
                    for risk in option.risks[:2]:  # Show top 2
                        print(f"       ⚠ {risk}", flush=True)

        print(f"\n💡 Recommendation:", flush=True)
        print(f"{response.recommendation}\n", flush=True)

        print(f"📊 Confidence: {response.confidence_level.upper()}", flush=True)

        print(f"\n🧠 Reasoning:", flush=True)
        print(f"{response.reasoning}\n", flush=True)

        print(f"📚 Evidence ({len(response.evidence)} citations):", flush=True)
        for i, evidence in enumerate(response.evidence[:5], 1):  # Show top 5
            print(f"  [{i}] {evidence.source}", flush=True)
            print(f"      {evidence.claim}", flush=True)
            if evidence.location:
                print(f"      Location: {evidence.location}", flush=True)
        if len(response.evidence) > 5:
            print(f"  ... and {len(response.evidence) - 5} more citations", flush=True)

        if response.conflicts_or_gaps:
            print(f"\n⚠️  Conflicts/Gaps ({len(response.conflicts_or_gaps)}):", flush=True)
            for i, conflict in enumerate(response.conflicts_or_gaps, 1):
                print(f"  {i}. {conflict}", flush=True)

        print("\n" + "=" * 60, flush=True)

    def run_cli(self):
        """
        Interactive CLI for querying the system

        Commands:
        - Any question: Get answer
        - 'quit' or 'exit': Exit
        - 'stats': Show system stats
        - 'examples': Show example queries
        """
        print("\n" + "=" * 60, flush=True)
        print("Interactive Mode", flush=True)
        print("=" * 60, flush=True)
        print("\nCommands:", flush=True)
        print("  - Ask any question to get a structured response", flush=True)
        print("  - 'stats': Show system statistics", flush=True)
        print("  - 'examples': Show example queries", flush=True)
        print("  - 'quit' or 'exit': Exit", flush=True)
        print("\n" + "=" * 60, flush=True)

        while True:
            try:
                query = input("\n> ").strip()

                if not query:
                    continue

                if query.lower() in ['quit', 'exit', 'q']:
                    print("\nGoodbye!", flush=True)
                    break

                if query.lower() == 'stats':
                    self._show_stats()
                    continue

                if query.lower() == 'examples':
                    self._show_examples()
                    continue

                # Process query
                response = self.query(query)
                self.display_response(response)

            except KeyboardInterrupt:
                print("\n\nGoodbye!", flush=True)
                break
            except Exception as e:
                print(f"\n❌ Error: {e}", flush=True)
                import traceback
                traceback.print_exc()

    def _show_stats(self):
        """Show system statistics"""
        stats = self.vector_store.stats()
        print("\n" + "=" * 60, flush=True)
        print("SYSTEM STATISTICS", flush=True)
        print("=" * 60, flush=True)
        print(f"\nTotal chunks: {stats['total_chunks']}", flush=True)
        print(f"\nBy document type:", flush=True)
        for doc_type, count in stats["by_doc_type"].items():
            print(f"  - {doc_type}: {count}", flush=True)
        print(f"\nBy source:", flush=True)
        for source, count in sorted(stats["by_source"].items()):
            print(f"  - {source}: {count}", flush=True)
        print("=" * 60, flush=True)

    def _show_examples(self):
        """Show example queries"""
        print("\n" + "=" * 60, flush=True)
        print("EXAMPLE QUERIES", flush=True)
        print("=" * 60, flush=True)
        print("\nDecision questions:", flush=True)
        print("  - Should we centralize incident response?", flush=True)
        print("  - What are the options for improving incident management?", flush=True)
        print("\nFactual questions:", flush=True)
        print("  - What caused the payment gateway incident?", flush=True)
        print("  - Which team has the most incidents?", flush=True)
        print("  - What do people think about centralization?", flush=True)
        print("\nAnalytical questions:", flush=True)
        print("  - What are the main challenges with our current incident response?", flush=True)
        print("  - What evidence supports centralization?", flush=True)
        print("=" * 60, flush=True)


def main():
    """
    Entry point for the copilot system
    """
    # Initialize system
    copilot = OperationsCopilot(
        vector_store_path="vector_store",
        model="gpt-4o-mini",
        default_k=15
    )

    # Run interactive CLI
    copilot.run_cli()


if __name__ == "__main__":
    main()
