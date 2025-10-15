#!/usr/bin/env python3
"""
Test script to validate the Gmail OAuth2 validation functionality
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from scripts.validate_gmail_oauth import (
    validate_credentials_file,
    validate_environment,
    display_setup_instructions
)

from rich.console import Console

console = Console()

def test_validation_functions():
    """Test the validation functions without interactive input."""
    console.print("[bold green]🧪 Testing Gmail OAuth2 Validation Functions[/bold green]\n")

    # Test 1: Environment validation
    console.print("[bold]Test 1: Environment Validation[/bold]")
    if validate_environment():
        console.print("[green]✅ Environment validation passed[/green]")
    else:
        console.print("[red]❌ Environment validation failed[/red]")
        return False

    # Test 2: Credentials file validation (should fail since no file exists)
    console.print("\n[bold]Test 2: Credentials File Validation[/bold]")
    credentials_path = "credentials/credentials.json"
    result = validate_credentials_file(credentials_path)

    if not result["exists"]:
        console.print("[yellow]⚠️  No credentials file found (expected for testing)[/yellow]")
        console.print(f"   Expected path: {credentials_path}")
    else:
        console.print("[green]✅ Credentials file found[/green]")

    # Test 3: Setup instructions
    console.print("\n[bold]Test 3: Setup Instructions Display[/bold]")
    try:
        display_setup_instructions()
        console.print("[green]✅ Setup instructions displayed successfully[/green]")
    except Exception as e:
        console.print(f"[red]❌ Setup instructions failed: {e}[/red]")
        return False

    console.print("\n[bold green]🎉 All validation tests completed successfully![/bold green]")
    console.print("[green]✅ Gmail OAuth2 Pre-Validation infrastructure is ready[/green]")
    return True

if __name__ == "__main__":
    try:
        success = test_validation_functions()
        sys.exit(0 if success else 1)
    except Exception as e:
        console.print(f"[red]❌ Test failed with error: {e}[/red]")
        sys.exit(1)