"""
Script to test chunking strategies on VinUni admission documents
"""
from src.chunking import ChunkingStrategyComparator
from pathlib import Path

# Read one of the VinUni documents
doc_path = Path("data/vinuni_admission_overview.md")
with open(doc_path, "r", encoding="utf-8") as f:
    text = f.read()

print(f"Document: {doc_path.name}")
print(f"Total characters: {len(text)}")
print("=" * 80)

# Compare chunking strategies
comparator = ChunkingStrategyComparator()
results = comparator.compare(text, chunk_size=300)

# Display results
for strategy_name, data in results.items():
    print(f"\n{strategy_name.upper()} STRATEGY:")
    print(f"  Number of chunks: {data['count']}")
    print(f"  Average chunk length: {data['avg_length']:.2f} characters")
    print(f"\n  First 3 chunks:")
    for i, chunk in enumerate(data['chunks'][:3], 1):
        preview = chunk[:100].replace('\n', ' ')
        print(f"    [{i}] {preview}...")

print("\n" + "=" * 80)
print("COMPARISON SUMMARY:")
print(f"Fixed Size: {results['fixed_size']['count']} chunks, avg {results['fixed_size']['avg_length']:.0f} chars")
print(f"By Sentences: {results['by_sentences']['count']} chunks, avg {results['by_sentences']['avg_length']:.0f} chars")
print(f"Recursive: {results['recursive']['count']} chunks, avg {results['recursive']['avg_length']:.0f} chars")
