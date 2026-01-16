"""
PDF Document Loader - Implements IDocumentLoader Interface

This loader extracts text from PDF files page by page.
Follows the Factory Method pattern - this is a "product" that
the factory creates.

Design Pattern: Factory Method (Product)
SOLID Principle: 
    - Single Responsibility (only handles PDF loading)
    - Liskov Substitution (can replace any IDocumentLoader)

Exception Handling:
    - Empty PDF → EmptyDocumentError
    - Corrupted PDF → CorruptedDocumentError
    - Password-protected → CorruptedDocumentError (with message)
"""
from io import BytesIO
from typing import List, Dict
from pypdf import PdfReader
from pypdf.errors import PdfReadError

from app.domain.interfaces.document_loader import IDocumentLoader
from app.core.logging import logger
from app.core.exceptions import EmptyDocumentError, CorruptedDocumentError


class PDFLoader(IDocumentLoader):
    """
    PDF document loader using pypdf.
    
    Extracts text from PDF files, returning page-by-page content.
    Handles edge cases: empty PDFs, corrupted files, password-protected PDFs.
    """
    
    def load(self, file_bytes: bytes, filename: str = "document.pdf") -> List[Dict]:
        """
        Load PDF and extract text by pages.
        
        Args:
            file_bytes: Raw bytes of the PDF file
            filename: Original filename for error messages
            
        Returns:
            List of dicts with page number and text content
            
        Raises:
            EmptyDocumentError: If PDF has no extractable text
            CorruptedDocumentError: If PDF is corrupted or password-protected
        """
        logger.debug(f"Loading PDF document: {filename}")
        
        # Edge case: Empty file
        if not file_bytes or len(file_bytes) == 0:
            logger.warning(f"Empty file received: {filename}")
            raise EmptyDocumentError(filename)
        
        try:
            # Load PDF from memory
            pdf_stream = BytesIO(file_bytes)
            reader = PdfReader(pdf_stream)
            
            # Edge case: Password-protected PDF
            if reader.is_encrypted:
                logger.warning(f"Password-protected PDF: {filename}")
                raise CorruptedDocumentError(
                    filename, 
                    "PDF is password-protected. Please provide an unprotected PDF."
                )
            
            pages = []
            
            # Extract text page by page
            for idx, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        pages.append({
                            "page": idx + 1,  # 1-indexed page number
                            "text": page_text.strip()
                        })
                except Exception as e:
                    # Log but continue - some pages might be image-only
                    logger.warning(f"Could not extract text from page {idx + 1}: {e}")
                    continue
            
            # Edge case: No text extracted (image-only PDF)
            if not pages:
                logger.warning(f"No text extracted from PDF: {filename}")
                raise EmptyDocumentError(filename)
            
            logger.info(f"Extracted {len(pages)} pages from PDF: {filename}")
            return pages
            
        except EmptyDocumentError:
            # Re-raise our custom exceptions
            raise
        except CorruptedDocumentError:
            raise
        except PdfReadError as e:
            # Corrupted or malformed PDF
            logger.error(f"PDF read error for {filename}: {e}")
            raise CorruptedDocumentError(filename, str(e))
        except Exception as e:
            # Unexpected error
            logger.error(f"Unexpected error loading PDF {filename}: {e}")
            raise CorruptedDocumentError(filename, str(e))
    
    @property
    def supported_extensions(self) -> List[str]:
        """Return supported file extensions"""
        return [".pdf"]
