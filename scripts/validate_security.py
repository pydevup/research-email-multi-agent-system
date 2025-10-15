#!/usr/bin/env python3
"""
Security validation script for Research Email Multi-Agent System.
Validates all security configurations, API keys, and security patterns.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, List, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from settings import settings
from providers import validate_llm_configuration, validate_tavily_configuration, validate_gmail_configuration

def setup_logging():
    """Setup logging for security validation."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('security_validation.log')
        ]
    )
    return logging.getLogger(__name__)


def validate_environment_variables() -> Tuple[bool, List[str]]:
    """
    Validate that all required environment variables are set.

    Returns:
        Tuple of (success, list of issues)
    """
    logger = logging.getLogger(__name__)
    issues = []

    required_vars = [
        "LLM_API_KEY",
        "TAVILY_API_KEY"
    ]

    optional_vars = [
        "LLM_PROVIDER",
        "LLM_MODEL",
        "LLM_BASE_URL",
        "GMAIL_CREDENTIALS_PATH",
        "GMAIL_TOKEN_PATH",
        "APP_ENV",
        "LOG_LEVEL",
        "DEBUG"
    ]

    # Check required variables
    for var in required_vars:
        value = getattr(settings, var.lower(), None)
        if not value or value.strip() == "":
            issues.append(f"Required environment variable {var} is not set or empty")
        elif "your_" in value.lower() or "test_" in value.lower():
            issues.append(f"Environment variable {var} appears to contain placeholder value")

    # Check optional variables
    for var in optional_vars:
        try:
            value = getattr(settings, var.lower(), None)
            if value and ("your_" in str(value).lower() or "test_" in str(value).lower()):
                issues.append(f"Environment variable {var} appears to contain placeholder value")
        except Exception as e:
            logger.warning(f"Could not check optional variable {var}: {e}")

    success = len(issues) == 0
    return success, issues


def validate_file_permissions() -> Tuple[bool, List[str]]:
    """
    Validate file permissions for sensitive files.

    Returns:
        Tuple of (success, list of issues)
    """
    logger = logging.getLogger(__name__)
    issues = []

    sensitive_files = [
        settings.gmail_credentials_path,
        settings.gmail_token_path,
        ".env"
    ]

    for file_path in sensitive_files:
        if os.path.exists(file_path):
            try:
                # Check if file permissions are too permissive
                stat_info = os.stat(file_path)
                permissions = stat_info.st_mode & 0o777

                # Warn if file is world-readable
                if permissions & 0o004:
                    issues.append(f"File {file_path} is world-readable (permissions: {oct(permissions)})")

                # Warn if file is world-writable
                if permissions & 0o002:
                    issues.append(f"File {file_path} is world-writable (permissions: {oct(permissions)})")

            except Exception as e:
                logger.warning(f"Could not check permissions for {file_path}: {e}")

    success = len(issues) == 0
    return success, issues


def validate_api_configurations() -> Tuple[bool, List[str]]:
    """
    Validate all API configurations.

    Returns:
        Tuple of (success, list of issues)
    """
    logger = logging.getLogger(__name__)
    issues = []

    # Validate LLM configuration
    if not validate_llm_configuration():
        issues.append("LLM configuration validation failed")

    # Validate Tavily configuration
    if not validate_tavily_configuration():
        issues.append("Tavily API configuration validation failed")

    # Validate Gmail configuration
    if not validate_gmail_configuration():
        issues.append("Gmail API configuration validation failed")

    success = len(issues) == 0
    return success, issues


def validate_security_patterns() -> Tuple[bool, List[str]]:
    """
    Validate security patterns in the codebase.

    Returns:
        Tuple of (success, list of issues)
    """
    logger = logging.getLogger(__name__)
    issues = []

    # Check for hardcoded API keys
    code_files = [
        "settings.py",
        "providers.py",
        "tools.py",
        "research_agent.py",
        "email_agent.py",
        "dependencies.py"
    ]

    sensitive_patterns = [
        r'api_key\s*=\s*["\'][^"\']{20,}["\']',
        r'password\s*=\s*["\'][^"\']+["\']',
        r'secret\s*=\s*["\'][^"\']+["\']',
        r'token\s*=\s*["\'][^"\']+["\']'
    ]

    for file_name in code_files:
        file_path = Path(__file__).parent.parent / file_name
        if file_path.exists():
            try:
                content = file_path.read_text()
                for pattern in sensitive_patterns:
                    import re
                    if re.search(pattern, content, re.IGNORECASE):
                        issues.append(f"Potential hardcoded credential found in {file_name}")
            except Exception as e:
                logger.warning(f"Could not scan {file_name}: {e}")

    success = len(issues) == 0
    return success, issues


def validate_credentials_directory() -> Tuple[bool, List[str]]:
    """
    Validate credentials directory structure and security.

    Returns:
        Tuple of (success, list of issues)
    """
    logger = logging.getLogger(__name__)
    issues = []

    credentials_dir = Path("credentials")

    # Check if credentials directory exists
    if not credentials_dir.exists():
        issues.append("Credentials directory does not exist")
        return False, issues

    # Check if credentials directory is in .gitignore
    gitignore_path = Path(".gitignore")
    if gitignore_path.exists():
        gitignore_content = gitignore_path.read_text()
        if "credentials/" not in gitignore_content:
            issues.append("Credentials directory not found in .gitignore")

    # Check for sensitive files in credentials directory
    sensitive_extensions = [".json", ".pem", ".key", ".crt"]
    for file_path in credentials_dir.iterdir():
        if file_path.is_file():
            if file_path.suffix in sensitive_extensions:
                # Check file permissions
                try:
                    stat_info = file_path.stat()
                    permissions = stat_info.st_mode & 0o777
                    if permissions & 0o004:  # World readable
                        issues.append(f"Sensitive file {file_path} is world-readable")
                except Exception as e:
                    logger.warning(f"Could not check permissions for {file_path}: {e}")

    success = len(issues) == 0
    return success, issues


def main():
    """Main security validation function."""
    logger = setup_logging()

    print("🔒 Security Validation for Research Email Multi-Agent System")
    print("=" * 60)

    all_issues = []
    validation_results = []

    # Run all validations
    validations = [
        ("Environment Variables", validate_environment_variables),
        ("File Permissions", validate_file_permissions),
        ("API Configurations", validate_api_configurations),
        ("Security Patterns", validate_security_patterns),
        ("Credentials Directory", validate_credentials_directory)
    ]

    for name, validation_func in validations:
        print(f"\n📋 Validating {name}...")
        success, issues = validation_func()

        if success:
            print(f"✅ {name}: PASSED")
            validation_results.append((name, True, []))
        else:
            print(f"❌ {name}: FAILED")
            for issue in issues:
                print(f"   - {issue}")
            validation_results.append((name, False, issues))
            all_issues.extend(issues)

    # Summary
    print("\n" + "=" * 60)
    print("📊 SECURITY VALIDATION SUMMARY")
    print("=" * 60)

    passed_count = sum(1 for _, success, _ in validation_results if success)
    total_count = len(validation_results)

    print(f"\nResults: {passed_count}/{total_count} checks passed")

    if all_issues:
        print(f"\n🚨 SECURITY ISSUES FOUND ({len(all_issues)}):")
        for i, issue in enumerate(all_issues, 1):
            print(f"{i}. {issue}")

        print(f"\n⚠️  Please address these security issues before deployment.")
        return 1
    else:
        print("\n✅ All security checks passed! The system is ready for use.")
        return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"❌ Security validation failed with error: {e}")
        sys.exit(1)