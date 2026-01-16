"""
PDF Loader Edge Case Tests

Tests for:
- Empty file
- Corrupted file
- Non-PDF with .pdf extension
- Valid PDF processing
"""
import pytest
from unittest.mock import patch, MagicMock
from pypdf.errors import PdfReadError

from app.infrastructure.document_loaders.pdf_loader import PDFLoader
from app.core.exceptions import EmptyDocumentError, CorruptedDocumentError


class TestPDFLoader:
    """Test suite for PDF document loader."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.loader = PDFLoader()
    
    # ========================================
    # EDGE CASE TESTS
    # ========================================
    
    def test_empty_file_raises_error(self, empty_bytes):
        """
        Edge Case: Empty file (0 bytes)
        Expected: EmptyDocumentError
        """
        with pytest.raises(EmptyDocumentError) as exc_info:
            self.loader.load(empty_bytes, filename="empty.pdf")
        
        assert "empty.pdf" in str(exc_info.value.message)
    
    def test_none_bytes_raises_error(self):
        """
        Edge Case: None instead of bytes
        Expected: EmptyDocumentError
        """
        with pytest.raises(EmptyDocumentError):
            self.loader.load(None, filename="none.pdf")
    
    def test_non_pdf_content_raises_error(self, non_pdf_bytes):
        """
        Edge Case: Non-PDF file content (text file renamed to .pdf)
        Expected: CorruptedDocumentError
        """
        with pytest.raises(CorruptedDocumentError) as exc_info:
            self.loader.load(non_pdf_bytes, filename="fake.pdf")
        
        assert "corrupted" in str(exc_info.value.message).lower()
    
    def test_password_protected_pdf(self):
        """
        Edge Case: Password-protected PDF
        Expected: CorruptedDocumentError with password message
        
        Note: This test mocks the PdfReader behavior
        """
        with patch('app.infrastructure.document_loaders.pdf_loader.PdfReader') as mock_reader:
            mock_instance = MagicMock()
            mock_instance.is_encrypted = True
            mock_reader.return_value = mock_instance
            
            with pytest.raises(CorruptedDocumentError) as exc_info:
                self.loader.load(b"fake pdf content", filename="protected.pdf")
            
            assert "password" in str(exc_info.value.details).lower()
    
    def test_image_only_pdf_raises_error(self):
        """
        Edge Case: PDF with only images (no extractable text)
        Expected: EmptyDocumentError
        
        Note: This test mocks pages with no text
        """
        with patch('app.infrastructure.document_loaders.pdf_loader.PdfReader') as mock_reader:
            mock_instance = MagicMock()
            mock_instance.is_encrypted = False
            
            # Create mock page that returns empty text
            mock_page = MagicMock()
            mock_page.extract_text.return_value = ""
            mock_instance.pages = [mock_page]
            
            mock_reader.return_value = mock_instance
            
            with pytest.raises(EmptyDocumentError):
                self.loader.load(b"fake pdf content", filename="image_only.pdf")
    
    def test_corrupted_pdf_structure(self):
        """
        Edge Case: PDF with corrupted internal structure
        Expected: CorruptedDocumentError
        """
        with patch('app.infrastructure.document_loaders.pdf_loader.PdfReader') as mock_reader:
            mock_reader.side_effect = PdfReadError("Invalid PDF structure")
            
            with pytest.raises(CorruptedDocumentError):
                self.loader.load(b"corrupted content", filename="corrupted.pdf")
    
    # ========================================
    # HAPPY PATH TESTS
    # ========================================
    
    def test_valid_pdf_returns_pages(self):
        """
        Happy Path: Valid PDF with extractable text
        Expected: List of page dicts with text
        """
        with patch('app.infrastructure.document_loaders.pdf_loader.PdfReader') as mock_reader:
            mock_instance = MagicMock()
            mock_instance.is_encrypted = False
            
            # Create mock pages with text
            mock_page1 = MagicMock()
            mock_page1.extract_text.return_value = "Page 1 content"
            mock_page2 = MagicMock()
            mock_page2.extract_text.return_value = "Page 2 content"
            mock_instance.pages = [mock_page1, mock_page2]
            
            mock_reader.return_value = mock_instance
            
            pages = self.loader.load(b"valid pdf content", filename="valid.pdf")
            
            assert len(pages) == 2
            assert pages[0]["page"] == 1
            assert pages[0]["text"] == "Page 1 content"
            assert pages[1]["page"] == 2
    
    def test_supported_extensions(self):
        """Test that PDF extension is supported."""
        assert ".pdf" in self.loader.supported_extensions
    
    # ========================================
    # BOUNDARY TESTS
    # ========================================
    
    def test_single_page_pdf(self):
        """
        Boundary: PDF with exactly 1 page
        """
        with patch('app.infrastructure.document_loaders.pdf_loader.PdfReader') as mock_reader:
            mock_instance = MagicMock()
            mock_instance.is_encrypted = False
            
            mock_page = MagicMock()
            mock_page.extract_text.return_value = "Single page content"
            mock_instance.pages = [mock_page]
            
            mock_reader.return_value = mock_instance
            
            pages = self.loader.load(b"single page pdf", filename="single.pdf")
            
            assert len(pages) == 1
    
    def test_page_with_only_whitespace_skipped(self):
        """
        Edge Case: Page with only whitespace is skipped
        """
        with patch('app.infrastructure.document_loaders.pdf_loader.PdfReader') as mock_reader:
            mock_instance = MagicMock()
            mock_instance.is_encrypted = False
            
            # Page 1 has content, Page 2 has only whitespace
            mock_page1 = MagicMock()
            mock_page1.extract_text.return_value = "Real content"
            mock_page2 = MagicMock()
            mock_page2.extract_text.return_value = "   \n\t  "
            mock_instance.pages = [mock_page1, mock_page2]
            
            mock_reader.return_value = mock_instance
            
            pages = self.loader.load(b"mixed pdf", filename="mixed.pdf")
            
            # Only page 1 should be included
            assert len(pages) == 1
            assert pages[0]["text"] == "Real content"
