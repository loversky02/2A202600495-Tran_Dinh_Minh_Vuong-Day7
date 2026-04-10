"""Test chunking strategies on real financial data.

Usage:
    python test_financial_chunking.py                          # Test on default file (BLS CPI)
    python test_financial_chunking.py data/fed_fomc_*.txt      # Test on specific file
    python test_financial_chunking.py --all                    # Test on all .txt files in data/
"""

import sys
from pathlib import Path
from src.chunking import ChunkingStrategyComparator, compute_similarity
from src.embeddings import _mock_embed
from src.custom_chunker import FinancialNewsChunker


def test_chunking_on_file(file_path: Path, max_chars: int = 3000):
    """Test chunking strategies on a single file."""
    if not file_path.exists():
        print(f"Error: {file_path} not found!")
        return
    
    text = file_path.read_text(encoding='utf-8')[:max_chars]
    
    print("="*80)
    print(f"CHUNKING STRATEGY COMPARISON - {file_path.name}")
    print(f"Testing first {max_chars} characters")
    print("="*80)
    
    comparator = ChunkingStrategyComparator()
    results = comparator.compare(text, chunk_size=300)
    
    # Add custom FinancialNewsChunker test
    custom_chunker = FinancialNewsChunker(max_chunk_size=300)
    custom_chunks = custom_chunker.chunk(text)
    custom_avg = sum(len(c) for c in custom_chunks) / len(custom_chunks) if custom_chunks else 0
    results['Financial Custom'] = {
        'count': len(custom_chunks),
        'avg_length': custom_avg,
        'chunks': custom_chunks
    }
    
    print(f"\nDocument length: {len(text)} characters")
    print("\nResults:")
    print(f"\n{'Strategy':<20} {'Chunks':<10} {'Avg Length':<15}")
    print("-"*50)
    
    for strategy_name, stats in results.items():
        print(f"{strategy_name:<20} {stats['count']:<10} {stats['avg_length']:<15.1f}")
    
    print("\n" + "="*80)
    print("FIRST 3 CHUNKS PREVIEW")
    print("="*80)
    
    for strategy_name, stats in results.items():
        print(f"\n{strategy_name.upper()}:")
        for i, chunk in enumerate(stats['chunks'][:3], 1):
            preview = chunk[:80].replace('\n', ' ')
            print(f"[{i}] {preview}...")
    
    print()


def test_similarity():
    """Test cosine similarity with financial sentence pairs."""
    print("="*80)
    print("COSINE SIMILARITY TEST - Financial Sentences")
    print("="*80)
    
    # Test pairs
    pairs = [
        ("The Federal Reserve lowered interest rates by 25 basis points.", 
         "The Fed reduced the federal funds rate by a quarter percentage point."),
        ("Consumer Price Index increased 2.7 percent year-over-year.", 
         "The CPI rose 2.7 percent over the last 12 months."),
        ("Inflation remains somewhat elevated above target.", 
         "The unemployment rate edged down to 4.0 percent."),
        ("The Committee decided to lower the target range.", 
         "Job gains have slowed this year."),
        ("The index for shelter rose 0.4 percent in December.", 
         "Housing costs increased 0.4 percent over the month.")
    ]
    
    print("\nTesting cosine similarity with mock embeddings:")
    print(f"\n{'Pair':<6} {'Score':<10} {'Sentence A':<50} {'Sentence B':<50}")
    print("-"*120)
    
    for i, (sent_a, sent_b) in enumerate(pairs, 1):
        vec_a = _mock_embed(sent_a)
        vec_b = _mock_embed(sent_b)
        score = compute_similarity(vec_a, vec_b)
        
        preview_a = sent_a[:47] + "..." if len(sent_a) > 50 else sent_a
        preview_b = sent_b[:47] + "..." if len(sent_b) > 50 else sent_b
        
        print(f"{i:<6} {score:<10.4f} {preview_a:<50} {preview_b:<50}")
    
    print("\n" + "="*80)
    print("NOTE: Mock embeddings use character hashing, not semantic meaning.")
    print("Real embeddings (OpenAI, sentence-transformers) would show much better results.")
    print("="*80)


def main():
    """Main function to handle command line arguments."""
    data_dir = Path("data")
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        
        if arg == "--all":
            # Test all .txt files in data/
            txt_files = sorted(data_dir.glob("*.txt"))
            if not txt_files:
                print(f"No .txt files found in {data_dir}/")
                return
            
            print(f"Found {len(txt_files)} .txt files in {data_dir}/\n")
            for txt_file in txt_files:
                test_chunking_on_file(txt_file)
                print()
        else:
            # Test specific file
            file_path = Path(arg)
            test_chunking_on_file(file_path)
    else:
        # Default: test BLS CPI file
        default_file = data_dir / "bls_cpi_december_2025.txt"
        test_chunking_on_file(default_file)
    
    # Always run similarity test at the end
    print()
    test_similarity()


if __name__ == "__main__":
    main()
