"""
Flexible provider configuration for LLM models in Research Email Multi-Agent System.
"""

from typing import Optional
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.anthropic import AnthropicProvider
from pydantic_ai.models.anthropic import AnthropicModel
from settings import settings


def get_llm_model(model_choice: Optional[str] = None) -> OpenAIModel:
    """
    Get LLM model configuration based on environment variables.

    Args:
        model_choice: Optional override for model choice

    Returns:
        Configured OpenAI-compatible model
    """
    llm_choice = model_choice or settings.llm_model
    base_url = settings.llm_base_url
    api_key = settings.llm_api_key

    # Create provider based on configuration
    provider = OpenAIProvider(base_url=base_url, api_key=api_key)

    return OpenAIModel(llm_choice, provider=provider)


def get_anthropic_model(model_choice: Optional[str] = None) -> AnthropicModel:
    """
    Get Anthropic model configuration.

    Args:
        model_choice: Optional override for model choice

    Returns:
        Configured Anthropic model
    """
    llm_choice = model_choice or "claude-3-5-sonnet-20241022"
    api_key = settings.llm_api_key

    # Create Anthropic provider
    provider = AnthropicProvider(api_key=api_key)

    return AnthropicModel(llm_choice, provider=provider)


def get_model_info() -> dict:
    """
    Get information about current model configuration.

    Returns:
        Dictionary with model configuration info
    """
    return {
        "llm_provider": settings.llm_provider,
        "llm_model": settings.llm_model,
        "llm_base_url": settings.llm_base_url,
        "tavily_api_key": "***" if settings.tavily_api_key else None,
        "app_env": settings.app_env,
        "debug": settings.debug,
    }


def validate_llm_configuration() -> bool:
    """
    Validate that LLM configuration is properly set.

    Returns:
        True if configuration is valid
    """
    try:
        # Check if we can create a model instance
        get_llm_model()
        return True
    except Exception as e:
        print(f"LLM configuration validation failed: {e}")
        return False


def validate_tavily_configuration() -> bool:
    """
    Validate that Tavily API configuration is properly set.

    Returns:
        True if configuration is valid
    """
    try:
        if not settings.tavily_api_key or settings.tavily_api_key.strip() == "":
            return False
        return True
    except Exception as e:
        print(f"Tavily configuration validation failed: {e}")
        return False


def validate_gmail_configuration() -> bool:
    """
    Validate that Gmail API configuration is properly set.

    Returns:
        True if configuration is valid
    """
    try:
        if not settings.gmail_credentials_path or not settings.gmail_token_path:
            return False
        # Check if credentials file exists
        import os
        if not os.path.exists(settings.gmail_credentials_path):
            print(f"Gmail credentials file not found: {settings.gmail_credentials_path}")
            return False
        return True
    except Exception as e:
        print(f"Gmail configuration validation failed: {e}")
        return False