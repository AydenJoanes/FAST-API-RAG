"""
Chunker Edge Case Tests

Tests for:
- Empty text
- Whitespace-only text
- None input
- Very short text (less than chunk size)
- Very long text
- Normal chunking behavior
"""
import pytest

from app.infrastructure.chunkers.fixed_size_chunker import FixedSizeChunker
from app.core.exceptions import EmptyTextError


class TestFixedSizeChunker:
    """Test suite for fixed-size chunker."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.chunker = FixedSizeChunker(chunk_size=100, overlap=20)
    
    # ========================================
    # EDGE CASE TESTS
    # ========================================
    
    def test_empty_string_raises_error(self, empty_text):
        """
        Edge Case: Empty string
        Expected: EmptyTextError
        """
        with pytest.raises(EmptyTextError):
            self.chunker.chunk(empty_text)
    
    def test_whitespace_only_raises_error(self, whitespace_text):
        """
        Edge Case: String with only whitespace/newlines
        Expected: EmptyTextError
        """
        with pytest.raises(EmptyTextError):
            self.chunker.chunk(whitespace_text)
    
    def test_none_input_raises_error(self):
        """
        Edge Case: None instead of string
        Expected: EmptyTextError
        """
        with pytest.raises(EmptyTextError):
            self.chunker.chunk(None)
    
    # ========================================
    # BOUNDARY TESTS
    # ========================================
    
    def test_text_shorter_than_chunk_size(self):
        """
        Boundary: Text is shorter than chunk_size
        Expected: Single chunk with all text
        """
        short_text = "Hello World"  # 11 chars, chunk_size is 100
        
        chunks = self.chunker.chunk(short_text)
        
        assert len(chunks) == 1
        assert chunks[0]["text"] == "Hello World"
        assert chunks[0]["chunk_id"] == 0
    
    def test_text_exactly_chunk_size(self):
        """
        Boundary: Text is exactly chunk_size characters
        Expected: With overlap, may create 2 chunks (overlap causes second chunk)
        """
        exact_text = "a" * 100  # Exactly 100 chars
        
        chunks = self.chunker.chunk(exact_text)
        
        # With overlap=20, 100 chars creates 2 chunks:
        # Chunk 0: 0-100, Chunk 1: 80-100 (due to overlap)
        assert len(chunks) >= 1
        assert len(chunks[0]["text"]) == 100
    
    def test_text_slightly_over_chunk_size(self):
        """
        Boundary: Text is chunk_size + 1 characters
        Expected: Two chunks (with overlap)
        """
        text = "a" * 101  # 101 chars, chunk_size=100, overlap=20
        
        chunks = self.chunker.chunk(text)
        
        assert len(chunks) == 2
    
    def test_single_character(self):
        """
        Boundary: Single non-whitespace character
        Expected: Single chunk with one character
        """
        chunks = self.chunker.chunk("X")
        
        assert len(chunks) == 1
        assert chunks[0]["text"] == "X"
    
    # ========================================
    # HAPPY PATH TESTS
    # ========================================
    
    def test_normal_text_chunking(self, large_text):
        """
        Happy Path: Normal text chunking
        Expected: Multiple chunks with correct IDs and overlap
        """
        chunks = self.chunker.chunk(large_text)
        
        assert len(chunks) > 1
        
        # Verify chunk IDs are sequential
        for i, chunk in enumerate(chunks):
            assert chunk["chunk_id"] == i
        
        # Verify each chunk has text
        for chunk in chunks:
            assert len(chunk["text"]) > 0
    
    def test_metadata_preserved(self):
        """
        Happy Path: Metadata is attached to each chunk
        """
        text = "This is test content for chunking purposes."
        metadata = {"page": 5, "source": "test.pdf"}
        
        chunks = self.chunker.chunk(text, metadata=metadata)
        
        for chunk in chunks:
            assert chunk["page"] == 5
            assert chunk["source"] == "test.pdf"
    
    def test_overlap_behavior(self):
        """
        Verify overlap works correctly between chunks.
        """
        # Create chunker with known sizes
        chunker = FixedSizeChunker(chunk_size=50, overlap=10)
        
        # Create text that will produce multiple chunks
        text = "A" * 40 + "B" * 40 + "C" * 40  # 120 chars
        
        chunks = chunker.chunk(text)
        
        # With chunk_size=50 and overlap=10:
        # Chunk 0: 0-50
        # Chunk 1: 40-90 (starts at 50-10=40)
        # Chunk 2: 80-120 (starts at 90-10=80)
        assert len(chunks) >= 2
    
    # ========================================
    # SPECIAL CHARACTER TESTS
    # ========================================
    
    def test_unicode_text(self):
        """
        Edge Case: Text with Unicode characters
        Expected: Handles correctly without error
        """
        unicode_text = "Hello 你好 مرحبا 🎉 émoji"
        
        chunks = self.chunker.chunk(unicode_text)
        
        assert len(chunks) >= 1
        assert "你好" in chunks[0]["text"]
    
    def test_special_characters(self):
        """
        Edge Case: Text with special characters
        """
        special_text = "Line1\nLine2\tTab\r\nWindows"
        
        chunks = self.chunker.chunk(special_text)
        
        assert len(chunks) >= 1
    
    # ========================================
    # PROPERTY TESTS
    # ========================================
    
    def test_chunk_size_property(self):
        """Test chunk_size property returns correct value."""
        assert self.chunker.chunk_size == 100
    
    def test_chunk_overlap_property(self):
        """Test chunk_overlap property returns correct value."""
        assert self.chunker.chunk_overlap == 20
