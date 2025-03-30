"""Configuration management module for the Code Assistant application."""

import os
from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class GoogleVertexAIConfig(BaseModel):
    """Configuration for Google Vertex AI."""

    project: str = Field(..., description="Google Cloud Project")
    location: str = Field("us-central1", description="Default location for Vertex AI")
    model: str = Field("chat-bison", description="Default model for chat")


class Settings(BaseModel):
    """Main settings class for the application."""

    google_vertex_ai: GoogleVertexAIConfig = Field(
        ..., description="Google Vertex AI configuration"
    )

    @classmethod
    def load(cls, config_path: str | None = None) -> "Settings":
        """Load settings from configuration file.

        Args:
            config_path: Path to the configuration file. If not provided,
                        will look for config.yaml in the project root.

        Returns:
            Settings: Loaded settings object.

        Raises:
            FileNotFoundError: If configuration file is not found.
            ValueError: If configuration file is invalid.

        """
        if config_path is None:
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config.yaml"

        if not os.path.exists(config_path):
            raise FileNotFoundError(
                f"Configuration file not found at {config_path}. "
                "Please copy config.template.yaml to config.yaml and fill in your values."
            )

        with open(config_path) as f:
            config_data = yaml.safe_load(f)

        return cls(**config_data)


# Global settings instance
settings: Settings | None = None


def get_settings(config_path: str | None = None) -> Settings:
    """Get the global settings instance.

    Args:
        config_path: Optional path to configuration file.

    Returns:
        Settings: Global settings instance.

    """
    global settings
    if settings is None:
        settings = Settings.load(config_path)
    return settings
