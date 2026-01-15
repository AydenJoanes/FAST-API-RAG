"""Routes package for rag_fastapi."""

from .ingest import router as ingest_router
from .retrieve import router as retrieve_router
from .chat import router as chat_router

__all__ = ["ingest_router", "retrieve_router", "chat_router"]
