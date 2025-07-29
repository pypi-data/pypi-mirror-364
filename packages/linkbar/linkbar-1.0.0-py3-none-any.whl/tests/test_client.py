"""
Tests for the module-level client functionality
"""

import pytest
import requests
from unittest.mock import patch, Mock
import linkbar


class TestModuleLevelClient:
    
    def setup_method(self):
        """Reset module state before each test"""
        linkbar.api_key = None
        linkbar.base_url = "https://api.linkbar.co/"
    
    def test_api_key_configuration(self):
        """Test setting and getting API key"""
        linkbar.api_key = "test_key_123"
        assert linkbar.api_key == "test_key_123"
    
    def test_base_url_configuration(self):
        """Test setting and getting base URL"""
        linkbar.base_url = "https://api.example.com/"
        assert linkbar.base_url == "https://api.example.com/"
    
    @patch('linkbar.requests.request')
    def test_successful_request(self, mock_request):
        """Test successful API request"""
        # Setup
        linkbar.api_key = "test_key"
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"id": "123", "status": "success"}
        mock_request.return_value = mock_response
        
        # Execute
        result = linkbar._request('GET', 'test/', {'param': 'value'})
        
        # Assert
        assert result == {"id": "123", "status": "success"}
        mock_request.assert_called_once_with(
            method='GET',
            url='https://api.linkbar.co/test/',
            headers={
                'X-API-Key': 'test_key',
                'Content-Type': 'application/json'
            },
            json=None,
            params={'param': 'value'}
        )
    
    @patch('linkbar.requests.request')
    def test_post_request_with_data(self, mock_request):
        """Test POST request with JSON data"""
        # Setup
        linkbar.api_key = "test_key"
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"created": True}
        mock_request.return_value = mock_response
        
        # Execute
        result = linkbar._request('POST', 'links/', {'long_url': 'https://example.com'})
        
        # Assert
        assert result == {"created": True}
        mock_request.assert_called_once_with(
            method='POST',
            url='https://api.linkbar.co/links/',
            headers={
                'X-API-Key': 'test_key',
                'Content-Type': 'application/json'
            },
            json={'long_url': 'https://example.com'},
            params=None
        )
    
    def test_request_without_api_key(self):
        """Test request fails when API key is not set"""
        linkbar.api_key = None
        
        with pytest.raises(ValueError, match="API key not set"):
            linkbar._request('GET', 'test/')
    
    @patch('linkbar.requests.request')
    def test_request_with_http_error(self, mock_request):
        """Test request handles HTTP errors properly"""
        # Setup
        linkbar.api_key = "test_key"
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("API Error")
        mock_request.return_value = mock_response
        
        # Execute & Assert
        with pytest.raises(requests.HTTPError):
            linkbar._request('GET', 'test/')
    
    def test_base_url_trailing_slash_handling(self):
        """Test base URL trailing slash is handled correctly"""
        linkbar.api_key = "test_key"
        linkbar.base_url = "https://api.example.com/"
        
        with patch('linkbar.requests.request') as mock_request:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {}
            mock_request.return_value = mock_response
            
            linkbar._request('GET', 'test/')
            
            # Should remove trailing slash from base_url before adding endpoint
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[1]['url'] == 'https://api.example.com/test/'
    
    def test_base_url_no_trailing_slash_handling(self):
        """Test base URL without trailing slash works correctly"""
        linkbar.api_key = "test_key"
        linkbar.base_url = "https://api.example.com"
        
        with patch('linkbar.requests.request') as mock_request:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {}
            mock_request.return_value = mock_response
            
            linkbar._request('GET', 'test/')
            
            # Should handle missing trailing slash correctly
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[1]['url'] == 'https://api.example.com/test/'