"""
Utility functions for Agentix
"""

import logging
import re
import sys
from typing import Any


def setup_logging(level: str = "INFO", format_string: str | None = None):
    """Setup logging configuration

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        format_string: Custom format string
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_string,
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def extract_code_blocks(text: str, language: str | None = None) -> list[dict[str, str]]:
    """Extract code blocks from markdown-formatted text

    Args:
        text: Text containing code blocks
        language: Filter by specific language

    Returns:
        List of dictionaries with 'language' and 'code' keys
    """
    # Pattern to match markdown code blocks
    pattern = r"```(\w+)?\n(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)

    code_blocks = []
    for lang, code in matches:
        if language is None or lang.lower() == language.lower():
            code_blocks.append({"language": lang or "text", "code": code.strip()})

    return code_blocks


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes = int(size_bytes / 1024.0)
    return f"{size_bytes:.1f} TB"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncating

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def validate_model_name(model_name: str) -> bool:
    """Validate model name format

    Args:
        model_name: Model name to validate

    Returns:
        True if valid, False otherwise
    """
    # Basic validation - alphanumeric, hyphens, underscores, dots
    pattern = r"^[a-zA-Z0-9._-]+$"
    return bool(re.match(pattern, model_name))


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing/replacing invalid characters

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove/replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', "_", filename)

    # Remove leading/trailing dots and spaces
    filename = filename.strip(". ")

    # Ensure it's not empty
    if not filename:
        filename = "untitled"

    return filename


def parse_model_response(response: dict[str, Any]) -> dict[str, Any]:
    """Parse and extract useful information from model response

    Args:
        response: Raw API response

    Returns:
        Parsed response information
    """
    try:
        choice = response["choices"][0]
        message = choice["message"]

        return {
            "content": message["content"],
            "role": message["role"],
            "finish_reason": choice.get("finish_reason"),
            "usage": response.get("usage", {}),
            "model": response.get("model"),
            "created": response.get("created"),
        }
    except (KeyError, IndexError) as e:
        raise ValueError(f"Invalid response format: {e}")


def estimate_tokens(text: str) -> int:
    """Rough estimation of token count

    Args:
        text: Text to estimate

    Returns:
        Estimated token count
    """
    # Rough estimation: ~4 characters per token on average
    return len(text) // 4


def format_code_output(code: str, language: str = "python") -> str:
    """Format code for display with syntax highlighting markers

    Args:
        code: Code to format
        language: Programming language

    Returns:
        Formatted code string
    """
    return f"```{language}\n{code}\n```"


def extract_error_message(error_text: str) -> str:
    """Extract the most relevant part of an error message

    Args:
        error_text: Full error text

    Returns:
        Cleaned error message
    """
    lines = error_text.strip().split("\n")

    # Look for common error indicators
    error_indicators = [
        "Error:",
        "Exception:",
        "Traceback",
        "SyntaxError:",
        "TypeError:",
    ]

    for line in lines:
        for indicator in error_indicators:
            if indicator in line:
                return line.strip()

    # If no specific error found, return last non-empty line
    for line in reversed(lines):
        if line.strip():
            return line.strip()

    return error_text


def is_code_complete(code: str, language: str = "python") -> bool:
    """Basic check if code appears to be complete

    Args:
        code: Code to check
        language: Programming language

    Returns:
        True if code appears complete
    """
    if not code.strip():
        return False

    if language.lower() == "python":
        # Check for unmatched brackets/parentheses
        brackets = {"(": ")", "[": "]", "{": "}"}
        stack = []

        for char in code:
            if char in brackets:
                stack.append(brackets[char])
            elif char in brackets.values():
                if not stack or stack.pop() != char:
                    return False

        return len(stack) == 0

    # For other languages, just check if it's not empty
    return True
