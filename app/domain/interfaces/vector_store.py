"""Interface for vector store - Repository Pattern"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class IVectorStore(ABC):
    """
    Abstract interface for vector storage and retrieval.
    
    Implements: Repository Pattern
    Enables: Swap database implementations (PostgreSQL, Pinecone, Chroma, etc.)
    """
    
    @abstractmethod
    def add(self, records: List[Dict]) -> None:
        """
        Store document chunks with embeddings.
        
        Args:
            records: List of dicts containing:
                - text: The chunk content
                - embedding: Vector representation
                - metadata: Dict with tag, page, chunk_id
        """
        pass
    
    @abstractmethod
    def search(
        self,
        query_embedding: Optional[List[float]] = None,
        tag: Optional[str] = None,
        top_k: int = 5,
    ) -> List[Dict]:
        """
        Search for similar documents.
        
        Args:
            query_embedding: Vector to search for (None for wildcard)
            tag: Optional tag filter
            top_k: Number of results to return
            
        Returns:
            List of matching documents with content and metadata
        """
        pass
    
    @abstractmethod
    def delete_by_tag(self, tag: str) -> int:
        """
        Delete all documents with a specific tag.
        
        Args:
            tag: Tag to filter by
            
        Returns:
            Number of deleted records
        """
        pass
