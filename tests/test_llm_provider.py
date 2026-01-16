"""
LLM Provider Edge Case Tests

Tests for:
- Missing API key
- API timeout
- Rate limit (429)
- Authentication error (401/403)
- Empty response
- Malformed response
- Connection error
"""
import pytest
from unittest.mock import patch, MagicMock
import requests

from app.core.exceptions import (
    LLMConnectionError,
    LLMRateLimitError,
    LLMAuthenticationError,
    LLMResponseError,
)


class TestOpenRouterAdapter:
    """Test suite for OpenRouter LLM adapter."""
    
    def setup_method(self):
        """Reset singleton before each test."""
        from app.infrastructure.llm_providers.openrouter_adapter import OpenRouterAdapter
        OpenRouterAdapter._instance = None
    
    # ========================================
    # EDGE CASE TESTS
    # ========================================
    
    def test_missing_api_key_raises_error(self):
        """
        Edge Case: No API key configured
        Expected: LLMAuthenticationError
        """
        with patch.dict('os.environ', {}, clear=True):
            with patch('app.infrastructure.llm_providers.openrouter_adapter.os.getenv', return_value=None):
                from app.infrastructure.llm_providers.openrouter_adapter import OpenRouterAdapter
                OpenRouterAdapter._instance = None
                
                adapter = OpenRouterAdapter(api_key=None)
                
                with pytest.raises(LLMAuthenticationError):
                    adapter.chat([{"role": "user", "content": "Hello"}])
    
    def test_api_timeout_raises_error(self):
        """
        Edge Case: API request times out
        Expected: LLMConnectionError
        """
        with patch('app.infrastructure.llm_providers.openrouter_adapter.requests.post') as mock_post:
            mock_post.side_effect = requests.exceptions.Timeout("Connection timed out")
            
            from app.infrastructure.llm_providers.openrouter_adapter import OpenRouterAdapter
            OpenRouterAdapter._instance = None
            
            adapter = OpenRouterAdapter(api_key="test-key")
            
            with pytest.raises(LLMConnectionError):
                adapter.chat([{"role": "user", "content": "Hello"}])
    
    def test_rate_limit_raises_error(self):
        """
        Edge Case: Rate limit exceeded (429)
        Expected: LLMRateLimitError
        """
        with patch('app.infrastructure.llm_providers.openrouter_adapter.requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 429
            mock_post.return_value = mock_response
            
            from app.infrastructure.llm_providers.openrouter_adapter import OpenRouterAdapter
            OpenRouterAdapter._instance = None
            
            adapter = OpenRouterAdapter(api_key="test-key")
            
            with pytest.raises(LLMRateLimitError):
                adapter.chat([{"role": "user", "content": "Hello"}])
    
    def test_auth_error_401_raises_error(self):
        """
        Edge Case: Invalid API key (401)
        Expected: LLMAuthenticationError
        """
        with patch('app.infrastructure.llm_providers.openrouter_adapter.requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_post.return_value = mock_response
            
            from app.infrastructure.llm_providers.openrouter_adapter import OpenRouterAdapter
            OpenRouterAdapter._instance = None
            
            adapter = OpenRouterAdapter(api_key="invalid-key")
            
            with pytest.raises(LLMAuthenticationError):
                adapter.chat([{"role": "user", "content": "Hello"}])
    
    def test_auth_error_403_raises_error(self):
        """
        Edge Case: Forbidden (403)
        Expected: LLMAuthenticationError
        """
        with patch('app.infrastructure.llm_providers.openrouter_adapter.requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 403
            mock_post.return_value = mock_response
            
            from app.infrastructure.llm_providers.openrouter_adapter import OpenRouterAdapter
            OpenRouterAdapter._instance = None
            
            adapter = OpenRouterAdapter(api_key="test-key")
            
            with pytest.raises(LLMAuthenticationError):
                adapter.chat([{"role": "user", "content": "Hello"}])
    
    def test_empty_choices_raises_error(self):
        """
        Edge Case: Response has no choices
        Expected: LLMResponseError
        """
        with patch('app.infrastructure.llm_providers.openrouter_adapter.requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.raise_for_status = MagicMock()
            mock_response.json.return_value = {"choices": []}
            mock_post.return_value = mock_response
            
            from app.infrastructure.llm_providers.openrouter_adapter import OpenRouterAdapter
            OpenRouterAdapter._instance = None
            
            adapter = OpenRouterAdapter(api_key="test-key")
            
            with pytest.raises(LLMResponseError):
                adapter.chat([{"role": "user", "content": "Hello"}])
    
    def test_empty_content_raises_error(self):
        """
        Edge Case: Response content is empty
        Expected: LLMResponseError
        """
        with patch('app.infrastructure.llm_providers.openrouter_adapter.requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.raise_for_status = MagicMock()
            mock_response.json.return_value = {
                "choices": [{"message": {"content": ""}}]
            }
            mock_post.return_value = mock_response
            
            from app.infrastructure.llm_providers.openrouter_adapter import OpenRouterAdapter
            OpenRouterAdapter._instance = None
            
            adapter = OpenRouterAdapter(api_key="test-key")
            
            with pytest.raises(LLMResponseError):
                adapter.chat([{"role": "user", "content": "Hello"}])
    
    def test_connection_error_raises_error(self):
        """
        Edge Case: Network connection fails
        Expected: LLMConnectionError
        """
        with patch('app.infrastructure.llm_providers.openrouter_adapter.requests.post') as mock_post:
            mock_post.side_effect = requests.exceptions.ConnectionError("Network unreachable")
            
            from app.infrastructure.llm_providers.openrouter_adapter import OpenRouterAdapter
            OpenRouterAdapter._instance = None
            
            adapter = OpenRouterAdapter(api_key="test-key")
            
            with pytest.raises(LLMConnectionError):
                adapter.chat([{"role": "user", "content": "Hello"}])
    
    # ========================================
    # HAPPY PATH TESTS
    # ========================================
    
    def test_successful_chat_returns_response(self):
        """
        Happy Path: Successful API call returns response
        """
        with patch('app.infrastructure.llm_providers.openrouter_adapter.requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.raise_for_status = MagicMock()
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "Hello, how can I help?"}}]
            }
            mock_post.return_value = mock_response
            
            from app.infrastructure.llm_providers.openrouter_adapter import OpenRouterAdapter
            OpenRouterAdapter._instance = None
            
            adapter = OpenRouterAdapter(api_key="test-key")
            response = adapter.chat([{"role": "user", "content": "Hello"}])
            
            assert response == "Hello, how can I help?"
    
    def test_generate_calls_chat(self):
        """
        Happy Path: generate() method uses chat() internally
        """
        with patch('app.infrastructure.llm_providers.openrouter_adapter.requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.raise_for_status = MagicMock()
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "Generated response"}}]
            }
            mock_post.return_value = mock_response
            
            from app.infrastructure.llm_providers.openrouter_adapter import OpenRouterAdapter
            OpenRouterAdapter._instance = None
            
            adapter = OpenRouterAdapter(api_key="test-key")
            response = adapter.generate("Hello")
            
            assert response == "Generated response"
    
    def test_model_name_property(self):
        """
        Test model_name property returns correct value
        """
        from app.infrastructure.llm_providers.openrouter_adapter import OpenRouterAdapter
        OpenRouterAdapter._instance = None
        
        adapter = OpenRouterAdapter(api_key="test-key", model="custom-model")
        
        assert adapter.model_name == "custom-model"
