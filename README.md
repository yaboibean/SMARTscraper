# Slack Message Scraper

A Python application that scrapes messages from a Slack channel and uses OpenAI's GPT to extract "progress" and "next steps" from each message.

## Features

- 🔍 **Slack Integration**: Scrapes messages from specific Slack channels using the Slack API
- 🤖 **AI-Powered Extraction**: Uses OpenAI GPT to intelligently separate progress updates from next steps
- 👥 **User Filtering**: Can filter messages by specific users
- 📊 **Multiple Output Formats**: Supports both JSON and CSV output
- 📋 **Rich CLI Interface**: Beautiful command-line interface with progress indicators
- ⚙️ **Configurable**: Easy configuration through environment variables

## Setup

### Prerequisites

- Python 3.8 or higher
- Slack Bot Token with appropriate permissions
- OpenAI API key

### Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   
4. Edit `.env` file with your credentials:
   ```
   SLACK_BOT_TOKEN=xoxb-your-bot-token-here
   SLACK_CHANNEL_ID=C1234567890
   OPENAI_API_KEY=sk-your-openai-api-key-here
   ```

### Slack App Setup

1. Go to [Slack API Apps](https://api.slack.com/apps)
2. Create a new app
3. Add OAuth permissions:
   - `channels:history` - Read messages from public channels
   - `users:read` - Read user information
4. Install the app to your workspace
5. Copy the Bot User OAuth Token

### Getting Channel ID

1. Open Slack in your browser
2. Navigate to the channel you want to scrape
3. The channel ID is in the URL: `https://app.slack.com/client/T.../C123456789`
4. Copy the part after the last `/` (starts with `C`)

## Usage

### Command Line Interface

Test your setup:
```bash
python main.py test
```

Scrape all messages from the channel:
```bash
python main.py scrape
```

Scrape messages from a specific user:
```bash
python main.py scrape --user U1234567890
```

Limit the number of messages:
```bash
python main.py scrape --limit 50
```

Change output format:
```bash
python main.py scrape --format csv
```

List users in the channel:
```bash
python main.py users
```

Show current configuration:
```bash
python main.py config
```

### Python API

```python
from src.agent import SlackMessageAgent

# Initialize the agent
agent = SlackMessageAgent()

# Scrape and process all messages
result = agent.scrape_and_process()

# Process messages from a specific user
result = agent.process_specific_user("U1234567890")

# Run full pipeline with output
output_file = agent.run_full_pipeline(
    user_id="U1234567890",
    limit=100,
    output_format="json"
)
```

## Configuration

All configuration is done through environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `SLACK_BOT_TOKEN` | Slack Bot User OAuth Token | Required |
| `SLACK_CHANNEL_ID` | Slack Channel ID to scrape | Required |
| `OPENAI_API_KEY` | OpenAI API Key | Required |
| `OPENAI_MODEL` | OpenAI model to use | `gpt-3.5-turbo` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `OUTPUT_FORMAT` | Default output format | `json` |
| `MAX_MESSAGES` | Maximum messages to process | `100` |

## Output

The application generates structured output with the following fields:

- **Original Message**: The full Slack message text
- **Progress**: Extracted progress information
- **Next Steps**: Extracted next steps or future actions
- **Confidence Score**: AI confidence in the extraction (0-1)
- **Metadata**: User info, timestamps, channel info

### Example Output

```json
{
  "total_messages": 25,
  "processed_messages": 23,
  "failed_messages": 2,
  "results": [
    {
      "user_id": "U1234567890",
      "username": "john.doe",
      "timestamp": "2024-01-15T10:30:00",
      "text": "Finished the database schema design. Next I need to implement the API endpoints.",
      "progress": "Finished the database schema design",
      "next_steps": "Implement the API endpoints",
      "confidence_score": 0.92
    }
  ]
}
```

## Error Handling

The application includes comprehensive error handling:

- **API Connection Errors**: Validates Slack and OpenAI API connections
- **Rate Limiting**: Handles API rate limits gracefully
- **Message Processing Errors**: Continues processing even if individual messages fail
- **Configuration Errors**: Clear error messages for missing or invalid configuration

## Development

### Project Structure

```
src/
├── agent.py              # Main orchestrator class
├── config.py             # Configuration management
├── models.py             # Data models
├── slack_scraper.py      # Slack API integration
├── message_processor.py  # OpenAI integration
└── output_manager.py     # Output formatting
main.py                   # CLI interface
requirements.txt          # Dependencies
.env.example             # Environment template
```

### Running Tests

```bash
python main.py test
```

## Troubleshooting

### Common Issues

1. **Slack API Permission Errors**
   - Ensure your bot has the required OAuth scopes
   - Check that the bot is added to the channel

2. **OpenAI API Errors**
   - Verify your API key is valid
   - Check your OpenAI account has sufficient credits

3. **No Messages Found**
   - Verify the channel ID is correct
   - Check that there are messages in the channel
   - Ensure the bot has access to the channel

### Debug Mode

Enable debug logging by setting:
```
LOG_LEVEL=DEBUG
```

## License

This project is open source and available under the MIT License.
