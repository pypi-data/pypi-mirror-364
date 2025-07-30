"""
Core agent functionality for code generation, chat, and execution
"""

import logging
from typing import Any

from .client import APIClient
from .config import Config
from .executor import CodeExecutor
from .utils import extract_code_blocks

logger = logging.getLogger(__name__)


class Agent:
    """Main agent class providing Cursor/Replit-like functionality"""

    def __init__(self, config: Config):
        """Initialize agent with configuration

        Args:
            config: Configuration instance
        """
        self.config = config

        # Initialize API client
        api_key = config.get_api_key()
        base_url = config.get_base_url()
        self.client = APIClient(api_key, base_url)

        # Get default model
        self.default_model = config.get_model()

        # Initialize code executor
        self.executor = CodeExecutor()

        # Chat history
        self.chat_history: list[dict[str, str]] = []

        # Test connection on initialization
        if not self.client.test_connection(self.default_model):
            raise Exception("Failed to connect to API provider")

        logger.info(f"Agent initialized with provider: {config.active_provider}")

    def chat(self, message: str, model: str | None = None) -> str:
        """Chat with the agent

        Args:
            message: User message
            model: Model to use (defaults to configured model)

        Returns:
            Agent response
        """
        # Add user message to history
        self.chat_history.append({"role": "user", "content": message})

        # Prepare messages for API
        messages = [
            {
                "role": "system",
                "content": (
                    "You are Agentix, an intelligent coding assistant similar to Cursor or Replit. "
                    "You can help with code generation, debugging, explanations, and general programming tasks. "
                    "Be helpful, accurate, and provide practical solutions. "
                    "When generating code, make sure it's complete and runnable."
                ),
            }
        ] + self.chat_history

        try:
            response = self.client.chat_completion(
                messages=messages, model=model or self.default_model, temperature=0.7
            )

            assistant_response = response["choices"][0]["message"]["content"]

            # Add assistant response to history
            self.chat_history.append(
                {"role": "assistant", "content": assistant_response}
            )

            # Keep chat history manageable (last 20 messages)
            if len(self.chat_history) > 20:
                self.chat_history = self.chat_history[-20:]

            return assistant_response

        except Exception as e:
            logger.error(f"Chat error: {e}")
            raise Exception(f"Chat failed: {str(e)}")

    def generate_code(
        self, prompt: str, language: str = "python", model: str | None = None
    ) -> str:
        """Generate code based on prompt

        Args:
            prompt: Code generation prompt
            language: Target programming language
            model: Model to use (defaults to configured model)

        Returns:
            Generated code
        """
        system_prompt = f"""
        You are an expert {language} programmer. Generate clean, well-commented, and functional code based on the user's request.

        Guidelines:
        - Write complete, runnable code
        - Include necessary imports and dependencies
        - Add helpful comments explaining complex logic
        - Follow best practices for {language}
        - Make the code production-ready
        - Only return the code, no additional explanation unless specifically asked
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]

        try:
            response = self.client.chat_completion(
                messages=messages,
                model=model or self.default_model,
                temperature=0.3,  # Lower temperature for more consistent code generation
            )

            generated_text = response["choices"][0]["message"]["content"]

            # Extract code blocks if present
            code_blocks = extract_code_blocks(generated_text, language)

            if code_blocks:
                # Return the first code block found
                return code_blocks[0]["code"]
            else:
                # If no code blocks found, return the full response
                return generated_text.strip()

        except Exception as e:
            logger.error(f"Code generation error: {e}")
            raise Exception(f"Code generation failed: {str(e)}")

    def execute_code(self, code: str, language: str = "python") -> dict[str, Any]:
        """Execute code safely

        Args:
            code: Code to execute
            language: Programming language

        Returns:
            Execution result with success status, output, and error info
        """
        try:
            return self.executor.execute(code, language)
        except Exception as e:
            logger.error(f"Code execution error: {e}")
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "execution_time": 0,
            }

    def analyze_code(
        self, code: str, language: str = "python", model: str | None = None
    ) -> str:
        """Analyze code for issues, improvements, and explanations

        Args:
            code: Code to analyze
            language: Programming language
            model: Model to use (defaults to configured model)

        Returns:
            Code analysis and suggestions
        """
        system_prompt = f"""
        You are an expert code reviewer and {language} programmer. Analyze the provided code and provide:

        1. Code quality assessment
        2. Potential bugs or issues
        3. Performance improvements
        4. Best practice recommendations
        5. Security considerations
        6. Code explanation if complex

        Be thorough but concise in your analysis.
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"Analyze this {language} code:\n\n```{language}\n{code}\n```",
            },
        ]

        try:
            response = self.client.chat_completion(
                messages=messages, model=model or self.default_model, temperature=0.4
            )

            return response["choices"][0]["message"]["content"]

        except Exception as e:
            logger.error(f"Code analysis error: {e}")
            raise Exception(f"Code analysis failed: {str(e)}")

    def debug_code(
        self,
        code: str,
        error_message: str,
        language: str = "python",
        model: str | None = None,
    ) -> str:
        """Help debug code issues

        Args:
            code: Code with issues
            error_message: Error message or description
            language: Programming language
            model: Model to use (defaults to configured model)

        Returns:
            Debugging suggestions and fixed code
        """
        system_prompt = f"""
        You are an expert {language} debugger. Help fix the provided code based on the error message.

        Provide:
        1. Explanation of what's causing the error
        2. Step-by-step fix instructions
        3. Corrected code
        4. Prevention tips for similar issues

        Be clear and practical in your response.
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"Debug this {language} code:\n\nCode:\n```{language}\n{code}\n```\n\nError: {error_message}",
            },
        ]

        try:
            response = self.client.chat_completion(
                messages=messages, model=model or self.default_model, temperature=0.3
            )

            return response["choices"][0]["message"]["content"]

        except Exception as e:
            logger.error(f"Code debugging error: {e}")
            raise Exception(f"Code debugging failed: {str(e)}")

    def explain_code(
        self, code: str, language: str = "python", model: str | None = None
    ) -> str:
        """Explain how code works

        Args:
            code: Code to explain
            language: Programming language
            model: Model to use (defaults to configured model)

        Returns:
            Code explanation
        """
        system_prompt = f"""
        You are an expert {language} teacher. Explain the provided code in a clear, educational manner.

        Include:
        1. Overall purpose and functionality
        2. Step-by-step breakdown of key parts
        3. Explanation of important concepts used
        4. How the code works together

        Make it understandable for someone learning {language}.
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"Explain this {language} code:\n\n```{language}\n{code}\n```",
            },
        ]

        try:
            response = self.client.chat_completion(
                messages=messages, model=model or self.default_model, temperature=0.5
            )

            return response["choices"][0]["message"]["content"]

        except Exception as e:
            logger.error(f"Code explanation error: {e}")
            raise Exception(f"Code explanation failed: {str(e)}")

    def clear_history(self):
        """Clear chat history"""
        self.chat_history.clear()
        logger.info("Chat history cleared")

    def get_usage_stats(self) -> dict[str, Any]:
        """Get usage statistics

        Returns:
            Usage statistics dictionary
        """
        # This would be enhanced to track actual usage
        return {
            "messages_sent": len([m for m in self.chat_history if m["role"] == "user"]),
            "responses_received": len(
                [m for m in self.chat_history if m["role"] == "assistant"]
            ),
            "active_provider": self.config.active_provider,
            "model": self.default_model,
        }
