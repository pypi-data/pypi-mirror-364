"""Configuration management for Genesis Agent CLI."""

import os
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field, HttpUrl, validator


class LLMConfig(BaseModel):
    """LLM integration configuration."""

    enabled: bool = Field(default=False, description="Enable LLM integration")
    provider: str = Field(
        default="anthropic", description="LLM provider (anthropic, openai, azure)"
    )
    config: dict = Field(
        default_factory=dict, description="Provider-specific configuration"
    )


class GenesisStudioConfig(BaseModel):
    """Genesis Studio connection configuration."""

    url: HttpUrl = Field(
        default="http://localhost:7860", description="Genesis Studio API URL"
    )
    api_key: Optional[str] = Field(
        default=None, description="API key for authentication"
    )


class Config(BaseModel):
    """Main configuration for Genesis Agent CLI."""

    genesis_studio: GenesisStudioConfig = Field(default_factory=GenesisStudioConfig)
    llm_integration: LLMConfig = Field(default_factory=LLMConfig)
    config_path: Optional[Path] = None

    @property
    def genesis_studio_url(self) -> str:
        """Get Genesis Studio URL as string."""
        return str(self.genesis_studio.url)

    @property
    def api_key(self) -> Optional[str]:
        """Get API key."""
        return self.genesis_studio.api_key


def get_default_config_path() -> Path:
    """Get the default configuration file path."""
    return Path.home() / ".genesis-agent.yaml"


def load_config(config_path: Optional[Path] = None) -> Config:
    """Load configuration from file or environment variables.

    Args:
        config_path: Optional path to configuration file

    Returns:
        Config object
    """
    # Determine config file path
    if config_path is None:
        # First check current directory
        local_config = Path(".genesis-agent.yaml")
        if local_config.exists():
            config_path = local_config
        else:
            config_path = get_default_config_path()

    # Initialize with defaults
    config_data = {}

    # Load from file if it exists
    if config_path.exists():
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f) or {}

    # Override with environment variables
    if url := os.getenv("GENESIS_STUDIO_URL"):
        if "genesis_studio" not in config_data:
            config_data["genesis_studio"] = {}
        config_data["genesis_studio"]["url"] = url

    # Support multiple ways to provide authentication
    if api_key := os.getenv("GENESIS_STUDIO_API_KEY"):
        if "genesis_studio" not in config_data:
            config_data["genesis_studio"] = {}
        config_data["genesis_studio"]["api_key"] = api_key
    elif bearer_token := os.getenv("GENESIS_STUDIO_BEARER_TOKEN"):
        if "genesis_studio" not in config_data:
            config_data["genesis_studio"] = {}
        config_data["genesis_studio"]["api_key"] = bearer_token
    elif access_token := os.getenv("GENESIS_ACCESS_TOKEN"):
        if "genesis_studio" not in config_data:
            config_data["genesis_studio"] = {}
        config_data["genesis_studio"]["api_key"] = access_token

    # Override with LLM environment variables
    if llm_enabled := os.getenv("GENESIS_LLM_ENABLED"):
        if "llm_integration" not in config_data:
            config_data["llm_integration"] = {}
        config_data["llm_integration"]["enabled"] = llm_enabled.lower() == "true"

    if llm_provider := os.getenv("GENESIS_LLM_PROVIDER"):
        if "llm_integration" not in config_data:
            config_data["llm_integration"] = {}
        config_data["llm_integration"]["provider"] = llm_provider

    # Load provider-specific environment variables
    llm_config = {}

    # OpenAI configuration
    if openai_key := os.getenv("OPENAI_API_KEY"):
        llm_config["api_key"] = openai_key
    if openai_model := os.getenv("OPENAI_MODEL"):
        llm_config["model"] = openai_model
    if openai_base_url := os.getenv("OPENAI_BASE_URL"):
        llm_config["base_url"] = openai_base_url

    # Anthropic configuration
    if anthropic_key := os.getenv("ANTHROPIC_API_KEY"):
        llm_config["api_key"] = anthropic_key
    if anthropic_model := os.getenv("ANTHROPIC_MODEL"):
        llm_config["model"] = anthropic_model

    # Azure OpenAI configuration
    if azure_key := os.getenv("AZURE_OPENAI_API_KEY"):
        llm_config["api_key"] = azure_key
    if azure_endpoint := os.getenv("AZURE_OPENAI_ENDPOINT"):
        llm_config["endpoint"] = azure_endpoint
    if azure_deployment := os.getenv("AZURE_OPENAI_DEPLOYMENT"):
        llm_config["deployment"] = azure_deployment
    if azure_version := os.getenv("AZURE_OPENAI_API_VERSION"):
        llm_config["api_version"] = azure_version

    if llm_config:
        if "llm_integration" not in config_data:
            config_data["llm_integration"] = {}
        config_data["llm_integration"]["config"] = llm_config

    # Create config object
    config = Config(**config_data)
    config.config_path = config_path

    return config


def save_config(config: Config, config_path: Optional[Path] = None) -> None:
    """Save configuration to file.

    Args:
        config: Configuration object
        config_path: Optional path to save configuration
    """
    if config_path is None:
        config_path = config.config_path or get_default_config_path()

    # Convert to dict and remove None values
    config_data = config.model_dump(exclude_none=True, exclude={"config_path"})

    # Ensure parent directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Save to file
    with open(config_path, "w") as f:
        yaml.dump(config_data, f, default_flow_style=False)
