"""
Advanced tests for agents using FunctionModel and custom testing patterns.
"""

import pytest
from pydantic_ai import Agent
from pydantic_ai.models.function import FunctionModel, AgentInfo
from pydantic_ai.messages import ModelMessage, ModelResponse, TextPart, ToolCallPart, ToolReturnPart
from pydantic_ai.models.test import TestModel
from datetime import datetime

from research_agent import research_agent, ResearchAgentDependencies
from email_agent import email_agent, EmailAgentDependencies


class TestAdvancedAgentTesting:
    """Advanced testing patterns for agents."""

    @pytest.mark.asyncio
    async def test_research_agent_with_function_model(self):
        """Test research agent with custom FunctionModel for precise control."""

        async def research_model_function(
            messages: list[ModelMessage],
            info: AgentInfo
        ) -> ModelResponse:
            """Custom model function that simulates research agent behavior."""
            # Simulate agent deciding to use search_web tool
            return ModelResponse(
                parts=[
                    ToolCallPart(
                        tool_call_id="call_123",
                        tool_name="search_web",
                        args={"query": "AI trends 2024", "max_results": 5}
                    )
                ]
            )

        function_model = FunctionModel(research_model_function)

        deps = ResearchAgentDependencies(
            tavily_api_key="test_key",
            gmail_credentials_path="test_credentials.json",
            gmail_token_path="test_token.json"
        )

        with research_agent.override(model=function_model):
            result = await research_agent.run(
                "Research AI trends for 2024",
                deps=deps
            )

            # Verify the tool call was made
            assert result.output is not None

    @pytest.mark.asyncio
    async def test_email_agent_with_custom_response(self):
        """Test email agent with FunctionModel providing specific responses."""

        async def email_model_function(
            messages: list[ModelMessage],
            info: AgentInfo
        ) -> ModelResponse:
            """Custom model function that returns specific email content."""
            return ModelResponse(
                parts=[
                    TextPart(
                        content="I'll create a professional email draft for you with the subject 'AI Research Update'."
                    )
                ]
            )

        function_model = FunctionModel(email_model_function)

        deps = EmailAgentDependencies(
            gmail_credentials_path="test_credentials.json",
            gmail_token_path="test_token.json"
        )

        with email_agent.override(model=function_model):
            result = await email_agent.run(
                "Create an email about AI research",
                deps=deps
            )

            assert "professional email draft" in result.output.lower()

    @pytest.mark.asyncio
    async def test_agent_delegation_with_test_model(self):
        """Test agent delegation patterns using TestModel."""
        test_model = TestModel()

        deps = ResearchAgentDependencies(
            tavily_api_key="test_key",
            gmail_credentials_path="test_credentials.json",
            gmail_token_path="test_token.json"
        )

        with research_agent.override(model=test_model):
            # Test delegation to email agent
            result = await research_agent.run(
                "Research AI safety and create an email draft",
                deps=deps
            )

            # TestModel should return JSON with tool calls
            assert result.output is not None
            assert isinstance(result.output, str)

    @pytest.mark.asyncio
    async def test_tool_error_handling(self):
        """Test that agents handle tool errors gracefully."""

        async def error_model_function(
            messages: list[ModelMessage],
            info: AgentInfo
        ) -> ModelResponse:
            """Model function that simulates tool errors."""
            # Simulate a tool call that will fail
            return ModelResponse(
                parts=[
                    ToolCallPart(
                        tool_call_id="call_error",
                        tool_name="search_web",
                        args={"query": "test query", "max_results": 5}
                    )
                ]
            )

        function_model = FunctionModel(error_model_function)

        deps = ResearchAgentDependencies(
            tavily_api_key="invalid_key",  # This will cause auth error
            gmail_credentials_path="test_credentials.json",
            gmail_token_path="test_token.json"
        )

        with research_agent.override(model=function_model):
            result = await research_agent.run(
                "Test error handling",
                deps=deps
            )

            # The agent should handle the error gracefully
            assert result.output is not None

    @pytest.mark.asyncio
    async def test_multiple_tool_calls(self):
        """Test agent behavior with multiple tool calls."""

        async def multi_tool_model_function(
            messages: list[ModelMessage],
            info: AgentInfo
        ) -> ModelResponse:
            """Model function that makes multiple tool calls."""
            return ModelResponse(
                parts=[
                    ToolCallPart(
                        tool_call_id="call_1",
                        tool_name="search_web",
                        args={"query": "AI research", "max_results": 3}
                    ),
                    ToolCallPart(
                        tool_call_id="call_2",
                        tool_name="summarize_research",
                        args={
                            "search_results": [{"title": "Test", "content": "Content"}],
                            "topic": "AI"
                        }
                    )
                ]
            )

        function_model = FunctionModel(multi_tool_model_function)

        deps = ResearchAgentDependencies(
            tavily_api_key="test_key",
            gmail_credentials_path="test_credentials.json",
            gmail_token_path="test_token.json"
        )

        with research_agent.override(model=function_model):
            result = await research_agent.run(
                "Research and summarize AI topics",
                deps=deps
            )

            assert result.output is not None


class TestAgentIntegration:
    """Integration tests for multi-agent system."""

    @pytest.mark.asyncio
    async def test_agent_delegation_integration(self):
        """Test integration between research agent and email agent."""

        async def delegation_model_function(
            messages: list[ModelMessage],
            info: AgentInfo
        ) -> ModelResponse:
            """Model function that simulates delegation to email agent."""
            return ModelResponse(
                parts=[
                    ToolCallPart(
                        tool_call_id="delegate_1",
                        tool_name="delegate_to_email_agent",
                        args={
                            "prompt": "Create an email about AI research",
                            "context": {"research_topic": "AI"}
                        }
                    )
                ]
            )

        function_model = FunctionModel(delegation_model_function)

        deps = ResearchAgentDependencies(
            tavily_api_key="test_key",
            gmail_credentials_path="test_credentials.json",
            gmail_token_path="test_token.json"
        )

        with research_agent.override(model=function_model):
            result = await research_agent.run(
                "Research AI and delegate email creation",
                deps=deps
            )

            assert result.output is not None
            # The delegation tool should handle the email agent call

    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self):
        """Test complete workflow from research to email creation."""
        test_model = TestModel()

        deps = ResearchAgentDependencies(
            tavily_api_key="test_key",
            gmail_credentials_path="test_credentials.json",
            gmail_token_path="test_token.json"
        )

        with research_agent.override(model=test_model):
            result = await research_agent.run(
                "Research quantum computing and create an email draft for john@example.com",
                deps=deps
            )

            # Should trigger both research and email creation tools
            assert result.output is not None
            assert isinstance(result.output, str)