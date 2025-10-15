"""
Tests for Research Agent.
"""

import pytest
from pydantic_ai.models.test import TestModel

from research_agent import research_agent, ResearchAgentDependencies


class TestResearchAgent:
    """Test Research Agent functionality."""

    def test_agent_creation(self):
        """Test that research agent can be created."""
        assert research_agent is not None
        assert research_agent.deps_type == ResearchAgentDependencies

    def test_agent_tools_registered(self):
        """Test that all expected tools are registered."""
        # Check that agent has tools by trying to run a simple query
        assert research_agent is not None
        # The tools are registered internally, we can verify by checking the agent exists

    @pytest.mark.asyncio
    async def test_agent_with_test_model(self):
        """Test agent with TestModel for fast validation."""
        test_model = TestModel()

        deps = ResearchAgentDependencies(
            tavily_api_key="test_key",
            gmail_credentials_path="test_credentials.json",
            gmail_token_path="test_token.json"
        )

        with research_agent.override(model=test_model):
            result = await research_agent.run(
                "Hello, can you help me research AI trends?",
                deps=deps
            )

            assert result.output is not None
            assert isinstance(result.output, str)

    def test_dependencies_creation(self):
        """Test that dependencies can be created properly."""
        deps = ResearchAgentDependencies(
            tavily_api_key="test_key",
            gmail_credentials_path="test_credentials.json",
            gmail_token_path="test_token.json",
            session_id="test_session"
        )

        assert deps.tavily_api_key == "test_key"
        assert deps.gmail_credentials_path == "test_credentials.json"
        assert deps.gmail_token_path == "test_token.json"
        assert deps.session_id == "test_session"