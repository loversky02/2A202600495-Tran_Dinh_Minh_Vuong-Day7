# Day 7 Lab Report - Data Foundations: Embedding & Vector Store

**Student Name:** Tran Dinh Minh Vuong  
**Student ID:** 2A202600495  
**Date:** April 10, 2026

---

## Section 1: Warm-up Exercises

### Exercise 1.1 — Cosine Similarity in Plain Language

**What does it mean for two text chunks to have high cosine similarity?**

When two text chunks have high cosine similarity, it means they are semantically similar or talk about related topics. The cosine similarity measures the angle between two vectors in high-dimensional space - when the angle is small (cosine close to 1), the vectors point in similar directions, indicating the texts share similar meaning or context.

**Examples:**

HIGH Similarity:
- Sentence 1: "VinUni offers scholarships to talented students."
- Sentence 2: "VinUniversity provides financial aid for excellent learners."
- These sentences have high similarity because they both discuss the same concept (financial support for good students at VinUni), just using different words.

LOW Similarity:
- Sentence 1: "The tuition fee is 530 million VND per year."
- Sentence 2: "The weather in Hanoi is very hot in summer."
- These sentences have low similarity because they discuss completely unrelated topics (tuition vs weather).

**Why is cosine similarity preferred over Euclidean distance for text embeddings?**

Cosine similarity is preferred because:

1. **Scale-invariant:** Cosine similarity measures the angle between vectors, not their magnitude. This means a short document and a long document can still be considered similar if they discuss the same topic, even though their embedding magnitudes differ.

2. **Normalized comparison:** Euclidean distance is affected by the length of the vectors. Two documents about the same topic but with different lengths would have large Euclidean distance, even though they're semantically similar.

3. **Better for high-dimensional spaces:** In high-dimensional embedding spaces (e.g., 384 or 1536 dimensions), Euclidean distance becomes less meaningful due to the "curse of dimensionality." Cosine similarity remains effective because it focuses on direction rather than magnitude.

4. **Range interpretation:** Cosine similarity ranges from -1 to 1, making it easy to interpret (1 = identical direction, 0 = orthogonal/unrelated, -1 = opposite direction).

---

### Exercise 1.2 — Chunking Math

**Problem 1:**
- Document length: 10,000 characters
- Chunk size: 500
- Overlap: 50

Formula: `num_chunks = ceil((doc_length - overlap) / (chunk_size - overlap))`

Calculation:
```
num_chunks = ceil((10,000 - 50) / (500 - 50))
           = ceil(9,950 / 450)
           = ceil(22.11)
           = 23 chunks
```

**Expected number of chunks: 23**

**Problem 2:**
If overlap is increased to 100:

```
num_chunks = ceil((10,000 - 100) / (500 - 100))
           = ceil(9,900 / 400)
           = ceil(24.75)
           = 25 chunks
```

**New number of chunks: 25**

**Why would you want more overlap?**

More overlap is beneficial because:

1. **Context preservation:** Overlap ensures that important information spanning chunk boundaries isn't lost. If a key concept is split across two chunks, the overlap helps maintain context.

2. **Better retrieval:** When searching, queries might match content near chunk boundaries. With overlap, relevant information is more likely to be captured in at least one chunk.

3. **Reduced fragmentation:** Sentences or paragraphs that would be awkwardly split are more likely to appear complete in at least one chunk.

4. **Trade-off:** However, more overlap means more chunks (more storage, more processing time) and potential redundancy in search results. The optimal overlap depends on your use case - typically 10-20% of chunk size is a good balance.

---

## Section 2: Document Selection (Group Work)

**Domain:** University Admission Information

**Documents Prepared:**

| # | Document Name | Source | Characters | Metadata |
|---|--------------|--------|-----------|----------|
| 1 | vinuni_admission_overview.md | https://vinuni.edu.vn/admission/ | 3,196 | category: overview, language: en, type: general_info |
| 2 | vinuni_tuition_scholarships.md | https://admissions.vinuni.edu.vn/ | 8,547 | category: financial, language: en, type: tuition_scholarships |
| 3 | vinuni_admission_faq.txt | https://families.vinuni.edu.vn/faq/ | 10,234 | category: faq, language: en, type: questions_answers |

**Metadata Schema:**
- `category`: Type of information (overview, financial, faq, requirements, etc.)
- `language`: Language of the document (en, vi)
- `type`: Content format (general_info, tuition_scholarships, questions_answers, etc.)
- `source`: URL or origin of the document
- `last_updated`: Date when information was last updated (optional)

**Rationale for Domain Choice:**

I chose university admission information because:
1. It's a real-world use case where RAG systems can provide significant value
2. The information is structured but diverse (requirements, fees, FAQs, deadlines)
3. It contains both factual data (numbers, dates) and descriptive content
4. Metadata filtering is naturally useful (e.g., filter by category or language)
5. It's relevant to students and can demonstrate practical applications

---

## Section 3: Chunking Strategy Comparison

### Baseline Comparison

I ran `ChunkingStrategyComparator().compare()` on the VinUni admission overview document (3,196 characters) with chunk_size=300.

**Results:**

| Strategy | Number of Chunks | Avg Chunk Length | Min Length | Max Length |
|----------|-----------------|------------------|------------|------------|
| Fixed Size | 13 | 292 chars | 250 | 300 |
| By Sentences | 6 | 530 chars | 200 | 800 |
| Recursive | 18 | 176 chars | 50 | 300 |

**Analysis:**

1. **Fixed Size Strategy:**
   - Most predictable and consistent chunk sizes
   - May split sentences awkwardly at boundaries
   - Good for: Documents where uniform chunk size is important for processing

2. **By Sentences Strategy:**
   - Creates larger, more coherent chunks
   - Preserves sentence boundaries, maintaining readability
   - Variable chunk sizes (some very large)
   - Good for: Documents where semantic coherence is critical

3. **Recursive Strategy:**
   - Creates the most chunks with smallest average size
   - Tries to split at natural boundaries (paragraphs, then sentences, then words)
   - More granular, potentially better for precise retrieval
   - Good for: Documents with clear hierarchical structure

**First 3 Chunks Preview:**

**Fixed Size:**
```
[1] # VinUni Admission Overview  ## About VinUniversity  VinUniversity (VinUni) is a premier private uni...
[2] ike Cornell University and the University of Pennsylvania, VinUni provides an internationally recogn...
[3] e - Marketing - Operations and Supply Management - Hospitality Leadership - Entrepreneurship - Busin...
```

**By Sentences:**
```
[1] # VinUni Admission Overview  ## About VinUniversity  VinUniversity (VinUni) is a premier private uni...
[2] College of Business & Management - Finance - Marketing - Operations and Supply Management - Hospital...
[3] College of Engineering and Computer Science - Computer Science - Electrical Engineering - Mechanical...
```

**Recursive:**
```
[1] # VinUni Admission Overview  ## About VinUniversity...
[2] VinUniversity (VinUni) is a premier private university in Vietnam, known for its world-class educati...
[3] Partnering with top global institutions like Cornell University and the University of Pennsylvania, ...
```

### My Strategy Choice

For the VinUni admission documents, I would choose **Recursive Chunking with chunk_size=400** because:

1. **Natural boundaries:** Admission documents have clear structure (sections, paragraphs, lists)
2. **Balanced granularity:** 400 chars allows complete thoughts while staying focused
3. **Better retrieval:** Smaller, focused chunks mean more precise matching for specific queries
4. **Flexibility:** Recursive strategy adapts to document structure rather than forcing uniform sizes

**Parameters:**
- `chunk_size=400`
- `separators=["\n\n", "\n", ". ", " ", ""]` (default)
- Metadata: Include section headers in metadata for better filtering

---

## Section 4: My Implementation Approach

### Chunking Implementation

**SentenceChunker:**
- Used regex `r'(?<=[.!?])\s+|\.\n'` to split on sentence boundaries
- Grouped sentences into chunks of `max_sentences_per_chunk`
- Stripped whitespace to clean up chunks

**RecursiveChunker:**
- Implemented recursive splitting with separator priority
- Base case: no more separators or text fits in chunk_size
- Recursive case: split by current separator, recurse on oversized pieces
- Handles edge cases like empty separators (character-level splitting)

**compute_similarity:**
- Implemented standard cosine similarity formula: `dot(a,b) / (||a|| * ||b||)`
- Added guards for zero-magnitude vectors
- Used existing `_dot` helper function for efficiency

### Store Implementation

**EmbeddingStore:**
- Dual-mode design: ChromaDB when available, in-memory fallback
- `_make_record`: Creates normalized dict with id, content, embedding, metadata
- `add_documents`: Batch embedding and storage
- `search`: Embeds query, computes similarities, returns top_k sorted by score
- `search_with_filter`: Pre-filters by metadata, then searches filtered set
- `delete_document`: Removes all chunks matching doc_id

**Key Design Decisions:**
1. Used dot product for in-memory similarity (equivalent to cosine for normalized vectors)
2. Sorted results by score descending for relevance ranking
3. Metadata filtering done before similarity search for efficiency

### Agent Implementation

**KnowledgeBaseAgent:**
- Simple RAG pattern: retrieve → build prompt → call LLM
- Retrieves top_k chunks using store.search()
- Builds structured prompt with numbered context chunks
- Delegates answer generation to llm_fn

**Prompt Template:**
```
Based on the following context, answer the question.

Context:
[1] {chunk1}
[2] {chunk2}
[3] {chunk3}

Question: {question}

Answer:
```

This template provides clear structure for the LLM to ground its response in the retrieved context.

---

## Section 5: Cosine Similarity Predictions (Exercise 3.3)

### Predictions and Results

| Pair | Sentence A | Sentence B | Prediction | Actual Score | Surprised? |
|------|-----------|-----------|------------|--------------|------------|
| 1 | VinUni offers scholarships to talented students. | VinUniversity provides financial aid for excellent learners. | HIGH (0.7-0.9) | 0.0178 | YES |
| 2 | The tuition fee is approximately 530 million VND per year. | Students need to pay around 530 million VND annually for tuition. | VERY HIGH (0.9+) | -0.0689 | YES |
| 3 | VinUni has partnerships with Cornell University. | The weather in Hanoi is very hot in summer. | VERY LOW (<0.2) | 0.1796 | NO |
| 4 | Students can apply for merit-based scholarships. | The application deadline is in January. | LOW (0.3-0.5) | -0.0836 | YES |
| 5 | IELTS 6.5 is required for admission. | English proficiency test score of 6.5 IELTS needed to enroll. | VERY HIGH (0.9+) | -0.0225 | YES |

### Reflection

**What surprised me most:**

The mock embedder produced very different results from what I expected! All similarity scores were very low (close to 0 or even negative), even for pairs that should be highly similar (Pairs 2 and 5).

**Why this happened:**

The `_mock_embed` function uses character-based hashing, which doesn't capture semantic meaning. It essentially treats text as random character sequences, so:
- Synonyms (scholarships vs financial aid) aren't recognized as similar
- Rephrased sentences (Pairs 2 and 5) get completely different embeddings
- Even unrelated sentences (Pair 3) can have similar scores by chance

**What I learned:**

1. **Embeddings matter:** The quality of embeddings is crucial for RAG systems. Mock embeddings are fine for testing code structure, but real semantic embeddings (OpenAI, sentence-transformers) are essential for production.

2. **Semantic understanding:** Real embeddings capture meaning, not just characters. They understand that "scholarships" and "financial aid" are related concepts.

3. **Testing limitations:** When testing with mock data, we need to be aware of its limitations and not draw conclusions about real-world performance.

**Expected results with real embeddings:**
- Pairs 2 and 5: 0.9+ (nearly identical meaning)
- Pair 1: 0.7-0.9 (same concept, different words)
- Pair 4: 0.3-0.6 (related but different aspects)
- Pair 3: <0.2 (completely unrelated)

---

## Section 6: Benchmark Results (Group Work)

**Note:** This section will be completed after group discussion and benchmark query design.

### Benchmark Queries and Gold Answers

| # | Query | Gold Answer | Expected Chunk |
|---|-------|-------------|----------------|
| 1 | TBD | TBD | TBD |
| 2 | TBD | TBD | TBD |
| 3 | TBD | TBD | TBD |
| 4 | TBD | TBD | TBD |
| 5 | TBD | TBD | TBD |

### My Strategy Results

**Strategy:** Recursive Chunking (chunk_size=400)

| Query | Top-3 Retrieved Chunks | Precision | Notes |
|-------|----------------------|-----------|-------|
| 1 | TBD | TBD | TBD |
| 2 | TBD | TBD | TBD |
| 3 | TBD | TBD | TBD |
| 4 | TBD | TBD | TBD |
| 5 | TBD | TBD | TBD |

### Group Comparison

**Strategies tested:**
- Member 1: TBD
- Member 2: TBD
- Member 3: TBD
- Me: Recursive (chunk_size=400)

**Findings:**
- TBD after group discussion

---

## Section 7: What I Learned

### Key Takeaways

1. **Chunking is an art and science:**
   - No one-size-fits-all strategy
   - Document structure matters (FAQs vs essays vs technical docs)
   - Trade-offs between coherence and granularity

2. **Embeddings are the foundation:**
   - Quality of embeddings directly impacts retrieval quality
   - Mock embeddings are useful for testing but not for evaluation
   - Real semantic embeddings understand context and synonyms

3. **RAG pattern is powerful but simple:**
   - Three steps: retrieve, build prompt, generate
   - The quality of retrieval determines answer quality
   - Prompt engineering matters for grounding

4. **Metadata is underutilized:**
   - Filtering by metadata can dramatically improve precision
   - Good metadata schema design is crucial
   - Hybrid search (semantic + metadata) is often best

### Failure Analysis

**Failure Case:** (To be completed after benchmark testing)

**Query:** TBD

**What went wrong:** TBD

**Why it failed:**
- TBD

**Proposed improvements:**
- TBD

### Technical Challenges Overcome

1. **Recursive splitting logic:**
   - Challenge: Handling edge cases (empty separators, no separators left)
   - Solution: Clear base cases and careful separator reconstruction

2. **In-memory vs ChromaDB abstraction:**
   - Challenge: Supporting both backends with same interface
   - Solution: Conditional logic in each method, normalized return format

3. **Metadata filtering:**
   - Challenge: Efficient filtering before similarity search
   - Solution: Pre-filter records, then search only filtered subset

### Future Improvements

1. **Better chunking strategies:**
   - Semantic chunking (split when topic changes)
   - Sliding window with dynamic overlap
   - Header-aware chunking for structured documents

2. **Hybrid search:**
   - Combine semantic search with keyword search (BM25)
   - Use metadata filtering more aggressively
   - Re-ranking based on multiple signals

3. **Evaluation metrics:**
   - Implement precision@k, recall@k
   - Measure chunk coherence automatically
   - A/B test different strategies systematically

4. **Production considerations:**
   - Caching for frequently accessed chunks
   - Batch processing for large document sets
   - Monitoring and logging for debugging

---

## Section 8: Code Quality and Testing

### Test Results

All 42 tests passed successfully:

```
======================== 42 passed in 0.24s =========================
```

**Test Coverage:**
- Chunking strategies: 19 tests ✅
- EmbeddingStore: 14 tests ✅
- KnowledgeBaseAgent: 2 tests ✅
- Similarity computation: 4 tests ✅
- Project structure: 3 tests ✅

### Code Organization

**Strengths:**
- Clear separation of concerns (chunking, store, agent)
- Consistent interfaces across chunking strategies
- Good error handling (zero-magnitude vectors, empty inputs)
- Dual-mode store design (ChromaDB + in-memory fallback)

**Areas for improvement:**
- Add type hints to all helper functions
- More comprehensive docstrings
- Unit tests for edge cases
- Performance benchmarks for large documents

---

## Conclusion

This lab provided hands-on experience with the fundamental building blocks of RAG systems: chunking, embeddings, vector stores, and retrieval-augmented generation. The most valuable lesson was understanding that these components are interconnected - the quality of chunking affects retrieval, which affects the final answer quality.

The VinUni admission documents proved to be an excellent test case, with diverse content types (overviews, FAQs, financial information) that benefit from different chunking strategies. Moving forward, I'm excited to test these implementations with real embeddings and see how they perform in production-like scenarios.

**Total time spent:** ~6 hours (implementation + testing + documentation)

**Most challenging part:** Implementing recursive chunking with proper separator handling

**Most rewarding part:** Seeing all 42 tests pass and understanding how RAG systems work end-to-end

---

## Appendix: Code Snippets

### Chunking Comparison Script

See `test_chunking_comparison.py` for the full script used to compare strategies.

### Similarity Testing Script

See `test_similarity.py` for the cosine similarity prediction experiments.

### Documents Created

1. `data/vinuni_admission_overview.md` - General admission information
2. `data/vinuni_tuition_scholarships.md` - Detailed financial information
3. `data/vinuni_admission_faq.txt` - Frequently asked questions

All documents sourced from official VinUni websites with proper attribution.
