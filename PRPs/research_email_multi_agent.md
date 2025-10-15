---
name: "Research Email Multi-Agent System"
description: "Multi-agent Pydantic AI system with research agent and email draft agent integration using Tavily API and Gmail API with streaming CLI"
---

## Purpose

Build a production-grade multi-agent Pydantic AI system where a primary research agent can delegate email drafting tasks to a sub-agent, with real-time streaming CLI interface using `.iter()` function and proper error handling.

## Core Principles

1. **Multi-Agent Architecture**: Research agent delegates to email agent as a tool
2. **Streaming First**: Use `.iter()` function for real-time output streaming
3. **Production Ready**: Security, testing, and monitoring for production deployments
4. **Type Safety**: Leverage Pydantic validation throughout the system
5. **Error Resilience**: Comprehensive error handling and retry mechanisms

---

## Goal

Create a multi-agent system where:
- **Research Agent**: Uses Tavily API to search the web and find relevant information
- **Email Agent**: Creates professional email drafts using Gmail API
- **CLI Interface**: Beautiful streaming interface using Rich and Typer
- **Agent Delegation**: Research agent can delegate email creation to email agent
- **Streaming Output**: Real-time streaming of agent responses and tool calls

## Why

This system solves the problem of automated research and communication by combining web search capabilities with professional email drafting. The multi-agent approach allows specialization while maintaining a unified user experience through the streaming CLI.

## What

### Agent Type Classification
- [x] **Tool-Enabled Agent**: Research agent with web search and delegation capabilities
- [x] **Tool-Enabled Agent**: Email agent with Gmail API integration
- [x] **Multi-Agent System**: Agent delegation and coordination
- [x] **Structured Output Agent**: Email drafts with Pydantic validation

### Model Provider Requirements
- [x] **OpenAI**: `openai:gpt-4o` or `openai:gpt-4o-mini`
- [x] **Anthropic**: `anthropic:claude-3-5-sonnet-20241022` or `anthropic:claude-3-5-haiku-20241022`
- [x] **Fallback Strategy**: Multiple provider support with automatic failover

### External Integrations
- [x] **Tavily API**: Web search and research capabilities
- [x] **Gmail API**: Email draft creation with OAuth2 authentication
- [x] **Rich/Typer**: Beautiful CLI with streaming output
- [x] **Environment Configuration**: Secure API key management

### Success Criteria
- [ ] Research agent successfully searches web using Tavily API
- [ ] Email agent creates Gmail drafts with proper authentication
- [ ] Agent delegation works seamlessly between research and email agents
- [ ] CLI streams output in real-time using `.iter()` function
- [ ] Comprehensive error handling for all external API calls
- [ ] Security measures implemented (API keys, OAuth2, rate limiting)

## All Needed Context

### PydanticAI Documentation & Research

```yaml
# MCP servers
- mcp: Archon
  query: "PydanticAI multi-agent patterns streaming .iter function"
  why: Core framework understanding for multi-agent systems

# ESSENTIAL PYDANTIC AI DOCUMENTATION
- url: https://ai.pydantic.dev/
  why: Official PydanticAI documentation with getting started guide
  content: Agent creation, model providers, dependency injection patterns

- url: https://ai.pydantic.dev/agents/
  why: Agent architecture and configuration patterns
  content: System prompts, output types, execution methods, agent composition

- url: https://ai.pydantic.dev/tools/
  why: Tool integration patterns and function registration
  content: @agent.tool decorators, RunContext usage, parameter validation

- url: https://ai.pydantic.dev/testing/
  why: Testing strategies specific to PydanticAI agents
  content: TestModel, FunctionModel, Agent.override(), pytest patterns

# Streaming and .iter() function research
- url: https://ai.pydantic.dev/changelog/
  why: Streaming implementation with .iter() API
  content: "Use .iter() API to fully replace existing streaming implementation"

# Tavily API Integration
- url: https://docs.tavily.com/sdk/python/quick-start
  why: Tavily Python SDK documentation for web search
  content: Installation, usage, search function, error handling

- url: https://github.com/tavily-ai/tavily-python
  why: Tavily Python SDK source code and examples
  content: TavilyClient usage, search parameters, response formats

# Gmail API Integration
- url: https://developers.google.com/gmail/api/quickstart/python
  why: Gmail API Python quickstart guide
  content: OAuth2 setup, draft creation, authentication patterns

- url: https://developers.google.com/identity/protocols/oauth2/scopes
  why: OAuth2 scopes for Gmail API
  content: Required scopes for draft creation and authentication

# Rich/Typer CLI Integration
- path: examples/main_agent_reference/cli.py
  why: Reference implementation for streaming CLI with Rich/Typer
  content: Real-time tool call display, streaming output, conversation history

# Existing Codebase Patterns
- path: examples/main_agent_reference/research_agent.py
  why: Reference research agent implementation
  content: Agent structure, tool patterns, dependency injection

- path: examples/main_agent_reference/tools.py
  why: Reference tool implementation patterns
  content: Pure tool functions, error handling, async patterns

- path: examples/main_agent_reference/models.py
  why: Reference Pydantic model patterns
  content: Structured output models, validation, configuration

- path: examples/main_agent_reference/settings.py
  why: Reference configuration management
  content: Environment variables, pydantic-settings, API key management
```

### Agent Architecture Research

```yaml
# PydanticAI Multi-Agent Patterns
agent_structure:
  research_agent:
    configuration:
      - settings.py: Environment-based configuration with pydantic-settings
      - providers.py: Model provider abstraction with get_llm_model()
      - Environment variables for Tavily API key and model selection

    agent_definition:
      - Default to string output (no result_type unless structured output needed)
      - Use get_llm_model() from providers.py for model configuration
      - System prompt for truthful research assistant behavior
      - Dataclass dependencies for Tavily API key and Gmail credentials

    tool_integration:
      - @agent.tool for search_web with Tavily API
      - @agent.tool for delegate_to_email_agent with email agent delegation
      - Proper error handling and logging in tool implementations
      - Dependency injection through RunContext.deps

  email_agent:
    configuration:
      - Same settings.py and providers.py as research agent
      - Environment variables for Gmail OAuth2 credentials

    agent_definition:
      - Default to string output
      - System prompt for professional email composition
      - Dataclass dependencies for Gmail credentials and token paths

    tool_integration:
      - @agent.tool for authenticate_gmail with OAuth2 flow
      - @agent.tool for create_gmail_draft with EmailDraft model
      - Proper OAuth2 token management and refresh

# Streaming CLI Architecture
cli_structure:
  streaming:
    - Use agent.iter() for real-time streaming
    - Rich console for beautiful output formatting
    - Real-time tool call visibility
    - Conversation history management

  tool_display:
    - Show tool calls as they happen
    - Display tool arguments and results
    - Handle streaming events properly
    - Maintain conversation context
```

### Security and Production Considerations

```yaml
# Security Patterns
security_requirements:
  api_management:
    environment_variables: ["TAVILY_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY"]
    secure_storage: "Never commit API keys to version control"
    gmail_credentials: "Store OAuth2 credentials in credentials/ directory"

  input_validation:
    sanitization: "Validate all user inputs with Pydantic models"
    prompt_injection: "Implement prompt injection prevention strategies"
    rate_limiting: "Prevent abuse with proper throttling"

  output_security:
    data_filtering: "Ensure no sensitive data in agent responses"
    content_validation: "Validate output structure and content"
    logging_safety: "Safe logging without exposing secrets"

# Production Readiness
production_patterns:
  error_handling:
    - Comprehensive try/except blocks for all external API calls
    - Retry mechanisms for transient failures
    - Graceful degradation when services are unavailable

  monitoring:
    - Structured logging for observability
    - Performance metrics for API calls
    - Error tracking and alerting

  configuration:
    - Environment-based configuration
    - Validation of all required settings
    - Fallback values for optional settings
```

### Common PydanticAI Gotchas

```yaml
# Multi-Agent Specific Gotchas
implementation_gotchas:
  agent_delegation:
    issue: "Agent-to-agent delegation requires proper dependency passing"
    research: "examples/main_agent_reference/research_agent.py:150-154"
    solution: "Pass dependencies correctly when calling sub-agent.run()"

  streaming_complexity:
    issue: "Streaming with .iter() requires proper event handling"
    research: "examples/main_agent_reference/cli.py:44-142"
    solution: "Follow reference implementation for streaming event handling"

  oauth2_authentication:
    issue: "Gmail OAuth2 requires local server flow for initial auth"
    research: "Gmail API Python quickstart documentation"
    solution: "Implement OAuth2 flow with token storage and refresh"

  tool_error_propagation:
    issue: "Tool failures in sub-agents can break main agent execution"
    research: "examples/main_agent_reference/tools.py:115-120"
    solution: "Implement comprehensive error handling in all tools"
```

## Implementation Blueprint

### Technology Research Phase

**RESEARCH COMPLETED - Ready for implementation:**

✅ **PydanticAI Framework Deep Dive:**
- [x] Agent creation patterns and best practices
- [x] Model provider configuration and fallback strategies
- [x] Tool integration patterns (@agent.tool vs @agent.tool_plain)
- [x] Dependency injection system and type safety
- [x] Testing strategies with TestModel and FunctionModel

✅ **Multi-Agent Architecture Investigation:**
- [x] Agent delegation patterns and dependency passing
- [x] Project structure conventions for multi-agent systems
- [x] System prompt design for specialized agents
- [x] Async/sync patterns and streaming support with .iter()
- [x] Error handling and retry mechanisms across agents

✅ **External API Integration Research:**
- [x] Tavily API Python SDK usage and error handling
- [x] Gmail API OAuth2 authentication and draft creation
- [x] Rich/Typer CLI streaming implementation patterns
- [x] Environment configuration and security patterns

### Agent Implementation Plan

```yaml
Implementation Task 1 - Project Structure Setup:
  CREATE multi-agent project structure:
    - settings.py: Environment-based configuration with pydantic-settings
    - providers.py: Model provider abstraction with get_llm_model()
    - research_agent.py: Main research agent with Tavily integration
    - email_agent.py: Email drafting agent with Gmail integration
    - tools.py: Shared tool functions for both agents
    - models.py: Pydantic models for structured outputs
    - dependencies.py: External service dependencies
    - cli.py: Streaming CLI interface with Rich/Typer
    - tests/: Comprehensive test suite

Implementation Task 2 - Gmail OAuth2 Pre-Validation:
  CREATE OAuth2 validation infrastructure:
    - scripts/validate_gmail_oauth.py: Step-by-step OAuth2 setup validation
    - credentials/.gitkeep: Ensure credentials folder exists in repo
    - Guided credential setup with clear error messages
    - Test OAuth2 flow before agent implementation begins
    - Validate Gmail API access and permissions

Implementation Task 3 - Research Agent Development:
  IMPLEMENT research_agent.py:
    - Use get_llm_model() from providers.py
    - System prompt for truthful research assistant
    - Dataclass dependencies for Tavily API key
    - search_web tool with Tavily API integration
    - delegate_to_email_agent tool for agent delegation
    - Error handling for external API calls

Implementation Task 4 - Email Agent Development:
  IMPLEMENT email_agent.py:
    - Use get_llm_model() from providers.py
    - System prompt for professional email composition
    - Dataclass dependencies for Gmail credentials
    - authenticate_gmail tool with OAuth2 flow
    - create_gmail_draft tool with EmailDraft model
    - OAuth2 token management and refresh

Implementation Task 5 - Tool Integration:
  DEVELOP tools.py:
    - search_web_tool: Pure function for Tavily API calls
    - gmail_auth_tool: OAuth2 authentication helper
    - create_draft_tool: Gmail draft creation function
    - Parameter validation with proper type hints
    - Comprehensive error handling and retry mechanisms

Implementation Task 6 - Data Models and Dependencies:
  CREATE models.py and dependencies.py:
    - EmailDraft: Pydantic model for email creation
    - ResearchAgentDependencies: Tavily API key and Gmail credentials
    - EmailAgentDependencies: Gmail OAuth2 credentials
    - Input validation models for all tools

Implementation Task 7 - Streaming CLI Development:
  IMPLEMENT cli.py:
    - Use agent.iter() for real-time streaming
    - Rich console for beautiful output formatting
    - Real-time tool call visibility
    - Conversation history management
    - Error handling and user-friendly messages

Implementation Task 8 - Comprehensive Testing:
  IMPLEMENT testing suite:
    - TestModel integration for rapid development
    - FunctionModel tests for custom behavior
    - Agent.override() patterns for isolation
    - Integration tests with real providers 
    - Tool validation and error scenario testing

Implementation Task 9 - Security and Configuration:
  SETUP security patterns:
    - Environment variable management for all API keys
    - OAuth2 credential storage and management
    - Input sanitization and validation
    - Rate limiting implementation
    - Secure logging and monitoring

Implementation Task 10 - Documentation:
  CREATE documentation:
    - README with setup instructions including credentials/ folder setup
    - Google Cloud Console credential setup guide
    - API key configuration guide
    - Usage examples and CLI commands
    - Project structure documentation
```

## Validation Loop

### Level 1: Multi-Agent Structure Validation

```bash
# Verify complete multi-agent project structure
find . -name "*.py" | grep -E "(agent|tools|models|dependencies|settings|providers|cli)" | sort

# Verify all required files present
test -f research_agent.py && echo "Research agent present"
test -f email_agent.py && echo "Email agent present"
test -f tools.py && echo "Tools module present"
test -f models.py && echo "Models module present"
test -f dependencies.py && echo "Dependencies module present"
test -f settings.py && echo "Settings module present"
test -f providers.py && echo "Providers module present"
test -f cli.py && echo "CLI module present"

# Verify proper PydanticAI imports
grep -q "from pydantic_ai import Agent" research_agent.py
grep -q "from pydantic_ai import Agent" email_agent.py
grep -q "@agent.tool" tools.py
grep -q "from pydantic import BaseModel" models.py

# Expected: All required files with proper PydanticAI patterns
# If missing: Generate missing components with correct patterns
```

### Level 2: Agent Functionality Validation

```bash
# Test both agents can be imported and instantiated
python -c "
from research_agent import research_agent
from email_agent import email_agent
print('Both agents created successfully')
print(f'Research agent tools: {len(research_agent.tools)}')
print(f'Email agent tools: {len(email_agent.tools)}')
"

# Test agent delegation with TestModel
python -c "
from pydantic_ai.models.test import TestModel
from research_agent import research_agent
from dependencies import ResearchAgentDependencies

test_model = TestModel()
with research_agent.override(model=test_model):
    deps = ResearchAgentDependencies(tavily_api_key='test', gmail_credentials_path='test', gmail_token_path='test')
    result = research_agent.run_sync('Search for AI trends', deps=deps)
    print(f'Research agent response: {result.output}')
"

# Expected: Both agents instantiate, tools registered, delegation works
# If failing: Debug agent configuration and tool registration
```

### Level 3: Streaming CLI Validation

```bash
# Test CLI can be imported and basic functions work
python -c "
from cli import stream_agent_interaction
print('CLI module imports successfully')
"

# Test streaming functionality (basic test)
python -c "
import asyncio
from cli import stream_agent_interaction

async def test_streaming():
    streamed, final = await stream_agent_interaction('test', [])
    print(f'Streaming test completed: {len(streamed)} chars streamed')

asyncio.run(test_streaming())
"

# Expected: CLI imports successfully, streaming functions work
# If failing: Debug streaming implementation and async patterns
```

### Level 4: Comprehensive Testing Validation

```bash
# Run complete test suite
python -m pytest tests/ -v

# Test specific agent behavior
python -m pytest tests/test_research_agent.py -v
python -m pytest tests/test_email_agent.py -v
python -m pytest tests/test_tools.py -v
python -m pytest tests/test_cli.py -v

# Expected: All tests pass, comprehensive coverage achieved
# If failing: Fix implementation based on test failures
```

### Level 5: Production Readiness Validation

```bash
# Verify security patterns
grep -r "API_KEY" . | grep -v ".py:" | grep -v ".env.example" # Should not expose keys
test -f .env.example && echo "Environment template present"

# Check error handling
grep -r "try:" . | wc -l  # Should have error handling
grep -r "except" . | wc -l  # Should have exception handling

# Verify logging setup
grep -r "logging\|logger" . | wc -l  # Should have logging

# Expected: Security measures in place, error handling comprehensive, logging configured
# If issues: Implement missing security and production patterns
```

## Final Validation Checklist

### Multi-Agent Implementation Completeness

- [ ] Complete project structure with all required modules
- [ ] Research agent with Tavily API integration and delegation
- [ ] Email agent with Gmail API integration and OAuth2
- [ ] Agent delegation working seamlessly
- [ ] Streaming CLI with real-time output
- [ ] Comprehensive test suite with TestModel and FunctionModel

### PydanticAI Best Practices

- [ ] Type safety throughout with proper type hints and validation
- [ ] Security patterns implemented (API keys, OAuth2, input validation)
- [ ] Error handling and retry mechanisms for robust operation
- [ ] Async/sync patterns consistent and appropriate
- [ ] Documentation and code comments for maintainability

### Production Readiness

- [ ] Environment configuration with .env files and validation
- [ ] OAuth2 credential management and token refresh
- [ ] Logging and monitoring setup for observability
- [ ] Performance optimization and resource management
- [ ] Deployment readiness with proper configuration management

---

## Anti-Patterns to Avoid

### Multi-Agent Development

- ❌ Don't skip agent delegation testing - always test agent-to-agent calls
- ❌ Don't hardcode API keys - use environment variables for all credentials
- ❌ Don't ignore OAuth2 token management - implement proper token refresh
- ❌ Don't create complex tool chains - keep tools focused and composable
- ❌ Don't skip streaming validation - test .iter() functionality thoroughly

### Agent Architecture

- ❌ Don't mix agent responsibilities - keep research and email agents separate
- ❌ Don't ignore dependency injection - use proper type-safe dependency management
- ❌ Don't skip output validation - always use Pydantic models for structured responses
- ❌ Don't forget tool documentation - ensure all tools have proper descriptions

### Security and Production

- ❌ Don't expose sensitive data - validate all outputs and logs for security
- ❌ Don't skip input validation - sanitize and validate all user inputs
- ❌ Don't ignore rate limiting - implement proper throttling for external services
- ❌ Don't deploy without monitoring - include proper observability from the start

**RESEARCH STATUS: COMPLETED** - Comprehensive research completed, ready for implementation.

**CONFIDENCE SCORE: 9/10** - High confidence due to extensive research, existing reference implementations, and clear implementation blueprint.