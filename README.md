# Research Email Multi-Agent System

A production-grade multi-agent Pydantic AI system that combines web research capabilities with professional email drafting. The system features a research agent that can search the web using Tavily API and delegate email creation tasks to an email agent with Gmail API integration.

## Features

- **Multi-Agent Architecture**: Research agent delegates to email agent as a tool
- **Web Research**: Uses Tavily API for comprehensive web searches
- **Email Drafting**: Creates professional email drafts with Gmail API
- **Streaming CLI**: Real-time streaming interface using Rich and Typer
- **Security First**: Comprehensive security patterns and input validation
- **Production Ready**: Error handling, retry mechanisms, and monitoring

## Prerequisites

Before you begin, ensure you have the following:

- Python 3.9 or higher
- [UV package manager](https://github.com/astral-sh/uv) (recommended) or pip
- API keys for:
  - OpenAI or compatible LLM provider
  - [Tavily](https://tavily.com/) for web search
- Google Cloud Console project with Gmail API enabled

## Installation

### 1. Clone the Repository

```bash
git clone git@github.com:pydevup/research-email-multi-agent-system.git
cd research-email-multi-agent-system
```

### 2. Install Dependencies

Using UV (recommended):
```bash
uv sync
```

Using pip:
```bash
pip install -e .
```

### 3. Set Up Environment Variables

Copy the environment template:
```bash
cp .env.example .env
```

Edit `.env` with your API keys and configuration:
```bash
# LLM Configuration
LLM_PROVIDER=openai
LLM_API_KEY=your_openai_api_key_here
LLM_MODEL=gpt-4o
LLM_BASE_URL=https://api.openai.com/v1

# Tavily API Configuration
TAVILY_API_KEY=your_tavily_api_key_here

# Gmail API Configuration
GMAIL_CREDENTIALS_PATH=credentials/credentials.json
GMAIL_TOKEN_PATH=credentials/token.json

# Application Configuration
APP_ENV=development
LOG_LEVEL=INFO
DEBUG=false
```

## API Key Setup

### OpenAI API Key

1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Create an account or sign in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key to your `.env` file as `LLM_API_KEY`

### Tavily API Key

1. Visit [Tavily](https://tavily.com/)
2. Sign up for a free account
3. Get your API key from the dashboard
4. Copy the key to your `.env` file as `TAVILY_API_KEY`

## Google Cloud Console Setup

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Gmail API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"

### 2. Configure OAuth 2.0 Consent Screen

1. Go to "APIs & Services" > "OAuth consent screen"
2. Choose "External" user type
3. Fill in required information:
   - App name: "Research Email Agent"
   - User support email: your email
   - Developer contact information: your email
4. Add scopes:
   - `https://www.googleapis.com/auth/gmail.compose`
5. Add test users (your email address)

### 3. Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Choose "Desktop application" as application type
4. Download the credentials file
5. Save it as `credentials/credentials.json` in your project

### 4. Set Up Credentials Directory

```bash
mkdir -p credentials
chmod 700 credentials  # Secure the directory
# Move your downloaded credentials.json to credentials/
```

## Usage

### Command Line Interface

The system provides a streaming CLI with real-time output:

```bash
# Start the CLI
python cli.py chat

# Or to get help
python cli.py --help
```

### Example Usage

1. **Research and Email Drafting**:
   ```
   User: Research the latest AI trends and draft an email to my team about them

   Agent: I'll search for the latest AI trends and create a draft email for your team.
   [Searching Tavily...]
   [Found 8 relevant articles]
   [Creating email draft...]
   [Draft created successfully!]
   ```

2. **Web Research Only**:
   ```
   User: Search for information about climate change solutions

   Agent: I'll search for information about climate change solutions.
   [Searching Tavily...]
   [Found 12 relevant articles]
   Here's what I found about climate change solutions...
   ```

3. **Email Drafting Only**:
   ```
   User: Draft an email to john@example.com about our meeting tomorrow

   Agent: I'll create a draft email to john@example.com about your meeting.
   [Creating email draft...]
   [Draft created successfully!]
   ```

## Project Structure

```
Reseach-Email-Multi-Agent/
├── research_agent.py      # Main research agent with Tavily integration
├── email_agent.py         # Email drafting agent with Gmail integration
├── tools.py               # Pure tool functions for both agents
├── models.py              # Pydantic models for structured outputs
├── dependencies.py        # External service dependencies
├── settings.py            # Environment-based configuration
├── providers.py           # Model provider abstraction
├── cli.py                 # Streaming CLI interface
├── scripts/               # Utility scripts
│   ├── validate_security.py
│   └── validate_gmail_oauth.py
├── credentials/           # OAuth2 credentials (gitignored)
│   ├── credentials.json
│   └── token.json
├── tests/                 # Test suite
├── .env.example           # Environment template
└── pyproject.toml         # Project configuration
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | LLM provider (openai, anthropic) | `openai` |
| `LLM_API_KEY` | API key for LLM provider | Required |
| `LLM_MODEL` | Model name | `gpt-4o` |
| `LLM_BASE_URL` | Base URL for API | OpenAI URL |
| `TAVILY_API_KEY` | Tavily API key | Required |
| `GMAIL_CREDENTIALS_PATH` | Path to OAuth2 credentials | `credentials/credentials.json` |
| `GMAIL_TOKEN_PATH` | Path to OAuth2 token | `credentials/token.json` |
| `APP_ENV` | Application environment | `development` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `DEBUG` | Debug mode | `false` |

### Security Configuration

The system includes comprehensive security measures:

- **Rate Limiting**: Prevents API abuse
- **Input Sanitization**: Protects against injection attacks
- **Secure Logging**: No sensitive data in logs
- **File Permissions**: Secure credential storage
- **Error Handling**: Comprehensive retry mechanisms

Run security validation:
```bash
python scripts/validate_security.py
```

## Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test files
python -m pytest tests/test_research_agent.py -v
python -m pytest tests/test_email_agent.py -v
python -m pytest tests/test_tools.py -v
```

## Troubleshooting

### Common Issues

**1. Gmail Authentication Fails**
- Ensure `credentials/credentials.json` exists
- Check OAuth2 consent screen is configured
- Verify scopes include `gmail.compose`

**2. Tavily API Errors**
- Verify API key is correct
- Check rate limits (10 requests/minute)
- Ensure internet connectivity

**3. LLM Provider Issues**
- Verify API key and base URL
- Check model compatibility
- Ensure sufficient API credits

**4. File Permission Errors**
```bash
chmod 600 credentials/*.json
chmod 700 credentials/
```

### Debug Mode

Enable debug mode for detailed logging:
```bash
DEBUG=true python cli.py chat
```

## Security Best Practices

1. **Never commit API keys** - Use environment variables
2. **Secure credential files** - Set proper file permissions
3. **Regular security audits** - Use the validation script
4. **Monitor API usage** - Watch for unusual activity
5. **Keep dependencies updated** - Regular security updates

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and security validation
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Pydantic AI](https://ai.pydantic.dev/) for the agent framework
- [Tavily](https://tavily.com/) for web search capabilities
- [Google Gmail API](https://developers.google.com/gmail/api) for email integration
- [Rich](https://github.com/Textualize/rich) for beautiful CLI output