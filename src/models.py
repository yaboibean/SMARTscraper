from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class SlackMessage:
    """Represents a Slack message with extracted progress and next steps."""
    
    user_id: str
    username: str
    timestamp: datetime
    text: str
    channel_id: str
    thread_ts: Optional[str] = None
    
    # Extracted content
    progress: Optional[str] = None
    next_steps: Optional[str] = None
    
    # Metadata
    processed_at: Optional[datetime] = None
    confidence_score: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for JSON serialization."""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'timestamp': self.timestamp.isoformat(),
            'text': self.text,
            'channel_id': self.channel_id,
            'thread_ts': self.thread_ts,
            'progress': self.progress,
            'next_steps': self.next_steps,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'confidence_score': self.confidence_score
        }


@dataclass
class ProcessingResult:
    """Result of processing messages."""
    
    total_messages: int
    processed_messages: int
    failed_messages: int
    results: List[SlackMessage]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for JSON serialization."""
        return {
            'total_messages': self.total_messages,
            'processed_messages': self.processed_messages,
            'failed_messages': self.failed_messages,
            'results': [msg.to_dict() for msg in self.results]
        }
