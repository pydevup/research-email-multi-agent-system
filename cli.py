"""
Streaming CLI interface for Research Email Multi-Agent System using Rich and Typer.
"""

import asyncio
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.table import Table
from rich.spinner import Spinner
from rich.prompt import Prompt
from rich.markdown import Markdown

from pydantic_ai import Agent
from research_agent import research_agent
from email_agent import email_agent
from dependencies import create_research_dependencies, create_email_dependencies
from models import ChatMessage, SessionState
from providers import validate_llm_configuration, validate_tavily_configuration, validate_gmail_configuration

console = Console()
app = typer.Typer(name="Research Email Multi-Agent System CLI", help="Research Email Multi-Agent System CLI")


class StreamingCLI:
    """Streaming CLI interface for the multi-agent system."""

    def __init__(self):
        self.session_state = SessionState(
            session_id=f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        self.current_agent = "research_agent"

    async def stream_agent_interaction(
        self,
        user_input: str,
        agent_name: str = "research_agent"
    ) -> tuple[str, str]:
        """
        Stream agent interaction with real-time output.

        Args:
            user_input: User input message
            agent_name: Name of the agent to use

        Returns:
            Tuple of (streamed_output, final_output)
        """
        # Select agent and create appropriate dependencies
        if agent_name == "research_agent":
            agent = research_agent
            deps = create_research_dependencies()
        elif agent_name == "email_agent":
            agent = email_agent
            deps = create_email_dependencies()
        else:
            raise ValueError(f"Unknown agent: {agent_name}")

        deps.session_id = self.session_state.session_id

        # Add user message to session
        self.session_state.messages.append(
            ChatMessage(role="user", content=user_input)
        )

        # Stream the response
        streamed_output = ""
        final_output = ""

        with Live("", console=console, refresh_per_second=10) as live:
            try:
                async with agent.iter(user_input, deps=deps) as run:
                    async for node in run:
                        # Handle user prompt node
                        if Agent.is_user_prompt_node(node):
                            pass  # Clean start - no processing messages

                        # Handle model request node - stream the thinking process
                        elif Agent.is_model_request_node(node):
                            # Stream model request events for real-time text
                            async with node.stream(run.ctx) as request_stream:
                                async for event in request_stream:
                                    # Handle different event types based on their type
                                    event_type = type(event).__name__

                                    if event_type == "PartDeltaEvent":
                                        # Extract content from delta
                                        if hasattr(event, 'delta') and hasattr(event.delta, 'content_delta'):
                                            delta_text = event.delta.content_delta
                                            if delta_text:
                                                streamed_output += delta_text
                                                live.update(self._format_streaming_output(streamed_output))
                                    elif event_type == "FinalResultEvent":
                                        # Final result event - no action needed, we'll get result from run.result
                                        pass

                        # Handle tool calls
                        elif Agent.is_call_tools_node(node):
                            # Stream tool execution events
                            async with node.stream(run.ctx) as tool_stream:
                                async for event in tool_stream:
                                    event_type = type(event).__name__

                                    if event_type == "FunctionToolCallEvent":
                                        # Extract tool name and arguments
                                        tool_name = "Unknown Tool"
                                        args = None

                                        # Check if the part attribute contains the tool call
                                        if hasattr(event, 'part'):
                                            part = event.part

                                            # Check if part has tool_name directly
                                            if hasattr(part, 'tool_name'):
                                                tool_name = part.tool_name
                                            elif hasattr(part, 'function_name'):
                                                tool_name = part.function_name
                                            elif hasattr(part, 'name'):
                                                tool_name = part.name

                                            # Check for arguments in part
                                            if hasattr(part, 'args'):
                                                args = part.args
                                            elif hasattr(part, 'arguments'):
                                                args = part.arguments

                                        self._display_tool_call({
                                            "name": tool_name,
                                            "arguments": args or {}
                                        })

                                    elif event_type == "FunctionToolResultEvent":
                                        # Display tool result
                                        # Pydantic AI stores tool results in event.result.content
                                        if hasattr(event, 'result') and hasattr(event.result, 'content'):
                                            tool_result = event.result.content
                                            if tool_result is not None:
                                                # Convert result to string for display
                                                if isinstance(tool_result, (dict, list)):
                                                    result = json.dumps(tool_result, indent=2, default=str)
                                                else:
                                                    result = str(tool_result)
                                            else:
                                                result = "None result"
                                        else:
                                            result = "No result"

                                        self._display_tool_result({
                                            "name": "tool_result",  # We don't have tool_name in this event
                                            "result": result
                                        })

                        # Handle end node
                        elif Agent.is_end_node(node):
                            pass

                # Get final result if not already set
                if not final_output:
                    final_result = run.result
                    if hasattr(final_result, 'output') and final_result.output:
                        final_output = final_result.output
                    else:
                        # Ensure we have a valid string
                        final_output = str(final_result) if final_result else "No response generated"

                # If final_output is still empty, use streamed_output
                if not final_output:
                    final_output = streamed_output

                # Ensure final_output is a valid string for ChatMessage
                if not isinstance(final_output, str) or not final_output.strip():
                    final_output = "No response generated"

                # Add assistant message to session
                self.session_state.messages.append(
                    ChatMessage(role="assistant", content=final_output)
                )

            except Exception as e:
                error_msg = f"Error during agent execution: {str(e)}"
                console.print(f"[red]Error: {error_msg}[/red]")
                final_output = error_msg

                # Add error message to session as a valid string
                self.session_state.messages.append(
                    ChatMessage(role="assistant", content=error_msg)
                )

        return streamed_output, final_output

    def _format_streaming_output(self, text: str) -> Panel:
        """Format streaming output as a rich panel."""
        # Convert agent name from "research_agent" to "Research Agent"
        agent_name = self.current_agent.replace("_", " ").title()
        return Panel(
            Markdown(text),
            title=f"🤖 {agent_name}",
            title_align="left",
            border_style="blue"
        )

    def _display_tool_call(self, tool_call: Dict[str, Any]):
        """Display tool call information."""
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Tool Call", style="cyan")
        table.add_column("Arguments", style="white")

        tool_name = tool_call.get("name", "unknown")
        args = json.dumps(tool_call.get("arguments", {}), indent=2)

        table.add_row(tool_name, args)
        console.print(table)

    def _display_tool_result(self, tool_result: Dict[str, Any]):
        """Display tool result information."""
        table = Table(show_header=True, header_style="bold green")
        table.add_column("Tool Result", style="cyan")
        table.add_column("Result", style="white")

        tool_name = tool_result.get("name", "unknown")
        result = json.dumps(tool_result.get("result", {}), indent=2)

        table.add_row(tool_name, result)
        console.print(table)

    def display_conversation_history(self):
        """Display the conversation history."""
        if not self.session_state.messages:
            console.print("[yellow]No conversation history yet.[/yellow]")
            return

        console.print("\n[bold]Conversation History:[/bold]")
        for msg in self.session_state.messages:
            role_emoji = "👤" if msg.role == "user" else "🤖"
            role_color = "green" if msg.role == "user" else "blue"
            console.print(
                f"{role_emoji} [{role_color}]{msg.role.title()}:[/{role_color}] {msg.content}"
            )

    def display_agent_info(self):
        """Display information about available agents."""
        table = Table(title="Available Agents", show_header=True, header_style="bold magenta")
        table.add_column("Agent", style="cyan")
        table.add_column("Description", style="white")
        table.add_column("Tools", style="yellow")

        # Research Agent info - use hardcoded tool count for now
        table.add_row(
            "Research Agent",
            "Searches web and creates email drafts",
            "4 tools"
        )

        # Email Agent info - use hardcoded tool count for now
        table.add_row(
            "Email Agent",
            "Creates professional email drafts",
            "2 tools"
        )

        console.print(table)


# Global CLI instance
cli = StreamingCLI()


@app.command()
def chat():
    """Start interactive chat with the research agent."""
    console.print("[bold green]🤖 Research Email Multi-Agent System[/bold green]")
    console.print("[dim]Type 'quit' to exit, 'help' for commands[/dim]\n")

    # Validate configuration
    if not validate_llm_configuration():
        console.print("[red]❌ LLM configuration validation failed. Please check your .env file.[/red]")
        return

    if not validate_tavily_configuration():
        console.print("[yellow]⚠️  Tavily API configuration may be incomplete.[/yellow]")

    if not validate_gmail_configuration():
        console.print("[yellow]⚠️  Gmail API configuration may be incomplete.[/yellow]")

    while True:
        try:
            user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")

            if user_input.lower() in ['quit', 'exit', 'q']:
                console.print("[green]👋 Goodbye![/green]")
                break
            elif user_input.lower() in ['help', 'h']:
                _display_help()
                continue
            elif user_input.lower() in ['history', 'hist']:
                cli.display_conversation_history()
                continue
            elif user_input.lower() in ['agents', 'agent']:
                cli.display_agent_info()
                continue
            elif user_input.lower() in ['clear', 'cls']:
                cli.session_state.messages.clear()
                console.print("[green]🗑️  Conversation history cleared.[/green]")
                continue

            # Process the input
            asyncio.run(cli.stream_agent_interaction(user_input))

        except KeyboardInterrupt:
            console.print("\n[green]👋 Goodbye![/green]")
            break
        except Exception as e:
            console.print(f"[red]❌ Error: {str(e)}[/red]")


@app.command()
def research(query: str):
    """Perform a research query."""
    console.print(f"[bold green]🔍 Researching: {query}[/bold green]")
    asyncio.run(cli.stream_agent_interaction(f"Research: {query}"))


@app.command()
def email(
    recipient: str,
    subject: str,
    context: str,
    research_query: Optional[str] = None
):
    """Create an email draft."""
    if research_query:
        prompt = f"""Create an email to {recipient} with subject "{subject}".

Context: {context}

Please research: {research_query}

Then create a professional email draft based on the research findings."""
    else:
        prompt = f"""Create an email to {recipient} with subject "{subject}".

Context: {context}"""

    console.print(f"[bold green]📧 Creating email draft for {recipient}[/bold green]")
    asyncio.run(cli.stream_agent_interaction(prompt))


@app.command()
def validate_config():
    """Validate system configuration."""
    console.print("[bold]🔧 Validating System Configuration[/bold]")

    checks = [
        ("LLM Configuration", validate_llm_configuration()),
        ("Tavily API", validate_tavily_configuration()),
        ("Gmail API", validate_gmail_configuration()),
    ]

    table = Table(show_header=True, header_style="bold")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="white")

    for component, status in checks:
        status_text = "✅ Valid" if status else "❌ Invalid"
        status_style = "green" if status else "red"
        table.add_row(component, f"[{status_style}]{status_text}[/{status_style}]")

    console.print(table)


@app.command()
def agents():
    """Display information about available agents."""
    cli.display_agent_info()


@app.command()
def history():
    """Display conversation history."""
    cli.display_conversation_history()


def _display_help():
    """Display help information."""
    help_text = """
**Available Commands:**
- `research <query>` - Perform a research query
- `email <recipient> <subject> <context> [research_query]` - Create email draft
- `validate-config` - Validate system configuration
- `agents` - Show available agents
- `history` - Show conversation history
- `clear` - Clear conversation history
- `help` - Show this help
- `quit` - Exit the application

**Interactive Features:**
- Real-time streaming responses
- Tool call visibility
- Conversation history
- Multiple agent support
    """
    console.print(Markdown(help_text))


if __name__ == "__main__":
    app()