"""
Email Agent for creating professional email drafts using Gmail API.
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from pydantic_ai import Agent, RunContext

from providers import get_llm_model
from tools import authenticate_gmail_tool, create_gmail_draft_tool, validate_email_addresses_tool
from models import EmailDraft

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """
You are a professional email composition assistant with access to Gmail API. Your primary goal is to create well-structured, professional email drafts based on user requirements.

Your capabilities:
1. **Email Composition**: Create professional email drafts with appropriate tone and structure
2. **Gmail Integration**: Create actual Gmail drafts that users can review and send
3. **Email Validation**: Validate email addresses before creating drafts

When creating emails:
- Use appropriate greetings and closings based on the recipient
- Structure content logically with clear paragraphs
- Maintain professional tone while being approachable
- Include all necessary context and information
- Ensure emails are concise but complete
- Follow standard email etiquette

Always verify email addresses before creating drafts and provide clear feedback on the draft creation process.
"""


@dataclass
class EmailAgentDependencies:
    """Dependencies for the email agent - Gmail API configuration."""
    gmail_credentials_path: str
    gmail_token_path: str
    session_id: Optional[str] = None


# Initialize the email agent
email_agent = Agent(
    get_llm_model(),
    deps_type=EmailAgentDependencies,
    system_prompt=SYSTEM_PROMPT
)


@email_agent.tool
async def authenticate_gmail(
    ctx: RunContext[EmailAgentDependencies]
) -> Dict[str, Any]:
    """
    Authenticate with Gmail API.

    Returns:
        Dictionary with authentication status
    """
    try:
        result = await authenticate_gmail_tool(
            credentials_path=ctx.deps.gmail_credentials_path,
            token_path=ctx.deps.gmail_token_path
        )

        logger.info("Gmail authentication successful")
        return result

    except Exception as e:
        logger.error(f"Gmail authentication failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "authenticated": False
        }


@email_agent.tool
async def create_gmail_draft(
    ctx: RunContext[EmailAgentDependencies],
    to: List[str],
    subject: str,
    body: str,
    cc: Optional[List[str]] = None,
    bcc: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Create a Gmail draft.

    Args:
        to: List of recipient email addresses
        subject: Email subject line
        body: Email body content
        cc: Optional list of CC recipients
        bcc: Optional list of BCC recipients

    Returns:
        Dictionary with draft creation results
    """
    try:
        # Validate email addresses first
        validation_result = await validate_email_addresses_tool(to)
        if cc:
            cc_validation = await validate_email_addresses_tool(cc)
            validation_result["invalid_emails"].extend(cc_validation["invalid_emails"])
        if bcc:
            bcc_validation = await validate_email_addresses_tool(bcc)
            validation_result["invalid_emails"].extend(bcc_validation["invalid_emails"])

        if validation_result["invalid_emails"]:
            return {
                "success": False,
                "error": f"Invalid email addresses: {', '.join(validation_result['invalid_emails'])}",
                "valid_emails": validation_result["valid_emails"],
                "invalid_emails": validation_result["invalid_emails"]
            }

        # Create the draft
        result = await create_gmail_draft_tool(
            credentials_path=ctx.deps.gmail_credentials_path,
            token_path=ctx.deps.gmail_token_path,
            to=to,
            subject=subject,
            body=body,
            cc=cc,
            bcc=bcc
        )

        logger.info(f"Gmail draft created successfully for: {', '.join(to)}")
        return result

    except Exception as e:
        logger.error(f"Failed to create Gmail draft: {e}")
        return {
            "success": False,
            "error": str(e),
            "to": to,
            "subject": subject
        }


@email_agent.tool
async def validate_emails(
    ctx: RunContext[EmailAgentDependencies],
    emails: List[str]
) -> Dict[str, Any]:
    """
    Validate email addresses.

    Args:
        emails: List of email addresses to validate

    Returns:
        Dictionary with validation results
    """
    try:
        result = await validate_email_addresses_tool(emails)
        return result

    except Exception as e:
        logger.error(f"Email validation failed: {e}")
        return {
            "valid_emails": [],
            "invalid_emails": emails,
            "total_valid": 0,
            "total_invalid": len(emails),
            "error": str(e)
        }


@email_agent.tool
async def suggest_email_improvements(
    ctx: RunContext[EmailAgentDependencies],
    email_content: str,
    recipient_type: str = "professional"
) -> Dict[str, Any]:
    """
    Suggest improvements for email content.

    Args:
        email_content: The email content to analyze
        recipient_type: Type of recipient ("professional", "casual", "formal")

    Returns:
        Dictionary with improvement suggestions
    """
    try:
        # This is a simple implementation - in a real system, this would use
        # more sophisticated analysis or call another AI model
        suggestions = []

        # Basic content analysis
        if len(email_content) > 1000:
            suggestions.append("Consider making the email more concise. Aim for 300-500 words for better readability.")

        if len(email_content) < 50:
            suggestions.append("The email might be too brief. Consider adding more context or details.")

        # Check for common issues
        if "!!!" in email_content:
            suggestions.append("Avoid excessive exclamation marks for professional emails.")

        if email_content.count("I") > email_content.count("you") * 2:
            suggestions.append("Consider using more 'you-focused' language to engage the recipient.")

        # Tone suggestions based on recipient type
        if recipient_type == "professional":
            suggestions.append("Maintain professional tone with clear structure and formal language.")
        elif recipient_type == "casual":
            suggestions.append("Use friendly, approachable language while maintaining clarity.")
        elif recipient_type == "formal":
            suggestions.append("Use formal language with proper salutations and closings.")

        return {
            "success": True,
            "suggestions": suggestions,
            "total_suggestions": len(suggestions),
            "recipient_type": recipient_type
        }

    except Exception as e:
        logger.error(f"Failed to analyze email content: {e}")
        return {
            "success": False,
            "error": str(e),
            "suggestions": []
        }


# Convenience function to create email agent with dependencies
def create_email_agent(
    gmail_credentials_path: str,
    gmail_token_path: str,
    session_id: Optional[str] = None
) -> Agent:
    """
    Create an email agent with specified dependencies.

    Args:
        gmail_credentials_path: Path to Gmail credentials.json
        gmail_token_path: Path to Gmail token.json
        session_id: Optional session identifier

    Returns:
        Configured email agent
    """
    return email_agent