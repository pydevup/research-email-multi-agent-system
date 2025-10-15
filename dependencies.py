"""
External service dependencies for Research Email Multi-Agent System.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ResearchAgentDependencies:
    """Dependencies for the research agent - only configuration, no tool instances."""
    tavily_api_key: str
    gmail_credentials_path: str
    gmail_token_path: str
    session_id: Optional[str] = None


@dataclass
class EmailAgentDependencies:
    """Dependencies for the email agent - Gmail API configuration."""
    gmail_credentials_path: str
    gmail_token_path: str
    session_id: Optional[str] = None


@dataclass
class MultiAgentDependencies:
    """Combined dependencies for both agents."""
    tavily_api_key: str
    gmail_credentials_path: str
    gmail_token_path: str
    session_id: Optional[str] = None


def create_research_dependencies() -> ResearchAgentDependencies:
    """
    Create research agent dependencies from settings.

    Returns:
        ResearchAgentDependencies instance
    """
    from settings import settings
    return ResearchAgentDependencies(
        tavily_api_key=settings.tavily_api_key,
        gmail_credentials_path=settings.gmail_credentials_path,
        gmail_token_path=settings.gmail_token_path
    )


def create_email_dependencies() -> EmailAgentDependencies:
    """
    Create email agent dependencies from settings.

    Returns:
        EmailAgentDependencies instance
    """
    from settings import settings
    return EmailAgentDependencies(
        gmail_credentials_path=settings.gmail_credentials_path,
        gmail_token_path=settings.gmail_token_path
    )


def create_multi_agent_dependencies() -> MultiAgentDependencies:
    """
    Create combined dependencies for both agents.

    Returns:
        MultiAgentDependencies instance
    """
    from settings import settings
    return MultiAgentDependencies(
        tavily_api_key=settings.tavily_api_key,
        gmail_credentials_path=settings.gmail_credentials_path,
        gmail_token_path=settings.gmail_token_path
    )