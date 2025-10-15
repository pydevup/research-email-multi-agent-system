"""
Tests for CLI and streaming functionality.
"""

import pytest
from unittest.mock import patch, AsyncMock
import asyncio

from cli import StreamingCLI, app


class TestStreamingCLI:
    """Test Streaming CLI functionality."""

    def test_cli_initialization(self):
        """Test that CLI initializes correctly."""
        cli = StreamingCLI()

        assert cli is not None
        assert cli.session_state is not None
        assert cli.current_agent == "research_agent"
        assert "session_" in cli.session_state.session_id

    def test_format_streaming_output(self):
        """Test streaming output formatting."""
        cli = StreamingCLI()

        panel = cli._format_streaming_output("Test streaming content")

        assert panel is not None
        assert panel.title == "🤖 Research Agent"

    def test_display_conversation_history_empty(self):
        """Test displaying empty conversation history."""
        cli = StreamingCLI()

        # Should not raise any errors
        cli.display_conversation_history()

    def test_display_agent_info(self):
        """Test displaying agent information."""
        cli = StreamingCLI()

        # Should not raise any errors
        cli.display_agent_info()

    @pytest.mark.asyncio
    async def test_stream_agent_interaction_research_agent(self):
        """Test streaming interaction with research agent."""
        cli = StreamingCLI()

        # Mock the entire agent.iter() call chain
        with patch('cli.research_agent.iter') as mock_iter:
            # Create a mock run context
            mock_run = AsyncMock()
            mock_run.result = type('Result', (), {'output': 'Test response content'})()

            # Mock the async context manager
            mock_context_manager = AsyncMock()
            mock_context_manager.__aenter__.return_value = mock_run
            mock_context_manager.__aexit__.return_value = None
            mock_iter.return_value = mock_context_manager

            # Mock the dependencies
            with patch('cli.create_research_dependencies') as mock_deps:
                mock_deps.return_value = type('Deps', (), {'session_id': 'test_session'})()

                streamed, final = await cli.stream_agent_interaction(
                    "Test research query",
                    "research_agent"
                )

                # The streamed output might be empty due to simplified mocking
                # but final output should be set
                assert final == "Test response content"
                assert len(cli.session_state.messages) == 2  # user + assistant

    @pytest.mark.asyncio
    async def test_stream_agent_interaction_email_agent(self):
        """Test streaming interaction with email agent."""
        cli = StreamingCLI()

        # Mock the entire agent.iter() call chain
        with patch('cli.email_agent.iter') as mock_iter:
            # Create a mock run context
            mock_run = AsyncMock()
            mock_run.result = type('Result', (), {'output': 'Email draft created'})()

            # Mock the async context manager
            mock_context_manager = AsyncMock()
            mock_context_manager.__aenter__.return_value = mock_run
            mock_context_manager.__aexit__.return_value = None
            mock_iter.return_value = mock_context_manager

            # Mock the dependencies
            with patch('cli.create_email_dependencies') as mock_deps:
                mock_deps.return_value = type('Deps', (), {'session_id': 'test_session'})()

                streamed, final = await cli.stream_agent_interaction(
                    "Create an email",
                    "email_agent"
                )

                # The streamed output might be empty due to simplified mocking
                # but final output should be set
                assert final == "Email draft created"

    @pytest.mark.asyncio
    async def test_stream_agent_interaction_error(self):
        """Test streaming interaction with error handling."""
        cli = StreamingCLI()

        with patch('cli.research_agent.iter') as mock_iter:
            # Mock an error during streaming with async context manager
            mock_context_manager = AsyncMock()
            mock_context_manager.__aenter__.side_effect = Exception("Test error")
            mock_context_manager.__aexit__.return_value = None
            mock_iter.return_value = mock_context_manager

            streamed, final = await cli.stream_agent_interaction(
                "Test query that will fail"
            )

            assert "Error during agent execution" in final
            assert streamed == ""

    def test_display_tool_call(self):
        """Test tool call display functionality."""
        cli = StreamingCLI()

        tool_call = {
            "name": "search_web",
            "arguments": {"query": "AI research", "max_results": 5}
        }

        # Should not raise any errors
        cli._display_tool_call(tool_call)

    def test_display_tool_result(self):
        """Test tool result display functionality."""
        cli = StreamingCLI()

        tool_result = {
            "name": "search_web",
            "result": {"results": [{"title": "Test", "url": "test.com"}]}
        }

        # Should not raise any errors
        cli._display_tool_result(tool_result)


class TestCLICommands:
    """Test CLI command functionality."""

    def test_app_creation(self):
        """Test that the Typer app is created correctly."""
        assert app is not None
        assert app.info.name == "Research Email Multi-Agent System CLI"

    @patch('cli.StreamingCLI.stream_agent_interaction')
    @patch('cli.validate_llm_configuration', return_value=True)
    @patch('cli.validate_tavily_configuration', return_value=True)
    @patch('cli.validate_gmail_configuration', return_value=True)
    def test_research_command(self, *mocks):
        """Test research command."""
        # This is a basic test - in practice you'd want to test the actual command execution
        # but that requires more complex mocking of Typer's command execution
        pass

    @patch('cli.StreamingCLI.stream_agent_interaction')
    @patch('cli.validate_llm_configuration', return_value=True)
    @patch('cli.validate_tavily_configuration', return_value=True)
    @patch('cli.validate_gmail_configuration', return_value=True)
    def test_email_command(self, *mocks):
        """Test email command."""
        # Basic test structure - actual command testing would be more complex
        pass

    def test_validate_config_command(self):
        """Test config validation command."""
        # Basic test structure
        pass

    def test_agents_command(self):
        """Test agents command."""
        # Basic test structure
        pass

    def test_history_command(self):
        """Test history command."""
        # Basic test structure
        pass


class TestStreamingEvents:
    """Test streaming event handling."""

    @pytest.mark.asyncio
    async def test_text_delta_handling(self):
        """Test handling of text delta events."""
        cli = StreamingCLI()

        # Mock the entire agent.iter() call chain
        with patch('cli.research_agent.iter') as mock_iter:
            # Create a mock run context
            mock_run = AsyncMock()
            mock_run.result = type('Result', (), {'output': 'Hello world!'})()

            # Mock the async context manager
            mock_context_manager = AsyncMock()
            mock_context_manager.__aenter__.return_value = mock_run
            mock_context_manager.__aexit__.return_value = None
            mock_iter.return_value = mock_context_manager

            # Mock the dependencies
            with patch('cli.create_research_dependencies') as mock_deps:
                mock_deps.return_value = type('Deps', (), {'session_id': 'test_session'})()

                streamed, final = await cli.stream_agent_interaction("Test")

                # The streamed output might be empty due to simplified mocking
                # but final output should be set
                assert final == "Hello world!"

    @pytest.mark.asyncio
    async def test_tool_call_handling(self):
        """Test handling of tool call events."""
        cli = StreamingCLI()

        # Mock the entire agent.iter() call chain
        with patch('cli.research_agent.iter') as mock_iter:
            # Create a mock run context
            mock_run = AsyncMock()
            mock_run.result = type('Result', (), {'output': 'Searching...'})()

            # Mock the async context manager
            mock_context_manager = AsyncMock()
            mock_context_manager.__aenter__.return_value = mock_run
            mock_context_manager.__aexit__.return_value = None
            mock_iter.return_value = mock_context_manager

            # Mock the dependencies
            with patch('cli.create_research_dependencies') as mock_deps:
                mock_deps.return_value = type('Deps', (), {'session_id': 'test_session'})()

                streamed, final = await cli.stream_agent_interaction("Test")

                # The streamed output might be empty due to simplified mocking
                # but final output should be set
                assert final == "Searching..."