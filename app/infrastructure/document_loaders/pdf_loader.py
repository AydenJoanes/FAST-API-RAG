"""
PDF Document Loader - Implements IDocumentLoader Interface

This loader extracts text from PDF files page by page.
Follows the Factory Method pattern - this is a "product" that
the factory creates.

Design Pattern: Factory Method (Product)
SOLID Principle: 
    - Single Responsibility (only handles PDF loading)
    - Liskov Substitution (can replace any IDocumentLoader)
"""
from io import BytesIO
from typing import List, Dict
from pypdf import PdfReader

from app.domain.interfaces.document_loader import IDocumentLoader
from app.core.logging import logger


class PDFLoader(IDocumentLoader):
    """
    PDF document loader using pypdf.
    
    Extracts text from PDF files, returning page-by-page content.
    """
    
    def load(self, file_bytes: bytes) -> List[Dict]:
        """
        Load PDF and extract text by pages.
        
        Args:
            file_bytes: Raw bytes of the PDF file
            
        Returns:
            List of dicts with page number and text content
        """
        logger.debug("Loading PDF document...")
        
        # Load PDF from memory
        pdf_stream = BytesIO(file_bytes)
        reader = PdfReader(pdf_stream)
        
        pages = []
        
        # Extract text page by page
        for idx, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                pages.append({
                    "page": idx + 1,  # 1-indexed page number
                    "text": page_text.strip()
                })
        
        logger.info(f"Extracted {len(pages)} pages from PDF")
        return pages
    
    @property
    def supported_extensions(self) -> List[str]:
        """Return supported file extensions"""
        return [".pdf"]
