"""
Test generation with retrieval

Run after: python scripts/build_index.py

Tests:
1. Load vector store
2. Retrieve chunks for a test query
3. Generate structured response
4. Verify output format and content
"""
import sys
sys.path.insert(0, "/Users/arielkatzir/Library/CloudStorage/GoogleDrive-ari.katzir@gmail.com/My Drive/Colab Notebooks/rag_enterprise")


from src.embedding.vector_store import VectorStore
from src.embedding.embedder import Embedder
from src.generation.generator import Generator
from src.generation.schemas import DecisionResponse


def main():
    print("=" * 60, flush=True)
    print("Testing End-to-End Generation", flush=True)
    print("=" * 60, flush=True)

    # Load vector store
    print("\n1. Loading vector store...", flush=True)
    vs = VectorStore()
    vs.load("vector_store")
    print(f"✓ Loaded {vs.index.ntotal} vectors", flush=True)

    # Initialize embedder and generator
    print("\n2. Initializing embedder and generator...", flush=True)
    embedder = Embedder()
    generator = Generator(model="gpt-4o-mini")
    print("✓ Components initialized", flush=True)

    # Test query
    query = "Should we centralize incident response?"

    print(f"\n3. Query: {query}", flush=True)
    print("=" * 60, flush=True)

    # Embed query
    print("\nEmbedding query...", flush=True)
    query_embedding = embedder.embed_query(query)
    print("✓ Query embedded", flush=True)

    # Retrieve relevant chunks
    print("\nRetrieving top 15 chunks...", flush=True)
    retrieved_chunks = vs.search(query_embedding, k=15)
    print(f"✓ Retrieved {len(retrieved_chunks)} chunks", flush=True)

    # Show what was retrieved
    print("\nRetrieved sources:", flush=True)
    for i, chunk in enumerate(retrieved_chunks[:5], 1):
        meta = chunk["metadata"]
        print(f"  [{i}] {meta['source']} (distance: {chunk['_distance']:.3f})", flush=True)
    if len(retrieved_chunks) > 5:
        print(f"  ... and {len(retrieved_chunks) - 5} more", flush=True)

    # Generate response
    print("\n4. Generating structured response...", flush=True)
    print("(This may take 10-30 seconds depending on context size)", flush=True)
    response = generator.generate(
        query=query,
        retrieved_chunks=retrieved_chunks,
        response_schema=DecisionResponse
    )

    # Display structured response
    print("\n" + "=" * 60, flush=True)
    print("GENERATED RESPONSE", flush=True)
    print("=" * 60, flush=True)

    print(f"\n📋 Decision Summary:", flush=True)
    print(f"   {response.decision_summary}", flush=True)

    if response.options:
        print(f"\n🔍 Options Identified: {len(response.options)}", flush=True)
        for i, option in enumerate(response.options, 1):
            print(f"\n   Option {i}: {option.option}", flush=True)
            if option.cost:
                print(f"   Cost: {option.cost}", flush=True)
            print(f"   Pros: {len(option.pros)} | Cons: {len(option.cons)} | Risks: {len(option.risks)}", flush=True)

    print(f"\n💡 Recommendation:", flush=True)
    print(f"   {response.recommendation}", flush=True)

    print(f"\n📊 Confidence: {response.confidence_level.upper()}", flush=True)

    print(f"\n🧠 Reasoning:", flush=True)
    print(f"   {response.reasoning[:200]}...", flush=True)

    print(f"\n📚 Evidence Citations: {len(response.evidence)}", flush=True)
    for i, evidence in enumerate(response.evidence[:3], 1):
        print(f"   [{i}] {evidence.source}: {evidence.claim[:80]}...", flush=True)
    if len(response.evidence) > 3:
        print(f"   ... and {len(response.evidence) - 3} more citations", flush=True)

    if response.conflicts_or_gaps:
        print(f"\n⚠️  Conflicts/Gaps: {len(response.conflicts_or_gaps)}", flush=True)
        for i, conflict in enumerate(response.conflicts_or_gaps, 1):
            print(f"   [{i}] {conflict[:100]}...", flush=True)

    # Validation checks
    print("\n" + "=" * 60, flush=True)
    print("VALIDATION CHECKS", flush=True)
    print("=" * 60, flush=True)

    checks_passed = 0
    total_checks = 0

    # Check 1: Options extracted
    total_checks += 1
    if len(response.options) >= 2:
        print("✓ Multiple options extracted", flush=True)
        checks_passed += 1
    else:
        print("✗ Expected multiple options", flush=True)

    # Check 2: Evidence citations
    total_checks += 1
    if len(response.evidence) >= 3:
        print("✓ Multiple evidence sources cited", flush=True)
        checks_passed += 1
    else:
        print("✗ Expected multiple evidence citations", flush=True)

    # Check 3: Costs mentioned
    total_checks += 1
    has_costs = any(opt.cost for opt in response.options)
    if has_costs:
        print("✓ Cost information included", flush=True)
        checks_passed += 1
    else:
        print("✗ Expected cost information", flush=True)

    # Check 4: Conflicts detected
    total_checks += 1
    if len(response.conflicts_or_gaps) > 0:
        print("✓ Conflicts/gaps identified", flush=True)
        checks_passed += 1
    else:
        print("⚠  No conflicts detected (expected some from Slack vs docs)", flush=True)

    # Check 5: Source attribution
    total_checks += 1
    sources_mentioned = [e.source for e in response.evidence]
    if len(set(sources_mentioned)) >= 2:
        print("✓ Multiple source types cited", flush=True)
        checks_passed += 1
    else:
        print("✗ Expected citations from multiple sources", flush=True)

    print(f"\n📈 Validation: {checks_passed}/{total_checks} checks passed", flush=True)

    print("\n" + "=" * 60, flush=True)
    print("✓ Generation test complete!", flush=True)
    print("=" * 60, flush=True)


if __name__ == "__main__":
    main()
