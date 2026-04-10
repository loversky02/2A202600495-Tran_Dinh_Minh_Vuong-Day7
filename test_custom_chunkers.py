"""
Optional: Test custom chunking strategies
"""
from pathlib import Path
from src.custom_chunker import FAQChunker, HeaderAwareChunker
from src.chunking import FixedSizeChunker, SentenceChunker, RecursiveChunker

# Test on FAQ document
faq_path = Path("data/vinuni_admission_faq.txt")
with open(faq_path, "r", encoding="utf-8") as f:
    faq_text = f.read()

# Test on markdown document
md_path = Path("data/vinuni_admission_overview.md")
with open(md_path, "r", encoding="utf-8") as f:
    md_text = f.read()

print("=" * 80)
print("CUSTOM CHUNKERS COMPARISON")
print("=" * 80)

# Test FAQ Chunker on FAQ document
print("\n1. FAQ DOCUMENT (vinuni_admission_faq.txt)")
print(f"   Total characters: {len(faq_text)}")
print("-" * 80)

chunkers = {
    "Fixed Size (300)": FixedSizeChunker(chunk_size=300, overlap=50),
    "Sentence (3)": SentenceChunker(max_sentences_per_chunk=3),
    "Recursive (300)": RecursiveChunker(chunk_size=300),
    "FAQ Custom (500)": FAQChunker(max_chunk_size=500),
}

for name, chunker in chunkers.items():
    chunks = chunker.chunk(faq_text)
    avg_len = sum(len(c) for c in chunks) / len(chunks) if chunks else 0
    print(f"\n{name}:")
    print(f"  Chunks: {len(chunks)}, Avg length: {avg_len:.0f} chars")
    if chunks:
        print(f"  First chunk preview: {chunks[0][:100].replace(chr(10), ' ')}...")

# Test Header-Aware Chunker on Markdown document
print("\n" + "=" * 80)
print("2. MARKDOWN DOCUMENT (vinuni_admission_overview.md)")
print(f"   Total characters: {len(md_text)}")
print("-" * 80)

md_chunkers = {
    "Fixed Size (300)": FixedSizeChunker(chunk_size=300, overlap=50),
    "Recursive (300)": RecursiveChunker(chunk_size=300),
    "Header-Aware (500)": HeaderAwareChunker(max_chunk_size=500),
}

for name, chunker in md_chunkers.items():
    chunks = chunker.chunk(md_text)
    avg_len = sum(len(c) for c in chunks) / len(chunks) if chunks else 0
    print(f"\n{name}:")
    print(f"  Chunks: {len(chunks)}, Avg length: {avg_len:.0f} chars")
    if chunks:
        print(f"  First chunk preview: {chunks[0][:100].replace(chr(10), ' ')}...")

print("\n" + "=" * 80)
print("ANALYSIS:")
print("- FAQ Chunker: Designed to keep Q&A pairs together")
print("- Header-Aware Chunker: Respects markdown structure, keeps headers with content")
print("- Both custom chunkers produce more coherent chunks for their respective domains")
print("- Trade-off: More complex logic, but better semantic preservation")
print("=" * 80)
