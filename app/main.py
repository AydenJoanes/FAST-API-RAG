"""
RAG FastAPI Application - Main Entry Point

This is the main application file that:
1. Creates the FastAPI app
2. Registers global exception handlers
3. Mounts static files
4. Includes all route modules

Exception Handling:
- Global handlers catch all custom exceptions
- Return user-friendly JSON error responses
- Log technical details for debugging
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path

from app.routes.ingest import router as ingest_router
from app.routes.retrieve import router as retrieve_router
from app.routes.chat import router as chat_router
from app.routes.health import router as health_router
from app.core.logging import logger
from app.core.exceptions import (
    RAGBaseException,
    DocumentProcessingError,
    ChunkingError,
    EmbeddingError,
    VectorStoreError,
    LLMProviderError,
    ValidationError,
    RetrievalError,
)

app = FastAPI(title="RAG FastAPI")

logger.info("Starting RAG FastAPI application")


# ============================================================
# GLOBAL EXCEPTION HANDLERS
# ============================================================

@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    """Handle input validation errors - return 400 Bad Request"""
    logger.warning(f"Validation error: {exc.details}")
    return JSONResponse(
        status_code=400,
        content={
            "error": "validation_error",
            "message": exc.message,
            "status": "error"
        }
    )


@app.exception_handler(DocumentProcessingError)
async def document_error_handler(request: Request, exc: DocumentProcessingError):
    """Handle document processing errors - return 422 Unprocessable Entity"""
    logger.warning(f"Document processing error: {exc.details}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "document_processing_error",
            "message": exc.message,
            "status": "error"
        }
    )


@app.exception_handler(ChunkingError)
async def chunking_error_handler(request: Request, exc: ChunkingError):
    """Handle chunking errors - return 422 Unprocessable Entity"""
    logger.warning(f"Chunking error: {exc.details}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "chunking_error",
            "message": exc.message,
            "status": "error"
        }
    )


@app.exception_handler(EmbeddingError)
async def embedding_error_handler(request: Request, exc: EmbeddingError):
    """Handle embedding errors - return 503 Service Unavailable"""
    logger.error(f"Embedding error: {exc.details}")
    return JSONResponse(
        status_code=503,
        content={
            "error": "embedding_error",
            "message": exc.message,
            "status": "error"
        }
    )


@app.exception_handler(VectorStoreError)
async def vector_store_error_handler(request: Request, exc: VectorStoreError):
    """Handle database errors - return 503 Service Unavailable"""
    logger.error(f"Vector store error: {exc.details}")
    return JSONResponse(
        status_code=503,
        content={
            "error": "database_error",
            "message": exc.message,
            "status": "error"
        }
    )


@app.exception_handler(LLMProviderError)
async def llm_error_handler(request: Request, exc: LLMProviderError):
    """Handle LLM API errors - return 503 Service Unavailable"""
    logger.error(f"LLM provider error: {exc.details}")
    return JSONResponse(
        status_code=503,
        content={
            "error": "llm_error",
            "message": exc.message,
            "status": "error"
        }
    )


@app.exception_handler(RetrievalError)
async def retrieval_error_handler(request: Request, exc: RetrievalError):
    """Handle retrieval errors - return 404 Not Found"""
    logger.warning(f"Retrieval error: {exc.details}")
    return JSONResponse(
        status_code=404,
        content={
            "error": "retrieval_error",
            "message": exc.message,
            "status": "error"
        }
    )


@app.exception_handler(RAGBaseException)
async def rag_base_error_handler(request: Request, exc: RAGBaseException):
    """Catch-all for any other RAG exceptions - return 500"""
    logger.error(f"Unhandled RAG exception: {exc.details}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "message": exc.message,
            "status": "error"
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Catch-all for unexpected exceptions - return 500"""
    logger.error(f"Unexpected error: {type(exc).__name__}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "message": "An unexpected error occurred. Please try again later.",
            "status": "error"
        }
    )


# ============================================================
# STATIC FILES AND ROUTES
# ============================================================

# Get the directory where main.py is located
BASE_DIR = Path(__file__).resolve().parent

# Mount static files
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# Serve the chat frontend at root
@app.get("/", include_in_schema=False)
async def serve_frontend():
    return FileResponse(BASE_DIR / "static" / "index.html")

app.include_router(ingest_router, prefix="/ingest", tags=["ingest"])
app.include_router(retrieve_router, prefix="/retrieve", tags=["retrieve"])
app.include_router(chat_router, prefix="/chat", tags=["chat"])
app.include_router(health_router, prefix="/health", tags=["health"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
