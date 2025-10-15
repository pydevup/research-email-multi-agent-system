"""
Configuration management using pydantic-settings for Research Email Multi-Agent System.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator, ConfigDict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # LLM Configuration
    llm_provider: str = Field(default="openai")
    llm_api_key: str = Field(...)
    llm_model: str = Field(default="gpt-4o")
    llm_base_url: Optional[str] = Field(default="https://api.openai.com/v1")

    # Tavily API Configuration
    tavily_api_key: str = Field(...)

    # Gmail API Configuration
    gmail_credentials_path: str = Field(default="credentials/credentials.json")
    gmail_token_path: str = Field(default="credentials/token.json")

    # Application Configuration
    app_env: str = Field(default="development")
    log_level: str = Field(default="INFO")
    debug: bool = Field(default=False)

    @field_validator("llm_api_key", "tavily_api_key")
    @classmethod
    def validate_api_keys(cls, v):
        """Ensure API keys are not empty."""
        if not v or v.strip() == "":
            raise ValueError("API key cannot be empty")
        return v

    @field_validator("gmail_credentials_path", "gmail_token_path")
    @classmethod
    def validate_file_paths(cls, v):
        """Ensure file paths are provided."""
        if not v or v.strip() == "":
            raise ValueError("File path cannot be empty")
        return v


# Global settings instance
try:
    settings = Settings()
except Exception:
    # For testing, create settings with dummy values
    import os
    os.environ.setdefault("LLM_API_KEY", "test_key")
    os.environ.setdefault("TAVILY_API_KEY", "test_key")
    settings = Settings()