from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional

from app.services.pdf_loader import pdf_to_pages
from app.services.chunker import chunk_page
from app.services.embeddings import EmbeddingService
from app.db.vector_store import VectorStore
from app.core.logging import logger

router = APIRouter()

vector_store = VectorStore()
embedder = EmbeddingService()


@router.post("/")
async def ingest_pdf(
    file: UploadFile = File(...),
    tag: Optional[str] = Form(None)
):
    logger.info(f"Ingesting PDF: {file.filename}, tag: {tag}")
    
    # 1. Read PDF bytes
    pdf_bytes = await file.read()

    # 2. Extract pages
    pages = pdf_to_pages(pdf_bytes)
    logger.info(f"Extracted {len(pages)} pages from PDF")

    records = []

    # 3. Chunk + embed page-wise
    for page in pages:
        chunks = chunk_page(
            page_text=page["text"],
            page_number=page["page"]
        )

        for chunk in chunks:
            embedding = embedder.embed_text(chunk["text"])

            records.append({
                "text": chunk["text"],
                "embedding": embedding,
                "metadata": {
                    "tag": tag,
                    "page": chunk["page"],
                    "chunk_id": chunk["chunk_id"]
                }
            })

    # 4. Store records
    vector_store.add(records)
    logger.success(f"Stored {len(records)} chunks for {file.filename}")

    return {
        "status": "success",
        "file_name": file.filename,
        "tag": tag,
        "pages": len(pages),
        "chunks_stored": len(records)
    }
