"""Interface for embedding services - Strategy Pattern"""
from abc import ABC, abstractmethod
from typing import List


class IEmbedder(ABC):
    """
    Abstract interface for text embedding services.
    
    Implements: Interface Segregation Principle (ISP)
    Enables: Strategy Pattern - swap embedding models at runtime
    """
    
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding vector for a single text.
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        pass
    
    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embedding vectors for multiple texts.
        
        Args:
            texts: List of input texts to embed
            
        Returns:
            List of embedding vectors
        """
        pass
    
    @property
    @abstractmethod
    def dimension(self) -> int:
        """Return the dimension of the embedding vectors"""
        pass
