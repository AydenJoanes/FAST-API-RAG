from typing import List, Dict, Optional
from app.db.models import get_connection


class VectorStore:
    """
    PostgreSQL + pgvector-backed vector store
    """

    def add(self, records: List[Dict]):
        conn = get_connection()
        cur = conn.cursor()

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
        cur.close()
        conn.close()

    def search(
        self,
        query_embedding: Optional[List[float]] = None,
        tag: Optional[str] = None,
        top_k: int = 5,
    ) -> List[Dict]:

        conn = get_connection()
        cur = conn.cursor()

        # 🔹 Wildcard: return full document
        if query_embedding is None:
            if tag:
                cur.execute(
                    """
                    SELECT content, tag, page_number, chunk_id
                    FROM document_chunks
                    WHERE tag = %s
                    """,
                    (tag,),
                )
            else:
                cur.execute(
                    """
                    SELECT content, tag, page_number, chunk_id
                    FROM document_chunks
                    """
                )

        # 🔹 Semantic search
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
        cur.close()
        conn.close()

        return [
            {
                "content": r[0],
                "tag": r[1],
                "page": r[2],
                "chunk_id": r[3],
            }
            for r in rows
        ]
