"""
Tests for Agent functionality
"""

import os
import tempfile
from unittest.mock import Mock, patch

import pytest

from flexai.agent import Agent
from flexai.config import Config


class TestAgent:
    """Test cases for Agent class"""

    def setup_method(self):
        """Setup test fixtures"""
        # Create temporary config file
        self.temp_config = tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        )
        self.temp_config.write(
            """
active_provider: test
providers:
  test:
    api_key: test-key
    base_url: https://api.test.com/v1
    model: gpt-4o
"""
        )
        self.temp_config.close()

        # Mock config and client
        self.config = Config(self.temp_config.name)

    def teardown_method(self):
        """Cleanup test fixtures"""
        os.unlink(self.temp_config.name)

    @patch("flexai.agent.APIClient")
    def test_agent_initialization(self, mock_client_class):
        """Test agent initialization"""
        # Mock client instance
        mock_client = Mock()
        mock_client.test_connection.return_value = True
        mock_client_class.return_value = mock_client

        # Create agent
        agent = Agent(self.config)

        # Verify initialization
        assert agent.config == self.config
        assert agent.default_model == "gpt-4o"
        assert len(agent.chat_history) == 0

        # Verify client was created with correct parameters
        mock_client_class.assert_called_once_with("test-key", "https://api.test.com/v1")
        mock_client.test_connection.assert_called_once()

    @patch("flexai.agent.APIClient")
    def test_agent_initialization_connection_failure(self, mock_client_class):
        """Test agent initialization with connection failure"""
        # Mock client instance with failed connection
        mock_client = Mock()
        mock_client.test_connection.return_value = False
        mock_client_class.return_value = mock_client

        # Should raise exception
        with pytest.raises(Exception, match="Failed to connect to API provider"):
            Agent(self.config)

    @patch("flexai.agent.APIClient")
    def test_chat_functionality(self, mock_client_class):
        """Test chat functionality"""
        # Mock client and response
        mock_client = Mock()
        mock_client.test_connection.return_value = True
        mock_client.chat_completion.return_value = {
            "choices": [{"message": {"content": "Hello! How can I help you?"}}]
        }
        mock_client_class.return_value = mock_client

        # Create agent and chat
        agent = Agent(self.config)
        response = agent.chat("Hello")

        # Verify response
        assert response == "Hello! How can I help you?"
        assert len(agent.chat_history) == 2  # User message + assistant response
        assert agent.chat_history[0]["role"] == "user"
        assert agent.chat_history[1]["role"] == "assistant"

        # Verify API call
        mock_client.chat_completion.assert_called_once()
        call_args = mock_client.chat_completion.call_args[1]
        assert call_args["model"] == "gpt-4o"
        assert call_args["temperature"] == 0.7
        assert len(call_args["messages"]) == 2  # System + user message

    @patch("flexai.agent.APIClient")
    def test_generate_code(self, mock_client_class):
        """Test code generation"""
        # Mock client and response with code block
        mock_client = Mock()
        mock_client.test_connection.return_value = True
        mock_client.chat_completion.return_value = {
            "choices": [
                {"message": {"content": "```python\nprint('Hello, World!')\n```"}}
            ]
        }
        mock_client_class.return_value = mock_client

        # Create agent and generate code
        agent = Agent(self.config)
        code = agent.generate_code("Print hello world", "python")

        # Verify code extraction
        assert code == "print('Hello, World!')"

        # Verify API call
        mock_client.chat_completion.assert_called_once()
        call_args = mock_client.chat_completion.call_args[1]
        assert call_args["temperature"] == 0.3  # Lower temperature for code generation

    @patch("flexai.agent.APIClient")
    def test_generate_code_without_code_blocks(self, mock_client_class):
        """Test code generation without markdown code blocks"""
        # Mock client and response without code blocks
        mock_client = Mock()
        mock_client.test_connection.return_value = True
        mock_client.chat_completion.return_value = {
            "choices": [{"message": {"content": "print('Hello, World!')"}}]
        }
        mock_client_class.return_value = mock_client

        # Create agent and generate code
        agent = Agent(self.config)
        code = agent.generate_code("Print hello world", "python")

        # Should return full response when no code blocks found
        assert code == "print('Hello, World!')"

    @patch("flexai.agent.APIClient")
    @patch("flexai.agent.CodeExecutor")
    def test_execute_code(self, mock_executor_class, mock_client_class):
        """Test code execution"""
        # Mock client
        mock_client = Mock()
        mock_client.test_connection.return_value = True
        mock_client_class.return_value = mock_client

        # Mock executor
        mock_executor = Mock()
        mock_executor.execute.return_value = {
            "success": True,
            "output": "Hello, World!",
            "error": "",
            "execution_time": 0.1,
        }
        mock_executor_class.return_value = mock_executor

        # Create agent and execute code
        agent = Agent(self.config)
        result = agent.execute_code("print('Hello, World!')", "python")

        # Verify result
        assert result["success"] is True
        assert result["output"] == "Hello, World!"

        # Verify executor was called
        mock_executor.execute.assert_called_once_with(
            "print('Hello, World!')", "python"
        )

    @patch("flexai.agent.APIClient")
    def test_analyze_code(self, mock_client_class):
        """Test code analysis"""
        # Mock client and response
        mock_client = Mock()
        mock_client.test_connection.return_value = True
        mock_client.chat_completion.return_value = {
            "choices": [
                {"message": {"content": "This code prints a greeting message."}}
            ]
        }
        mock_client_class.return_value = mock_client

        # Create agent and analyze code
        agent = Agent(self.config)
        analysis = agent.analyze_code("print('Hello')", "python")

        # Verify analysis
        assert analysis == "This code prints a greeting message."

        # Verify API call
        mock_client.chat_completion.assert_called_once()
        call_args = mock_client.chat_completion.call_args[1]
        assert call_args["temperature"] == 0.4

    @patch("flexai.agent.APIClient")
    def test_debug_code(self, mock_client_class):
        """Test code debugging"""
        # Mock client and response
        mock_client = Mock()
        mock_client.test_connection.return_value = True
        mock_client.chat_completion.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "The error is caused by a missing import statement."
                    }
                }
            ]
        }
        mock_client_class.return_value = mock_client

        # Create agent and debug code
        agent = Agent(self.config)
        debug_info = agent.debug_code(
            "print(math.pi)", "NameError: name 'math' is not defined", "python"
        )

        # Verify debug info
        assert debug_info == "The error is caused by a missing import statement."

        # Verify API call
        mock_client.chat_completion.assert_called_once()
        call_args = mock_client.chat_completion.call_args[1]
        assert call_args["temperature"] == 0.3

    @patch("flexai.agent.APIClient")
    def test_explain_code(self, mock_client_class):
        """Test code explanation"""
        # Mock client and response
        mock_client = Mock()
        mock_client.test_connection.return_value = True
        mock_client.chat_completion.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "This function calculates the factorial of a number."
                    }
                }
            ]
        }
        mock_client_class.return_value = mock_client

        # Create agent and explain code
        agent = Agent(self.config)
        explanation = agent.explain_code(
            "def factorial(n): return 1 if n <= 1 else n * factorial(n-1)", "python"
        )

        # Verify explanation
        assert explanation == "This function calculates the factorial of a number."

        # Verify API call
        mock_client.chat_completion.assert_called_once()
        call_args = mock_client.chat_completion.call_args[1]
        assert call_args["temperature"] == 0.5

    @patch("flexai.agent.APIClient")
    def test_clear_history(self, mock_client_class):
        """Test clearing chat history"""
        # Mock client
        mock_client = Mock()
        mock_client.test_connection.return_value = True
        mock_client.chat_completion.return_value = {
            "choices": [{"message": {"content": "Response"}}]
        }
        mock_client_class.return_value = mock_client

        # Create agent, add some history, then clear
        agent = Agent(self.config)
        agent.chat("Hello")  # Add to history
        assert len(agent.chat_history) > 0

        agent.clear_history()
        assert len(agent.chat_history) == 0

    @patch("flexai.agent.APIClient")
    def test_get_usage_stats(self, mock_client_class):
        """Test getting usage statistics"""
        # Mock client
        mock_client = Mock()
        mock_client.test_connection.return_value = True
        mock_client.chat_completion.return_value = {
            "choices": [{"message": {"content": "Response"}}]
        }
        mock_client_class.return_value = mock_client

        # Create agent and get stats
        agent = Agent(self.config)
        agent.chat("Hello")  # Add some activity

        stats = agent.get_usage_stats()

        # Verify stats structure
        assert "messages_sent" in stats
        assert "responses_received" in stats
        assert "active_provider" in stats
        assert "model" in stats
        assert stats["active_provider"] == "test"
        assert stats["model"] == "gpt-4o"

    @patch("flexai.agent.APIClient")
    def test_chat_error_handling(self, mock_client_class):
        """Test error handling in chat"""
        # Mock client with error
        mock_client = Mock()
        mock_client.test_connection.return_value = True
        mock_client.chat_completion.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client

        # Create agent and test error handling
        agent = Agent(self.config)

        with pytest.raises(Exception, match="Chat failed: API Error"):
            agent.chat("Hello")
