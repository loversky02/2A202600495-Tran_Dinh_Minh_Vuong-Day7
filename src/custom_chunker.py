"""
Optional: Custom chunking strategy for VinUni admission documents

This is a bonus implementation to demonstrate domain-specific chunking.
"""
import re


class FAQChunker:
    """
    Custom chunker designed for FAQ documents.
    
    Design rationale:
    - FAQ documents have Q&A structure that should be kept together
    - Each Q&A pair is a semantic unit
    - Splitting Q from A would break context
    
    Strategy:
    - Detect Q&A patterns (Q:, A:, or numbered questions)
    - Keep each Q&A pair as one chunk
    - If a Q&A pair is too large, split at sentence boundaries within the answer
    """
    
    def __init__(self, max_chunk_size: int = 500):
        self.max_chunk_size = max_chunk_size
    
    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        
        # Try to detect Q&A patterns
        # Pattern 1: "Q: ... A: ..."
        qa_pattern1 = r'Q:\s*(.+?)\s*A:\s*(.+?)(?=Q:|$)'
        matches1 = re.findall(qa_pattern1, text, re.DOTALL | re.IGNORECASE)
        
        if matches1:
            return self._chunk_qa_pairs(matches1)
        
        # Pattern 2: "Question: ... Answer: ..."
        qa_pattern2 = r'Question:\s*(.+?)\s*Answer:\s*(.+?)(?=Question:|$)'
        matches2 = re.findall(qa_pattern2, text, re.DOTALL | re.IGNORECASE)
        
        if matches2:
            return self._chunk_qa_pairs(matches2)
        
        # Fallback: split by double newline (sections)
        sections = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
            
            if len(current_chunk) + len(section) + 2 <= self.max_chunk_size:
                current_chunk += ("\n\n" if current_chunk else "") + section
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                
                # If section itself is too large, split by sentences
                if len(section) > self.max_chunk_size:
                    chunks.extend(self._split_by_sentences(section))
                    current_chunk = ""
                else:
                    current_chunk = section
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def _chunk_qa_pairs(self, qa_pairs: list[tuple[str, str]]) -> list[str]:
        """Chunk Q&A pairs, keeping each pair together when possible."""
        chunks = []
        
        for question, answer in qa_pairs:
            question = question.strip()
            answer = answer.strip()
            qa_text = f"Q: {question}\nA: {answer}"
            
            if len(qa_text) <= self.max_chunk_size:
                chunks.append(qa_text)
            else:
                # Q&A pair too large, split answer by sentences
                chunks.append(f"Q: {question}")
                answer_chunks = self._split_by_sentences(f"A: {answer}")
                chunks.extend(answer_chunks)
        
        return chunks
    
    def _split_by_sentences(self, text: str) -> list[str]:
        """Split text by sentences when it's too large."""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 1 <= self.max_chunk_size:
                current_chunk += (" " if current_chunk else "") + sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                
                # If single sentence is too large, force split
                if len(sentence) > self.max_chunk_size:
                    for i in range(0, len(sentence), self.max_chunk_size):
                        chunks.append(sentence[i:i + self.max_chunk_size])
                    current_chunk = ""
                else:
                    current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks


class FinancialNewsChunker:
    """
    Custom chunker designed for financial news articles.
    
    Design rationale:
    - Financial news has specific structure: headline, key data, analysis, market reaction
    - Economic indicators (numbers, percentages) should stay with context
    - Section headers like "Key Highlights:", "Market Impact:" are semantic boundaries
    - Preserving data tables and bullet points improves retrieval accuracy
    
    Strategy:
    - Detect section headers (lines ending with ":")
    - Keep data points (numbers, percentages) with their context
    - Split at paragraph boundaries when sections are too large
    - Preserve bullet lists as complete units
    """
    
    def __init__(self, max_chunk_size: int = 600):
        self.max_chunk_size = max_chunk_size
    
    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        
        # Split by section headers (lines ending with ":")
        lines = text.split('\n')
        chunks = []
        current_section = []
        current_header = None
        
        for line in lines:
            stripped = line.strip()
            
            # Detect section headers (e.g., "Key Highlights:", "Market Impact:")
            if stripped and stripped.endswith(':') and len(stripped) < 100:
                # Save previous section
                if current_section:
                    section_text = '\n'.join(current_section)
                    chunks.extend(self._split_section(section_text))
                
                current_header = line
                current_section = [line]
            else:
                current_section.append(line)
        
        # Save last section
        if current_section:
            section_text = '\n'.join(current_section)
            chunks.extend(self._split_section(section_text))
        
        return [c for c in chunks if c.strip()]
    
    def _split_section(self, section_text: str) -> list[str]:
        """Split a section if it's too large, preserving bullet lists."""
        if len(section_text) <= self.max_chunk_size:
            return [section_text]
        
        # Try to split by double newline (paragraphs)
        paragraphs = section_text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # Check if adding this paragraph would exceed limit
            test_chunk = current_chunk + ("\n\n" if current_chunk else "") + para
            
            if len(test_chunk) <= self.max_chunk_size:
                current_chunk = test_chunk
            else:
                # Current chunk is full, save it
                if current_chunk:
                    chunks.append(current_chunk)
                
                # If paragraph itself is too large, split by sentences
                if len(para) > self.max_chunk_size:
                    chunks.extend(self._split_by_sentences(para))
                    current_chunk = ""
                else:
                    current_chunk = para
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def _split_by_sentences(self, text: str) -> list[str]:
        """Split text by sentences when it's too large."""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            test_chunk = current_chunk + (" " if current_chunk else "") + sentence
            
            if len(test_chunk) <= self.max_chunk_size:
                current_chunk = test_chunk
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                
                # If single sentence is too large, force split
                if len(sentence) > self.max_chunk_size:
                    for i in range(0, len(sentence), self.max_chunk_size):
                        chunks.append(sentence[i:i + self.max_chunk_size])
                    current_chunk = ""
                else:
                    current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks


class HeaderAwareChunker:
    """
    Custom chunker that respects markdown headers.
    
    Design rationale:
    - Markdown documents have hierarchical structure (# ## ###)
    - Each section under a header is a semantic unit
    - Keeping header with its content improves context
    
    Strategy:
    - Split by headers (# ## ###)
    - Keep header with its content
    - If section is too large, split at paragraph boundaries
    """
    
    def __init__(self, max_chunk_size: int = 500):
        self.max_chunk_size = max_chunk_size
    
    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        
        # Split by markdown headers
        header_pattern = r'^(#{1,6}\s+.+)$'
        lines = text.split('\n')
        
        chunks = []
        current_section = []
        current_header = None
        
        for line in lines:
            if re.match(header_pattern, line):
                # New header found, save previous section
                if current_section:
                    section_text = '\n'.join(current_section)
                    chunks.extend(self._split_section(section_text, current_header))
                
                current_header = line
                current_section = [line]
            else:
                current_section.append(line)
        
        # Save last section
        if current_section:
            section_text = '\n'.join(current_section)
            chunks.extend(self._split_section(section_text, current_header))
        
        return chunks
    
    def _split_section(self, section_text: str, header: str = None) -> list[str]:
        """Split a section if it's too large."""
        if len(section_text) <= self.max_chunk_size:
            return [section_text]
        
        # Section too large, split by paragraphs
        paragraphs = section_text.split('\n\n')
        chunks = []
        current_chunk = header if header else ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            if para == header:
                continue
            
            if len(current_chunk) + len(para) + 2 <= self.max_chunk_size:
                current_chunk += ("\n\n" if current_chunk and current_chunk != header else "") + para
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                
                if len(para) > self.max_chunk_size:
                    # Paragraph too large, force split
                    for i in range(0, len(para), self.max_chunk_size):
                        chunks.append(para[i:i + self.max_chunk_size])
                    current_chunk = ""
                else:
                    current_chunk = para
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
