#!/usr/bin/env python3
"""
100cli - The 100 LoC CLI agent made to be hacked
A simple, extensible CLI agent framework
"""

import os
from typing import Optional

import typer
from rich.console import Console

from .UI import show_banner, show_welcome, get_boxed_input

console = Console()

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

app = typer.Typer(
    help="🤖 The 100 LoC CLI agent made to be hacked", invoke_without_command=True
)


@app.callback()
def main_callback(
    message: Optional[str] = typer.Argument(None, help="Message to send to the agent"),
    version: bool = typer.Option(
        False, "--version", "-v", help="Show version information"
    ),
):
    """
    🤖 The 100 LoC CLI agent made to be hacked
    """
    if version:
        show_version()
        return

    if message:
        process_message(message)
    else:
        interactive_mode()


def interactive_mode():
    """Run the CLI in interactive mode"""
    show_banner()
    show_welcome()

    while True:
        try:
            user_input = get_boxed_input("100cli")

            if user_input.lower() in ["exit", "quit", "q"]:
                typer.echo("Goodbye! 👋")
                break
            elif user_input.lower() in ["help", "h"]:
                show_help()
            elif user_input:
                process_message(user_input)

        except KeyboardInterrupt:
            typer.echo("\nGoodbye! 👋")
            break
        except EOFError:
            typer.echo("\nGoodbye! 👋")
            break


def process_message(message: str):
    """Process a user message and generate a response using OpenAI"""
    if not OPENAI_AVAILABLE:
        console.print("❌ [red]OpenAI not installed[/red]")
        console.print("💡 Install with: pip install '100cli[openai]'")
        console.print(f"🔧 [dim]You said: {message}[/dim]")
        return
    
    try:
        # Initialize OpenAI client (requires OPENAI_API_KEY environment variable)
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        if not os.getenv("OPENAI_API_KEY"):
            console.print("❌ [red]Error: OPENAI_API_KEY environment variable not set[/red]")
            console.print("💡 Set your API key: export OPENAI_API_KEY='your-key-here'")
            return
        
        # Make API call to OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant in a CLI tool called 100cli."},
                {"role": "user", "content": message}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        # Display the response
        ai_response = response.choices[0].message.content
        console.print(f"🤖 [bold green]{ai_response}[/bold green]")
        
    except Exception as e:
        console.print(f"❌ [red]Error: {str(e)}[/red]")
        console.print("💡 Make sure your OPENAI_API_KEY is valid and you have credits available.")


def show_help():
    """Show available commands"""
    help_text = """
Available commands:
  help, h     - Show this help message
  exit, quit, q - Exit the CLI

To extend 100cli:
1. Add new commands to the process_message() function
2. Integrate with your favorite AI model or API
3. Add new tools and capabilities
4. Customize the UI in the UI/ folder

Happy hacking! ✨
    """
    typer.echo(help_text)


def show_version():
    """Show version information"""
    typer.echo("100cli v0.0.1")
    typer.echo("🤖 The 100 LoC CLI agent made to be hacked")


def main():
    """Entry point for the CLI"""
    app()


if __name__ == "__main__":
    main()
