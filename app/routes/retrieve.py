from fastapi import APIRouter
from typing import Optional

from app.services.embeddings import EmbeddingService
from app.db.vector_store import VectorStore

router = APIRouter()

embedder = EmbeddingService()
vector_store = VectorStore()


@router.post("/")
def retrieve(
    query: str,
    tag: Optional[str] = None
):
    # 1. Wildcard logic
    if query.strip() == "*":
        results = vector_store.search(
            query_embedding=None,
            tag=tag
        )
        return {
            "query": query,
            "results": results
        }

    # 2. Normal semantic search
    query_embedding = embedder.embed_text(query)

    results = vector_store.search(
        query_embedding=query_embedding,
        tag=tag
    )

    return {
        "query": query,
        "results": results
    }
