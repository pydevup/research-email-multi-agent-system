## FEATURE:

- Pydantic AI agent that has another Pydantic AI agent as a tool.
- Research Agent for the primary agent and then an email draft Agent for the subagent.
- Beautiful CLI to interact with the agent with streaming (use the .iter function to stream from the primary (research) Pydantic AI agent).
- Gmail for the email draft agent, Tavily API for the research agent.

## TOOLS:

**Research Agent Tools:**
- `search_web(query: str)` - Searches web using Tavily API. Returns formatted search results with titles, descriptions, and URLs. Handles errors gracefully with clear failure messages.
- `delegate_to_email_agent(research_findings: str, recipients: List[str])` - Delegates email creation to the email agent. Validates Gmail credentials before attempting delegation.

**Email Agent Tools:**
- `authenticate_gmail()` - Handles OAuth2 authentication with Gmail API. Uses local server flow for initial auth.
- `create_gmail_draft(email_draft: EmailDraft)` - Creates a draft email in Gmail without sending. EmailDraft contains to, subject, body, cc, and bcc fields.

## DEPENDENCIES

**ResearchAgentDependencies:**
- `tavily_api_key: str` - API key for Tavily Search API

**EmailAgentDependencies:**
- `credentials_file: str` - Path to Gmail OAuth2 credentials JSON file
- `token_file: str` - Path to stored OAuth2 token

## SYSTEM PROMPT(S)

**Research Agent:**
Truthful research assistant that MUST be completely honest about operation results. Key rules:
- Only claim success when operations actually succeed
- Report tool failures honestly with clear explanations
- Never claim to have sent emails or created drafts unless actually done
- Be helpful but always truthful about capabilities

**Email Agent:**
Professional email composition agent that creates well-structured emails based on research findings. Guidelines:
- Use clear, professional language for business communication
- Structure emails with proper greeting, body, and closing
- Include relevant research insights
- Return properly formatted EmailDraft objects
- Creates drafts only - does not send emails

## EXAMPLES:

- examples/basic_chat_agent - Basic chat agent with conversation memory
- examples/tool_enabled_agent - Tool-enabled agent with web search capabilities  
- examples/structured_output_agent - Structured output agent for data validation
- examples/testing_examples - Testing examples with TestModel and FunctionModel
- examples/main_agent_reference - Best practices for building Pydantic AI agents

## DOCUMENTATION:

Use the Archon MCP server for Pydantic AI documentation
Supplement with Pydantic AI documentation on the web: https://ai.pydantic.dev/

## OTHER CONSIDERATIONS:

- Include a .env.example, README with instructions for setup including how to configure Gmail and Tavily.
- Include the project structure in the README.
- Virtual environment has already been set up with the necessary dependencies.
- Use python_dotenv and load_env() for environment variables
- It's very important that you use .iter and look at the documentation for it to stream output from the Pydantic AI agent
