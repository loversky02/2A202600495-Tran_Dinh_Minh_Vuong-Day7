"""
So sánh Mock Embeddings vs OpenAI Embeddings
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from src.chunking import compute_similarity
from src.embeddings import _mock_embed
from src import OpenAIEmbedder

load_dotenv(Path(".env"))

print("=" * 80)
print("SO SÁNH: MOCK EMBEDDINGS vs OPENAI EMBEDDINGS")
print("=" * 80)

# Initialize embedders
print("\n1. Khởi tạo embedders...")
mock_embedder = _mock_embed
openai_embedder = OpenAIEmbedder()
print(f"   ✓ Mock embedder: character-based hashing")
print(f"   ✓ OpenAI embedder: {openai_embedder._backend_name}")

# Test pairs
pairs = [
    ("VinUni offers scholarships", "VinUniversity provides financial aid"),
    ("Tuition is 530 million VND", "Students pay 530 million VND for tuition"),
    ("VinUni partners with Cornell", "The weather is hot in summer"),
]

print("\n2. So sánh similarity scores...")
print("=" * 80)

for i, (text_a, text_b) in enumerate(pairs, 1):
    print(f"\nPair {i}:")
    print(f"  A: {text_a}")
    print(f"  B: {text_b}")
    
    # Mock embeddings
    mock_vec_a = mock_embedder(text_a)
    mock_vec_b = mock_embedder(text_b)
    mock_sim = compute_similarity(mock_vec_a, mock_vec_b)
    
    # OpenAI embeddings
    openai_vec_a = openai_embedder(text_a)
    openai_vec_b = openai_embedder(text_b)
    openai_sim = compute_similarity(openai_vec_a, openai_vec_b)
    
    print(f"\n  Mock similarity:   {mock_sim:7.4f}")
    print(f"  OpenAI similarity: {openai_sim:7.4f}")
    
    # Analysis
    if i <= 2:
        print(f"  Expected: HIGH (similar meaning)")
        if openai_sim > 0.7:
            print(f"  ✓ OpenAI correctly identifies similarity!")
        else:
            print(f"  ✗ OpenAI score lower than expected")
    else:
        print(f"  Expected: LOW (unrelated)")
        if openai_sim < 0.3:
            print(f"  ✓ OpenAI correctly identifies difference!")
        else:
            print(f"  ✗ OpenAI score higher than expected")

print("\n" + "=" * 80)
print("KẾT LUẬN")
print("=" * 80)

print("\nMock Embeddings:")
print("  - Dựa trên character hashing (không hiểu nghĩa)")
print("  - Scores ngẫu nhiên, không đáng tin")
print("  - Chỉ tốt cho testing code structure")
print("  - ✗ KHÔNG phù hợp cho production")

print("\nOpenAI Embeddings:")
print("  - Hiểu semantic meaning (nghĩa của câu)")
print("  - Scores phản ánh đúng độ tương tự")
print("  - Nhận biết synonyms và paraphrases")
print("  - ✓ Phù hợp cho production RAG systems")

print("\n💡 Recommendation:")
print("  - Development/Testing: Mock embeddings (nhanh, free)")
print("  - Production: OpenAI embeddings (chính xác, có phí)")

print("\n" + "=" * 80)
