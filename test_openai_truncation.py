"""
Quick test to verify OpenAI truncation fix works.
Tests with just one large chunk to confirm no token limit error.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Force fresh imports
for module in list(sys.modules.keys()):
    if module.startswith('src.'):
        del sys.modules[module]

# Now import
from src.chunking import SentenceChunker
from src.embeddings import OpenAIEmbedder

# Load environment
load_dotenv()

def test_truncation():
    """Test that large chunks are truncated properly."""
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY not found!")
        return False
    
    print("Testing OpenAI truncation fix...")
    print("="*60)
    
    # Load one document
    content = Path("data/bls_cpi_december_2025.txt").read_text(encoding='utf-8')
    
    # Create chunks
    chunker = SentenceChunker(max_sentences_per_chunk=3)
    chunks = chunker.chunk(content)
    
    print(f"Total chunks: {len(chunks)}")
    print(f"Max chunk length: {max(len(c) for c in chunks)} chars")
    print(f"Chunks over 6000 chars: {sum(1 for c in chunks if len(c) > 6000)}")
    
    # Find the largest chunk
    largest_chunk = max(chunks, key=len)
    print(f"\nLargest chunk: {len(largest_chunk)} chars")
    print(f"First 100 chars: {largest_chunk[:100]}...")
    
    # Try to embed it
    print("\nTesting embedding with OpenAI...")
    embedder = OpenAIEmbedder()
    
    try:
        embedding = embedder(largest_chunk)
        print(f"✓ SUCCESS! Embedding created: {len(embedding)} dimensions")
        print(f"✓ Truncation fix is working!")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

if __name__ == "__main__":
    success = test_truncation()
    sys.exit(0 if success else 1)
