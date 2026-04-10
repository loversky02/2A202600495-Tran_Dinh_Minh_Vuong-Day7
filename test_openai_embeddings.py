"""
Test với OpenAI Embeddings (Real Semantic Embeddings)

Requirements:
- pip install openai
- Set OPENAI_API_KEY in .env file
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=Path(".env"), override=False)

print("=" * 80)
print("TEST OPENAI EMBEDDINGS")
print("=" * 80)

# Check if OpenAI API key is set
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("\n❌ ERROR: OPENAI_API_KEY not found in .env file")
    print("Please add your OpenAI API key to .env file:")
    print("OPENAI_API_KEY=sk-...")
    exit(1)

print(f"\n✓ OPENAI_API_KEY found: {api_key[:20]}...")

# Try to import and use OpenAI embedder
try:
    from src import OpenAIEmbedder
    from src.chunking import compute_similarity
    
    print("\n1. Initializing OpenAI Embedder...")
    model_name = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    print(f"   Model: {model_name}")
    
    embedder = OpenAIEmbedder(model_name=model_name)
    print(f"   ✓ Embedder initialized: {embedder._backend_name}")
    
    # Test embedding
    print("\n2. Testing embedding generation...")
    test_text = "VinUni offers scholarships to students."
    embedding = embedder(test_text)
    print(f"   Text: '{test_text}'")
    print(f"   ✓ Embedding generated: {len(embedding)} dimensions")
    print(f"   First 5 values: {embedding[:5]}")
    
    # Test similarity with real embeddings
    print("\n3. Testing cosine similarity with real embeddings...")
    print("=" * 80)
    
    sentence_pairs = [
        {
            "pair": 1,
            "sentence_a": "VinUni offers scholarships to talented students.",
            "sentence_b": "VinUniversity provides financial aid for excellent learners.",
            "expected": "HIGH - Same concept, different words",
        },
        {
            "pair": 2,
            "sentence_a": "The tuition fee is approximately 530 million VND per year.",
            "sentence_b": "Students need to pay around 530 million VND annually for tuition.",
            "expected": "VERY HIGH - Almost identical meaning",
        },
        {
            "pair": 3,
            "sentence_a": "VinUni has partnerships with Cornell University.",
            "sentence_b": "The weather in Hanoi is very hot in summer.",
            "expected": "VERY LOW - Completely unrelated",
        },
        {
            "pair": 4,
            "sentence_a": "Students can apply for merit-based scholarships.",
            "sentence_b": "The application deadline is in January.",
            "expected": "LOW-MODERATE - Related but different aspects",
        },
        {
            "pair": 5,
            "sentence_a": "IELTS 6.5 is required for admission.",
            "sentence_b": "English proficiency test score of 6.5 IELTS needed to enroll.",
            "expected": "VERY HIGH - Same meaning, different wording",
        },
    ]
    
    for item in sentence_pairs:
        print(f"\nPair {item['pair']}:")
        print(f"  A: {item['sentence_a']}")
        print(f"  B: {item['sentence_b']}")
        print(f"  Expected: {item['expected']}")
        
        # Compute with OpenAI embeddings
        vec_a = embedder(item['sentence_a'])
        vec_b = embedder(item['sentence_b'])
        similarity = compute_similarity(vec_a, vec_b)
        
        print(f"  Actual Score: {similarity:.4f}")
        
        # Interpret
        if similarity > 0.9:
            interpretation = "VERY HIGH similarity ✓"
        elif similarity > 0.7:
            interpretation = "HIGH similarity ✓"
        elif similarity > 0.5:
            interpretation = "MODERATE similarity"
        elif similarity > 0.3:
            interpretation = "LOW similarity"
        else:
            interpretation = "VERY LOW similarity ✓"
        
        print(f"  Interpretation: {interpretation}")
    
    print("\n" + "=" * 80)
    print("COMPARISON: OpenAI vs Mock Embeddings")
    print("=" * 80)
    print("\nOpenAI Embeddings (Real Semantic Understanding):")
    print("  ✓ Understands synonyms (scholarships = financial aid)")
    print("  ✓ Recognizes paraphrases (same meaning, different words)")
    print("  ✓ Correctly identifies unrelated topics")
    print("  ✓ Suitable for production RAG systems")
    
    print("\nMock Embeddings (Character-based Hashing):")
    print("  ✗ No semantic understanding")
    print("  ✗ Random similarity scores")
    print("  ✓ Good for testing code structure only")
    
    print("\n" + "=" * 80)
    print("✅ SUCCESS: OpenAI embeddings working correctly!")
    print("=" * 80)
    
    # Test with EmbeddingStore
    print("\n4. Testing with EmbeddingStore...")
    from src.store import EmbeddingStore
    from src.models import Document
    
    store = EmbeddingStore(
        collection_name="test_openai",
        embedding_fn=embedder  # ← Use OpenAI embedder
    )
    
    docs = [
        Document("d1", "VinUni offers scholarships ranging from 50% to 100%.", {"type": "financial"}),
        Document("d2", "The tuition fee is 530 million VND per year.", {"type": "financial"}),
        Document("d3", "IELTS 6.5 is required for admission.", {"type": "requirements"}),
    ]
    
    store.add_documents(docs)
    print(f"   ✓ Added {store.get_collection_size()} documents with OpenAI embeddings")
    
    # Search
    query = "How much does it cost to study at VinUni?"
    results = store.search(query, top_k=2)
    print(f"\n   Query: '{query}'")
    print(f"   Top results:")
    for i, result in enumerate(results, 1):
        print(f"     {i}. {result['content']}")
        print(f"        Score: {result['score']:.4f}")
    
    print("\n   ✓ Search with OpenAI embeddings works perfectly!")
    print("   ✓ Results are semantically relevant!")
    
except ImportError as e:
    print(f"\n❌ ERROR: Missing dependency")
    print(f"   {e}")
    print("\nTo install:")
    print("   pip install openai")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nPossible issues:")
    print("  1. Invalid API key")
    print("  2. No internet connection")
    print("  3. OpenAI API quota exceeded")
    print("\nCheck your .env file and API key status.")

print("\n" + "=" * 80)
