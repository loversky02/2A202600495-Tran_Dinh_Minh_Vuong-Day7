"""
Script to test cosine similarity predictions (Exercise 3.3)
"""
from src.chunking import compute_similarity
from src.embeddings import _mock_embed

# Define 5 pairs of sentences
sentence_pairs = [
    {
        "pair": 1,
        "sentence_a": "VinUni offers scholarships to talented students.",
        "sentence_b": "VinUniversity provides financial aid for excellent learners.",
        "prediction": "HIGH - Both sentences talk about VinUni giving money to good students",
    },
    {
        "pair": 2,
        "sentence_a": "The tuition fee is approximately 530 million VND per year.",
        "sentence_b": "Students need to pay around 530 million VND annually for tuition.",
        "prediction": "VERY HIGH - Almost identical meaning, just rephrased",
    },
    {
        "pair": 3,
        "sentence_a": "VinUni has partnerships with Cornell University.",
        "sentence_b": "The weather in Hanoi is very hot in summer.",
        "prediction": "VERY LOW - Completely unrelated topics",
    },
    {
        "pair": 4,
        "sentence_a": "Students can apply for merit-based scholarships.",
        "sentence_b": "The application deadline is in January.",
        "prediction": "LOW - Both about applications but different aspects",
    },
    {
        "pair": 5,
        "sentence_a": "IELTS 6.5 is required for admission.",
        "sentence_b": "English proficiency test score of 6.5 IELTS needed to enroll.",
        "prediction": "VERY HIGH - Same meaning, different wording",
    },
]

print("=" * 80)
print("COSINE SIMILARITY PREDICTIONS vs ACTUAL RESULTS")
print("=" * 80)

for item in sentence_pairs:
    print(f"\nPair {item['pair']}:")
    print(f"  Sentence A: {item['sentence_a']}")
    print(f"  Sentence B: {item['sentence_b']}")
    print(f"  Prediction: {item['prediction']}")
    
    # Compute actual similarity
    vec_a = _mock_embed(item['sentence_a'])
    vec_b = _mock_embed(item['sentence_b'])
    similarity = compute_similarity(vec_a, vec_b)
    
    print(f"  Actual Score: {similarity:.4f}")
    
    # Interpret the score
    if similarity > 0.9:
        interpretation = "VERY HIGH similarity"
    elif similarity > 0.7:
        interpretation = "HIGH similarity"
    elif similarity > 0.5:
        interpretation = "MODERATE similarity"
    elif similarity > 0.3:
        interpretation = "LOW similarity"
    else:
        interpretation = "VERY LOW similarity"
    
    print(f"  Interpretation: {interpretation}")

print("\n" + "=" * 80)
print("REFLECTION:")
print("The mock embedder uses character-based hashing, so results may differ from")
print("real semantic embeddings. With real embeddings (like OpenAI or sentence-transformers),")
print("we would expect:")
print("- Pairs 2 and 5 to have very high similarity (0.9+)")
print("- Pair 1 to have high similarity (0.7-0.9)")
print("- Pair 4 to have low-moderate similarity (0.3-0.6)")
print("- Pair 3 to have very low similarity (< 0.2)")
print("=" * 80)
