"""
API client abstraction layer for different providers
"""

import json
import logging
from collections.abc import Generator
from typing import Any

import requests

logger = logging.getLogger(__name__)


class APIClient:
    """Generic API client for OpenAI-compatible endpoints"""

    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1"):
        """Initialize API client

        Args:
            api_key: API key for authentication
            base_url: Base URL for the API endpoint
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update(
            {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        )

    def _make_request(self, endpoint: str, data: dict[str, Any]) -> dict[str, Any]:
        """Make API request with error handling

        Args:
            endpoint: API endpoint (e.g., '/chat/completions')
            data: Request payload

        Returns:
            Response data dictionary
        """
        url = f"{self.base_url}{endpoint}"

        try:
            logger.debug(f"Making request to {url}")
            logger.debug(f"Request data: {json.dumps(data, indent=2)}")

            response = self.session.post(url, json=data, timeout=120)

            logger.debug(f"Response status: {response.status_code}")

            if response.status_code != 200:
                error_msg = f"API request failed with status {response.status_code}"
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_msg += f": {error_data['error'].get('message', str(error_data['error']))}"
                except:
                    error_msg += f": {response.text}"

                raise Exception(error_msg)

            response_data = response.json()
            logger.debug(f"Response data: {json.dumps(response_data, indent=2)}")

            return response_data

        except requests.RequestException as e:
            raise Exception(f"Network error: {str(e)}")
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON response: {str(e)}")

    def chat_completion(
        self, messages: list[dict[str, str]], model: str = "gpt-4o-mini", **kwargs
    ) -> dict[str, Any]:
        """Make chat completion request

        Args:
            messages: List of messages
            model: Model to use (defaults to gpt-4o-mini for better compatibility)
            **kwargs: Additional parameters

        Returns:
            API response
        """
        data = {
            "model": model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            **kwargs,
        }

        # Handle streaming separately
        if kwargs.get("stream", False):
            return self._stream_completion(data)

        return self._make_request("/chat/completions", data)

    def _stream_completion(
        self, data: dict[str, Any]
    ) -> Generator[dict[str, Any], None, None]:
        """Stream chat completion response

        Args:
            data: Request payload with stream=True

        Yields:
            Streaming response chunks
        """
        url = f"{self.base_url}/chat/completions"

        try:
            with self.session.post(
                url, json=data, stream=True, timeout=120
            ) as response:
                if response.status_code != 200:
                    raise Exception(
                        f"Stream request failed with status {response.status_code}"
                    )

                for line in response.iter_lines():
                    if line:
                        line = line.decode("utf-8")
                        if line.startswith("data: "):
                            line = line[6:]  # Remove 'data: ' prefix

                            if line.strip() == "[DONE]":
                                break

                            try:
                                chunk = json.loads(line)
                                yield chunk
                            except json.JSONDecodeError:
                                continue

        except requests.RequestException as e:
            raise Exception(f"Streaming error: {str(e)}")

    def list_models(self) -> list[dict[str, Any]]:
        """List available models

        Returns:
            List of model information dictionaries
        """
        try:
            response = self._make_request("/models", {})
            return response.get("data", [])
        except Exception:
            # If models endpoint is not available, return empty list
            logger.warning("Models endpoint not available")
            return []

    def test_connection(self, model: str = None) -> bool:
        """Test API connection

        Args:
            model: Model to test with (optional)

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Try a simple completion request
            response = self.chat_completion(
                messages=[{"role": "user", "content": "Hello"}],
                model=model or "gpt-4o-mini",
                max_tokens=1,
            )
            return "choices" in response
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            print(f"DEBUG: Connection test error: {e}")  # Debug output
            return False

    def get_usage_info(self, response: dict[str, Any]) -> dict[str, Any]:
        """Extract usage information from response

        Args:
            response: API response dictionary

        Returns:
            Usage information dictionary
        """
        usage = response.get("usage", {})
        return {
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
        }
