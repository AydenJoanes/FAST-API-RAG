# RAG FastAPI - Design Patterns & SOLID Principles Implementation

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Project Structure](#project-structure)
3. [Phase-by-Phase Implementation](#phase-by-phase-implementation)
4. [SOLID Principles Applied](#solid-principles-applied)
5. [Code File Explanations](#code-file-explanations)
6. [Why This Architecture?](#why-this-architecture)

---

## 🎯 Project Overview

### What is this project?
A **RAG (Retrieval-Augmented Generation)** application built with FastAPI that:
- Ingests PDF documents and stores them as vector embeddings
- Retrieves relevant document chunks based on semantic similarity
- Generates AI-powered responses using retrieved context

### Tech Stack
- **FastAPI** - Python web framework
- **PostgreSQL + pgvector** - Vector database for embeddings
- **MiniLM** - Local embedding model (sentence-transformers)
- **OpenRouter API** - LLM provider (Mistral-7B)
- **Docker** - Containerization

### Before vs After Refactoring

| Aspect | Before | After |
|--------|--------|-------|
| Structure | Flat files in services/ | Layered architecture |
| Dependencies | Tightly coupled | Loosely coupled via interfaces |
| Testability | Hard to test | Easy to mock and test |
| Extensibility | Modify existing code | Add new implementations |
| Maintenance | Changes ripple everywhere | Changes isolated to one layer |

---

## 🏗️ Project Structure

```
rag_fastapi/
├── app/
│   ├── domain/                    # LAYER 1: Core Business Logic (Abstractions)
│   │   ├── interfaces/            # Abstract interfaces (contracts)
│   │   │   ├── embedder.py        # IEmbedder interface
│   │   │   ├── vector_store.py    # IVectorStore interface
│   │   │   ├── document_loader.py # IDocumentLoader interface
│   │   │   ├── chunker.py         # IChunker interface
│   │   │   └── llm_provider.py    # ILLMProvider interface
│   │   └── builders/              # Builder pattern implementations
│   │       └── prompt_builder.py  # PromptBuilder, RAGPromptBuilder
│   │
│   ├── infrastructure/            # LAYER 2: Concrete Implementations
│   │   ├── embedders/
│   │   │   └── minilm_embedder.py # MiniLMEmbedder (Singleton)
│   │   ├── persistence/
│   │   │   └── postgres_vector_store.py # PostgresVectorStore (Repository)
│   │   ├── document_loaders/
│   │   │   ├── pdf_loader.py      # PDFLoader
│   │   │   └── loader_factory.py  # DocumentLoaderFactory (Factory)
│   │   ├── chunkers/
│   │   │   └── fixed_size_chunker.py # FixedSizeChunker (Strategy)
│   │   └── llm_providers/
│   │       └── openrouter_adapter.py # OpenRouterAdapter (Adapter)
│   │
│   ├── application/               # LAYER 3: Service Layer (Facade)
│   │   ├── ingest_service.py      # IngestService
│   │   ├── retrieval_service.py   # RetrievalService
│   │   └── chat_service.py        # ChatService
│   │
│   ├── routes/                    # LAYER 4: HTTP Controllers (Thin)
│   │   ├── ingest.py              # POST /ingest/
│   │   ├── retrieve.py            # POST /retrieve/
│   │   ├── chat.py                # POST /chat/
│   │   └── health.py              # GET /health/
│   │
│   ├── db/                        # Database utilities
│   │   └── models.py              # get_connection()
│   │
│   ├── services/                  # Business logic utilities
│   │   └── tag_inference.py       # Auto-detect document tags
│   │
│   ├── core/                      # Shared utilities
│   │   └── logging.py             # Logging configuration
│   │
│   └── main.py                    # FastAPI app entry point
│
├── docker-compose.yml             # Container orchestration
├── Dockerfile                     # App container definition
├── init.sql                       # Database schema
└── requirements.txt               # Python dependencies
```

### Layer Explanation

```
┌─────────────────────────────────────────────────────────────┐
│                      ROUTES (HTTP Layer)                     │
│         Thin controllers - only handle HTTP concerns         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   APPLICATION (Service Layer)                │
│     Facade Pattern - orchestrates business operations        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 INFRASTRUCTURE (Implementations)             │
│   Concrete classes implementing domain interfaces            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    DOMAIN (Abstractions)                     │
│         Interfaces & core business logic contracts           │
└─────────────────────────────────────────────────────────────┘
```

---

## 📝 Phase-by-Phase Implementation

### Phase 1: Interfaces + Singleton + Repository Pattern

#### What was done:
Created abstract interfaces for all core components and implemented Singleton for the embedder.

#### Files Created:
```
app/domain/interfaces/
├── __init__.py
├── embedder.py          # IEmbedder interface
├── vector_store.py      # IVectorStore interface  
├── document_loader.py   # IDocumentLoader interface
├── chunker.py           # IChunker interface
└── llm_provider.py      # ILLMProvider interface

app/infrastructure/
├── embedders/
│   └── minilm_embedder.py    # Singleton implementation
└── persistence/
    └── postgres_vector_store.py  # Repository implementation
```

#### Why Interfaces?
```python
# BEFORE: Direct dependency on concrete class
class IngestRoute:
    def __init__(self):
        self.embedder = MiniLMEmbedder()  # ❌ Tightly coupled

# AFTER: Depend on abstraction
class IngestRoute:
    def __init__(self, embedder: IEmbedder):  # ✅ Loosely coupled
        self.embedder = embedder
```

**Benefits:**
- Can swap MiniLM for OpenAI embeddings without changing business logic
- Easy to mock for testing
- Follows Dependency Inversion Principle

#### Why Singleton for Embedder?
```python
class MiniLMEmbedder(IEmbedder):
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._model = SentenceTransformer('all-MiniLM-L6-v2')  # ~90MB model
        return cls._instance
```

**Problem Solved:** The MiniLM model is ~90MB. Without Singleton:
- Each request could load a new model instance
- Memory usage would explode
- Slow response times

**With Singleton:** Model loads once, shared across all requests.

#### Why Repository Pattern?
```python
class PostgresVectorStore(IVectorStore):
    def add(self, records: List[Dict]) -> None:
        # SQL INSERT logic hidden here
        
    def search(self, embedding: List[float], top_k: int) -> List[Dict]:
        # SQL SELECT with vector similarity hidden here
```

**Benefits:**
- Business logic doesn't know about SQL/PostgreSQL
- Can swap to Pinecone, Chroma, or Weaviate easily
- Centralizes all data access in one place

---

### Phase 2: Factory Method Pattern

#### What was done:
Created a factory to dynamically create document loaders based on file type.

#### Files Created:
```
app/infrastructure/document_loaders/
├── __init__.py
├── pdf_loader.py         # PDFLoader implementation
└── loader_factory.py     # DocumentLoaderFactory
```

#### The Factory Pattern:
```python
class DocumentLoaderFactory:
    """Creates appropriate loader based on file extension"""
    
    _loaders = {
        '.pdf': PDFLoader,
        # Future: '.docx': DocxLoader,
        # Future: '.txt': TextLoader,
    }
    
    @classmethod
    def create_loader(cls, filename: str) -> IDocumentLoader:
        ext = Path(filename).suffix.lower()
        loader_class = cls._loaders.get(ext)
        if not loader_class:
            raise ValueError(f"No loader for {ext}")
        return loader_class()
```

#### Why Factory?
```python
# BEFORE: Manual if-else chain
def load_document(filename):
    if filename.endswith('.pdf'):
        loader = PDFLoader()
    elif filename.endswith('.docx'):
        loader = DocxLoader()  # ❌ Must modify this code for new types
    # ...

# AFTER: Factory handles creation
def load_document(filename):
    loader = DocumentLoaderFactory.create_loader(filename)  # ✅ Open/Closed
    return loader.load(file_bytes)
```

**Benefits:**
- Adding new file types = register in factory, no other code changes
- Follows Open/Closed Principle
- Centralizes object creation logic

---

### Phase 3: Strategy Pattern

#### What was done:
Made chunking algorithm interchangeable at runtime.

#### Files Created:
```
app/infrastructure/chunkers/
├── __init__.py
└── fixed_size_chunker.py  # FixedSizeChunker (Strategy)
```

#### The Strategy Pattern:
```python
# Interface defines the contract
class IChunker(ABC):
    @abstractmethod
    def chunk(self, pages: List[Dict]) -> List[Dict]:
        pass

# Strategy 1: Fixed size chunks
class FixedSizeChunker(IChunker):
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk(self, pages: List[Dict]) -> List[Dict]:
        # Split by character count with overlap

# Strategy 2: Semantic chunks (could add later)
class SemanticChunker(IChunker):
    def chunk(self, pages: List[Dict]) -> List[Dict]:
        # Split by sentence boundaries
```

#### Why Strategy?
```python
# Can swap chunking strategies without changing caller
ingest_service = IngestService(chunker=FixedSizeChunker(chunk_size=500))
# OR
ingest_service = IngestService(chunker=SemanticChunker())
```

**Use Cases:**
- Small documents → larger chunks
- Technical documents → smaller, precise chunks
- Different languages → different chunking rules

---

### Phase 4: Adapter Pattern

#### What was done:
Created an adapter to wrap the external OpenRouter API behind our interface.

#### Files Created:
```
app/infrastructure/llm_providers/
├── __init__.py
└── openrouter_adapter.py  # OpenRouterAdapter
```

#### The Adapter Pattern:
```python
class ILLMProvider(ABC):
    """Our interface - what WE want"""
    @abstractmethod
    def chat(self, messages: List[Dict]) -> str:
        pass

class OpenRouterAdapter(ILLMProvider):
    """Adapts OpenRouter API to our interface"""
    
    def chat(self, messages: List[Dict]) -> str:
        # Translate our format to OpenRouter's format
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": self.model,
                "messages": messages  # OpenRouter expects this format
            }
        )
        return response.json()["choices"][0]["message"]["content"]
```

#### Why Adapter?
```
┌─────────────┐      ┌─────────────────┐      ┌──────────────────┐
│  Our Code   │ ───► │ OpenRouterAdapter│ ───► │ OpenRouter API   │
│ (ILLMProvider)     │   (Translator)   │      │ (External Service)│
└─────────────┘      └─────────────────┘      └──────────────────┘
```

**Benefits:**
- Can swap to OpenAI, Anthropic, local LLM without changing business logic
- Isolates external API changes to one file
- Standardizes different API formats to our interface

---

### Phase 5: Service Layer + Facade Pattern

#### What was done:
Created a service layer that orchestrates complex operations behind simple methods.

#### Files Created:
```
app/application/
├── __init__.py
├── ingest_service.py      # Document ingestion facade
├── retrieval_service.py   # Document retrieval facade
└── chat_service.py        # RAG chat facade
```

#### The Facade Pattern:
```python
class IngestService:
    """
    Facade that hides complexity of:
    - Document loading (Factory)
    - Text chunking (Strategy)
    - Embedding generation (Singleton)
    - Vector storage (Repository)
    """
    
    def ingest(self, filename: str, file_bytes: bytes, tag: str) -> int:
        # 1. Create loader (Factory Pattern)
        loader = self._loader_factory.create_loader(filename)
        
        # 2. Load document
        pages = loader.load(file_bytes)
        
        # 3. Chunk text (Strategy Pattern)
        chunks = self._chunker.chunk(pages)
        
        # 4. Generate embeddings (Singleton)
        for chunk in chunks:
            chunk["embedding"] = self._embedder.embed(chunk["text"])
        
        # 5. Store in vector DB (Repository)
        self._vector_store.add(chunks)
        
        return len(chunks)
```

#### Why Facade?
```python
# BEFORE: Route knows all the steps
@router.post("/")
async def ingest(file: UploadFile):
    loader = PDFLoader()
    pages = loader.load(await file.read())
    chunker = FixedSizeChunker()
    chunks = chunker.chunk(pages)
    embedder = MiniLMEmbedder()
    for chunk in chunks:
        chunk["embedding"] = embedder.embed(chunk["text"])
    store = PostgresVectorStore()
    store.add(chunks)
    # ❌ Route is doing too much!

# AFTER: Route delegates to service
@router.post("/")
async def ingest(file: UploadFile):
    count = ingest_service.ingest(file.filename, await file.read())
    return {"chunks_stored": count}
    # ✅ Clean and simple!
```

**Benefits:**
- Routes become thin controllers (only HTTP concerns)
- Business logic centralized in services
- Easy to reuse (CLI, API, tests all use same service)

---

### Phase 6: Builder Pattern

#### What was done:
Created a flexible prompt builder for constructing LLM prompts.

#### Files Created:
```
app/domain/builders/
├── __init__.py
└── prompt_builder.py  # PromptBuilder, RAGPromptBuilder
```

#### The Builder Pattern:
```python
class RAGPromptBuilder(PromptBuilder):
    """Builds prompts step-by-step with fluent API"""
    
    def reset(self) -> 'RAGPromptBuilder':
        self._components = PromptComponents()
        self._add_default_instructions()
        return self
    
    def add_context(self, context: str, label: str = "Context") -> 'RAGPromptBuilder':
        self._components.context_sections.append(f"### {label}\n{context}")
        return self
    
    def set_query(self, query: str) -> 'RAGPromptBuilder':
        self._components.user_query = query
        return self
    
    def build_messages(self) -> List[Dict]:
        return [
            {"role": "system", "content": self.build_system_prompt()},
            {"role": "user", "content": self.build_user_prompt()}
        ]
```

#### Usage - Fluent API:
```python
# Build prompt step-by-step
messages = (
    RAGPromptBuilder()
    .reset()
    .add_context(retrieved_docs, "Retrieved Documents")
    .set_query(user_question)
    .add_constraint("Answer in 2-3 sentences")
    .build_messages()
)

response = llm_provider.chat(messages)
```

#### Why Builder?
```python
# BEFORE: Hardcoded prompt string
prompt = f"""You are a helpful assistant.
Context: {context}
Question: {question}
Answer:"""  # ❌ Hard to customize

# AFTER: Flexible construction
builder = RAGPromptBuilder().reset()
builder.add_context(context)
builder.set_query(question)
if user_wants_brief:
    builder.add_constraint("Be brief")
messages = builder.build_messages()  # ✅ Customizable
```

**Benefits:**
- Separate prompt construction from usage
- Easy to create different prompt styles
- Readable, self-documenting code

---

## ⚖️ SOLID Principles Applied

### S - Single Responsibility Principle
> "A class should have only one reason to change"

| Class | Single Responsibility |
|-------|----------------------|
| `PDFLoader` | Only loads PDF files |
| `FixedSizeChunker` | Only chunks text |
| `MiniLMEmbedder` | Only generates embeddings |
| `PostgresVectorStore` | Only handles database operations |
| `OpenRouterAdapter` | Only communicates with OpenRouter |
| `IngestService` | Only orchestrates ingestion workflow |

### O - Open/Closed Principle
> "Open for extension, closed for modification"

```python
# Adding new file type - NO modification to existing code
# Just add new loader and register in factory

class DocxLoader(IDocumentLoader):  # NEW class
    def load(self, file_bytes: bytes) -> List[Dict]:
        # DOCX loading logic

# Register in factory
DocumentLoaderFactory._loaders['.docx'] = DocxLoader
```

### L - Liskov Substitution Principle
> "Subtypes must be substitutable for their base types"

```python
# Any IChunker can be used interchangeably
def process_document(chunker: IChunker, pages: List[Dict]):
    return chunker.chunk(pages)

# All these work identically:
process_document(FixedSizeChunker(), pages)
process_document(SemanticChunker(), pages)
process_document(SentenceChunker(), pages)
```

### I - Interface Segregation Principle
> "Clients should not depend on interfaces they don't use"

```python
# WRONG: One big interface
class IDocumentProcessor(ABC):
    def load(self): pass
    def chunk(self): pass
    def embed(self): pass
    def store(self): pass

# RIGHT: Segregated interfaces
class IDocumentLoader(ABC):
    def load(self): pass

class IChunker(ABC):
    def chunk(self): pass

class IEmbedder(ABC):
    def embed(self): pass
```

### D - Dependency Inversion Principle
> "Depend on abstractions, not concretions"

```python
# WRONG: High-level depends on low-level
class ChatService:
    def __init__(self):
        self.llm = OpenRouterAdapter()  # ❌ Concrete class

# RIGHT: Both depend on abstraction
class ChatService:
    def __init__(self, llm_provider: ILLMProvider):  # ✅ Interface
        self.llm = llm_provider
```

---

## 📁 Code File Explanations

### Domain Layer (app/domain/)

#### `interfaces/embedder.py`
```python
class IEmbedder(ABC):
    @abstractmethod
    def embed(self, text: str) -> List[float]:
        """Convert text to vector embedding"""
        pass
```
**Purpose:** Defines contract for any embedding provider (MiniLM, OpenAI, Cohere, etc.)

#### `interfaces/vector_store.py`
```python
class IVectorStore(ABC):
    @abstractmethod
    def add(self, records: List[Dict]) -> None:
        """Store embeddings"""
        pass
    
    @abstractmethod
    def search(self, embedding: List[float], top_k: int) -> List[Dict]:
        """Find similar vectors"""
        pass
```
**Purpose:** Defines contract for any vector database (PostgreSQL, Pinecone, Chroma, etc.)

#### `builders/prompt_builder.py`
```python
class PromptBuilder(ABC):
    """Abstract builder for LLM prompts"""
    
class RAGPromptBuilder(PromptBuilder):
    """Concrete builder for RAG-style prompts"""
```
**Purpose:** Flexible prompt construction without hardcoding

---

### Infrastructure Layer (app/infrastructure/)

#### `embedders/minilm_embedder.py`
```python
class MiniLMEmbedder(IEmbedder):
    _instance = None  # Singleton
    
    def embed(self, text: str) -> List[float]:
        return self._model.encode(text).tolist()
```
**Purpose:** Generates 384-dimensional embeddings using local MiniLM model

#### `persistence/postgres_vector_store.py`
```python
class PostgresVectorStore(IVectorStore):
    def add(self, records):
        # INSERT INTO document_chunks ...
        
    def search(self, embedding, top_k):
        # SELECT ... ORDER BY embedding <-> %s LIMIT %s
```
**Purpose:** Stores and retrieves vectors from PostgreSQL + pgvector

#### `document_loaders/loader_factory.py`
```python
class DocumentLoaderFactory:
    _loaders = {'.pdf': PDFLoader}
    
    @classmethod
    def create_loader(cls, filename: str) -> IDocumentLoader:
        ext = Path(filename).suffix.lower()
        return cls._loaders[ext]()
```
**Purpose:** Creates appropriate loader based on file extension

#### `chunkers/fixed_size_chunker.py`
```python
class FixedSizeChunker(IChunker):
    def chunk(self, pages: List[Dict]) -> List[Dict]:
        # Split text into overlapping chunks
```
**Purpose:** Splits documents into manageable pieces for embedding

#### `llm_providers/openrouter_adapter.py`
```python
class OpenRouterAdapter(ILLMProvider):
    def chat(self, messages: List[Dict]) -> str:
        # POST to openrouter.ai/api/v1/chat/completions
```
**Purpose:** Translates our interface to OpenRouter's API format

---

### Application Layer (app/application/)

#### `ingest_service.py`
```python
class IngestService:
    def ingest(self, filename, file_bytes, tag) -> int:
        # Load → Chunk → Embed → Store
```
**Purpose:** Orchestrates document ingestion workflow

#### `retrieval_service.py`
```python
class RetrievalService:
    def retrieve(self, query, top_k, tag) -> List[Dict]:
        # Embed query → Search vector DB
```
**Purpose:** Orchestrates document retrieval workflow

#### `chat_service.py`
```python
class ChatService:
    def chat(self, message, tag) -> Dict:
        # Retrieve context → Build prompt → Generate response
```
**Purpose:** Orchestrates RAG chat workflow with prompt builder

---

### Routes Layer (app/routes/)

#### `ingest.py`, `retrieve.py`, `chat.py`, `health.py`
```python
@router.post("/")
async def endpoint(request):
    result = service.do_something(request.data)
    return {"result": result}
```
**Purpose:** Thin HTTP controllers that delegate to services

---

## 🤔 Why This Architecture?

### 1. **Testability**
```python
# Easy to test with mocks
def test_chat_service():
    mock_llm = Mock(spec=ILLMProvider)
    mock_llm.chat.return_value = "Test response"
    
    service = ChatService(llm_provider=mock_llm)
    result = service.chat("Hello")
    
    assert result["response"] == "Test response"
```

### 2. **Extensibility**
```python
# Adding new embedding provider
class OpenAIEmbedder(IEmbedder):
    def embed(self, text: str) -> List[float]:
        return openai.embeddings.create(input=text).data[0].embedding

# Just swap in configuration - no other changes needed
```

### 3. **Maintainability**
- Bug in PDF loading? → Fix only `pdf_loader.py`
- Change database? → Fix only `postgres_vector_store.py`
- Changes are isolated, don't ripple through codebase

### 4. **Team Scalability**
- Developer A works on new file loaders
- Developer B works on new chunking strategies
- Developer C works on LLM integration
- No conflicts - separate interfaces and implementations

### 5. **Production Readiness**
- Easy to add logging, monitoring, caching at service layer
- Easy to swap local MiniLM for cloud embedding service
- Easy to add new API endpoints using existing services

---

## 📊 Design Patterns Summary

| Pattern | Location | Problem Solved |
|---------|----------|----------------|
| **Singleton** | `MiniLMEmbedder` | Prevent multiple model loads (memory) |
| **Factory Method** | `DocumentLoaderFactory` | Dynamic object creation by type |
| **Strategy** | `IChunker` implementations | Interchangeable algorithms |
| **Repository** | `PostgresVectorStore` | Abstract data access |
| **Adapter** | `OpenRouterAdapter` | Integrate external API |
| **Facade** | Service Layer | Simplify complex subsystems |
| **Builder** | `RAGPromptBuilder` | Flexible object construction |

---

## 🚀 How to Explain to Your Supervisor

### Elevator Pitch (30 seconds):
> "I refactored the RAG application using 7 design patterns and SOLID principles. The code is now organized into layers: domain (interfaces), infrastructure (implementations), application (services), and routes (HTTP). This makes it easy to test, extend, and maintain. For example, we can swap PostgreSQL for Pinecone without changing any business logic."

### Key Points to Mention:
1. **Interfaces** allow swapping implementations (testing, scaling)
2. **Singleton** prevents memory issues with ML models
3. **Factory** makes adding new file types trivial
4. **Strategy** allows different chunking for different documents
5. **Adapter** isolates external API dependencies
6. **Facade** keeps routes thin and business logic centralized
7. **Builder** makes prompts flexible and readable

### Demo Flow:
1. Show project structure - explain layers
2. Show an interface and its implementation
3. Show how service orchestrates multiple patterns
4. Explain how easy it would be to add a new feature

---

*Document created: January 15, 2026*
*Project: RAG FastAPI with Design Patterns*
