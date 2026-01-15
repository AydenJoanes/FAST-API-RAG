"""
Ingest Route - Thin Controller using Service Layer

Design Pattern: Facade (via IngestService)
- Route is now a thin controller that delegates to IngestService
- All business logic is encapsulated in the service layer

SOLID Principles:
- SRP: Route only handles HTTP concerns (request/response)
- DIP: Depends on IngestService abstraction
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional

from app.application import IngestService
from app.core.logging import logger

router = APIRouter()

# Service instance (Facade Pattern)
ingest_service = IngestService()


@router.post("/")
async def ingest_document(
    file: UploadFile = File(...),
    tag: Optional[str] = Form(None)
):
    """
    Ingest a document (PDF, and future: DOCX, TXT, etc.)
    
    The route is now a thin controller:
    - Validates input
    - Delegates to IngestService (Facade)
    - Returns response
    """
    logger.info(f"Ingest request: {file.filename}, tag: {tag}")
    
    # 1. Validate file type
    if not ingest_service.is_file_supported(file.filename):
        supported = ingest_service.get_supported_extensions()
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Supported: {supported}"
        )
    
    # 2. Read file bytes
    file_bytes = await file.read()
    
    # 3. Delegate to service (Facade Pattern)
    result = ingest_service.ingest(
        file_bytes=file_bytes,
        filename=file.filename,
        tag=tag
    )
    
    return result


@router.delete("/{tag}")
async def delete_by_tag(tag: str):
    """Delete all documents with a specific tag."""
    logger.info(f"Delete request for tag: {tag}")
    
    result = ingest_service.delete_by_tag(tag)
    return result

