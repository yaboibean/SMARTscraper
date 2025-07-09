from typing import List, Optional, Tuple
from datetime import datetime
import logging
import json
import openai
from src.models import SlackMessage
from src.config import Settings


class MessageProcessor:
    """Handles OpenAI API interactions to extract progress and next steps."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        openai.api_key = settings.openai_api_key  # Set the API key globally
        self.logger = logging.getLogger(__name__)
    
    def process_message(self, message: SlackMessage) -> SlackMessage:
        """
        Process a single message to extract progress and next steps.
        
        Args:
            message: SlackMessage object to process
            
        Returns:
            Updated SlackMessage with progress and next_steps populated
        """
        try:
            progress, next_steps, confidence = self._extract_progress_and_next_steps(message.text)
            
            message.progress = progress
            message.next_steps = next_steps
            message.confidence_score = confidence
            message.processed_at = datetime.now()
            
            self.logger.debug(f"Processed message from {message.username}")
            
        except Exception as e:
            self.logger.error(f"Error processing message from {message.username}: {e}")
            message.progress = None
            message.next_steps = None
            message.confidence_score = 0.0
            message.processed_at = datetime.now()
        
        return message
    
    def process_messages(self, messages: List[SlackMessage]) -> List[SlackMessage]:
        """
        Process multiple messages to extract progress and next steps.
        
        Args:
            messages: List of SlackMessage objects to process
            
        Returns:
            List of updated SlackMessage objects
        """
        processed_messages = []
        
        for i, message in enumerate(messages):
            self.logger.info(f"Processing message {i+1}/{len(messages)} from {message.username}")
            processed_message = self.process_message(message)
            processed_messages.append(processed_message)
        
        return processed_messages
    
    def _extract_progress_and_next_steps(self, text: str) -> Tuple[Optional[str], Optional[str], float]:
        """
        Use OpenAI to extract progress and next steps from message text.
        
        Args:
            text: Message text to analyze
            
        Returns:
            Tuple of (progress, next_steps, confidence_score)
        """
        prompt = self._build_extraction_prompt(text)
        
        try:
            response = openai.chat.completions.create(
                model=self.settings.openai_model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            result = response.choices[0].message.content if response.choices and response.choices[0].message and hasattr(response.choices[0].message, 'content') else None
            if result is not None:
                return self._parse_extraction_result(result)
            else:
                self.logger.error("OpenAI API returned no content in response.")
                return None, None, 0.0
        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            return None, None, 0.0
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for OpenAI."""
        return """You are an expert at analyzing workplace communication messages to extract progress updates and next steps. 

Your task is to:
1. Identify any progress or accomplishments mentioned in the message
2. Identify any next steps, plans, or future actions mentioned
3. Provide a confidence score (0-1) for your extraction

Return your response in the following JSON format:
{
    "progress": "extracted progress information or null if none found",
    "next_steps": "extracted next steps information or null if none found",
    "confidence": 0.85
}

Be concise and focus on the key information. If no clear progress or next steps are mentioned, return null for those fields."""
    
    def _build_extraction_prompt(self, text: str) -> str:
        """Build the extraction prompt for a specific message."""
        return f"""Please analyze the following message and extract any progress updates and next steps:

Message: "{text}"

Please provide your response in the specified JSON format."""
    
    def _parse_extraction_result(self, result: str) -> Tuple[Optional[str], Optional[str], float]:
        """Parse the OpenAI response to extract progress, next steps, and confidence."""
        try:
            # Try to parse as JSON
            parsed = json.loads(result)
            
            progress = parsed.get('progress')
            next_steps = parsed.get('next_steps')
            confidence = float(parsed.get('confidence', 0.0))
            
            # Convert "null" strings to None
            if progress == "null":
                progress = None
            if next_steps == "null":
                next_steps = None
            
            return progress, next_steps, confidence
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            self.logger.error(f"Error parsing OpenAI response: {e}")
            self.logger.debug(f"Response was: {result}")
            return None, None, 0.0
