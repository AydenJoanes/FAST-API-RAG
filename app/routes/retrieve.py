"""
Retrieve Route - Thin Controller using Service Layer

Design Pattern: Facade (via RetrievalService)
- Route is now a thin controller that delegates to RetrievalService
- All business logic is encapsulated in the service layer

SOLID Principles:
- SRP: Route only handles HTTP concerns
- DIP: Depends on RetrievalService abstraction
"""
from fastapi import APIRouter
from typing import Optional

from app.application import RetrievalService
from app.core.logging import logger

router = APIRouter()

# Service instance (Facade Pattern)
retrieval_service = RetrievalService()


@router.post("/")
def retrieve(
    query: str,
    tag: Optional[str] = None,
    top_k: int = 5
):
    """
    Retrieve relevant documents for a query.
    
    The route is now a thin controller:
    - Receives request parameters
    - Delegates to RetrievalService (Facade)
    - Returns response
    """
    logger.info(f"Retrieve request: {query[:50]}..., tag: {tag}")
    
    # Delegate to service (Facade Pattern)
    result = retrieval_service.retrieve(
        query=query,
        tag=tag,
        top_k=top_k
    )
    
    return result
