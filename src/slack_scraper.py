from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from src.models import SlackMessage
from src.config import Settings


class SlackScraper:
    """Handles Slack API interactions and message scraping."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = WebClient(token=settings.slack_bot_token)
        self.logger = logging.getLogger(__name__)
    
    def get_channel_messages(self, limit: Optional[int] = None) -> List[SlackMessage]:
        """
        Retrieve messages from the specified Slack channel.
        
        Args:
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of SlackMessage objects
        """
        limit = limit or self.settings.max_messages
        messages = []
        
        try:
            # Get channel history
            response = self.client.conversations_history(
                channel=self.settings.slack_channel_id,
                limit=limit
            )
            
            messages_data = response.get('messages')
            if not messages_data:
                return messages
            
            # Get user information for username mapping
            user_cache = {}
            
            for msg in messages_data:
                # Skip bot messages and system messages
                if msg.get('bot_id') or msg.get('subtype'):
                    continue
                
                user_id = msg.get('user')
                if not user_id:
                    continue
                
                # Get username if not cached
                if user_id not in user_cache:
                    try:
                        user_info = self.client.users_info(user=user_id)
                        user_obj = user_info.get('user') if user_info else None
                        user_cache[user_id] = user_obj.get('name') if user_obj and user_obj.get('name') else f"user_{user_id}"
                    except SlackApiError as e:
                        self.logger.warning(f"Could not get user info for {user_id}: {e}")
                        user_cache[user_id] = f"user_{user_id}"
                
                # Create SlackMessage object
                message = SlackMessage(
                    user_id=user_id,
                    username=user_cache[user_id],
                    timestamp=datetime.fromtimestamp(float(msg['ts'])),
                    text=msg.get('text', ''),
                    channel_id=self.settings.slack_channel_id,
                    thread_ts=msg.get('thread_ts')
                )
                
                messages.append(message)
                
        except SlackApiError as e:
            self.logger.error(f"Error fetching messages: {e}")
            raise
        
        self.logger.info(f"Retrieved {len(messages)} messages from Slack")
        return messages
    
    def get_user_messages(self, user_id: str, limit: Optional[int] = None) -> List[SlackMessage]:
        """
        Get messages from a specific user.
        
        Args:
            user_id: Slack user ID
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of SlackMessage objects from the specified user
        """
        all_messages = self.get_channel_messages(limit)
        user_messages = [msg for msg in all_messages if msg.user_id == user_id]
        
        self.logger.info(f"Found {len(user_messages)} messages from user {user_id}")
        return user_messages
    
    def test_connection(self) -> bool:
        """
        Test the Slack API connection.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            response = self.client.auth_test()
            self.logger.info(f"Connected to Slack as {response['user']}")
            return True
        except SlackApiError as e:
            self.logger.error(f"Slack connection test failed: {e}")
            return False
