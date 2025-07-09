#!/usr/bin/env python3
"""
Slack Message Scraper CLI

A command-line interface for scraping Slack messages and extracting progress and next steps.
"""

import typer
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from src.agent import SlackMessageAgent
from src.config import get_settings

app = typer.Typer(help="Slack Message Scraper - Extract progress and next steps from Slack messages")
console = Console()


@app.command()
def scrape(
    user_id: Optional[str] = typer.Option(None, "--user", "-u", help="Scrape messages from a specific user"),
    limit: Optional[int] = typer.Option(None, "--limit", "-l", help="Maximum number of messages to process"),
    output_format: Optional[str] = typer.Option(None, "--format", "-f", help="Output format (json or csv)"),
    show_results: bool = typer.Option(True, "--show/--no-show", help="Show results in console"),
):
    """Scrape messages from Slack channel and process them."""
    try:
        agent = SlackMessageAgent()
        
        rprint("[bold green]Starting Slack message scraping...[/bold green]")
        
        output_file = agent.run_full_pipeline(
            user_id=user_id,
            limit=limit,
            output_format=output_format,
            show_results=show_results
        )
        
        rprint(f"[bold green]✅ Results saved to: {output_file}[/bold green]")
        
    except Exception as e:
        rprint(f"[bold red]❌ Error: {e}[/bold red]")
        raise typer.Exit(1)


@app.command()
def users(
    limit: Optional[int] = typer.Option(None, "--limit", "-l", help="Maximum number of messages to scan")
):
    """List users who have posted in the channel."""
    try:
        agent = SlackMessageAgent()
        
        rprint("[bold blue]Scanning channel for users...[/bold blue]")
        
        users = agent.get_users_in_channel()
        
        if not users:
            rprint("[yellow]No users found in the channel.[/yellow]")
            return
        
        # Create a table
        table = Table(title="Channel Users")
        table.add_column("User ID", style="cyan")
        table.add_column("Username", style="magenta")
        table.add_column("Message Count", style="green")
        
        for user in sorted(users, key=lambda x: x['message_count'], reverse=True):
            table.add_row(
                user['user_id'],
                user['username'],
                str(user['message_count'])
            )
        
        console.print(table)
        
    except Exception as e:
        rprint(f"[bold red]❌ Error: {e}[/bold red]")
        raise typer.Exit(1)


@app.command()
def test():
    """Test connections to Slack and OpenAI APIs."""
    try:
        settings = get_settings()
        agent = SlackMessageAgent(settings)
        
        rprint("[bold blue]Testing API connections...[/bold blue]")
        
        # Test Slack connection
        if agent.slack_scraper.test_connection():
            rprint("[green]✅ Slack API connection successful[/green]")
        else:
            rprint("[red]❌ Slack API connection failed[/red]")
            raise typer.Exit(1)
        
        # Test OpenAI by processing a simple message
        from src.models import SlackMessage
        from datetime import datetime
        
        test_message = SlackMessage(
            user_id="test_user",
            username="test_user",
            timestamp=datetime.now(),
            text="I completed the project setup yesterday. Next, I need to implement the API endpoints.",
            channel_id="test_channel"
        )
        
        processed = agent.message_processor.process_message(test_message)
        
        if processed.progress and processed.next_steps:
            rprint("[green]✅ OpenAI API connection successful[/green]")
            rprint(f"[dim]Test extraction - Progress: {processed.progress}[/dim]")
            rprint(f"[dim]Test extraction - Next Steps: {processed.next_steps}[/dim]")
        else:
            rprint("[yellow]⚠️  OpenAI API connected but extraction may need tuning[/yellow]")
        
        rprint("[bold green]🎉 All systems ready![/bold green]")
        
    except Exception as e:
        rprint(f"[bold red]❌ Error: {e}[/bold red]")
        raise typer.Exit(1)


@app.command()
def config():
    """Show current configuration."""
    try:
        settings = get_settings()
        
        table = Table(title="Current Configuration")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="magenta")
        
        table.add_row("Slack Channel ID", settings.slack_channel_id)
        table.add_row("OpenAI Model", settings.openai_model)
        table.add_row("Log Level", settings.log_level)
        table.add_row("Output Format", settings.output_format)
        table.add_row("Max Messages", str(settings.max_messages))
        
        console.print(table)
        
    except Exception as e:
        rprint(f"[bold red]❌ Error: {e}[/bold red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
