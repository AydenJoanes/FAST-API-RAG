"""
Fixed Size Chunker - Strategy Pattern Implementation

This chunker splits text into fixed-size chunks with configurable overlap.
It's one of several possible chunking strategies that can be swapped at runtime.

Design Pattern: Strategy
SOLID Principles:
    - Single Responsibility (only handles chunking)
    - Open/Closed (add new strategies without modifying existing code)
    - Liskov Substitution (interchangeable with other IChunker implementations)
    - Dependency Inversion (implements IChunker interface)

Exception Handling:
    - Empty/whitespace text → EmptyTextError
"""
import re
from typing import List, Dict, Optional

from app.domain.interfaces.chunker import IChunker
from app.core.logging import logger
from app.core.exceptions import EmptyTextError


class FixedSizeChunker(IChunker):
    """
    Fixed-size text chunking strategy.
    
    Splits text into chunks of a fixed character size with overlap
    to maintain context between chunks.
    
    Usage:
        chunker = FixedSizeChunker(chunk_size=500, overlap=50)
        chunks = chunker.chunk(text, metadata={"page": 1})
    """
    
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        """
        Initialize the chunker with size parameters.
        
        Args:
            chunk_size: Target size of each chunk in characters
            overlap: Number of characters to overlap between chunks
        """
        self._chunk_size = chunk_size
        self._overlap = overlap
        logger.debug(f"FixedSizeChunker initialized: size={chunk_size}, overlap={overlap}")
    
    def chunk(self, text: str, metadata: Optional[Dict] = None) -> List[Dict]:
        """
        Split text into fixed-size chunks with metadata.
        
        Args:
            text: Input text to chunk
            metadata: Additional metadata to attach to each chunk
            
        Returns:
            List of chunk dicts with text, chunk_id, and metadata
            
        Raises:
            EmptyTextError: If text is empty or whitespace-only
        """
        metadata = metadata or {}
        
        # Edge case: None or empty text
        if text is None:
            logger.warning("Received None text for chunking")
            raise EmptyTextError()
        
        # Clean and normalize text
        cleaned_text = self._clean_text(text)
        
        # Edge case: Empty or whitespace-only text after cleaning
        if not cleaned_text:
            logger.warning("Text is empty or whitespace-only after cleaning")
            raise EmptyTextError()
        
        chunks = []
        start = 0
        length = len(cleaned_text)
        chunk_id = 0
        
        while start < length:
            end = start + self._chunk_size
            chunk_text = cleaned_text[start:end]
            
            # Build chunk with metadata
            chunk_data = {
                "text": chunk_text,
                "chunk_id": chunk_id,
                **metadata  # Include any passed metadata (page, etc.)
            }
            
            chunks.append(chunk_data)
            
            chunk_id += 1
            start = end - self._overlap
        
        logger.debug(f"Created {len(chunks)} chunks from text of length {length}")
        return chunks
    
    @property
    def chunk_size(self) -> int:
        """Return the target chunk size"""
        return self._chunk_size
    
    @property
    def chunk_overlap(self) -> int:
        """Return the overlap between chunks"""
        return self._overlap
    
    @staticmethod
    def _clean_text(text: str) -> str:
        """
        Normalize whitespace in text.
        
        Args:
            text: Raw input text
            
        Returns:
            Text with normalized whitespace
        """
        text = re.sub(r"\s+", " ", text)
        return text.strip()
