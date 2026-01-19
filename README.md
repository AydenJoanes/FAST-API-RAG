# 🚀 RAG FastAPI - Design Patterns Implementation

A **Retrieval-Augmented Generation (RAG)** application built with FastAPI, implementing **7 Design Patterns** and **SOLID Principles**.

## 🎯 Features

- **PDF Ingestion** - Upload PDFs, extract text, chunk, embed, and store
- **Semantic Search** - Find similar documents using vector similarity
- **AI Chat** - Answer questions using retrieved context + LLM
- **Clean Architecture** - 4-layer architecture for maintainability

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ ROUTES (app/routes/)          - HTTP Controllers            │
└───────────────────────────┬─────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ APPLICATION (app/application/) - Business Logic/Facades     │
└───────────────────────────┬─────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ INFRASTRUCTURE (app/infrastructure/) - Implementations      │
└───────────────────────────┬─────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ DOMAIN (app/domain/)       - Interfaces & Contracts         │
└─────────────────────────────────────────────────────────────┘
```

## 📋 Design Patterns

| Pattern | Location | Purpose |
|---------|----------|---------|
| **Singleton** | `MiniLMEmbedder`, `OpenRouterAdapter` | Load heavy resources once |
| **Factory** | `DocumentLoaderFactory` | Create loaders by file type |
| **Strategy** | `IChunker`, `IEmbedder` | Swap algorithms at runtime |
| **Repository** | `PostgresVectorStore` | Abstract database operations |
| **Adapter** | `OpenRouterAdapter` | Integrate external APIs |
| **Facade** | `ChatService`, `IngestService` | Simplify complex subsystems |
| **Builder** | `RAGPromptBuilder` | Construct prompts step-by-step |

## 🛠️ Tech Stack

- **FastAPI** - Web framework
- **PostgreSQL + pgvector** - Vector database
- **MiniLM** - Embedding model (sentence-transformers)
- **OpenRouter API** - LLM provider (Mistral-7B)
- **Docker Compose** - Containerization

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- OpenRouter API key ([Get one here](https://openrouter.ai))

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/AydenJoanes/FAST-API-RAG.git
   cd FAST-API-RAG
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENROUTER_API_KEY
   ```

3. **Run with Docker**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Chat UI: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health/

## 📖 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Chat UI |
| `POST` | `/ingest/` | Upload and process PDF |
| `POST` | `/retrieve/` | Search documents |
| `POST` | `/chat/` | Ask questions |
| `GET` | `/health/` | Health check |

## 📂 Project Structure

```
app/
├── domain/                 # Layer 1: Contracts
│   ├── interfaces/         # Abstract interfaces
│   └── builders/           # Builder pattern
├── infrastructure/         # Layer 2: Implementations
│   ├── embedders/          # MiniLM, etc.
│   ├── llm_providers/      # OpenRouter
│   ├── persistence/        # PostgreSQL
│   ├── chunkers/           # Text chunking
│   └── document_loaders/   # PDF loader + factory
├── application/            # Layer 3: Business Logic
│   ├── chat_service.py
│   ├── ingest_service.py
│   └── retrieval_service.py
├── routes/                 # Layer 4: HTTP
│   ├── chat.py
│   ├── ingest.py
│   ├── retrieve.py
│   └── health.py
└── core/                   # Utilities
    ├── logging.py
    └── exceptions.py       # Custom exception hierarchy
```

## ⚖️ SOLID Principles

- **S**ingle Responsibility - Each class has one job
- **O**pen/Closed - Extend without modifying existing code
- **L**iskov Substitution - Implementations are interchangeable
- **I**nterface Segregation - Small, focused interfaces
- **D**ependency Inversion - Depend on abstractions

## 🛡️ Error Handling

Custom exception hierarchy with 15+ specific exceptions:

```
RAGBaseException
├── DocumentProcessingError (Empty, Corrupted, Unsupported)
├── ChunkingError
├── EmbeddingError
├── VectorStoreError (Connection, Query)
├── LLMProviderError (Connection, RateLimit, Auth)
└── ValidationError (EmptyQuery, TooLong)
```

## 🧪 Running Tests

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Run tests
pytest tests/ -v
```

## 📄 Documentation

- [DESIGN_PATTERN_PHASE.md](DESIGN_PATTERN_PHASE.md) - Detailed pattern explanations
- [EXECUTION_FLOW.md](EXECUTION_FLOW.md) - Request flow documentation

## 🔧 Extending the Application

### Adding a new embedder:
```python
# 1. Create new file
class OpenAIEmbedder(IEmbedder):
    def embed_text(self, text): ...

# 2. Use it
IngestService(embedder=OpenAIEmbedder())
```

### Adding a new document loader:
```python
# 1. Create loader
class DocxLoader(IDocumentLoader): ...

# 2. Register
DocumentLoaderFactory.register(".docx", DocxLoader)
```

## 📝 License

MIT License

## 👤 Author

Ayden Joanes
