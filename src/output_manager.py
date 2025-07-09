from typing import List, Optional
import json
import csv
from datetime import datetime
from pathlib import Path
import logging
from src.models import SlackMessage, ProcessingResult


class OutputManager:
    """Handles output formatting and file writing."""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
    
    def save_results(self, result: ProcessingResult, format: str = "json") -> str:
        """
        Save processing results to file.
        
        Args:
            result: ProcessingResult object
            format: Output format ("json" or "csv")
            
        Returns:
            Path to the saved file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format.lower() == "json":
            filename = f"slack_messages_{timestamp}.json"
            return self._save_as_json(result, filename)
        elif format.lower() == "csv":
            filename = f"slack_messages_{timestamp}.csv"
            return self._save_as_csv(result, filename)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _save_as_json(self, result: ProcessingResult, filename: str) -> str:
        """Save results as JSON file."""
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Results saved to {filepath}")
        return str(filepath)
    
    def _save_as_csv(self, result: ProcessingResult, filename: str) -> str:
        """Save results as CSV file."""
        filepath = self.output_dir / filename
        
        fieldnames = [
            'user_id', 'username', 'timestamp', 'text', 'channel_id',
            'thread_ts', 'progress', 'next_steps', 'processed_at', 'confidence_score'
        ]
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for message in result.results:
                writer.writerow(message.to_dict())
        
        self.logger.info(f"Results saved to {filepath}")
        return str(filepath)
    
    def print_summary(self, result: ProcessingResult):
        """Print a summary of the processing results."""
        print(f"\n{'='*50}")
        print(f"PROCESSING SUMMARY")
        print(f"{'='*50}")
        print(f"Total messages: {result.total_messages}")
        print(f"Processed messages: {result.processed_messages}")
        print(f"Failed messages: {result.failed_messages}")
        print(f"Success rate: {result.processed_messages/result.total_messages*100:.1f}%")
        print(f"{'='*50}")
    
    def print_results(self, result: ProcessingResult, limit: Optional[int] = None):
        """Print detailed results to console."""
        messages_to_show = result.results[:limit] if limit else result.results
        
        for i, message in enumerate(messages_to_show, 1):
            print(f"\n{'-'*50}")
            print(f"Message {i} - {message.username} ({message.timestamp})")
            print(f"{'-'*50}")
            print(f"Original: {message.text}")
            print(f"\nProgress: {message.progress or 'None identified'}")
            print(f"Next Steps: {message.next_steps or 'None identified'}")
            print(f"Confidence: {message.confidence_score:.2f}")
        
        if limit and len(result.results) > limit:
            print(f"\n... and {len(result.results) - limit} more messages")
