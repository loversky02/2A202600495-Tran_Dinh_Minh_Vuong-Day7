"""
Benchmark queries with REAL OpenAI embeddings AND LLM answers.

This script tests end-to-end RAG: retrieval + answer generation.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from src.chunking import SentenceChunker
from src.embeddings import OpenAIEmbedder
from src.store import EmbeddingStore
from src.agent import KnowledgeBaseAgent
from src.models import Document

# Load environment variables
load_dotenv()


def openai_llm(prompt: str) -> str:
    """Call OpenAI GPT to generate answer."""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # hoặc "gpt-3.5-turbo" để rẻ hơn
            messages=[
                {"role": "system", "content": "You are a helpful financial analyst assistant. Answer questions based on the provided context. Be concise and accurate."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,  # Deterministic answers
            max_tokens=200
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[ERROR] Failed to call OpenAI: {e}"


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
            indicators = "cpi,mom_change,yoy_change"
        elif "employment" in doc_id.lower():
            category = "employment"
            indicators = "unemployment_rate,nonfarm_payrolls"
        elif "fomc" in doc_id.lower():
            category = "monetary_policy"
            indicators = "interest_rates,federal_funds_rate"
        else:
            category = "general"
            indicators = ""
        
        # Extract date from filename if present
        date = None
        parts = doc_id.split('_')
        for i, part in enumerate(parts):
            if part.isdigit() and len(part) == 4:  # Year
                if i + 1 < len(parts) and i + 2 < len(parts):
                    try:
                        month = parts[i + 1]
                        day = parts[i + 2] if parts[i + 2].isdigit() else None
                        date = f"{part}-{month}-{day}" if day else f"{part}-{month}"
                    except:
                        pass
        
        # Build metadata without None values (ChromaDB doesn't accept None)
        metadata = {
            'category': category,
            'indicators': indicators,
            'source': 'BLS' if 'bls' in doc_id else 'Federal Reserve'
        }
        if date:
            metadata['date'] = date
        
        documents.append({
            'doc_id': doc_id,
            'content': content,
            'metadata': metadata
        })
    
    return documents


def create_store_with_documents(max_sentences=3):
    """Create embedding store with OpenAI embeddings."""
    documents = load_documents()
    
    # Initialize OpenAI embedder
    print("Initializing OpenAI embedder (text-embedding-3-small)...")
    embedder = OpenAIEmbedder()
    
    # Initialize chunker and store
    chunker = SentenceChunker(max_sentences_per_chunk=max_sentences)
    store = EmbeddingStore(embedding_fn=embedder)
    
    # Add documents
    print("Embedding documents (this may take a minute)...")
    for i, doc in enumerate(documents, 1):
        print(f"  [{i}/{len(documents)}] Processing {doc['doc_id']}...")
        chunks = chunker.chunk(doc['content'])
        
        # Create Document objects for each chunk
        doc_objects = []
        for j, chunk in enumerate(chunks):
            doc_obj = Document(
                id=f"{doc['doc_id']}_chunk_{j}",
                content=chunk,
                metadata={**doc['metadata'], 'doc_id': doc['doc_id'], 'chunk_index': j}
            )
            doc_objects.append(doc_obj)
        
        store.add_documents(doc_objects)
    
    return store, documents


def run_benchmark():
    """Run benchmark queries with OpenAI embeddings AND LLM."""
    print("="*80)
    print("BENCHMARK QUERIES - Full RAG Pipeline (OpenAI Embeddings + GPT)")
    print("="*80)
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n❌ ERROR: OPENAI_API_KEY not found in environment!")
        print("Please set your OpenAI API key in .env file")
        return
    
    # Create store
    print("\nLoading documents and creating embeddings...")
    store, documents = create_store_with_documents(max_sentences=3)
    
    print(f"\n✓ Loaded {len(documents)} documents")
    print(f"✓ Total chunks in store: {store.get_collection_size()}")
    
    # Create agent
    print("\nInitializing KnowledgeBaseAgent with OpenAI GPT...")
    agent = KnowledgeBaseAgent(store=store, llm_fn=openai_llm)
    
    # Define benchmark queries
    queries = [
        {
            'id': 1,
            'query': "What was the CPI year-over-year change in December 2025?",
            'gold_answer': "2.7% year-over-year",
            'expected_doc': "bls_cpi_december_2025",
            'filter': {'category': 'inflation'}
        },
        {
            'id': 2,
            'query': "What was the federal funds rate decision in July 2025?",
            'gold_answer': "Maintained at 5-1/4 to 5-1/2 percent",
            'expected_doc': "fed_fomc_statement_2025_07_30",
            'filter': {'category': 'monetary_policy'}
        },
        {
            'id': 3,
            'query': "What drove the monthly CPI increase in December 2025?",
            'gold_answer': "Shelter (+0.4%), food index (+0.7%), energy (+0.3%)",
            'expected_doc': "bls_cpi_december_2025",
            'filter': {'category': 'inflation'}
        },
        {
            'id': 4,
            'query': "How did the Fed describe the labor market in its 2025 statements?",
            'gold_answer': "Job gains moderated but remain strong, unemployment rate low",
            'expected_doc': "fed_fomc_statement_2025_07_30",
            'filter': {'category': 'monetary_policy'}
        },
        {
            'id': 5,
            'query': "What interest rate did the Fed set in December 2025?",
            'gold_answer': "3-1/2 to 3-3/4 percent",
            'expected_doc': "fed_fomc_statement_2025_12_10",
            'filter': {'category': 'monetary_policy'}
        }
    ]
    
    print("\n" + "="*80)
    print("RUNNING BENCHMARK QUERIES WITH LLM ANSWERS")
    print("="*80)
    
    results = []
    
    for q in queries:
        print(f"\n{'#'*80}")
        print(f"#: {q['id']}")
        print(f"Query: {q['query']}")
        print(f"{'─'*80}")
        
        # Get LLM answer using agent
        print("Generating answer...")
        answer = agent.answer(q['query'], top_k=3)
        
        print(f"Answer from my code: {answer}")
        print(f"Gold Answer: {q['gold_answer']}")
        
        # Also show which document was retrieved
        search_results = store.search_with_filter(
            q['query'], 
            top_k=3, 
            metadata_filter=q.get('filter')
        )
        
        if search_results:
            top_doc = search_results[0]['metadata'].get('doc_id', 'unknown')
            print(f"File chứa thông tin: {top_doc}.txt")
            print(f"Filter used: {q.get('filter', {})}")
            
            # Show evidence from top chunk
            evidence = search_results[0]['content'][:200]
            print(f"Evidence: \"{evidence}...\"")
        
        print(f"{'─'*80}")
        
        results.append({
            'query_id': q['id'],
            'query': q['query'],
            'answer': answer,
            'gold_answer': q['gold_answer'],
            'expected_doc': q['expected_doc']
        })
    
    print("\n" + "="*80)
    print("BENCHMARK COMPLETE")
    print("="*80)
    print("\nAll 5 queries have been answered using:")
    print("  • OpenAI text-embedding-3-small for retrieval")
    print("  • OpenAI GPT-4o-mini for answer generation")
    print("  • RecursiveChunker with chunk_size=400")
    print("\nCompare the answers above with gold answers to evaluate quality.")
    
    return results


if __name__ == "__main__":
    run_benchmark()
