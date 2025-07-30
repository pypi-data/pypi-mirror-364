"""
Configuration management for Agentix
"""

import os
from pathlib import Path
from typing import Any

import yaml


class Config:
    """Configuration manager for API providers and settings"""

    def __init__(self, config_file: str | None = None):
        """Initialize configuration manager

        Args:
            config_file: Path to configuration file. Defaults to ~/.agentix/config.yaml
        """
        if config_file:
            self.config_file = Path(config_file)
        else:
            self.config_file = Path.home() / ".flexai" / "config.yaml"

        # Ensure config directory exists
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        self.config_data = self._load_config()
        self.active_provider = self.config_data.get("active_provider")

    def _load_config(self) -> dict[str, Any]:
        """Load configuration from file"""
        if not self.config_file.exists():
            return {"providers": {}, "active_provider": None}

        try:
            with open(self.config_file) as f:
                return yaml.safe_load(f) or {"providers": {}, "active_provider": None}
        except Exception as e:
            print(f"Warning: Could not load config file: {e}")
            return {"providers": {}, "active_provider": None}

    def save(self):
        """Save current configuration to file"""
        try:
            with open(self.config_file, "w") as f:
                yaml.dump(self.config_data, f, default_flow_style=False)
        except Exception as e:
            raise Exception(f"Failed to save configuration: {e}")

    def add_provider(self, name: str, config: dict[str, Any]):
        """Add or update an API provider configuration

        Args:
            name: Provider name
            config: Provider configuration dictionary
        """
        if "providers" not in self.config_data:
            self.config_data["providers"] = {}

        self.config_data["providers"][name] = config

    def get_provider(self, name: str | None = None) -> dict[str, Any]:
        """Get provider configuration

        Args:
            name: Provider name. If None, returns active provider

        Returns:
            Provider configuration dictionary
        """
        provider_name = name or self.active_provider

        if not provider_name:
            raise Exception("No active provider set")

        providers = self.config_data.get("providers", {})
        if provider_name not in providers:
            raise Exception(f"Provider '{provider_name}' not found")

        return providers[provider_name]

    def list_providers(self) -> list[str]:
        """List all configured provider names"""
        return list(self.config_data.get("providers", {}).keys())

    def set_active_provider(self, name: str):
        """Set the active provider

        Args:
            name: Provider name to set as active
        """
        if name not in self.list_providers():
            raise Exception(f"Provider '{name}' not found")

        self.active_provider = name
        self.config_data["active_provider"] = name

    def remove_provider(self, name: str):
        """Remove a provider configuration

        Args:
            name: Provider name to remove
        """
        providers = self.config_data.get("providers", {})
        if name not in providers:
            raise Exception(f"Provider '{name}' not found")

        del providers[name]

        # If this was the active provider, clear it
        if self.active_provider == name:
            self.active_provider = None
            self.config_data["active_provider"] = None

    def get_api_key(self, provider_name: str | None = None) -> str:
        """Get API key for provider, with environment variable fallback

        Args:
            provider_name: Provider name. If None, uses active provider

        Returns:
            API key string
        """
        provider_name = provider_name or self.active_provider

        if not provider_name:
            raise Exception(
                "No active provider set. Please configure a provider first."
            )

        provider_config = self.get_provider(provider_name)

        # Try getting from config first
        api_key = provider_config.get("api_key")

        # Fallback to environment variable
        if not api_key or api_key == "not-needed":
            env_var_name = f"{provider_name.upper()}_API_KEY"
            api_key = os.getenv(env_var_name)

        # Final fallback to generic API_KEY
        if not api_key:
            api_key = os.getenv("API_KEY")

        # Special case for local providers that don't need real API keys
        if not api_key and provider_name.lower() in ["local", "ollama", "lm-studio"]:
            return "not-needed"

        if not api_key:
            raise Exception(
                f"No API key found for provider '{provider_name}'. "
                f"Please set {provider_name.upper()}_API_KEY environment variable or configure it directly."
            )

        return api_key

    def get_base_url(self, provider_name: str | None = None) -> str:
        """Get base URL for provider

        Args:
            provider_name: Provider name. If None, uses active provider

        Returns:
            Base URL string
        """
        provider_config = self.get_provider(provider_name)
        return provider_config.get("base_url", "https://api.openai.com/v1")

    def get_model(self, provider_name: str | None = None) -> str:
        """Get default model for provider

        Args:
            provider_name: Provider name. If None, uses active provider

        Returns:
            Model name string
        """
        provider_config = self.get_provider(provider_name)
        # Return the configured model or a sensible default based on provider
        model = provider_config.get("model")
        if not model:
            # Default models based on provider type
            if provider_name and "ollama" in provider_name.lower():
                return "llama2:latest"
            else:
                return "gpt-4o-mini"
        return model
