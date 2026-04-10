# OpenAI Embeddings Benchmark Results

## Test Configuration
- **Embedding Model**: OpenAI text-embedding-3-small (1536 dimensions)
- **Chunking Strategy**: SentenceChunker with max_sentences_per_chunk=3
- **Total Documents**: 6 financial documents
- **Total Chunks**: 383 chunks
- **Test Date**: 2026-04-10

## Benchmark Queries Results

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|----------------------------------|-------|-----------|------------------------|
| 1 | What was the CPI inflation rate in December 2025? | `bls_cpi_december_2025.txt` - Consumer Price Index (CPI) Report chứa thông tin về CPI tháng 12/2025 với Year-over-Year Change: 2.7% và Month-over-Month: 0.3% | 0.6880 | Có | Agent có thể trả lời rằng CPI tháng 12/2025 tăng 2.7% so với cùng kỳ năm trước và 0.3% so với tháng trước |
| 2 | What did the Federal Reserve decide about interest rates in December 2025? | `fed_fomc_statement_2025_07_30.txt` - Federal Reserve FOMC Statement tháng 7/2025 (KHÔNG ĐÚNG - cần document tháng 12/2025) | 0.5568 | Không | Agent cần document đúng để trả lời: Fed hạ lãi suất 25 basis points vào tháng 12/2025 |
| 3 | What was the unemployment rate in March 2026? | `bls_employment_situation_march_2026.txt` - Employment Situation Report nêu rõ "unemployment rate, at 4.3 percent" | 0.7238 | Có | Agent có thể trả lời rằng tỷ lệ thất nghiệp tháng 3/2026 là 4.3% |
| 4 | How many jobs were added in March 2026? | `bls_employment_situation_march_2026.txt` - Employment Situation Report chứa thông tin về nonfarm payrolls tăng 178,000 jobs | 0.8097 | Có | Agent có thể trả lời rằng có 178,000 việc làm được thêm vào trong tháng 3/2026 |
| 5 | What was the Fed's interest rate decision in September 2025? | `fed_fomc_statement_2025_07_30.txt` - Federal Reserve FOMC Statement tháng 7/2025 (KHÔNG ĐÚNG - cần document tháng 9/2025) | 0.5327 | Không | Agent cần document đúng để trả lời: Fed hạ lãi suất 50 basis points vào tháng 9/2025 |

## Performance Metrics

### Precision@1 (Top-1 Accuracy)
- **Relevant Results**: 3/5 queries (60%)
- **Average Similarity Score**: 0.6622

### Precision@3 (Top-3 Accuracy)
- **Relevant Results**: From full benchmark - 73% average precision
- **Queries with Perfect Precision (3/3)**: 
  - Query 1: CPI inflation rate (100%)
  - Query 3: Unemployment rate (100%)
  - Query 4: Jobs added (100%)
- **Queries with Partial Precision**:
  - Query 2: Fed December decision (33% - 1/3 relevant)
  - Query 5: Fed September decision (33% - 1/3 relevant)

## Comparison with Mock Embeddings

| Metric | Mock Embeddings | OpenAI Embeddings | Improvement |
|--------|----------------|-------------------|-------------|
| Average Precision@3 | 0.27 (27%) | 0.73 (73%) | +171.6% |
| Embedding Quality | Deterministic hash-based | Semantic understanding | Significantly better |
| Query Understanding | No semantic meaning | Understands context | Much better |

## Key Findings

### Strengths
1. **Excellent performance on factual queries**: CPI rates, unemployment rates, job numbers (100% precision)
2. **Strong semantic understanding**: OpenAI embeddings capture meaning, not just keywords
3. **Massive improvement over mock**: 171.6% better than hash-based embeddings

### Weaknesses
1. **Date-specific queries struggle**: Fed interest rate decisions for specific months (December, September) had lower precision
2. **Similar documents confuse retrieval**: Multiple FOMC statements with similar content cause confusion
3. **Top-1 vs Top-3 gap**: Precision@1 (60%) is lower than Precision@3 (73%), suggesting relevant documents are often in positions 2-3

### Recommendations
1. **Add date metadata filtering**: Pre-filter by date before semantic search for time-specific queries
2. **Hybrid search**: Combine keyword matching (for dates) with semantic search (for concepts)
3. **Chunk size optimization**: Current chunks (up to 18,592 chars) are truncated to 6,000 chars - consider smaller chunks for better granularity

## Technical Notes

### Truncation Handling
- OpenAI API has 8,192 token limit
- Implemented automatic truncation at 6,000 characters
- Financial text with numbers/symbols uses more tokens per character
- 1 chunk exceeded 6,000 chars and was automatically truncated

### Chunking Statistics
- Total chunks: 383
- Average chunk length: ~1,500 characters (estimated)
- Max chunk length: 18,592 characters (before truncation)
- Chunks requiring truncation: 1

## Conclusion

OpenAI embeddings provide **significantly better retrieval quality** than mock embeddings, with 73% precision@3 compared to 27% for mock embeddings. The system works well for factual queries but could benefit from hybrid search combining semantic understanding with metadata filtering for date-specific queries.
