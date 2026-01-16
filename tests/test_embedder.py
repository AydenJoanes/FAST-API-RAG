"""
Embedder Edge Case Tests

Tests for:
- Empty text
- None input
- Model loading failure
- Batch embedding with empty list
- Normal embedding behavior
"""
import pytest
from unittest.mock import patch, MagicMock

from app.core.exceptions import EmbeddingError, EmbeddingModelError


class TestMiniLMEmbedder:
    """Test suite for MiniLM embedder."""
    
    # ========================================
    # EDGE CASE TESTS
    # ========================================
    
    def test_empty_string_raises_error(self):
        """
        Edge Case: Empty string
        Expected: EmbeddingError
        """
        with patch('app.infrastructure.embedders.minilm_embedder.SentenceTransformer'):
            from app.infrastructure.embedders.minilm_embedder import MiniLMEmbedder
            
            # Reset singleton for testing
            MiniLMEmbedder._instance = None
            MiniLMEmbedder._initialized = False
            
            embedder = MiniLMEmbedder()
            
            with pytest.raises(EmbeddingError):
                embedder.embed_text("")
    
    def test_whitespace_only_raises_error(self):
        """
        Edge Case: Whitespace-only string
        Expected: EmbeddingError
        """
        with patch('app.infrastructure.embedders.minilm_embedder.SentenceTransformer'):
            from app.infrastructure.embedders.minilm_embedder import MiniLMEmbedder
            
            MiniLMEmbedder._instance = None
            MiniLMEmbedder._initialized = False
            
            embedder = MiniLMEmbedder()
            
            with pytest.raises(EmbeddingError):
                embedder.embed_text("   \n\t  ")
    
    def test_none_input_raises_error(self):
        """
        Edge Case: None input
        Expected: EmbeddingError
        """
        with patch('app.infrastructure.embedders.minilm_embedder.SentenceTransformer'):
            from app.infrastructure.embedders.minilm_embedder import MiniLMEmbedder
            
            MiniLMEmbedder._instance = None
            MiniLMEmbedder._initialized = False
            
            embedder = MiniLMEmbedder()
            
            with pytest.raises(EmbeddingError):
                embedder.embed_text(None)
    
    def test_empty_list_raises_error(self):
        """
        Edge Case: Empty list for batch embedding
        Expected: EmbeddingError
        """
        with patch('app.infrastructure.embedders.minilm_embedder.SentenceTransformer'):
            from app.infrastructure.embedders.minilm_embedder import MiniLMEmbedder
            
            MiniLMEmbedder._instance = None
            MiniLMEmbedder._initialized = False
            
            embedder = MiniLMEmbedder()
            
            with pytest.raises(EmbeddingError):
                embedder.embed_texts([])
    
    def test_list_of_empty_strings_raises_error(self):
        """
        Edge Case: List with only empty strings
        Expected: EmbeddingError
        """
        with patch('app.infrastructure.embedders.minilm_embedder.SentenceTransformer'):
            from app.infrastructure.embedders.minilm_embedder import MiniLMEmbedder
            
            MiniLMEmbedder._instance = None
            MiniLMEmbedder._initialized = False
            
            embedder = MiniLMEmbedder()
            
            with pytest.raises(EmbeddingError):
                embedder.embed_texts(["", "   ", "\n"])
    
    def test_model_loading_failure(self):
        """
        Edge Case: Model fails to load
        Expected: EmbeddingModelError
        """
        with patch('app.infrastructure.embedders.minilm_embedder.SentenceTransformer') as mock_st:
            mock_st.side_effect = Exception("Model download failed")
            
            from app.infrastructure.embedders.minilm_embedder import MiniLMEmbedder
            
            MiniLMEmbedder._instance = None
            MiniLMEmbedder._initialized = False
            
            with pytest.raises(EmbeddingModelError):
                MiniLMEmbedder()
    
    # ========================================
    # HAPPY PATH TESTS (with mocked model)
    # ========================================
    
    def test_valid_text_returns_embedding(self):
        """
        Happy Path: Valid text returns 384-dim embedding
        """
        import numpy as np
        
        with patch('app.infrastructure.embedders.minilm_embedder.SentenceTransformer') as mock_st:
            mock_model = MagicMock()
            mock_model.encode.return_value = np.array([0.1] * 384)
            mock_st.return_value = mock_model
            
            from app.infrastructure.embedders.minilm_embedder import MiniLMEmbedder
            
            MiniLMEmbedder._instance = None
            MiniLMEmbedder._initialized = False
            
            embedder = MiniLMEmbedder()
            embedding = embedder.embed_text("Hello world")
            
            assert len(embedding) == 384
            assert isinstance(embedding, list)
    
    def test_batch_embedding_returns_list(self):
        """
        Happy Path: Batch embedding returns list of vectors
        """
        import numpy as np
        
        with patch('app.infrastructure.embedders.minilm_embedder.SentenceTransformer') as mock_st:
            mock_model = MagicMock()
            mock_model.encode.return_value = np.array([[0.1] * 384, [0.2] * 384])
            mock_st.return_value = mock_model
            
            from app.infrastructure.embedders.minilm_embedder import MiniLMEmbedder
            
            MiniLMEmbedder._instance = None
            MiniLMEmbedder._initialized = False
            
            embedder = MiniLMEmbedder()
            embeddings = embedder.embed_texts(["Hello", "World"])
            
            assert len(embeddings) == 2
            assert len(embeddings[0]) == 384
    
    def test_dimension_property(self):
        """
        Test dimension property returns 384
        """
        with patch('app.infrastructure.embedders.minilm_embedder.SentenceTransformer'):
            from app.infrastructure.embedders.minilm_embedder import MiniLMEmbedder
            
            MiniLMEmbedder._instance = None
            MiniLMEmbedder._initialized = False
            
            embedder = MiniLMEmbedder()
            
            assert embedder.dimension == 384
    
    # ========================================
    # SINGLETON TESTS
    # ========================================
    
    def test_singleton_returns_same_instance(self):
        """
        Test that singleton pattern works correctly
        """
        with patch('app.infrastructure.embedders.minilm_embedder.SentenceTransformer'):
            from app.infrastructure.embedders.minilm_embedder import MiniLMEmbedder
            
            MiniLMEmbedder._instance = None
            MiniLMEmbedder._initialized = False
            
            embedder1 = MiniLMEmbedder()
            embedder2 = MiniLMEmbedder()
            
            assert embedder1 is embedder2
