"""
Common test fixtures and configuration for the test suite.
"""

import pytest
import os
from unittest.mock import patch


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    with patch('settings.settings') as mock_settings:
        mock_settings.tavily_api_key = "test_tavily_key"
        mock_settings.openai_api_key = "test_openai_key"
        mock_settings.anthropic_api_key = "test_anthropic_key"
        mock_settings.gmail_credentials_path = "test_credentials.json"
        mock_settings.gmail_token_path = "test_token.json"
        mock_settings.llm_provider = "openai"
        mock_settings.llm_model = "gpt-4o"
        yield mock_settings


@pytest.fixture
def research_agent_dependencies():
    """Test dependencies for research agent."""
    from dependencies import ResearchAgentDependencies
    return ResearchAgentDependencies(
        tavily_api_key="test_tavily_key",
        gmail_credentials_path="test_credentials.json",
        gmail_token_path="test_token.json",
        session_id="test_session"
    )


@pytest.fixture
def email_agent_dependencies():
    """Test dependencies for email agent."""
    from dependencies import EmailAgentDependencies
    return EmailAgentDependencies(
        gmail_credentials_path="test_credentials.json",
        gmail_token_path="test_token.json",
        session_id="test_session"
    )


@pytest.fixture
def mock_httpx_client():
    """Mock httpx client for external API calls."""
    with patch('tools.httpx.AsyncClient') as mock_client:
        mock_response = type('Response', (), {
            'status_code': 200,
            'json': lambda: {
                "results": [
                    {
                        "title": "Test Result",
                        "url": "https://example.com",
                        "content": "Test content"
                    }
                ],
                "answer": "Test summary"
            }
        })()

        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
        yield mock_client


@pytest.fixture
def mock_gmail_auth():
    """Mock Gmail authentication."""
    with patch('tools.InstalledAppFlow') as mock_flow:
        with patch('tools.Credentials') as mock_creds:
            mock_creds.from_authorized_user_file.return_value = type('Creds', (), {
                'valid': True,
                'expired': False,
                'refresh_token': 'test_refresh_token',
                'to_json': lambda: '{"token": "test"}'
            })()

            mock_flow.from_client_secrets_file.return_value.run_local_server.return_value = mock_creds.from_authorized_user_file.return_value
            yield


@pytest.fixture
def mock_gmail_service():
    """Mock Gmail service."""
    with patch('tools.build') as mock_build:
        mock_service = type('Service', (), {
            'users': lambda: type('Users', (), {
                'drafts': lambda: type('Drafts', (), {
                    'create': lambda **kwargs: type('Create', (), {
                        'execute': lambda: {
                            'id': 'draft_123',
                            'message': {
                                'id': 'msg_123',
                                'threadId': 'thread_123'
                            }
                        }
                    })()
                })()
            })()
        })()

        mock_build.return_value = mock_service
        yield mock_build