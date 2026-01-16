"""Interface for document loaders - Factory Pattern"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class IDocumentLoader(ABC):
    """
    Abstract interface for document loading.
    
    Implements: Factory Method Pattern
    Enables: Add new document types (PDF, DOCX, TXT) without modifying existing code
    """
    
    @abstractmethod
    def load(self, file_bytes: bytes, filename: Optional[str] = None) -> List[Dict]:
        """
        Load document and extract text by pages.
        
        Args:
            file_bytes: Raw bytes of the document
            filename: Original filename (for error messages)
            
        Returns:
            List of dicts containing:
                - page: Page number (1-indexed)
                - text: Extracted text content
                
        Raises:
            EmptyDocumentError: If document has no extractable text
            CorruptedDocumentError: If document is corrupted
        """
        pass
    
    @property
    @abstractmethod
    def supported_extensions(self) -> List[str]:
        """Return list of supported file extensions (e.g., ['.pdf'])"""
        pass
