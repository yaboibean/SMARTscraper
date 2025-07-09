import os
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv


class Settings:
    """Application settings loaded from environment variables."""
    
    def __init__(self):
        load_dotenv()
        
        # Slack Configuration
        self.slack_bot_token: str = os.getenv('SLACK_BOT_TOKEN', '')
        self.slack_channel_id: str = os.getenv('SLACK_CHANNEL_ID', '')
        
        # OpenAI Configuration
        self.openai_api_key: str = os.getenv('OPENAI_API_KEY', '')
        self.openai_model: str = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        
        # Application Settings
        self.log_level: str = os.getenv('LOG_LEVEL', 'INFO')
        self.output_format: str = os.getenv('OUTPUT_FORMAT', 'json')
        max_messages_raw = os.getenv('MAX_MESSAGES', '100')
        # Remove inline comments and whitespace
        max_messages_clean = max_messages_raw.split('#')[0].strip()
        self.max_messages: int = int(max_messages_clean)
        
        # Validate required settings
        if not self.slack_bot_token:
            raise ValueError("SLACK_BOT_TOKEN environment variable is required")
        if not self.slack_channel_id:
            raise ValueError("SLACK_CHANNEL_ID environment variable is required")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()
