"""
Ingest Service - Facade Pattern Implementation

Design Pattern: Facade
- Provides a simplified interface to the document ingestion subsystem
- Orchestrates: Document Loaders, Chunkers, Embedders, Vector Store

SOLID Principles:
- SRP: Only handles document ingestion workflow
- OCP: New loaders/chunkers can be added without modifying this service
- DIP: Depends on abstractions (IDocumentLoader, IChunker, IEmbedder, IVectorStore)
"""
from typing import List, Dict, Any, Optional

from app.domain.interfaces import IEmbedder, IVectorStore, IDocumentLoader, IChunker
from app.infrastructure.embedders import get_embedder
from app.infrastructure.persistence import PostgresVectorStore
from app.infrastructure.document_loaders import DocumentLoaderFactory
from app.infrastructure.chunkers import FixedSizeChunker
from app.core.logging import logger


class IngestService:
    """
    Facade for document ingestion operations.
    
    Orchestrates the complete ingestion pipeline:
    1. Load document (Factory Pattern selects loader)
    2. Chunk text (Strategy Pattern for chunking algorithm)
    3. Generate embeddings (Singleton Pattern for model)
    4. Store in vector database (Repository Pattern)
    """
    
    def __init__(
        self,
        embedder: Optional[IEmbedder] = None,
        vector_store: Optional[IVectorStore] = None,
        chunker: Optional[IChunker] = None
    ):
        """
        Initialize with dependencies (Dependency Injection).
        
        Args:
            embedder: Embedding service (defaults to Singleton MiniLM)
            vector_store: Vector storage (defaults to PostgresVectorStore)
            chunker: Chunking strategy (defaults to FixedSizeChunker)
        """
        self._embedder = embedder or get_embedder()
        self._vector_store = vector_store or PostgresVectorStore()
        self._chunker = chunker or FixedSizeChunker(chunk_size=500, overlap=50)
        
        logger.debug("IngestService initialized with dependencies")
    
    def is_file_supported(self, filename: str) -> bool:
        """Check if file type is supported for ingestion."""
        return DocumentLoaderFactory.is_supported(filename)
    
    def get_supported_extensions(self) -> List[str]:
        """Get list of supported file extensions."""
        return DocumentLoaderFactory.get_supported_extensions()
    
    def ingest(
        self,
        file_bytes: bytes,
        filename: str,
        tag: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ingest a document into the vector store.
        
        This is the Facade method that orchestrates:
        - Document loading (via Factory)
        - Text chunking (via Strategy)
        - Embedding generation (via Singleton)
        - Vector storage (via Repository)
        
        Args:
            file_bytes: Raw file content
            filename: Original filename (for loader selection)
            tag: Optional tag for filtering
            
        Returns:
            Dict with ingestion statistics
        """
        logger.info(f"Starting ingestion: {filename}, tag: {tag}")
        
        # 1. Get appropriate loader from factory
        loader = DocumentLoaderFactory.get_loader(filename)
        
        # 2. Extract pages
        pages = loader.load(file_bytes)
        logger.info(f"Extracted {len(pages)} pages from document")
        
        # 3. Process pages: chunk + embed
        records = []
        total_chunks = 0
        
        for page in pages:
            # Chunk the page text (Strategy Pattern)
            chunks = self._chunker.chunk(
                text=page["text"],
                metadata={"page": page["page"]}
            )
            
            # Embed each chunk
            for chunk in chunks:
                embedding = self._embedder.embed_text(chunk["text"])
                
                records.append({
                    "text": chunk["text"],
                    "embedding": embedding,
                    "metadata": {
                        "tag": tag,
                        "page": chunk["page"],
                        "chunk_id": chunk["chunk_id"]
                    }
                })
                total_chunks += 1
        
        # 4. Store in vector database (Repository Pattern)
        self._vector_store.add(records)
        logger.success(f"Stored {total_chunks} chunks for {filename}")
        
        return {
            "filename": filename,
            "tag": tag,
            "pages_processed": len(pages),
            "chunks_created": total_chunks,
            "status": "success"
        }
    
    def delete_by_tag(self, tag: str) -> Dict[str, Any]:
        """
        Delete all documents with a specific tag.
        
        Args:
            tag: Tag to filter by
            
        Returns:
            Dict with deletion result
        """
        logger.info(f"Deleting documents with tag: {tag}")
        deleted_count = self._vector_store.delete_by_tag(tag)
        logger.success(f"Deleted {deleted_count} records with tag: {tag}")
        
        return {
            "tag": tag,
            "deleted_count": deleted_count,
            "status": "success"
        }
