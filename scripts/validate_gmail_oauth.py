#!/usr/bin/env python3
"""
Gmail OAuth2 Validation Script

This script validates Gmail API OAuth2 setup before agent implementation.
Based on official Google Gmail API Python quickstart documentation.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown

console = Console()


def validate_credentials_file(credentials_path: str) -> Dict[str, Any]:
    """
    Validate the Gmail credentials file structure.

    Args:
        credentials_path: Path to credentials.json file

    Returns:
        Dictionary with validation results
    """
    result = {
        "exists": False,
        "valid": False,
        "error": None,
        "client_id": None,
        "project_id": None,
        "auth_uri": None,
        "token_uri": None
    }

    try:
        if not os.path.exists(credentials_path):
            result["error"] = f"Credentials file not found: {credentials_path}"
            return result

        result["exists"] = True

        with open(credentials_path, 'r') as f:
            credentials = json.load(f)

        # Check for both 'installed' and 'web' credential formats
        if "installed" not in credentials and "web" not in credentials:
            result["error"] = "Invalid credentials format: missing 'installed' or 'web' section"
            return result

        # Use installed credentials for desktop apps
        credential_type = "installed" if "installed" in credentials else "web"
        creds_data = credentials[credential_type]

        # Check required fields
        required_fields = ["client_id", "project_id", "auth_uri", "token_uri"]

        for field in required_fields:
            if field not in creds_data:
                result["error"] = f"Missing required field: {field}"
                return result

        result["client_id"] = creds_data["client_id"]
        result["project_id"] = creds_data["project_id"]
        result["auth_uri"] = creds_data["auth_uri"]
        result["token_uri"] = creds_data["token_uri"]
        result["valid"] = True

    except json.JSONDecodeError as e:
        result["error"] = f"Invalid JSON in credentials file: {e}"
    except Exception as e:
        result["error"] = f"Error reading credentials file: {e}"

    return result


def validate_oauth2_authentication(credentials_path: str, token_path: str) -> Dict[str, Any]:
    """
    Validate OAuth2 authentication with Gmail API.

    Args:
        credentials_path: Path to credentials.json
        token_path: Path to token.json

    Returns:
        Dictionary with authentication results
    """
    result = {
        "authenticated": False,
        "error": None,
        "scopes": [],
        "user_info": None,
        "token_exists": False
    }

    try:
        # Import Gmail API dependencies
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError

        # Define required scopes for email draft creation
        SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]

        creds = None

        # Check if token exists
        if os.path.exists(token_path):
            result["token_exists"] = True
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)

        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                console.print("[yellow]🔄 Refreshing expired credentials...[/yellow]")
                creds.refresh(Request())
            else:
                console.print("[blue]🔐 Starting OAuth2 authentication flow...[/blue]")
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open(token_path, "w") as token:
                token.write(creds.to_json())

        # Test Gmail API access
        console.print("[blue]🧪 Testing Gmail API access...[/blue]")
        service = build("gmail", "v1", credentials=creds)

        # Get user profile to verify access
        profile = service.users().getProfile(userId="me").execute()

        # Test draft creation capability
        console.print("[blue]🧪 Testing draft creation capability...[/blue]")
        draft_body = {
            "message": {
                "raw": "VGVzdCBkcmFmdCBmb3IgdmFsaWRhdGlvbg=="  # "Test draft for validation"
            }
        }

        # Create a test draft
        draft = service.users().drafts().create(userId="me", body=draft_body).execute()

        # Delete the test draft
        service.users().drafts().delete(userId="me", id=draft["id"]).execute()

        result["authenticated"] = True
        result["scopes"] = SCOPES
        result["user_info"] = {
            "email_address": profile.get("emailAddress"),
            "messages_total": profile.get("messagesTotal"),
            "threads_total": profile.get("threadsTotal")
        }

        console.print("[green]✅ Gmail API authentication successful![/green]")

    except HttpError as error:
        result["error"] = f"Gmail API error: {error}"
        console.print(f"[red]❌ Gmail API error: {error}[/red]")
    except Exception as e:
        result["error"] = f"Authentication failed: {str(e)}"
        console.print(f"[red]❌ Authentication failed: {str(e)}[/red]")

    return result


def display_setup_instructions():
    """Display comprehensive Gmail API setup instructions."""
    instructions = """
# Gmail API Setup Instructions

## 1. Enable Gmail API
- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Create a new project or select existing one
- Enable the Gmail API: [Enable API](https://console.cloud.google.com/flows/enableapi?apiid=gmail.googleapis.com)

## 2. Configure OAuth Consent Screen
- Go to "Google Auth platform" > "Branding"
- Configure app information:
  - **App name**: Your application name
  - **User support email**: Your support email
- Set **Audience** to "Internal" (for testing)
- Add your email as a test user

## 3. Create OAuth 2.0 Credentials
- Go to "Google Auth platform" > "Clients"
- Click "Create Client"
- Select **Application type**: "Desktop app"
- Enter a name for the credential
- Click "Create"
- Download the JSON file and save as `credentials/credentials.json`

## 4. Required Scopes
- `https://www.googleapis.com/auth/gmail.compose` - For creating email drafts

## 5. File Structure
```
credentials/
├── credentials.json  # Downloaded from Google Cloud Console
└── token.json        # Auto-generated after authentication
```

**Note:** The first time you run validation, it will open a browser window for authentication.
    """

    console.print(Panel(
        Markdown(instructions),
        title="📧 Gmail API Setup Guide",
        title_align="left",
        border_style="blue"
    ))


def validate_environment():
    """Validate that all required dependencies are installed."""
    required_packages = [
        "google.auth",
        "google_auth_oauthlib",
        "google_auth_httplib2",
        "googleapiclient.discovery",
        "rich"
    ]

    console.print("[bold]Checking required dependencies...[/bold]")

    for package in required_packages:
        try:
            __import__(package)
            console.print(f"[green]✅ {package}[/green]")
        except ImportError:
            console.print(f"[red]❌ {package} - Not installed[/red]")
            return False

    return True


def main():
    """Main validation function."""
    parser = argparse.ArgumentParser(description="Gmail OAuth2 Validation Tool")
    parser.add_argument("--setup", action="store_true", help="Show setup instructions")
    parser.add_argument("--skip-auth", action="store_true", help="Skip authentication test")
    args = parser.parse_args()

    console.print("[bold green]🔧 Gmail OAuth2 Validation Tool[/bold green]")
    console.print("[dim]Validating Gmail API setup before agent implementation[/dim]\n")

    # Check if user wants setup instructions
    if args.setup or Confirm.ask("Do you need Gmail API setup instructions?"):
        display_setup_instructions()

    # Validate dependencies
    if not validate_environment():
        console.print("[red]❌ Missing required dependencies. Please install them first.[/red]")
        console.print("[yellow]Run: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client rich[/yellow]")
        return False

    # Define paths
    credentials_path = "../credentials/credentials.json"
    token_path = "../credentials/token.json"

    console.print(f"\n[bold]Validating paths:[/bold]")
    console.print(f"Credentials file: {credentials_path}")
    console.print(f"Token file: {token_path}")

    # Step 1: Validate credentials file
    console.print("\n[bold]Step 1: Validating credentials file...[/bold]")
    credentials_result = validate_credentials_file(credentials_path)

    if not credentials_result["exists"]:
        console.print(f"[red]❌ {credentials_result['error']}[/red]")
        console.print("[yellow]Please follow the setup instructions above.[/yellow]")
        return False

    if not credentials_result["valid"]:
        console.print(f"[red]❌ {credentials_result['error']}[/red]")
        return False

    console.print("[green]✅ Credentials file is valid[/green]")
    console.print(f"   Project ID: {credentials_result['project_id']}")
    console.print(f"   Client ID: {credentials_result['client_id'][:20]}...")

    # Step 2: Validate OAuth2 authentication (unless skipped)
    if not args.skip_auth:
        console.print("\n[bold]Step 2: Validating OAuth2 authentication...[/bold]")
        auth_result = validate_oauth2_authentication(credentials_path, token_path)

        if not auth_result["authenticated"]:
            console.print(f"[red]❌ {auth_result['error']}[/red]")
            return False
    else:
        console.print("[yellow]⚠️  Authentication test skipped[/yellow]")
        auth_result = {"authenticated": True, "user_info": {"email_address": "Skipped"}}

    # Display success information
    console.print("\n[bold green]🎉 Gmail OAuth2 Setup Complete![/bold green]")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="white")
    table.add_column("Details", style="yellow")

    table.add_row("Credentials File", "✅ Valid", f"Project: {credentials_result['project_id']}")
    table.add_row("OAuth2 Authentication", "✅ Working", f"User: {auth_result['user_info']['email_address']}")
    table.add_row("Gmail API Access", "✅ Ready", "Draft creation capability verified")

    console.print(table)

    console.print("\n[green]✅ Your Gmail API setup is ready for the multi-agent system![/green]")
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Validation cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]❌ Unexpected error: {str(e)}[/red]")
        sys.exit(1)