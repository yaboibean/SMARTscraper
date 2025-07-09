<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Slack Message Scraper Project

This is a Python application that scrapes Slack messages and uses OpenAI GPT to extract progress updates and next steps from each message.

## Project Structure

- `src/` - Main source code
  - `agent.py` - Main orchestrator class
  - `slack_scraper.py` - Slack API integration
  - `message_processor.py` - OpenAI integration for text processing
  - `output_manager.py` - Output formatting and file handling
  - `models.py` - Data models and types
  - `config.py` - Configuration management
- `main.py` - CLI interface using Typer
- `examples/` - Usage examples

## Key Dependencies

- `slack-sdk` - Slack API integration
- `openai` - OpenAI GPT API
- `typer` - CLI framework
- `rich` - Rich terminal output
- `pydantic` - Data validation

## Development Guidelines

- Use type hints throughout the codebase
- Follow the existing error handling patterns
- Use the logging module for debugging information
- Configuration should be managed through environment variables
- All API calls should include proper error handling
- Use the existing data models when working with Slack messages

## Code Style

- Follow PEP 8 style guidelines
- Use descriptive variable and function names
- Include docstrings for all classes and methods
- Use dataclasses for data structures
- Prefer composition over inheritance
