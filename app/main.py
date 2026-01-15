from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from app.routes.ingest import router as ingest_router
from app.routes.retrieve import router as retrieve_router
from app.routes.chat import router as chat_router
from app.routes.health import router as health_router
from app.core.logging import logger

app = FastAPI(title="RAG FastAPI")

logger.info("Starting RAG FastAPI application")

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
