"""
MiniLM Embedder - Singleton Pattern Implementation

This module implements the Singleton pattern to ensure only ONE instance
of the heavy ML model is loaded into memory, regardless of how many
times it's requested across the application.

Design Pattern: Singleton
SOLID Principle: Single Responsibility (only handles embedding)

Exception Handling:
    - Model loading failure → EmbeddingModelError
    - Empty text → EmbeddingError
"""
import threading
from typing import List
from sentence_transformers import SentenceTransformer

from app.domain.interfaces.embedder import IEmbedder
from app.core.logging import logger
from app.core.exceptions import EmbeddingModelError, EmbeddingError


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
            
            try:
                logger.info("Loading MiniLM embedding model (Singleton)...")
                self._model = SentenceTransformer("all-MiniLM-L6-v2")
                self._dimension = 384
                MiniLMEmbedder._initialized = True
                logger.success("MiniLM model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                raise EmbeddingModelError(str(e))
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding vector for a single text.
        
        Args:
            text: Input text to embed
            
        Returns:
            384-dimensional embedding vector
            
        Raises:
            EmbeddingError: If text is empty or embedding fails
        """
        # Edge case: Empty or None text
        if not text or not text.strip():
            logger.warning("Received empty text for embedding")
            raise EmbeddingError("Cannot embed empty text", "Empty text provided")
        
        try:
            embedding = self._model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise EmbeddingModelError(str(e))
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embedding vectors for multiple texts (batch processing).
        
        Args:
            texts: List of input texts to embed
            
        Returns:
            List of 384-dimensional embedding vectors
            
        Raises:
            EmbeddingError: If texts list is empty or embedding fails
        """
        # Edge case: Empty list
        if not texts:
            logger.warning("Received empty text list for embedding")
            raise EmbeddingError("Cannot embed empty text list", "Empty list provided")
        
        # Filter out empty strings
        valid_texts = [t for t in texts if t and t.strip()]
        if not valid_texts:
            logger.warning("All texts were empty after filtering")
            raise EmbeddingError("All provided texts are empty", "No valid texts")
        
        try:
            embeddings = self._model.encode(valid_texts)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Batch embedding generation failed: {e}")
            raise EmbeddingModelError(str(e))
    
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
