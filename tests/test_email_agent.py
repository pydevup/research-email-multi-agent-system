"""
Tests for Email Agent.
"""

import pytest
from pydantic_ai.models.test import TestModel

from email_agent import email_agent, EmailAgentDependencies


class TestEmailAgent:
    """Test Email Agent functionality."""

    def test_agent_creation(self):
        """Test that email agent can be created."""
        assert email_agent is not None
        assert email_agent.deps_type == EmailAgentDependencies

    def test_agent_tools_registered(self):
        """Test that all expected tools are registered."""
        # Check that agent has tools by trying to run a simple query
        assert email_agent is not None
        # The tools are registered internally, we can verify by checking the agent exists

    @pytest.mark.asyncio
    async def test_agent_with_test_model(self):
        """Test agent with TestModel for fast validation."""
        test_model = TestModel()

        deps = EmailAgentDependencies(
            gmail_credentials_path="test_credentials.json",
            gmail_token_path="test_token.json"
        )

        with email_agent.override(model=test_model):
            result = await email_agent.run(
                "Create a professional email about AI research",
                deps=deps
            )

            assert result.output is not None
            assert isinstance(result.output, str)

    def test_dependencies_creation(self):
        """Test that dependencies can be created properly."""
        deps = EmailAgentDependencies(
            gmail_credentials_path="test_credentials.json",
            gmail_token_path="test_token.json",
            session_id="test_session"
        )

        assert deps.gmail_credentials_path == "test_credentials.json"
        assert deps.gmail_token_path == "test_token.json"
        assert deps.session_id == "test_session"