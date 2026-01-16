"""
Pytest Configuration and Fixtures

This file contains shared fixtures used across all test files.
Fixtures provide reusable test data and mock objects.
"""
import pytest
from io import BytesIO
from unittest.mock import MagicMock, patch


# ============================================================
# PDF TEST FIXTURES
# ============================================================

@pytest.fixture
def valid_pdf_bytes():
    """
    Create minimal valid PDF bytes for testing.
    This is a simplified PDF structure.
    """
    # Minimal PDF with text "Hello World"
    pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]
   /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>
endobj
4 0 obj
<< /Length 44 >>
stream
BT /F1 12 Tf 100 700 Td (Hello World) Tj ET
endstream
endobj
5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000266 00000 n 
0000000359 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
434
%%EOF"""
    return pdf_content


@pytest.fixture
def empty_bytes():
    """Empty file bytes for edge case testing."""
    return b""


@pytest.fixture
def non_pdf_bytes():
    """Non-PDF file disguised as PDF."""
    return b"This is not a PDF file content"


@pytest.fixture
def large_text():
    """Large text for chunking tests."""
    return "Lorem ipsum dolor sit amet. " * 1000  # ~30,000 characters


@pytest.fixture
def empty_text():
    """Empty text for edge case testing."""
    return ""


@pytest.fixture
def whitespace_text():
    """Whitespace-only text for edge case testing."""
    return "   \n\t\n   "


# ============================================================
# MOCK FIXTURES
# ============================================================

@pytest.fixture
def mock_embedder():
    """Mock embedder that returns fake 384-dim vectors."""
    mock = MagicMock()
    mock.embed_text.return_value = [0.1] * 384
    mock.embed_texts.return_value = [[0.1] * 384]
    mock.dimension = 384
    return mock


@pytest.fixture
def mock_vector_store():
    """Mock vector store for testing without database."""
    mock = MagicMock()
    mock.add.return_value = None
    mock.search.return_value = [
        {"content": "Test content", "tag": "test", "page": 1, "chunk_id": 0}
    ]
    mock.delete_by_tag.return_value = 5
    return mock


@pytest.fixture
def mock_llm_provider():
    """Mock LLM provider for testing without API calls."""
    mock = MagicMock()
    mock.generate.return_value = "This is a mock LLM response."
    mock.chat.return_value = "This is a mock chat response."
    mock.generate_with_context.return_value = "This is a mock context response."
    mock.model_name = "mock-model"
    return mock


# ============================================================
# DATABASE FIXTURES (for integration tests)
# ============================================================

@pytest.fixture
def mock_db_connection():
    """Mock database connection."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = []
    mock_cursor.rowcount = 0
    return mock_conn
