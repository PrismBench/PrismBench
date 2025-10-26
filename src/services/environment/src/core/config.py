import os
from functools import lru_cache
from typing import Any, Dict, List, Optional

import yaml
from loguru import logger
from pydantic import BaseModel, Field


class EnvironmentConfig(BaseModel):
    """Configuration for a single environment including agents and parameters."""

    agents: List[str] = Field(description="List of agent names for this environment")
    max_attempts: Optional[int] = Field(
        default=3,
        description="Maximum solution attempts per problem",
    )
    timeout: Optional[int] = Field(
        default=300,
        description="Request timeout in seconds",
    )
    num_problems: Optional[int] = Field(
        default=1,
        description="Number of problems to generate",
    )

    class Config:
        extra = "allow"  # Allow additional environment-specific fields


class Settings(BaseModel):
    """Main application settings for the Environment Service."""

    app_name: str = "PrismBench Environment Service"
    version: str = "0.1.0"
    debug: bool = False

    # Configuration sections
    environment_configs: Optional[Dict[str, EnvironmentConfig]] = Field(default=None)

    llm_service_url: str = "http://llm-interface:8000"

    class Config:
        extra = "allow"  # Allow additional configurations


def load_yaml_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to the YAML configuration file

    Returns:
        Dictionary containing the configuration
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r") as f:
        try:
            config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Error parsing YAML config: {e}")

    if not isinstance(config, dict):
        raise ValueError(f"Config file {config_path} did not produce a dictionary.")

    logger.debug(f"Loaded config from {config_path}")
    return config


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings with caching.

    Returns:
        Settings: Application settings instance
    """
    # Load the environment config
    environment_config_path = os.path.join("configs", "environment_config.yaml")
    environment_config = load_yaml_config(environment_config_path)

    env_configs = {}
    for env_name, env_config in environment_config.items():
        env_configs[env_name] = EnvironmentConfig(**env_config)

    # Create settings instance - this will automatically load environment configs
    settings = Settings(environment_configs=env_configs)

    logger.info(f"Initialized settings: {settings.app_name} v{settings.version}")

    logger.info(f"Available environment configurations: {list(settings.environment_configs.keys())}")

    return settings
