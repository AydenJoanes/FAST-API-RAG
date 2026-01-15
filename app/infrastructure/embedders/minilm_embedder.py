"""
MiniLM Embedder - Singleton Pattern Implementation

This module implements the Singleton pattern to ensure only ONE instance
of the heavy ML model is loaded into memory, regardless of how many
times it's requested across the application.

Design Pattern: Singleton
SOLID Principle: Single Responsibility (only handles embedding)
"""
import threading
from typing import List
from sentence_transformers import SentenceTransformer

from app.domain.interfaces.embedder import IEmbedder
from app.core.logging import logger


class MiniLMEmbedder(IEmbedder):
    """
    Singleton implementation of MiniLM embedding model.
    
    Thread-safe singleton ensures the ~100MB model loads only once,
    saving memory when multiple routes need embeddings.
    """
    
    _instance = None
    _lock = threading.Lock()
    _initialized = False
    
    def __new__(cls):
        """Thread-safe singleton instantiation"""
        if cls._instance is None:
            with cls._lock:
                # Double-check locking pattern
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the model only once"""
        # Prevent re-initialization on subsequent calls
        if MiniLMEmbedder._initialized:
            return
            
        with MiniLMEmbedder._lock:
            if MiniLMEmbedder._initialized:
                return
                
            logger.info("Loading MiniLM embedding model (Singleton)...")
            self._model = SentenceTransformer("all-MiniLM-L6-v2")
            self._dimension = 384
            MiniLMEmbedder._initialized = True
            logger.success("MiniLM model loaded successfully")
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding vector for a single text.
        
        Args:
            text: Input text to embed
            
        Returns:
            384-dimensional embedding vector
        """
        embedding = self._model.encode(text)
        return embedding.tolist()
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embedding vectors for multiple texts (batch processing).
        
        Args:
            texts: List of input texts to embed
            
        Returns:
            List of 384-dimensional embedding vectors
        """
        embeddings = self._model.encode(texts)
        return embeddings.tolist()
    
    @property
    def dimension(self) -> int:
        """Return the dimension of embedding vectors (384 for MiniLM)"""
        return self._dimension


# Module-level singleton accessor function
_embedder_instance: MiniLMEmbedder = None
_embedder_lock = threading.Lock()


def get_embedder() -> IEmbedder:
    """
    Get the singleton embedder instance.
    
    This is the preferred way to access the embedder throughout the application.
    Follows Dependency Inversion Principle - returns interface type.
    
    Returns:
        IEmbedder: The singleton embedder instance
    """
    global _embedder_instance
    
    if _embedder_instance is None:
        with _embedder_lock:
            if _embedder_instance is None:
                _embedder_instance = MiniLMEmbedder()
    
    return _embedder_instance
