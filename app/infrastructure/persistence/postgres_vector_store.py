"""
PostgreSQL Vector Store - Repository Pattern Implementation

This module implements the Repository pattern, abstracting database
operations behind a clean interface. The business logic doesn't need
to know about PostgreSQL or pgvector specifics.

Design Pattern: Repository
SOLID Principle: 
    - Single Responsibility (only handles data persistence)
    - Dependency Inversion (implements IVectorStore interface)
"""
from typing import List, Dict, Optional

from app.domain.interfaces.vector_store import IVectorStore
from app.db.models import get_connection
from app.core.logging import logger


class PostgresVectorStore(IVectorStore):
    """
    PostgreSQL + pgvector implementation of vector store.
    
    Implements IVectorStore interface, allowing future swap to
    other vector databases (Pinecone, Chroma, Weaviate, etc.)
    """
    
    def add(self, records: List[Dict]) -> None:
        """
        Store document chunks with embeddings in PostgreSQL.
        
        Args:
            records: List of dicts with text, embedding, and metadata
        """
        conn = get_connection()
        cur = conn.cursor()
        
        try:
            for r in records:
                cur.execute(
                    """
                    INSERT INTO document_chunks
                    (content, embedding, tag, page_number, chunk_id)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        r["text"],
                        r["embedding"],
                        r["metadata"].get("tag"),
                        r["metadata"].get("page"),
                        r["metadata"].get("chunk_id"),
                    ),
                )
            
            conn.commit()
            logger.debug(f"Stored {len(records)} chunks in database")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to store records: {e}")
            raise
        finally:
            cur.close()
            conn.close()
    
    def search(
        self,
        query_embedding: Optional[List[float]] = None,
        tag: Optional[str] = None,
        top_k: int = 5,
    ) -> List[Dict]:
        """
        Search for similar documents using pgvector.
        
        Args:
            query_embedding: Vector to search for (None for wildcard)
            tag: Optional tag filter
            top_k: Number of results to return
            
        Returns:
            List of matching documents with content and metadata
        """
        conn = get_connection()
        cur = conn.cursor()
        
        try:
            # Wildcard: return all documents (optionally filtered by tag)
            if query_embedding is None:
                if tag:
                    cur.execute(
                        """
                        SELECT content, tag, page_number, chunk_id
                        FROM document_chunks
                        WHERE tag = %s
                        ORDER BY page_number, chunk_id
                        """,
                        (tag,),
                    )
                else:
                    cur.execute(
                        """
                        SELECT content, tag, page_number, chunk_id
                        FROM document_chunks
                        ORDER BY page_number, chunk_id
                        """
                    )
            
            # Semantic search using cosine distance
            else:
                if tag:
                    cur.execute(
                        """
                        SELECT content, tag, page_number, chunk_id
                        FROM document_chunks
                        WHERE tag = %s
                        ORDER BY embedding <-> %s::vector
                        LIMIT %s
                        """,
                        (tag, query_embedding, top_k),
                    )
                else:
                    cur.execute(
                        """
                        SELECT content, tag, page_number, chunk_id
                        FROM document_chunks
                        ORDER BY embedding <-> %s::vector
                        LIMIT %s
                        """,
                        (query_embedding, top_k),
                    )
            
            rows = cur.fetchall()
            
            return [
                {
                    "content": r[0],
                    "tag": r[1],
                    "page": r[2],
                    "chunk_id": r[3],
                }
                for r in rows
            ]
            
        finally:
            cur.close()
            conn.close()
    
    def delete_by_tag(self, tag: str) -> int:
        """
        Delete all documents with a specific tag.
        
        Args:
            tag: Tag to filter by
            
        Returns:
            Number of deleted records
        """
        conn = get_connection()
        cur = conn.cursor()
        
        try:
            cur.execute(
                """
                DELETE FROM document_chunks
                WHERE tag = %s
                """,
                (tag,),
            )
            
            deleted_count = cur.rowcount
            conn.commit()
            logger.info(f"Deleted {deleted_count} chunks with tag '{tag}'")
            
            return deleted_count
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to delete records: {e}")
            raise
        finally:
            cur.close()
            conn.close()
