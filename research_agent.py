"""
Research Agent that uses Tavily API and can invoke Email Agent.
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from pydantic_ai import Agent, RunContext

from providers import get_llm_model
from email_agent import email_agent, EmailAgentDependencies
from tools import search_web_tool
from models import AgentDelegationRequest, AgentDelegationResponse

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """
You are an expert research assistant with the ability to search the web, summarize research findings, and create email drafts. Your primary goal is to help users find relevant information and communicate findings effectively.

Your capabilities:
1. **Web Search**: Use Tavily Search to find current, relevant information on any topic
2. **Research Summarization**: Create comprehensive summaries of search results
3. **Email Creation**: Create professional email drafts through Gmail when requested

**IMPORTANT WORKFLOW:**
- When conducting research, FIRST use the search_web tool to gather information
- Store the search results from search_web - you MUST pass these results to summarize_research
- THEN use the summarize_research tool with the search results to create a summary
- The summarize_research tool REQUIRES search_results parameter from a previous search_web call
- You CANNOT call summarize_research without first calling search_web and passing the results

When conducting research:
- Use specific, targeted search queries
- Analyze search results for relevance and credibility
- Pass search results to the summarize_research tool for comprehensive summaries
- Synthesize information from multiple sources
- Provide clear, well-organized summaries
- Include source URLs for reference

When creating emails:
- Use research findings to create informed, professional content
- Adapt tone and detail level to the intended recipient
- Include relevant sources and citations when appropriate
- Ensure emails are clear, concise, and actionable

Always strive to provide accurate, helpful, and actionable information.
"""


@dataclass
class ResearchAgentDependencies:
    """Dependencies for the research agent - only configuration, no tool instances."""
    tavily_api_key: str
    gmail_credentials_path: str
    gmail_token_path: str
    session_id: Optional[str] = None


# Initialize the research agent
research_agent = Agent(
    get_llm_model(),
    deps_type=ResearchAgentDependencies,
    system_prompt=SYSTEM_PROMPT
)


@research_agent.tool
async def search_web(
    ctx: RunContext[ResearchAgentDependencies],
    query: str,
    max_results: int = 10
) -> List[Dict[str, Any]]:
    """
    Search the web using Tavily API.

    Args:
        query: Search query
        max_results: Maximum number of results to return (1-20)

    Returns:
        List of search results with title, URL, content, and score
    """
    try:
        # Ensure max_results is within valid range
        max_results = min(max(max_results, 1), 20)

        results = await search_web_tool(
            api_key=ctx.deps.tavily_api_key,
            query=query,
            max_results=max_results
        )

        logger.info(f"Found {len(results)} results for query: {query}")
        return results

    except Exception as e:
        logger.error(f"Web search failed: {e}")
        return [{"error": f"Search failed: {str(e)}"}]


@research_agent.tool
async def delegate_to_email_agent(
    ctx: RunContext[ResearchAgentDependencies],
    prompt: str,
    context: Optional[Dict[str, Any]] = None
) -> AgentDelegationResponse:
    """
    Delegate a task to the email agent.

    Args:
        prompt: Prompt for the email agent
        context: Optional additional context for the email agent

    Returns:
        Response from the email agent
    """
    try:
        # Create dependencies for email agent
        email_deps = EmailAgentDependencies(
            gmail_credentials_path=ctx.deps.gmail_credentials_path,
            gmail_token_path=ctx.deps.gmail_token_path,
            session_id=ctx.deps.session_id
        )

        # Run the email agent
        result = await email_agent.run(
            prompt,
            deps=email_deps,
            usage=ctx.usage  # Pass usage for token tracking
        )

        logger.info(f"Email agent invoked with prompt: {prompt[:100]}...")

        return AgentDelegationResponse(
            success=True,
            agent_response=result.output,
            target_agent="email_agent"
        )

    except Exception as e:
        logger.error(f"Failed to delegate to email agent: {e}")
        return AgentDelegationResponse(
            success=False,
            agent_response=f"Delegation failed: {str(e)}",
            target_agent="email_agent"
        )


@research_agent.tool
async def create_email_draft(
    ctx: RunContext[ResearchAgentDependencies],
    recipient_email: str,
    subject: str,
    context: str,
    research_summary: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create an email draft based on research context using the Email Agent.

    Args:
        recipient_email: Email address of the recipient
        subject: Email subject line
        context: Context or purpose for the email
        research_summary: Optional research findings to include

    Returns:
        Dictionary with draft creation results
    """
    try:
        # Prepare the email content prompt
        if research_summary:
            email_prompt = f"""
Create a professional email to {recipient_email} with the subject "{subject}".

Context: {context}

Research Summary:
{research_summary}

Please create a well-structured email that:
1. Has an appropriate greeting
2. Provides clear context
3. Summarizes the key research findings professionally
4. Includes actionable next steps if appropriate
5. Ends with a professional closing

The email should be informative but concise, and maintain a professional yet friendly tone.
"""
        else:
            email_prompt = f"""
Create a professional email to {recipient_email} with the subject "{subject}".

Context: {context}

Please create a well-structured email that addresses the context provided.
"""

        # Delegate to email agent
        delegation_result = await delegate_to_email_agent(
            ctx,
            prompt=email_prompt,
            context={
                "recipient": recipient_email,
                "subject": subject,
                "research_context": context
            }
        )

        if delegation_result.success:
            logger.info(f"Email draft created successfully for recipient: {recipient_email}")
            return {
                "success": True,
                "agent_response": delegation_result.agent_response,
                "recipient": recipient_email,
                "subject": subject,
                "context": context
            }
        else:
            return {
                "success": False,
                "error": delegation_result.agent_response,
                "recipient": recipient_email,
                "subject": subject
            }

    except Exception as e:
        logger.error(f"Failed to create email draft via Email Agent: {e}")
        return {
            "success": False,
            "error": str(e),
            "recipient": recipient_email,
            "subject": subject
        }


@research_agent.tool
async def summarize_research(
    ctx: RunContext[ResearchAgentDependencies],
    topic: str,
    search_results: Optional[List[Dict[str, Any]]] = None,
    focus_areas: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a comprehensive summary of research findings.

    Args:
        topic: Main research topic (required)
        search_results: Optional list of search result dictionaries from search_web tool
        focus_areas: Optional specific areas to focus on

    Returns:
        Dictionary with research summary
    """
    try:
        if search_results is None:
            return {
                "summary": "ERROR: No search results provided. You must first call search_web to get results, then pass those results to summarize_research.",
                "key_points": [],
                "sources": []
            }

        if not search_results:
            return {
                "summary": "No search results provided for summarization.",
                "key_points": [],
                "sources": []
            }

        # Check if search results contain errors
        if len(search_results) == 1 and "error" in search_results[0]:
            error_msg = search_results[0]["error"]
            return {
                "summary": f"Unable to summarize research due to search error: {error_msg}",
                "key_points": [],
                "sources": []
            }

        # Extract key information
        sources = []
        descriptions = []

        for result in search_results:
            # Skip error results
            if "error" in result:
                continue

            if "title" in result and "url" in result:
                sources.append(f"- {result['title']}: {result['url']}")
                if "content" in result:
                    descriptions.append(result["content"])

        # Check if we have any valid results
        if not sources:
            return {
                "summary": "No valid search results available for summarization.",
                "key_points": [],
                "sources": []
            }

        # Create summary content
        content_summary = "\n".join(descriptions[:5])  # Limit to top 5 descriptions
        sources_list = "\n".join(sources[:10])  # Limit to top 10 sources

        focus_text = f"\nSpecific focus areas: {focus_areas}" if focus_areas else ""

        summary = f"""
Research Summary: {topic}{focus_text}

Key Findings:
{content_summary}

Sources:
{sources_list}
"""

        return {
            "summary": summary,
            "topic": topic,
            "sources_count": len(sources),
            "key_points": descriptions[:5]
        }

    except Exception as e:
        logger.error(f"Failed to summarize research: {e}")
        return {
            "summary": f"Failed to summarize research: {str(e)}",
            "key_points": [],
            "sources": []
        }


# Convenience function to create research agent with dependencies
def create_research_agent(
    tavily_api_key: str,
    gmail_credentials_path: str,
    gmail_token_path: str,
    session_id: Optional[str] = None
) -> Agent:
    """
    Create a research agent with specified dependencies.

    Args:
        tavily_api_key: Tavily API key
        gmail_credentials_path: Path to Gmail credentials.json
        gmail_token_path: Path to Gmail token.json
        session_id: Optional session identifier

    Returns:
        Configured research agent
    """
    return research_agent