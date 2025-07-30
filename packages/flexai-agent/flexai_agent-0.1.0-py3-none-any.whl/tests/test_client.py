"""
Tests for API Client functionality
"""

import json
from unittest.mock import Mock, patch

import pytest
import requests

from flexai.client import APIClient


class TestAPIClient:
    """Test cases for APIClient class"""

    def setup_method(self):
        """Setup test fixtures"""
        self.api_key = "test-api-key"
        self.base_url = "https://api.test.com/v1"
        self.client = APIClient(self.api_key, self.base_url)

    def test_client_initialization(self):
        """Test client initialization"""
        assert self.client.api_key == self.api_key
        assert self.client.base_url == self.base_url
        assert "Authorization" in self.client.session.headers
        assert self.client.session.headers["Authorization"] == f"Bearer {self.api_key}"
        assert self.client.session.headers["Content-Type"] == "application/json"

    def test_base_url_normalization(self):
        """Test base URL normalization (removes trailing slash)"""
        client = APIClient("key", "https://api.test.com/v1/")
        assert client.base_url == "https://api.test.com/v1"

    @patch("requests.Session.post")
    def test_make_request_success(self, mock_post):
        """Test successful API request"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"test": "success"}
        mock_post.return_value = mock_response

        # Make request
        result = self.client._make_request("/test", {"data": "test"})

        # Verify result
        assert result == {"test": "success"}

        # Verify request was made correctly
        mock_post.assert_called_once_with(
            f"{self.base_url}/test", json={"data": "test"}, timeout=120
        )

    @patch("requests.Session.post")
    def test_make_request_error_status(self, mock_post):
        """Test API request with error status code"""
        # Mock error response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": {"message": "Bad request"}}
        mock_post.return_value = mock_response

        # Should raise exception
        with pytest.raises(
            Exception, match="API request failed with status 400: Bad request"
        ):
            self.client._make_request("/test", {"data": "test"})

    @patch("requests.Session.post")
    def test_make_request_network_error(self, mock_post):
        """Test API request with network error"""
        # Mock network error
        mock_post.side_effect = requests.RequestException("Network error")

        # Should raise exception
        with pytest.raises(Exception, match="Network error: Network error"):
            self.client._make_request("/test", {"data": "test"})

    @patch("requests.Session.post")
    def test_make_request_json_decode_error(self, mock_post):
        """Test API request with invalid JSON response"""
        # Mock response with invalid JSON
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_post.return_value = mock_response

        # Should raise exception
        with pytest.raises(Exception, match="Invalid JSON response"):
            self.client._make_request("/test", {"data": "test"})

    @patch.object(APIClient, "_make_request")
    def test_chat_completion_basic(self, mock_make_request):
        """Test basic chat completion"""
        # Mock response
        mock_make_request.return_value = {
            "choices": [{"message": {"content": "Hello!"}}]
        }

        # Make chat completion request
        messages = [{"role": "user", "content": "Hello"}]
        result = self.client.chat_completion(messages)

        # Verify result
        assert result["choices"][0]["message"]["content"] == "Hello!"

        # Verify request was made with correct parameters
        mock_make_request.assert_called_once_with(
            "/chat/completions",
            {
                "model": "gpt-4o-mini",  # Updated to match config default
                "messages": messages,
                "temperature": 0.7,
            },
        )

    @patch.object(APIClient, "_make_request")
    def test_chat_completion_with_options(self, mock_make_request):
        """Test chat completion with additional options"""
        # Mock response
        mock_make_request.return_value = {
            "choices": [{"message": {"content": "Response"}}]
        }

        # Make chat completion request with options
        messages = [{"role": "user", "content": "Test"}]
        self.client.chat_completion(
            messages=messages,
            model="custom-model",
            temperature=0.5,
            max_tokens=100,
            custom_param="value",
        )

        # Verify request was made with all parameters
        mock_make_request.assert_called_once_with(
            "/chat/completions",
            {
                "model": "custom-model",
                "messages": messages,
                "temperature": 0.5,
                "max_tokens": 100,
                "custom_param": "value",
            },
        )

    @patch("requests.Session.post")
    def test_stream_completion(self, mock_post):
        """Test streaming chat completion"""
        # Mock streaming response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.iter_lines.return_value = [
            b'data: {"choices": [{"delta": {"content": "Hello"}}]}',
            b'data: {"choices": [{"delta": {"content": " world"}}]}',
            b"data: [DONE]",
        ]
        mock_post.return_value.__enter__.return_value = mock_response

        # Make streaming request
        messages = [{"role": "user", "content": "Hello"}]
        chunks = list(self.client.chat_completion(messages, stream=True))

        # Verify chunks
        assert len(chunks) == 2  # Should exclude [DONE]
        assert chunks[0]["choices"][0]["delta"]["content"] == "Hello"
        assert chunks[1]["choices"][0]["delta"]["content"] == " world"

    @patch.object(APIClient, "_make_request")
    def test_list_models_success(self, mock_make_request):
        """Test listing models successfully"""
        # Mock response
        mock_make_request.return_value = {
            "data": [
                {"id": "gpt-4o", "object": "model"},
                {"id": "gpt-3.5-turbo", "object": "model"},
            ]
        }

        # Get models
        models = self.client.list_models()

        # Verify result
        assert len(models) == 2
        assert models[0]["id"] == "gpt-4o"
        assert models[1]["id"] == "gpt-3.5-turbo"

    @patch.object(APIClient, "_make_request")
    def test_list_models_failure(self, mock_make_request):
        """Test listing models when endpoint fails"""
        # Mock error
        mock_make_request.side_effect = Exception("Endpoint not available")

        # Should return empty list on failure
        models = self.client.list_models()
        assert models == []

    @patch.object(APIClient, "chat_completion")
    def test_test_connection_success(self, mock_chat_completion):
        """Test successful connection test"""
        # Mock successful response
        mock_chat_completion.return_value = {
            "choices": [{"message": {"content": "Test"}}]
        }

        # Test connection
        result = self.client.test_connection()

        # Verify result
        assert result is True
        mock_chat_completion.assert_called_once()

    @patch.object(APIClient, "chat_completion")
    def test_test_connection_failure(self, mock_chat_completion):
        """Test failed connection test"""
        # Mock error
        mock_chat_completion.side_effect = Exception("Connection failed")

        # Test connection
        result = self.client.test_connection()

        # Verify result
        assert result is False

    def test_get_usage_info(self):
        """Test extracting usage information from response"""
        response = {
            "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
        }

        usage = self.client.get_usage_info(response)

        assert usage["prompt_tokens"] == 10
        assert usage["completion_tokens"] == 20
        assert usage["total_tokens"] == 30

    def test_get_usage_info_missing(self):
        """Test extracting usage information when missing from response"""
        response = {}

        usage = self.client.get_usage_info(response)

        # Should return zeros for missing usage data
        assert usage["prompt_tokens"] == 0
        assert usage["completion_tokens"] == 0
        assert usage["total_tokens"] == 0
