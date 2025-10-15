"""
Tests for pure tool functions.
"""

import pytest
from unittest.mock import patch, AsyncMock

from tools import (
    search_web_tool,
    authenticate_gmail_tool,
    create_gmail_draft_tool,
    validate_email_addresses_tool
)


class TestSearchWebTool:
    """Test search_web_tool functionality."""

    @pytest.mark.asyncio
    async def test_search_web_tool_success(self):
        """Test successful web search."""
        mock_response = {
            "results": [
                {
                    "title": "Test Result 1",
                    "url": "https://example.com/1",
                    "content": "Test content 1"
                },
                {
                    "title": "Test Result 2",
                    "url": "https://example.com/2",
                    "content": "Test content 2"
                }
            ],
            "answer": "AI summary of results"
        }

        async def mock_post(*args, **kwargs):
            class MockResponse:
                def __init__(self):
                    self.status_code = 200

                async def json(self):
                    return mock_response

            return MockResponse()

        with patch('tools.httpx.AsyncClient') as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.post = mock_post
            mock_client.return_value.__aenter__.return_value = mock_client_instance

            results = await search_web_tool(
                api_key="test_api_key",
                query="test query",
                max_results=5
            )

            assert len(results) == 3  # 2 results + AI summary
            assert results[0]["title"] == "Test Result 1"
            assert results[0]["score"] == 1.0
            assert results[1]["score"] == 0.95
            assert results[2]["title"] == "AI Summary"

    @pytest.mark.asyncio
    async def test_search_web_tool_api_error(self):
        """Test web search with API error."""
        with patch('tools.httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post.return_value.status_code = 401

            with pytest.raises(Exception, match="Invalid Tavily API key"):
                await search_web_tool(
                    api_key="invalid_key",
                    query="test query"
                )

    @pytest.mark.asyncio
    async def test_search_web_tool_rate_limit(self):
        """Test web search with rate limiting."""
        with patch('tools.httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post.return_value.status_code = 429

            with pytest.raises(Exception, match="Rate limit exceeded"):
                await search_web_tool(
                    api_key="test_key",
                    query="test query"
                )

    def test_search_web_tool_validation(self):
        """Test input validation for search_web_tool."""
        with pytest.raises(ValueError, match="Tavily API key is required"):
            # This will raise synchronously due to validation
            import asyncio
            asyncio.run(search_web_tool(api_key="", query="test"))

        with pytest.raises(ValueError, match="Query cannot be empty"):
            import asyncio
            asyncio.run(search_web_tool(api_key="test", query=""))


class TestEmailValidationTool:
    """Test email validation tool."""

    @pytest.mark.asyncio
    async def test_validate_email_addresses_tool(self):
        """Test email address validation."""
        emails = [
            "valid@example.com",
            "invalid-email",
            "another.valid@domain.co.uk",
            "@nodomain.com"
        ]

        result = await validate_email_addresses_tool(emails)

        assert result["valid_emails"] == ["valid@example.com", "another.valid@domain.co.uk"]
        assert result["invalid_emails"] == ["invalid-email", "@nodomain.com"]
        assert result["total_valid"] == 2
        assert result["total_invalid"] == 2

    @pytest.mark.asyncio
    async def test_validate_email_addresses_all_valid(self):
        """Test with all valid emails."""
        emails = ["test1@example.com", "test2@domain.org"]

        result = await validate_email_addresses_tool(emails)

        assert result["valid_emails"] == emails
        assert result["invalid_emails"] == []
        assert result["total_valid"] == 2
        assert result["total_invalid"] == 0


class TestGmailTools:
    """Test Gmail-related tools."""

    @pytest.mark.asyncio
    async def test_authenticate_gmail_tool_missing_credentials(self):
        """Test authentication with missing credentials file."""
        with pytest.raises(Exception, match="Gmail credentials file not found"):
            await authenticate_gmail_tool(
                credentials_path="/nonexistent/credentials.json",
                token_path="/tmp/token.json"
            )

    @pytest.mark.asyncio
    async def test_create_gmail_draft_tool_auth_failure(self):
        """Test draft creation with authentication failure."""
        with patch('tools.authenticate_gmail_tool') as mock_auth:
            mock_auth.return_value = {"success": False, "error": "Auth failed"}

            with pytest.raises(Exception, match="Gmail authentication failed"):
                await create_gmail_draft_tool(
                    credentials_path="test.json",
                    token_path="token.json",
                    to=["test@example.com"],
                    subject="Test Subject",
                    body="Test Body"
                )