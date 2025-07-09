# Example usage script for the Slack Message Scraper

from src.agent import SlackMessageAgent
from src.config import get_settings
import logging

def main():
    """Example usage of the Slack Message Scraper."""
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize the agent
    agent = SlackMessageAgent()
    
    # Example 1: Get all users in the channel
    print("Getting users in channel...")
    users = agent.get_users_in_channel()
    print(f"Found {len(users)} users:")
    for user in users[:5]:  # Show first 5
        print(f"  - {user['username']} ({user['user_id']}): {user['message_count']} messages")
    
    # Example 2: Process messages from a specific user
    if users:
        example_user = users[0]  # Use first user as example
        print(f"\nProcessing messages from {example_user['username']}...")
        
        result = agent.process_specific_user(
            user_id=example_user['user_id'],
            limit=10
        )
        
        print(f"Processed {result.processed_messages} messages")
        
        # Show some results
        for message in result.results[:3]:  # Show first 3
            print(f"\nMessage from {message.username}:")
            print(f"  Original: {message.text}")
            print(f"  Progress: {message.progress}")
            print(f"  Next Steps: {message.next_steps}")
            print(f"  Confidence: {message.confidence_score:.2f}")
    
    # Example 3: Run full pipeline
    print("\nRunning full pipeline...")
    output_file = agent.run_full_pipeline(
        limit=20,
        output_format="json",
        show_results=False
    )
    
    print(f"Results saved to: {output_file}")

if __name__ == "__main__":
    main()
