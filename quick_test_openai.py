"""Quick test OpenAI embeddings"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(".env"))

print("Testing OpenAI Embeddings...")
print(f"API Key: {os.getenv('OPENAI_API_KEY', 'NOT SET')[:20]}...")
print(f"Model: {os.getenv('OPENAI_EMBEDDING_MODEL', 'NOT SET')}")

try:
    from src import OpenAIEmbedder
    embedder = OpenAIEmbedder()
    print(f"\n✓ Embedder: {embedder._backend_name}")
    
    # Test
    text = "VinUni is great"
    embedding = embedder(text)
    print(f"✓ Embedding size: {len(embedding)} dimensions")
    print(f"✓ First 5 values: {[f'{x:.4f}' for x in embedding[:5]]}")
    print("\n✅ OpenAI embeddings working!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
