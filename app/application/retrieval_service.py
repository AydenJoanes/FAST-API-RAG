"""
Retrieval Service - Facade Pattern Implementation

Design Pattern: Facade
- Provides a simplified interface to the retrieval subsystem
- Orchestrates: Embedder, Vector Store

SOLID Principles:
- SRP: Only handles document retrieval
- DIP: Depends on abstractions (IEmbedder, IVectorStore)
"""
from typing import List, Dict, Any, Optional

from app.domain.interfaces import IEmbedder, IVectorStore
from app.infrastructure.embedders import get_embedder
from app.infrastructure.persistence import PostgresVectorStore
from app.core.logging import logger


class RetrievalService:
    """
    Facade for document retrieval operations.
    
    Orchestrates:
    1. Query embedding generation
    2. Vector similarity search
    """
    
    def __init__(
        self,
        embedder: Optional[IEmbedder] = None,
        vector_store: Optional[IVectorStore] = None
    ):
        """
        Initialize with dependencies (Dependency Injection).
        
        Args:
            embedder: Embedding service (defaults to Singleton MiniLM)
            vector_store: Vector storage (defaults to PostgresVectorStore)
        """
        self._embedder = embedder or get_embedder()
        self._vector_store = vector_store or PostgresVectorStore()
        
        logger.debug("RetrievalService initialized with dependencies")
    
    def retrieve(
        self,
        query: str,
        tag: Optional[str] = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Retrieve relevant documents for a query.
        
        Facade method that handles:
        - Wildcard queries (return all with optional tag filter)
        - Semantic search (embed query + vector similarity)
        
        Args:
            query: Search query (use "*" for wildcard)
            tag: Optional tag filter
            top_k: Maximum results to return
            
        Returns:
            Dict with query and results
        """
        logger.info(f"Retrieving for query: {query[:50]}..., tag: {tag}")
        
        # Handle wildcard query
        if query.strip() == "*":
            results = self._vector_store.search(
                query_embedding=None,
                tag=tag,
                top_k=top_k
            )
            logger.info(f"Wildcard search returned {len(results)} results")
            
            return {
                "query": query,
                "tag": tag,
                "results": results,
                "result_count": len(results)
            }
        
        # Semantic search
        query_embedding = self._embedder.embed_text(query)
        
        results = self._vector_store.search(
            query_embedding=query_embedding,
            tag=tag,
            top_k=top_k
        )
        logger.info(f"Semantic search returned {len(results)} results")
        
        return {
            "query": query,
            "tag": tag,
            "results": results,
            "result_count": len(results)
        }
    
    def get_context(
        self,
        query: str,
        tag: Optional[str] = None,
        top_k: int = 5
    ) -> str:
        """
        Get concatenated context for RAG.
        
        Convenience method for chat service.
        
        Args:
            query: Search query
            tag: Optional tag filter
            top_k: Maximum chunks to include
            
        Returns:
            Concatenated context string
        """
        result = self.retrieve(query, tag, top_k)
        
        if not result["results"]:
            return "No relevant context found."
        
        return "\n\n".join([r["content"] for r in result["results"]])
