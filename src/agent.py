from typing import List, Optional
import logging
from datetime import datetime
from src.config import Settings, get_settings
from src.slack_scraper import SlackScraper
from src.message_processor import MessageProcessor
from src.output_manager import OutputManager
from src.models import ProcessingResult


class SlackMessageAgent:
    """Main agent class that orchestrates the entire process."""
    
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        self.logger = self._setup_logging()
        
        # Initialize components
        self.slack_scraper = SlackScraper(self.settings)
        self.message_processor = MessageProcessor(self.settings)
        self.output_manager = OutputManager()
    
    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration."""
        logging.basicConfig(
            level=getattr(logging, self.settings.log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def scrape_and_process(self, user_id: Optional[str] = None, limit: Optional[int] = None) -> ProcessingResult:
        """
        Main method to scrape messages and process them.
        
        Args:
            user_id: Optional user ID to filter messages for a specific user
            limit: Maximum number of messages to process
            
        Returns:
            ProcessingResult object with processing statistics and results
        """
        self.logger.info("Starting Slack message scraping and processing")
        
        # Test connections
        if not self.slack_scraper.test_connection():
            raise RuntimeError("Failed to connect to Slack API")
        
        # Scrape messages
        if user_id:
            messages = self.slack_scraper.get_user_messages(user_id, limit)
        else:
            messages = self.slack_scraper.get_channel_messages(limit)
        
        if not messages:
            self.logger.warning("No messages found to process")
            return ProcessingResult(
                total_messages=0,
                processed_messages=0,
                failed_messages=0,
                results=[]
            )
        
        # Process messages
        self.logger.info(f"Processing {len(messages)} messages")
        processed_messages = self.message_processor.process_messages(messages)
        
        # Calculate statistics
        successful_messages = [msg for msg in processed_messages if msg.progress is not None or msg.next_steps is not None]
        failed_messages = len(processed_messages) - len(successful_messages)
        
        result = ProcessingResult(
            total_messages=len(messages),
            processed_messages=len(successful_messages),
            failed_messages=failed_messages,
            results=processed_messages
        )
        
        self.logger.info(f"Processing complete. Success rate: {len(successful_messages)/len(messages)*100:.1f}%")
        return result
    
    def run_full_pipeline(self, user_id: Optional[str] = None, limit: Optional[int] = None, 
                         output_format: Optional[str] = None, show_results: bool = True) -> str:
        """
        Run the complete pipeline from scraping to output.
        
        Args:
            user_id: Optional user ID to filter messages
            limit: Maximum number of messages to process
            output_format: Output format ("json" or "csv"), defaults to settings
            show_results: Whether to print results to console
            
        Returns:
            Path to the saved output file
        """
        # Process messages
        result = self.scrape_and_process(user_id, limit)
        
        # Save results
        output_format = output_format or self.settings.output_format
        output_file = self.output_manager.save_results(result, output_format)
        
        # Print summary and results
        self.output_manager.print_summary(result)
        
        if show_results:
            self.output_manager.print_results(result, limit=5)  # Show first 5 results
        
        return output_file
    
    def get_users_in_channel(self) -> List[dict]:
        """
        Get list of users who have posted in the channel.
        
        Returns:
            List of user information dictionaries
        """
        messages = self.slack_scraper.get_channel_messages()
        users = {}
        
        for message in messages:
            if message.user_id not in users:
                users[message.user_id] = {
                    'user_id': message.user_id,
                    'username': message.username,
                    'message_count': 0
                }
            users[message.user_id]['message_count'] += 1
        
        return list(users.values())
    
    def process_specific_user(self, user_id: str, limit: Optional[int] = None) -> ProcessingResult:
        """
        Process messages from a specific user.
        
        Args:
            user_id: Slack user ID
            limit: Maximum number of messages to process
            
        Returns:
            ProcessingResult for the specific user
        """
        return self.scrape_and_process(user_id=user_id, limit=limit)
