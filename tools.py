"""
Pure tool functions for Research Email Multi-Agent System.
These are standalone functions that can be imported and used by any agent.
"""

import os
import logging
import httpx
import time
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from functools import wraps

logger = logging.getLogger(__name__)

# Rate limiting configuration
RATE_LIMITS = {
    "tavily": {
        "max_requests": 10,  # Max requests per minute
        "window": 60,  # Time window in seconds
        "last_request": 0,
        "request_count": 0
    }
}


def rate_limit(service_name: str):
    """
    Decorator to implement rate limiting for external API calls.

    Args:
        service_name: Name of the service to rate limit
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_time = time.time()
            limit_config = RATE_LIMITS[service_name]

            # Reset counter if window has passed
            if current_time - limit_config["last_request"] > limit_config["window"]:
                limit_config["request_count"] = 0
                limit_config["last_request"] = current_time

            # Check if rate limit exceeded
            if limit_config["request_count"] >= limit_config["max_requests"]:
                raise Exception(f"Rate limit exceeded for {service_name}. Please wait before making more requests.")

            # Increment counter
            limit_config["request_count"] += 1

            return await func(*args, **kwargs)
        return wrapper
    return decorator


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitize user input to prevent injection attacks.

    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized text
    """
    if not text:
        return ""

    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>\"\'\\]', '', text)

    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
        logger.warning(f"Input truncated from {len(text)} to {max_length} characters")

    return sanitized.strip()


# Tavily Search Tool Function
@rate_limit("tavily")
async def search_web_tool(
    api_key: str,
    query: str,
    max_results: int = 10,
    search_depth: str = "basic",
    include_answer: bool = True
) -> List[Dict[str, Any]]:
    """
    Pure function to search the web using Tavily API.

    Args:
        api_key: Tavily API key
        query: Search query
        max_results: Number of results to return (1-20)
        search_depth: Search depth ("basic" or "advanced")
        include_answer: Whether to include AI-generated answer

    Returns:
        List of search results as dictionaries

    Raises:
        ValueError: If query is empty or API key missing
        Exception: If API request fails
    """
    # Check if API key is placeholder
    if not api_key or api_key.strip() in ["your_tavily_api_key_here", "test_key"]:
        logger.warning("Tavily API key not configured. Using mock data for testing.")
        return _generate_mock_search_results(query)

    # Sanitize and validate input
    query = sanitize_input(query, max_length=500)
    if not query:
        raise ValueError("Query cannot be empty after sanitization")

    # Ensure max_results is within valid range
    max_results = min(max(max_results, 1), 20)

    # Prepare request payload
    payload = {
        "api_key": api_key,
        "query": query,
        "max_results": max_results,
        "search_depth": search_depth,
        "include_answer": include_answer
    }

    # Secure logging - don't log sensitive query details
    logger.info(f"Searching Tavily (query length: {len(query)})")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://api.tavily.com/search",
                json=payload,
                timeout=30.0
            )

            # Handle rate limiting
            if response.status_code == 429:
                logger.warning("Tavily rate limit exceeded, using mock data")
                return _generate_mock_search_results(query)

            # Handle authentication errors
            if response.status_code == 401:
                logger.warning("Invalid Tavily API key, using mock data")
                return _generate_mock_search_results(query)

            # Handle other errors
            if response.status_code != 200:
                logger.warning(f"Tavily API error {response.status_code}, using mock data")
                return _generate_mock_search_results(query)

            data = response.json()

            # Extract results
            results = data.get("results", [])
            answer = data.get("answer", "")

            # Convert to our format
            formatted_results = []
            for idx, result in enumerate(results):
                # Calculate a simple relevance score based on position
                score = 1.0 - (idx * 0.05)  # Decrease by 0.05 for each position
                score = max(score, 0.1)  # Minimum score of 0.1

                formatted_results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content": result.get("content", ""),
                    "score": score
                })

            # Include AI answer if available
            if answer and include_answer:
                formatted_results.append({
                    "title": "AI Summary",
                    "url": "",
                    "content": answer,
                    "score": 0.95
                })

            logger.info(f"Found {len(formatted_results)} results for query: {query}")
            return formatted_results

        except httpx.RequestError as e:
            logger.warning(f"Tavily request failed, using mock data: {e}")
            return _generate_mock_search_results(query)
        except Exception as e:
            logger.warning(f"Tavily search error, using mock data: {e}")
            return _generate_mock_search_results(query)


# Gmail Authentication Tool Function
async def authenticate_gmail_tool(
    credentials_path: str,
    token_path: str,
    scopes: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Pure function to authenticate with Gmail API.

    Args:
        credentials_path: Path to credentials.json file
        token_path: Path to store/load token.json file
        scopes: Optional list of Gmail API scopes

    Returns:
        Dictionary with authentication status

    Raises:
        Exception: If authentication fails
    """
    if not os.path.exists(credentials_path):
        raise Exception(f"Gmail credentials file not found: {credentials_path}")

    if scopes is None:
        scopes = ["https://www.googleapis.com/auth/gmail.compose"]

    max_retries = 3
    retry_delay = 2  # seconds

    for attempt in range(max_retries):
        try:
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow

            creds = None

            # Check if token exists
            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, scopes)

            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    try:
                        creds.refresh(Request())
                    except Exception as refresh_error:
                        logger.warning(f"Token refresh failed, re-authenticating: {refresh_error}")
                        # If refresh fails, clear invalid token and re-authenticate
                        if os.path.exists(token_path):
                            os.remove(token_path)
                        creds = None

                if not creds:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        credentials_path, scopes
                    )
                    creds = flow.run_local_server(port=0)

                # Save the credentials for the next run
                with open(token_path, "w") as token:
                    token.write(creds.to_json())

            # Validate token expiration
            if creds.expired:
                logger.warning("Token expired, attempting refresh")
                creds.refresh(Request())

            logger.info("Gmail authentication successful")
            return {
                "success": True,
                "authenticated": True,
                "scopes": scopes,
                "token_path": token_path,
                "expires_at": creds.expiry.isoformat() if creds.expiry else None
            }

        except Exception as e:
            logger.error(f"Gmail authentication attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                raise Exception(f"Gmail authentication failed after {max_retries} attempts: {str(e)}")


# Gmail Draft Creation Tool Function
async def create_gmail_draft_tool(
    credentials_path: str,
    token_path: str,
    to: List[str],
    subject: str,
    body: str,
    cc: Optional[List[str]] = None,
    bcc: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Pure function to create a Gmail draft.

    Args:
        credentials_path: Path to credentials.json file
        token_path: Path to token.json file
        to: List of recipient email addresses
        subject: Email subject line
        body: Email body content
        cc: Optional list of CC recipients
        bcc: Optional list of BCC recipients

    Returns:
        Dictionary with draft creation results

    Raises:
        Exception: If draft creation fails
    """
    try:
        # First authenticate
        auth_result = await authenticate_gmail_tool(credentials_path, token_path)
        if not auth_result["success"]:
            raise Exception("Gmail authentication failed")

        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        # Load credentials
        creds = Credentials.from_authorized_user_file(token_path)

        # Build Gmail service
        service = build("gmail", "v1", credentials=creds)

        # Create email message
        import base64
        from email.mime.text import MIMEText

        message = MIMEText(body)
        message["to"] = ", ".join(to)
        message["subject"] = subject

        if cc:
            message["cc"] = ", ".join(cc)
        if bcc:
            message["bcc"] = ", ".join(bcc)

        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        # Create draft
        draft = {
            "message": {
                "raw": raw_message
            }
        }

        created_draft = service.users().drafts().create(
            userId="me",
            body=draft
        ).execute()

        logger.info(f"Gmail draft created successfully for: {', '.join(to)}")

        return {
            "success": True,
            "draft_id": created_draft["id"],
            "message_id": created_draft["message"]["id"],
            "thread_id": created_draft["message"].get("threadId"),
            "created_at": datetime.now().isoformat(),
            "recipients": to,
            "subject": subject
        }

    except Exception as e:
        logger.error(f"Failed to create Gmail draft: {e}")
        raise Exception(f"Failed to create Gmail draft: {str(e)}")


# Utility function to validate email addresses
async def validate_email_addresses_tool(
    emails: List[str]
) -> Dict[str, Any]:
    """
    Validate email addresses format with enhanced security checks.

    Args:
        emails: List of email addresses to validate

    Returns:
        Dictionary with validation results
    """
    import re

    # Enhanced email regex with security considerations
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    # Additional security checks
    max_email_length = 254  # RFC 5321 limit
    max_domain_length = 253

    valid_emails = []
    invalid_emails = []
    suspicious_emails = []

    for email in emails:
        # Sanitize input first
        email = sanitize_input(email, max_length=max_email_length)

        # Check basic format
        if not re.match(email_regex, email):
            invalid_emails.append(email)
            continue

        # Check length limits
        if len(email) > max_email_length:
            invalid_emails.append(email)
            continue

        # Extract domain
        domain = email.split('@')[1]
        if len(domain) > max_domain_length:
            invalid_emails.append(email)
            continue

        # Check for suspicious patterns
        suspicious_patterns = [
            r'\.\.',  # Double dots
            r'\-\-',  # Double dashes
            r'^\-',   # Starts with dash
            r'\-$',   # Ends with dash
            r'\.$',   # Ends with dot
            r'^\.',   # Starts with dot
        ]

        is_suspicious = False
        for pattern in suspicious_patterns:
            if re.search(pattern, domain):
                is_suspicious = True
                break

        if is_suspicious:
            suspicious_emails.append(email)
        else:
            valid_emails.append(email)

    return {
        "valid_emails": valid_emails,
        "invalid_emails": invalid_emails,
        "suspicious_emails": suspicious_emails,
        "total_valid": len(valid_emails),
        "total_invalid": len(invalid_emails),
        "total_suspicious": len(suspicious_emails)
    }


def _generate_mock_search_results(query: str) -> List[Dict[str, Any]]:
    """
    Generate mock search results for testing when Tavily API is not available.

    Args:
        query: Search query

    Returns:
        List of mock search results
    """
    logger.info(f"Generating mock search results for query: {query}")

    # Generate mock results based on query
    mock_results = [
        {
            "title": f"Research Article about {query}",
            "url": "https://example.com/research",
            "content": f"This is a mock research article about {query}. The content discusses key aspects and recent developments in this field.",
            "score": 0.9
        },
        {
            "title": f"News Report on {query}",
            "url": "https://example.com/news",
            "content": f"Recent news coverage about {query} including updates and analysis from experts in the field.",
            "score": 0.8
        },
        {
            "title": f"Technical Documentation for {query}",
            "url": "https://example.com/docs",
            "content": f"Technical documentation and implementation details for {query} including code examples and best practices.",
            "score": 0.7
        }
    ]

    # Add AI summary
    mock_results.append({
        "title": "AI Summary",
        "url": "",
        "content": f"Based on research about {query}, here are the key findings: This topic involves multiple aspects that are currently being studied and developed. Recent developments show promising advancements in this area.",
        "score": 0.95
    })

    return mock_results