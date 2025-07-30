"""
Flexai - API-agnostic agentic Python package

A configurable agent system that works with any OpenAI-compatible API.
Provides Cursor/Replit-like functionality with code generation, chat, and execution.
"""

__version__ = "0.1.0"
__author__ = "Flexai Team"
__description__ = "API-agnostic agentic Python package with configurable providers"

from .agent import Agent
from .client import APIClient
from .config import Config

__all__ = ["Agent", "APIClient", "Config"]
