"""
Custom Exceptions for RAG FastAPI Application

Purpose: Define specific exception types for each component.
This allows us to:
1. Catch specific errors (not just generic Exception)
2. Return appropriate HTTP status codes
3. Give user-friendly error messages

Exception Hierarchy:
    RAGBaseException (base for all our exceptions)
    ├── DocumentProcessingError (PDF loading issues)
    ├── ChunkingError (text chunking issues)
    ├── EmbeddingError (embedding generation issues)
    ├── VectorStoreError (database issues)
    ├── LLMProviderError (OpenRouter API issues)
    └── ValidationError (input validation issues)
"""
from typing import Optional


class RAGBaseException(Exception):
    """
    Base exception for all RAG application errors.
    
    All custom exceptions inherit from this, making it easy to:
    - Catch ALL our custom exceptions with one handler
    - Add common functionality (like logging)
    """
    
    def __init__(self, message: str, details: Optional[str] = None):
        self.message = message
        self.details = details  # Technical details for logging
        super().__init__(self.message)


# ============================================================
# DOCUMENT PROCESSING EXCEPTIONS
# ============================================================

class DocumentProcessingError(RAGBaseException):
    """
    Raised when document loading fails.
    
    Edge cases this handles:
    - Empty PDF
    - Corrupted PDF
    - Password-protected PDF
    - Image-only PDF (no extractable text)
    - Unsupported file format
    """
    pass


class EmptyDocumentError(DocumentProcessingError):
    """Raised when document has no extractable text."""
    
    def __init__(self, filename: str):
        super().__init__(
            message=f"The document '{filename}' contains no extractable text.",
            details=f"Empty or image-only document: {filename}"
        )


class CorruptedDocumentError(DocumentProcessingError):
    """Raised when document is corrupted or unreadable."""
    
    def __init__(self, filename: str, original_error: Optional[str] = None):
        super().__init__(
            message=f"The document '{filename}' appears to be corrupted or unreadable.",
            details=f"Corrupted document: {filename}. Error: {original_error}"
        )


class UnsupportedDocumentError(DocumentProcessingError):
    """Raised when document type is not supported."""
    
    def __init__(self, filename: str, supported_types: list):
        super().__init__(
            message=f"File type not supported. Supported types: {', '.join(supported_types)}",
            details=f"Unsupported document: {filename}"
        )


# ============================================================
# CHUNKING EXCEPTIONS
# ============================================================

class ChunkingError(RAGBaseException):
    """
    Raised when text chunking fails.
    
    Edge cases this handles:
    - Empty text
    - Text with only whitespace
    - Extremely long text that causes memory issues
    """
    pass


class EmptyTextError(ChunkingError):
    """Raised when text to chunk is empty or whitespace only."""
    
    def __init__(self):
        super().__init__(
            message="Cannot process empty or whitespace-only text.",
            details="Empty text provided for chunking"
        )


# ============================================================
# EMBEDDING EXCEPTIONS
# ============================================================

class EmbeddingError(RAGBaseException):
    """
    Raised when embedding generation fails.
    
    Edge cases this handles:
    - Model not loaded
    - Text too long for model
    - Memory issues
    - Invalid input
    """
    pass


class EmbeddingModelError(EmbeddingError):
    """Raised when embedding model fails to load or process."""
    
    def __init__(self, original_error: Optional[str] = None):
        super().__init__(
            message="Embedding service is temporarily unavailable.",
            details=f"Embedding model error: {original_error}"
        )


# ============================================================
# VECTOR STORE / DATABASE EXCEPTIONS
# ============================================================

class VectorStoreError(RAGBaseException):
    """
    Raised when vector store operations fail.
    
    Edge cases this handles:
    - Database connection failed
    - Connection timeout
    - Table doesn't exist
    - Query execution failed
    """
    pass


class DatabaseConnectionError(VectorStoreError):
    """Raised when database connection fails."""
    
    def __init__(self, original_error: Optional[str] = None):
        super().__init__(
            message="Database is temporarily unavailable. Please try again later.",
            details=f"Database connection error: {original_error}"
        )


class DatabaseQueryError(VectorStoreError):
    """Raised when database query fails."""
    
    def __init__(self, operation: str, original_error: Optional[str] = None):
        super().__init__(
            message=f"Failed to {operation}. Please try again.",
            details=f"Database query error during {operation}: {original_error}"
        )


# ============================================================
# LLM PROVIDER EXCEPTIONS
# ============================================================

class LLMProviderError(RAGBaseException):
    """
    Raised when LLM API calls fail.
    
    Edge cases this handles:
    - API timeout
    - Rate limit exceeded
    - Invalid API key
    - Empty response
    - Malformed response
    """
    pass


class LLMConnectionError(LLMProviderError):
    """Raised when LLM API is unreachable."""
    
    def __init__(self, original_error: Optional[str] = None):
        super().__init__(
            message="AI service is temporarily unavailable. Please try again later.",
            details=f"LLM connection error: {original_error}"
        )


class LLMRateLimitError(LLMProviderError):
    """Raised when API rate limit is exceeded."""
    
    def __init__(self):
        super().__init__(
            message="Service is busy. Please wait a moment and try again.",
            details="LLM API rate limit exceeded"
        )


class LLMAuthenticationError(LLMProviderError):
    """Raised when API key is invalid."""
    
    def __init__(self):
        super().__init__(
            message="AI service configuration error. Please contact support.",
            details="Invalid or missing LLM API key"
        )


class LLMResponseError(LLMProviderError):
    """Raised when LLM returns empty or invalid response."""
    
    def __init__(self, original_error: Optional[str] = None):
        super().__init__(
            message="AI service returned an invalid response. Please try again.",
            details=f"LLM response error: {original_error}"
        )


# ============================================================
# INPUT VALIDATION EXCEPTIONS
# ============================================================

class ValidationError(RAGBaseException):
    """
    Raised when input validation fails.
    
    Edge cases this handles:
    - Empty query
    - Query too long
    - Invalid characters
    - Missing required fields
    """
    pass


class EmptyQueryError(ValidationError):
    """Raised when search/chat query is empty."""
    
    def __init__(self):
        super().__init__(
            message="Please enter a question or search query.",
            details="Empty query provided"
        )


class QueryTooLongError(ValidationError):
    """Raised when query exceeds maximum length."""
    
    def __init__(self, max_length: int):
        super().__init__(
            message=f"Query is too long. Maximum {max_length} characters allowed.",
            details=f"Query exceeded max length of {max_length}"
        )


# ============================================================
# RETRIEVAL EXCEPTIONS
# ============================================================

class RetrievalError(RAGBaseException):
    """Raised when document retrieval fails."""
    pass


class NoDocumentsFoundError(RetrievalError):
    """Raised when no relevant documents are found."""
    
    def __init__(self, query: str):
        super().__init__(
            message="No relevant documents found for your query. Try rephrasing or upload relevant documents first.",
            details=f"No documents found for query: {query[:100]}..."
        )
