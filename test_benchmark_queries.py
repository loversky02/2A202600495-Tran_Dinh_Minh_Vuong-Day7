"""
Benchmark queries for financial RAG system.

This script tests retrieval quality on real financial documents.
"""

from pathlib import Path
from src.chunking import SentenceChunker
from src.embeddings import _mock_embed
from src.store import EmbeddingStore


def load_documents():
    """Load all financial documents."""
    data_dir = Path("data")
    documents = []
    
    # Load all .txt files
    for txt_file in sorted(data_dir.glob("*.txt")):
        content = txt_file.read_text(encoding='utf-8')
        doc_id = txt_file.stem
        
        # Extract metadata from filename
        if "cpi" in doc_id.lower():
            category = "inflation"
            indicators = "cpi,mom_change,yoy_change"  # Convert to string
        elif "employment" in doc_id.lower():
            category = "employment"
            indicators = "unemployment_rate,nonfarm_payrolls"
        elif "fomc" in doc_id.lower():
            category = "monetary_policy"
            indicators = "interest_rates,federal_funds_rate"
        else:
            category = "general"
            indicators = ""
        
        documents.append({
            'doc_id': doc_id,
            'content': content,
            'metadata': {
                'category': category,
                'indicators': indicators,
                'source': 'BLS' if 'bls' in doc_id else 'Federal Reserve'
            }
        })
    
    return documents


def create_store_with_documents(max_sentences=3):
    """Create embedding store and add all documents."""
    from src.models import Document
    
    documents = load_documents()
    
    # Initialize chunker and store
    chunker = SentenceChunker(max_sentences_per_chunk=max_sentences)
    store = EmbeddingStore(embedding_fn=_mock_embed)
    
    # Add documents
    for doc in documents:
        chunks = chunker.chunk(doc['content'])
        
        # Create Document objects for each chunk
        doc_objects = []
        for i, chunk in enumerate(chunks):
            doc_obj = Document(
                id=f"{doc['doc_id']}_chunk_{i}",
                content=chunk,
                metadata={**doc['metadata'], 'doc_id': doc['doc_id'], 'chunk_index': i}
            )
            doc_objects.append(doc_obj)
        
        store.add_documents(doc_objects)
    
    return store, documents


def run_benchmark():
    """Run benchmark queries and display results."""
    print("="*80)
    print("BENCHMARK QUERIES - Financial RAG System")
    print("="*80)
    
    # Create store
    print("\nLoading documents and creating embeddings...")
    store, documents = create_store_with_documents(max_sentences=3)
    
    print(f"Loaded {len(documents)} documents")
    print(f"Total chunks in store: {store.get_collection_size()}")
    
    # Define benchmark queries
    queries = [
        {
            'id': 1,
            'query': "What was the CPI inflation rate in December 2025?",
            'gold_answer': "2.7% year-over-year, 0.3% month-over-month",
            'expected_doc': "bls_cpi_december_2025"
        },
        {
            'id': 2,
            'query': "What did the Federal Reserve decide about interest rates in December 2025?",
            'gold_answer': "Lowered the target range by 25 basis points",
            'expected_doc': "fed_fomc_statement_2025_12_10"
        },
        {
            'id': 3,
            'query': "What was the unemployment rate in March 2026?",
            'gold_answer': "4.3%",
            'expected_doc': "bls_employment_situation_march_2026"
        },
        {
            'id': 4,
            'query': "How many jobs were added in March 2026?",
            'gold_answer': "178,000 nonfarm payrolls",
            'expected_doc': "bls_employment_situation_march_2026"
        },
        {
            'id': 5,
            'query': "What was the Fed's interest rate decision in September 2025?",
            'gold_answer': "Lowered the target range by 50 basis points",
            'expected_doc': "fed_fomc_statement_2025_09_17"
        }
    ]
    
    print("\n" + "="*80)
    print("RUNNING BENCHMARK QUERIES")
    print("="*80)
    
    results = []
    
    for q in queries:
        print(f"\n{'='*80}")
        print(f"Query {q['id']}: {q['query']}")
        print(f"Gold Answer: {q['gold_answer']}")
        print(f"Expected Document: {q['expected_doc']}")
        print(f"{'='*80}")
        
        # Search
        search_results = store.search(q['query'], top_k=3)
        
        # Calculate precision
        relevant_count = 0
        retrieved_docs = []
        
        print("\nTop-3 Retrieved Chunks:")
        for i, result in enumerate(search_results, 1):
            doc_id = result['metadata'].get('doc_id', 'unknown')
            retrieved_docs.append(doc_id)
            
            # Check if relevant
            is_relevant = doc_id == q['expected_doc']
            if is_relevant:
                relevant_count += 1
            
            relevance_mark = "✓ RELEVANT" if is_relevant else "✗ NOT RELEVANT"
            
            print(f"\n[{i}] Score: {result['score']:.4f} | Doc: {doc_id} | {relevance_mark}")
            print(f"    Content: {result['content'][:150]}...")
        
        precision = relevant_count / 3
        
        print(f"\nPrecision@3: {precision:.2f} ({relevant_count}/3 relevant)")
        
        results.append({
            'query_id': q['id'],
            'query': q['query'],
            'precision': precision,
            'retrieved_docs': retrieved_docs,
            'expected_doc': q['expected_doc']
        })
    
    # Summary
    print("\n" + "="*80)
    print("BENCHMARK SUMMARY")
    print("="*80)
    
    avg_precision = sum(r['precision'] for r in results) / len(results)
    
    print(f"\nAverage Precision@3: {avg_precision:.2f}")
    print(f"\nResults by Query:")
    print(f"\n{'Query':<6} {'Precision':<12} {'Retrieved Documents':<50}")
    print("-"*80)
    
    for r in results:
        docs_str = ", ".join(r['retrieved_docs'])
        print(f"{r['query_id']:<6} {r['precision']:<12.2f} {docs_str:<50}")
    
    print("\n" + "="*80)
    print("NOTE: Using mock embeddings - results will be poor.")
    print("Real embeddings (OpenAI, sentence-transformers) would perform much better.")
    print("="*80)
    
    return results


if __name__ == "__main__":
    run_benchmark()
