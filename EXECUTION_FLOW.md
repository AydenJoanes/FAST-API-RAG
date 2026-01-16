# RAG FastAPI - Complete Execution Flow

## 📋 Table of Contents
1. [Startup Sequence (docker-compose up)](#startup-sequence)
2. [User Ingest Flow](#user-ingest-flow)
3. [User Retrieve Flow](#user-retrieve-flow)
4. [User Chat Flow](#user-chat-flow)
5. [Health Check Flow](#health-check-flow)
6. [Complete Call Chain](#complete-call-chain)

---

## 🚀 Startup Sequence (docker-compose up)

### Step 1: Docker Compose Starts Services

```
docker-compose up
        │
        ├─ Starts PostgreSQL container
        │   └─ Loads: init.sql (creates document_chunks table + pgvector extension)
        │
        └─ Starts FastAPI app container
            └─ Runs: python -m uvicorn app.main:app
```

### Step 2: main.py Loads

**File:** `app/main.py` (Lines 1-40)

```python
# SEQUENCE OF EXECUTION:

1. from fastapi import FastAPI
   └─ Imports FastAPI framework

2. from app.routes.ingest import router as ingest_router
   └─ File: app/routes/ingest.py (Lines 1-70)
      └─ Creates: ingest_service = IngestService()
         └─ File: app/application/ingest_service.py (Lines 1-151)
            └─ Calls: __init__(self)
               ├─ Line 47: self._embedder = embedder or get_embedder()
               │  └─ File: app/infrastructure/embedders/__init__.py
               │     └─ Calls: get_embedder()
               │        └─ File: app/infrastructure/embedders/minilm_embedder.py (Lines 1-80)
               │           └─ Calls: MiniLMEmbedder() (Singleton)
               │              └─ First time: Load 90MB model from HuggingFace
               │              └─ Logs: "Loading MiniLM embedding model (Singleton)..."
               │              └─ Wait 60+ seconds for model to download/load
               │              └─ Caches in memory for future use
               │
               ├─ Line 48: self._vector_store = vector_store or PostgresVectorStore()
               │  └─ File: app/infrastructure/persistence/postgres_vector_store.py (Lines 1-183)
               │     └─ Calls: __init__(self)
               │        └─ Creates connection pool to PostgreSQL
               │        └─ Tries to connect to: localhost:5432 (DB host)
               │        └─ Waits for database to be ready
               │
               └─ Line 49: self._chunker = chunker or FixedSizeChunker(...)
                  └─ File: app/infrastructure/chunkers/fixed_size_chunker.py
                     └─ Calls: FixedSizeChunker(chunk_size=500, overlap=50)
                        └─ Stores parameters, doesn't process anything yet

3. from app.routes.retrieve import router as retrieve_router
   └─ File: app/routes/retrieve.py
      └─ Creates: retrieval_service = RetrievalService()
         └─ File: app/application/retrieval_service.py
            └─ Same initialization as IngestService (shares embedder, vector_store)

4. from app.routes.chat import router as chat_router
   └─ File: app/routes/chat.py
      └─ Creates: chat_service = ChatService()
         └─ File: app/application/chat_service.py
            └─ Calls: __init__(self)
               ├─ Sets up embedder
               ├─ Sets up vector_store
               ├─ Sets up llm_provider
               │  └─ File: app/infrastructure/llm_providers/openrouter_adapter.py
               │     └─ Stores OpenRouter API key from .env
               │
               └─ Sets up prompt_builder
                  └─ File: app/domain/builders/prompt_builder.py
                     └─ Initializes: RAGPromptBuilder()

5. from app.routes.health import router as health_router
   └─ File: app/routes/health.py
      └─ No service initialization, just route definitions

6. app.include_router(ingest_router, prefix="/ingest", tags=["ingest"])
   └─ Registers HTTP routes
   └─ Routes become available at: POST /ingest/

7. app.include_router(retrieve_router, prefix="/retrieve", tags=["retrieve"])
   └─ Routes available at: POST /retrieve/

8. app.include_router(chat_router, prefix="/chat", tags=["chat"])
   └─ Routes available at: POST /chat/

9. app.include_router(health_router, prefix="/health", tags=["health"])
   └─ Routes available at: GET /health/

10. logger.info("Starting RAG FastAPI application")
    └─ File: app/core/logging.py
       └─ Logs startup message

11. if __name__ == "__main__":
    └─ Starts Uvicorn server
       └─ Logs: "INFO:     Uvicorn running on http://0.0.0.0:8000"
```

---

## 🟢 **APP IS NOW READY** ✅

```
All services initialized
All routes registered
All dependencies loaded
Waiting for user requests...
```

---

## 📤 User Ingest Flow (POST /ingest/)

### Scenario: User uploads "resume.pdf"

```
╔════════════════════════════════════════════════════════════════╗
║ USER ACTION: Click "Upload" button in browser                  ║
║ Sends: POST /ingest/ with file=resume.pdf, tag=resume         ║
╚════════════════════════════════════════════════════════════════╝
        │
        ▼
HTTP Request hits FastAPI
        │
        ▼
app/routes/ingest.py - ingest_document() function (Line 21-51)
│
├─ Line 26: logger.info("Ingest request: resume.pdf, tag: resume")
│   └─ File: app/core/logging.py - logs the request
│
├─ Line 29: if not ingest_service.is_file_supported(file.filename)
│   └─ File: app/application/ingest_service.py - is_file_supported() (Line 53-54)
│      └─ Calls: DocumentLoaderFactory.is_supported("resume.pdf")
│         └─ File: app/infrastructure/document_loaders/loader_factory.py
│            └─ Checks if ".pdf" is in _loaders dictionary
│            └─ Returns: True
│
├─ Line 34: file_bytes = await file.read()
│   └─ Reads file from HTTP request
│   └─ Returns: bytes of PDF content
│
└─ Line 37-41: result = ingest_service.ingest(file_bytes, "resume.pdf", "resume")
   │
   └─ File: app/application/ingest_service.py - ingest() (Line 66-111)
      │
      ├─ STEP 1: Load Document (Line 85)
      │   └─ loader = DocumentLoaderFactory.create_loader("resume.pdf")
      │      │
      │      └─ File: app/infrastructure/document_loaders/loader_factory.py
      │         ├─ Extract extension: ".pdf"
      │         ├─ Lookup _loaders[".pdf"]
      │         └─ Returns: PDFLoader() instance
      │
      │   └─ pages = loader.load(file_bytes)
      │      │
      │      └─ File: app/infrastructure/document_loaders/pdf_loader.py
      │         ├─ Uses: pdfplumber library to parse PDF
      │         ├─ Extracts text from each page
      │         └─ Returns: [{"page": 1, "text": "..."}, {"page": 2, "text": "..."}, ...]
      │
      ├─ STEP 2: Chunk Text (Line 89)
      │   └─ chunks = self._chunker.chunk(pages)
      │      │
      │      └─ File: app/infrastructure/chunkers/fixed_size_chunker.py - chunk() (Line 35-55)
      │         ├─ Takes pages: [{"page": 1, "text": "..."}, ...]
      │         ├─ Splits each page by chunk_size=500 characters
      │         ├─ Adds overlap=50 characters between chunks
      │         └─ Returns: [
      │            {"page": 1, "text": "...", "chunk_id": 0},
      │            {"page": 1, "text": "...", "chunk_id": 1},
      │            ...
      │         ]
      │
      ├─ STEP 3: Generate Embeddings (Line 93-96)
      │   └─ for chunk in chunks:
      │      └─ chunk["embedding"] = self._embedder.embed_text(chunk["text"])
      │         │
      │         └─ File: app/infrastructure/embedders/minilm_embedder.py - embed_text() (Line 65-72)
      │            ├─ Takes: "Some text from chunk"
      │            ├─ Uses: self._model.encode(text) (Singleton model)
      │            ├─ Returns: [0.123, 0.456, 0.789, ...] (384 dimensions)
      │            │
      │            └─ Now chunk looks like:
      │               {
      │                 "page": 1,
      │                 "text": "Some text from chunk",
      │                 "chunk_id": 0,
      │                 "embedding": [0.123, 0.456, 0.789, ...]
      │               }
      │
      ├─ STEP 4: Store in Vector Database (Line 100)
      │   └─ self._vector_store.add(chunks)
      │      │
      │      └─ File: app/infrastructure/persistence/postgres_vector_store.py - add() (Line 28-53)
      │         ├─ Takes: chunks with embeddings
      │         ├─ For each chunk, creates SQL INSERT:
      │         │   INSERT INTO document_chunks (content, embedding, tag, page_number, chunk_id)
      │         │   VALUES ('Some text', '[0.123, 0.456, ...]'::vector, 'resume', 1, 0)
      │         ├─ Connects to PostgreSQL database
      │         │  └─ File: app/db/models.py - get_connection() (Line 8-17)
      │         │     ├─ Reads: DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD from .env
      │         │     └─ Calls: psycopg2.connect(...) to PostgreSQL
      │         │
      │         └─ Commits transaction to database
      │
      └─ STEP 5: Return Result (Line 103-111)
         └─ Returns to app/routes/ingest.py
            └─ Returns JSON: {"chunks_stored": 25, "filename": "resume.pdf", "tag": "resume"}
                │
                └─ Sent back to user's browser as HTTP response
                   └─ User sees: "✓ 25 chunks stored successfully"
```

---

## 🔍 User Retrieve Flow (POST /retrieve/)

### Scenario: User searches for "salary negotiation"

```
╔════════════════════════════════════════════════════════════════╗
║ USER ACTION: Enter search query "salary negotiation"            ║
║ Sends: POST /retrieve/ with query="salary negotiation"         ║
╚════════════════════════════════════════════════════════════════╝
        │
        ▼
app/routes/retrieve.py - retrieve_documents() (Line 21-45)
│
├─ logger.info("Retrieve request: salary negotiation")
│
└─ File: app/application/retrieval_service.py - retrieve() (Line 53-93)
   │
   ├─ STEP 1: Embed Query (Line 66)
   │   └─ query_embedding = self._embedder.embed_text("salary negotiation")
   │      │
   │      └─ File: app/infrastructure/embedders/minilm_embedder.py
   │         └─ Returns: [0.234, 0.567, 0.890, ...] (384 dimensions)
   │
   ├─ STEP 2: Search Vector Database (Line 69)
   │   └─ results = self._vector_store.search(query_embedding, top_k=5, tag=tag)
   │      │
   │      └─ File: app/infrastructure/persistence/postgres_vector_store.py - search() (Line 83-120)
   │         ├─ Connects to PostgreSQL
   │         │  └─ File: app/db/models.py - get_connection()
   │         │
   │         ├─ Runs SQL query:
   │         │   SELECT content, tag, page_number, chunk_id
   │         │   FROM document_chunks
   │         │   ORDER BY embedding <-> %s (vector similarity)
   │         │   LIMIT 5
   │         │
   │         ├─ pgvector calculates similarity using: embedding <-> query_embedding
   │         │  └─ pgvector extension (built into PostgreSQL container)
   │         │
   │         └─ Returns: Top 5 most similar chunks
   │            [
   │              {"content": "...", "page": 5, "chunk_id": 2},
   │              {"content": "...", "page": 8, "chunk_id": 1},
   │              ...
   │            ]
   │
   └─ STEP 3: Return Results (Line 73-93)
      └─ Returns to app/routes/retrieve.py
         └─ Returns JSON: {"results": [...], "count": 5}
            │
            └─ Sent back to user's browser as HTTP response
```

---

## 💬 User Chat Flow (POST /chat/)

### Scenario: User asks "What is the salary range?"

```
╔════════════════════════════════════════════════════════════════╗
║ USER ACTION: Type message "What is the salary range?"           ║
║ Sends: POST /chat/ with message="What is the salary range?"    ║
╚════════════════════════════════════════════════════════════════╝
        │
        ▼
app/routes/chat.py - chat_endpoint() (Line 24-51)
│
├─ logger.info("Chat request: What is the salary range?")
│
└─ File: app/application/chat_service.py - chat() (Line 80-160)
   │
   ├─ STEP 1: Infer Tag (Line 90)
   │   └─ inferred_tag = tag or infer_tag_from_text(message)
   │      │
   │      └─ File: app/services/tag_inference.py - infer_tag_from_text() (Line 1-14)
   │         ├─ Checks if "salary" in message → Detects "FINANCE" tag
   │         └─ Returns: "FINANCE"
   │
   ├─ STEP 2: Retrieve Context (Line 93)
   │   └─ relevant_docs = self._retrieval_service.retrieve(message, tag=inferred_tag)
   │      │
   │      └─ File: app/application/retrieval_service.py - retrieve() (Line 53-93)
   │         ├─ Embed message: "What is the salary range?"
   │         │  └─ File: app/infrastructure/embedders/minilm_embedder.py
   │         │     └─ Returns: [0.345, 0.678, 0.901, ...]
   │         │
   │         └─ Search vector database
   │            └─ File: app/infrastructure/persistence/postgres_vector_store.py - search()
   │               └─ Returns: Top 5 most similar documents
   │                  └─ Example: ["The salary range is $50k-$70k", "Bonuses are...", ...]
   │
   ├─ STEP 3: Build Prompt (Line 96-99)
   │   └─ messages = (
   │      │    RAGPromptBuilder()
   │      │    .reset()
   │      │    .add_context(relevant_docs)
   │      │    .set_query(message)
   │      │    .build_messages()
   │      │)
   │      │
   │      └─ File: app/domain/builders/prompt_builder.py
   │         ├─ RAGPromptBuilder (Line 1-150)
   │         │  ├─ reset(): Initialize empty components
   │         │  ├─ add_context(): Add retrieved documents
   │         │  ├─ set_query(): Add user's question
   │         │  └─ build_messages(): Construct final prompt
   │         │
   │         └─ Returns: [
   │            {
   │              "role": "system",
   │              "content": "You are a helpful assistant. Use the context to answer."
   │            },
   │            {
   │              "role": "user",
   │              "content": "Context:\nThe salary range is $50k-$70k\n\nQuestion: What is the salary range?"
   │            }
   │         ]
   │
   ├─ STEP 4: Call LLM (Line 102)
   │   └─ response = self._llm_provider.chat(messages)
   │      │
   │      └─ File: app/infrastructure/llm_providers/openrouter_adapter.py - chat() (Line 85-120)
   │         ├─ Takes messages array
   │         ├─ Calls: requests.post("https://openrouter.ai/api/v1/chat/completions", ...)
   │         │  ├─ Sends: {
   │         │  │    "model": "mistralai/mistral-7b-instruct",
   │         │  │    "messages": [...]
   │         │  │  }
   │         │  └─ Authenticates with: Authorization: Bearer {API_KEY}
   │         │
   │         └─ Waits for OpenRouter API response (3-10 seconds)
   │            └─ Returns: "The salary range is $50k-$70k based on the documents provided."
   │
   ├─ STEP 5: Tag Document (Line 105-116)
   │   └─ Saves chat message to database with tag
   │      └─ File: app/infrastructure/persistence/postgres_vector_store.py
   │         └─ Stores for future context/history
   │
   └─ STEP 6: Return Response (Line 117-127)
      └─ Returns to app/routes/chat.py
         └─ Returns JSON: {
            "response": "The salary range is $50k-$70k based on the documents provided.",
            "sources": ["resume.pdf (page 5, chunk 2)", ...]
         }
            │
            └─ Sent back to user's browser
               └─ User sees answer + document sources
```

---

## 🏥 Health Check Flow (GET /health/)

### Scenario: Monitor service health

```
GET /health/
        │
        ▼
app/routes/health.py - health_check() (Line 20-50)
│
├─ Check PostgreSQL connection
│   └─ File: app/db/models.py - get_connection()
│      └─ Tries to connect to PostgreSQL
│         └─ Returns: ✓ Connected or ✗ Failed
│
├─ Check MiniLM model
│   └─ File: app/infrastructure/embedders/minilm_embedder.py
│      └─ Checks if model is loaded
│         └─ Returns: ✓ Loaded or ✗ Failed
│
└─ Returns JSON: {
   "status": "healthy",
   "database": "connected",
   "embedder": "loaded"
}
```

---

## 🔗 Complete Call Chain Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ DOCKER COMPOSE UP                                               │
│ ├─ PostgreSQL Container (init.sql)                              │
│ └─ FastAPI Container (app/main.py)                              │
└─────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│ APP INITIALIZATION (ONE TIME)                                   │
│ ├─ app/main.py loads                                            │
│ ├─ app/routes/ingest.py → IngestService()                       │
│ │   └─ app/application/ingest_service.py → __init__()           │
│ │       ├─ MiniLMEmbedder() (Singleton - load model)            │
│ │       ├─ PostgresVectorStore()                                │
│ │       └─ FixedSizeChunker()                                   │
│ ├─ app/routes/retrieve.py → RetrievalService()                  │
│ │   └─ app/application/retrieval_service.py → __init__()        │
│ ├─ app/routes/chat.py → ChatService()                           │
│ │   └─ app/application/chat_service.py → __init__()             │
│ │       ├─ RAGPromptBuilder()                                   │
│ │       └─ OpenRouterAdapter()                                  │
│ └─ app/routes/health.py (no initialization)                     │
└─────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│ SERVER READY - WAITING FOR USER REQUESTS                        │
└─────────────────────────────────────────────────────────────────┘
        │
        ├─────────────────────┬──────────────────────┬──────────────────────┐
        │                     │                      │                      │
        ▼                     ▼                      ▼                      ▼
   ┌─────────┐            ┌──────────┐          ┌────────┐            ┌────────┐
   │ INGEST  │            │ RETRIEVE │          │  CHAT  │            │ HEALTH │
   └────┬────┘            └────┬─────┘          └───┬────┘            └────────┘
        │                      │                    │
        ▼                      ▼                    ▼
   routes/ingest.py      routes/retrieve.py   routes/chat.py
        │                      │                    │
        ▼                      ▼                    ▼
   IngestService         RetrievalService      ChatService
        │                      │                    │
        ├─ Factory             ├─ Embedder         ├─ Tag Inference
        │  (PDFLoader)         │                   │
        ├─ Chunker             └─ Vector Store     ├─ Retrieval Service
        │                                          │
        ├─ Embedder                                ├─ Prompt Builder
        │                                          │
        └─ Vector Store                            ├─ LLM Adapter
                                                   │
                                                   └─ Vector Store
```

---

## 📊 File Dependency Map

```
app/
├── main.py (ENTRY POINT - runs first)
│   ├── routes/ingest.py
│   │   └── application/ingest_service.py
│   │       ├── infrastructure/embedders/minilm_embedder.py (Singleton)
│   │       ├── infrastructure/persistence/postgres_vector_store.py
│   │       │   └── db/models.py (get_connection)
│   │       ├── infrastructure/chunkers/fixed_size_chunker.py (Strategy)
│   │       └── infrastructure/document_loaders/loader_factory.py (Factory)
│   │           └── infrastructure/document_loaders/pdf_loader.py
│   │
│   ├── routes/retrieve.py
│   │   └── application/retrieval_service.py
│   │       ├── infrastructure/embedders/minilm_embedder.py (reused)
│   │       └── infrastructure/persistence/postgres_vector_store.py (reused)
│   │
│   ├── routes/chat.py
│   │   └── application/chat_service.py
│   │       ├── application/retrieval_service.py (reused)
│   │       ├── domain/builders/prompt_builder.py (Builder)
│   │       ├── infrastructure/llm_providers/openrouter_adapter.py (Adapter)
│   │       ├── services/tag_inference.py (Tag detection)
│   │       └── infrastructure/persistence/postgres_vector_store.py (reused)
│   │
│   └── routes/health.py
│       └── db/models.py (get_connection)
│
├── core/logging.py (used by all files)
└── domain/interfaces/ (used by all infrastructure files)
```

---

## ⏱️ Timeline View

```
TIME 00:00 - docker-compose up
TIME 00:05 - PostgreSQL starts, init.sql runs
TIME 00:10 - FastAPI app starts, main.py loads
TIME 00:20 - IngestService() created, MiniLM model loading starts...
TIME 01:20 - MiniLM model loaded (90 seconds to download/load)
TIME 01:21 - All services initialized, server ready

TIME 01:25 - USER UPLOADS resume.pdf
TIME 01:26 - PDF loaded (1 second)
TIME 01:27 - Text chunked (0.5 seconds)
TIME 01:28 - Embeddings generated (10 seconds for 25 chunks)
TIME 01:39 - Chunks stored to PostgreSQL (0.5 seconds)
TIME 01:40 - User sees "25 chunks stored" ✓

TIME 02:00 - USER SEARCHES for "salary negotiation"
TIME 02:01 - Query embedded (0.5 seconds)
TIME 02:02 - Vector search in PostgreSQL (0.5 seconds)
TIME 02:03 - Results returned ✓

TIME 02:30 - USER ASKS "What is the salary range?"
TIME 02:31 - Tag inferred: FINANCE (instant)
TIME 02:32 - Relevant docs retrieved (1 second)
TIME 02:33 - Prompt built (instant)
TIME 02:34 - OpenRouter API called (5-10 seconds)
TIME 02:45 - LLM response received ✓
```

---

## 🔄 Data Flow Example: Complete Chat Request

```
USER INPUT: "What is the salary range?"
        │
        ├─ [route: app/routes/chat.py]
        │
        ├─ [service: app/application/chat_service.py]
        │   ├─ Step 1: Tag Inference
        │   │   └─ app/services/tag_inference.py
        │   │      └─ Output: tag="FINANCE"
        │   │
        │   ├─ Step 2: Retrieve Relevant Documents
        │   │   └─ app/application/retrieval_service.py
        │   │       ├─ Embed query
        │   │       │  └─ app/infrastructure/embedders/minilm_embedder.py
        │   │       │     └─ Output: [0.234, 0.567, ...]
        │   │       │
        │   │       └─ Search database
        │   │           └─ app/infrastructure/persistence/postgres_vector_store.py
        │   │               └─ app/db/models.py (connection)
        │   │                  └─ Output: ["The salary is $50k-70k", ...]
        │   │
        │   ├─ Step 3: Build Prompt
        │   │   └─ app/domain/builders/prompt_builder.py
        │   │      └─ RAGPromptBuilder
        │   │         └─ Output: [
        │   │              {"role": "system", "content": "..."},
        │   │              {"role": "user", "content": "..."}
        │   │            ]
        │   │
        │   └─ Step 4: Call LLM
        │       └─ app/infrastructure/llm_providers/openrouter_adapter.py
        │          └─ OpenRouter API
        │             └─ Output: "The salary range is $50k-$70k based on..."
        │
        └─ [route returns response to user]
           └─ Browser displays answer ✓
```

---

## 🎯 Summary of File Execution Order

### On Startup (main.py):
1. `app/main.py` ⭐ STARTS HERE
2. `app/routes/ingest.py` - creates IngestService
3. `app/application/ingest_service.py` - initializes services
4. `app/infrastructure/embedders/minilm_embedder.py` - loads model
5. `app/infrastructure/persistence/postgres_vector_store.py` - connects to DB
6. `app/infrastructure/chunkers/fixed_size_chunker.py` - initializes
7. Similar for retrieve and chat routes
8. Server ready

### On Ingest Request:
1. `app/routes/ingest.py` - receives HTTP request
2. `app/application/ingest_service.py` - orchestrates
3. `app/infrastructure/document_loaders/loader_factory.py` - selects loader
4. `app/infrastructure/document_loaders/pdf_loader.py` - loads PDF
5. `app/infrastructure/chunkers/fixed_size_chunker.py` - chunks text
6. `app/infrastructure/embedders/minilm_embedder.py` - embeds chunks
7. `app/infrastructure/persistence/postgres_vector_store.py` - stores chunks
8. `app/db/models.py` - manages DB connection

### On Retrieve Request:
1. `app/routes/retrieve.py` - receives request
2. `app/application/retrieval_service.py` - orchestrates
3. `app/infrastructure/embedders/minilm_embedder.py` - embeds query
4. `app/infrastructure/persistence/postgres_vector_store.py` - searches
5. `app/db/models.py` - manages DB connection

### On Chat Request:
1. `app/routes/chat.py` - receives request
2. `app/application/chat_service.py` - orchestrates
3. `app/services/tag_inference.py` - infers tag
4. `app/application/retrieval_service.py` - gets context
5. `app/domain/builders/prompt_builder.py` - builds prompt
6. `app/infrastructure/llm_providers/openrouter_adapter.py` - calls LLM
7. Response returned to user

---

## 🗂️ Folder Structure with Execution Context

```
rag_fastapi/
├── Dockerfile ........................... Docker image definition
├── docker-compose.yml ................... Orchestrates PostgreSQL + App
├── init.sql ............................ Creates DB schema (runs once)
├── requirements.txt ..................... Python dependencies
│
└── app/
    ├── main.py ⭐ ...................... ENTRY POINT - loads everything
    │
    ├── routes/ (HTTP Controllers - Thin Layer)
    │   ├── ingest.py ................... POST /ingest/ endpoint
    │   ├── retrieve.py ................. POST /retrieve/ endpoint
    │   ├── chat.py ..................... POST /chat/ endpoint
    │   └── health.py ................... GET /health/ endpoint
    │
    ├── application/ (Service Layer - Facade)
    │   ├── ingest_service.py ........... Orchestrates document ingestion
    │   ├── retrieval_service.py ........ Orchestrates document retrieval
    │   └── chat_service.py ............. Orchestrates RAG chat
    │
    ├── infrastructure/ (Implementations - Concrete)
    │   ├── embedders/
    │   │   └── minilm_embedder.py ...... Generates embeddings (Singleton)
    │   ├── persistence/
    │   │   └── postgres_vector_store.py  Stores vectors (Repository)
    │   ├── document_loaders/
    │   │   ├── pdf_loader.py ........... Loads PDF files
    │   │   └── loader_factory.py ....... Creates loaders (Factory)
    │   ├── chunkers/
    │   │   └── fixed_size_chunker.py ... Chunks text (Strategy)
    │   └── llm_providers/
    │       └── openrouter_adapter.py ... Calls OpenRouter API (Adapter)
    │
    ├── domain/ (Abstractions - Contracts)
    │   ├── interfaces/
    │   │   ├── embedder.py ............. IEmbedder interface
    │   │   ├── vector_store.py ......... IVectorStore interface
    │   │   ├── document_loader.py ...... IDocumentLoader interface
    │   │   ├── chunker.py .............. IChunker interface
    │   │   └── llm_provider.py ......... ILLMProvider interface
    │   └── builders/
    │       └── prompt_builder.py ....... Builds prompts (Builder)
    │
    ├── db/
    │   └── models.py ................... get_connection() function
    │
    ├── services/
    │   └── tag_inference.py ............ Auto-detects document tags
    │
    └── core/
        └── logging.py .................. Logging utility
```

---

This is your complete mental map! Every file, every folder, every execution step. 🎯
