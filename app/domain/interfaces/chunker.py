"""Interface for text chunking - Strategy Pattern"""
from abc import ABC, abstractmethod
from typing import List, Dict


class IChunker(ABC):
    """
    Abstract interface for text chunking strategies.
    
    Implements: Strategy Pattern
    Enables: Swap chunking algorithms (fixed-size, semantic, recursive)
    """
    
    @abstractmethod
    def chunk(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Split text into chunks with metadata.
        
        Args:
            text: Input text to chunk
            metadata: Additional metadata to attach to each chunk
            
        Returns:
            List of dicts containing:
                - text: Chunk content
                - chunk_id: Unique identifier within document
                - Any additional metadata passed in
        """
        pass
    
    @property
    @abstractmethod
    def chunk_size(self) -> int:
        """Return the target chunk size"""
        pass
    
    @property
    @abstractmethod
    def chunk_overlap(self) -> int:
        """Return the overlap between chunks"""
        pass
