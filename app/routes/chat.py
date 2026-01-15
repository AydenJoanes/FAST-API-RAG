from fastapi import APIRouter

from app.services.tag_inference import infer_tag_from_text
from app.services.embeddings import EmbeddingService
from app.services.llm import call_llm
from app.db.vector_store import VectorStore
from app.core.logging import logger

router = APIRouter()

vector_store = VectorStore()
embedder = EmbeddingService()


@router.post("/")
def chat(message: str):
    logger.info(f"Chat request: {message[:50]}...")
    
    # 1. Infer tag from user message
    inferred_tag = infer_tag_from_text(message)
    logger.debug(f"Inferred tag: {inferred_tag}")

    # 2. Check for wildcard in message
    if "*" in message:
        query_embedding = None
    else:
        query_embedding = embedder.embed_text(message)

    # 3. Retrieve relevant chunks from DB
    results = vector_store.search(
        query_embedding=query_embedding,
        tag=inferred_tag,
        top_k=5
    )
    logger.info(f"Retrieved {len(results)} chunks from database")

    # 4. Build context for LLM
    if not results:
        context = "No relevant context found."
    else:
        context = "\n\n".join([r["content"] for r in results])

    # 5. Call LLM
    answer = call_llm(context=context, question=message)
    logger.success(f"Generated response for: {message[:30]}...")

    return {
        "message": message,
        "inferred_tag": inferred_tag,
        "answer": answer
    }
