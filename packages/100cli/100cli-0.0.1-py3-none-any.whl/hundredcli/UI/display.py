"""
Display utilities for 100cli
"""

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from rich.align import Align

console = Console()


def show_banner():
    """Display the 100cli banner"""
    banner_text = Text()
    banner_text.append("\n")
    banner_text.append(
        "    ██╗ ██████╗  ██████╗  ██████╗██╗     ██╗\n", style="bold white"
    )
    banner_text.append(
        "   ███║██╔═████╗██╔═████╗██╔════╝██║     ██║\n", style="bold white"
    )
    banner_text.append(
        "   ╚██║██║██╔██║██║██╔██║██║     ██║     ██║\n", style="bold white"
    )
    banner_text.append(
        "    ██║████╔╝██║████╔╝██║██║     ██║     ██║\n", style="bold white"
    )
    banner_text.append(
        "    ██║╚██████╔╝╚██████╔╝╚██████╗███████╗██║\n", style="bold white"
    )
    banner_text.append(
        "    ╚═╝ ╚═════╝  ╚═════╝  ╚═════╝╚══════╝╚═╝\n", style="bold white"
    )
    banner_text.append(
        "\n    🤖 The 100 LoC CLI agent made to be hacked ✨", style="bold green"
    )

    console.print(Panel(Align.center(banner_text), border_style="cyan"))


def show_welcome():
    """Display welcome message"""
    welcome_text = Text()
    welcome_text.append("Welcome to 100cli - Your hackable CLI agent!\n", style="bold")
    welcome_text.append(
        "Type 'help' for available commands or 'exit' to quit.", style="dim"
    )

    console.print(Panel(welcome_text, title="Welcome", border_style="green"))
    console.print()


def get_boxed_input(prompt_text="100cli"):
    """Get user input with a simple > prompt"""
    return Prompt.ask(f"[bold bright_blue]>[/bold bright_blue]", console=console)
