"""
Terminal UI components for Elyx
"""

import os
import platform
import pyperclip
import time
import random
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.table import Table
from rich.layout import Layout
from rich.columns import Columns
from rich import box
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn

# Initialize console
console = Console()

# Store last result for copy functionality
last_result = {
    "content": None,
    "type": None  # 'encrypted', 'decrypted', 'password'
}


def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if platform.system() == 'Windows' else 'clear')


def show_banner():
    """Display application banner with improved styling"""
    banner_text = """
╔═╗╦  ╦ ╦╔╗╔
║╣ ║  ╚╦╝╔╩╗
╚═╝╩═╝ ╩ ╩ ╩
    """
    
    subtitle = "🔐 Advanced Terminal Encryption Tool"
    credit = "Open-Sourced by Prince"
    
    banner_panel = Panel(
        Text(banner_text, style="bold cyan", justify="center") + "\n" + 
        Text(subtitle, style="dim white", justify="center") + "\n" +
        Text(credit, style="dim yellow", justify="center"),
        border_style="cyan",
        box=box.DOUBLE,
        padding=(1, 2)
    )
    
    console.print(banner_panel)
    console.print()


def show_menu():
    """Display main menu with improved layout"""
    menu_table = Table(show_header=False, box=None, padding=(0, 2))
    menu_table.add_column("Option", style="bold cyan", no_wrap=True)
    menu_table.add_column("Description", style="white")
    menu_table.add_column("Shortcut", style="dim yellow")
    
    menu_table.add_row("1", "Encrypt Text", "[E]")
    menu_table.add_row("2", "Decrypt Text", "[D]")
    menu_table.add_row("3", "Generate Secure Password", "[G]")
    menu_table.add_row("4", "Copy Last Result", "[C]")
    menu_table.add_row("5", "Help", "[H]")
    menu_table.add_row("6", "Exit", "[Q]")
    
    menu_panel = Panel(
        menu_table,
        title="[bold white]Main Menu[/bold white]",
        border_style="blue",
        box=box.ROUNDED,
        padding=(1, 2)
    )
    
    console.print(menu_panel)
    console.print()


def get_menu_choice():
    """Get user's menu choice with improved input handling"""
    choice = Prompt.ask(
        "[bold cyan]Select option[/bold cyan]",
        choices=["1", "2", "3", "4", "5", "6", "e", "d", "g", "c", "h", "q"],
        show_choices=False
    )
    
    # Map shortcuts to numbers
    shortcuts = {
        "e": "1", "d": "2", "g": "3", 
        "c": "4", "h": "5", "q": "6"
    }
    
    return shortcuts.get(choice.lower(), choice)


def get_text_input(prompt_text, multiline=True):
    """Get text input from user with improved handling"""
    if multiline:
        console.print(f"\n[bold yellow]{prompt_text}[/bold yellow]")
        console.print("[dim]💡 For multi-line input: Type your text and press Enter twice to finish[/dim]")
        console.print("[dim]💡 For single line: Type your text and press Enter once[/dim]\n")
        
        lines = []
        empty_line_count = 0
        
        while True:
            try:
                line = console.input("> ")
                if line == "" and lines:  # Empty line after some input
                    empty_line_count += 1
                    if empty_line_count >= 1:  # One empty line to finish
                        break
                else:
                    empty_line_count = 0
                    lines.append(line)
            except (EOFError, KeyboardInterrupt):
                break
        
        return "\n".join(lines)
    else:
        return Prompt.ask(f"\n[bold yellow]{prompt_text}[/bold yellow]")


def get_password_input(prompt_text="Enter password", mask=False):
    """Get password input (optionally with masking)"""
    return Prompt.ask(
        f"\n[bold yellow]{prompt_text}[/bold yellow]",
        password=mask
    )


def show_result(title, content, style="green", copyable=True):
    """Display result in a formatted panel with copy functionality"""
    global last_result
    
    # Store result for copy functionality
    if copyable:
        last_result["content"] = content
        last_result["type"] = title.lower()
    
    # Create result panel
    result_text = Text(content, style=style)
    result_panel = Panel(
        result_text,
        title=f"[bold]{title}[/bold]",
        border_style=style,
        box=box.ROUNDED,
        padding=(1, 2)
    )
    
    console.print(result_panel)
    
    # Auto-copy for important results (but not decrypted text)
    if copyable and title.lower() in ["encrypted data", "password"]:
        try:
            pyperclip.copy(content)
            console.print(f"[dim green]✓ Automatically copied to clipboard![/dim green]")
        except Exception:
            console.print(f"[dim yellow]💡 Press [bold]4[/bold] or [bold]C[/bold] in the menu to copy this result[/dim yellow]")
    
    console.print()


def copy_last_result():
    """Copy the last result to clipboard"""
    if last_result["content"] is None:
        show_error("No result to copy! Encrypt or generate a password first.")
        return False
    
    # Don't allow copying decrypted text through this menu option
    if last_result["type"] == "decrypted text":
        show_info("For security, decrypted text must be manually selected and copied.")
        return False
    
    try:
        pyperclip.copy(last_result["content"])
        result_type = last_result["type"] or "result"
        show_success(f"✓ Last {result_type} copied to clipboard!")
        return True
    except Exception as e:
        show_error(f"Failed to copy to clipboard: {str(e)}")
        return False


def show_success(message):
    """Display success message with improved styling"""
    success_panel = Panel(
        Text(f"✅ {message}", style="bold green"),
        border_style="green",
        box=box.ROUNDED,
        padding=(0, 2)
    )
    console.print(success_panel)
    console.print()


def show_error(message):
    """Display error message with improved styling"""
    error_panel = Panel(
        Text(f"❌ {message}", style="bold red"),
        border_style="red",
        box=box.ROUNDED,
        padding=(0, 2)
    )
    console.print(error_panel)
    console.print()


def show_info(message):
    """Display info message with improved styling"""
    info_panel = Panel(
        Text(f"ℹ️  {message}", style="bold blue"),
        border_style="blue",
        box=box.ROUNDED,
        padding=(0, 2)
    )
    console.print(info_panel)
    console.print()


def show_help():
    """Display help information with improved formatting"""
    help_text = """
[bold cyan]🔐 Elyx - Secure Encryption Tool[/bold cyan]

[bold yellow]Features:[/bold yellow]
• Strong AES encryption with PBKDF2 key derivation
• Secure password generation (10 characters)
• Easy copy-to-clipboard functionality
• Beautiful terminal interface

[bold yellow]How to Use:[/bold yellow]

[bold]1. Encrypting Text:[/bold]
   - Select option 1 or press E
   - Enter your text (press Enter twice for multi-line)
   - Choose password option (generate or custom)
   - Your encrypted text is automatically copied!

[bold]2. Decrypting Text:[/bold]
   - Select option 2 or press D
   - Paste your encrypted text
   - Enter the password used for encryption
   - Your original text is revealed

[bold]3. Generate Password:[/bold]
   - Select option 3 or press G
   - A secure 10-character password is created
   - Automatically copied to clipboard

[bold]4. Copy Last Result:[/bold]
   - Select option 4 or press C
   - Copies the last encryption/decryption result

[bold yellow]Security Notes:[/bold yellow]
• All operations happen locally
• Passwords are never stored
• Each encryption uses a unique salt
• 100,000 PBKDF2 iterations for key derivation

[bold yellow]Tips:[/bold yellow]
• Use generated passwords for maximum security
• Store passwords in a secure password manager
• Encrypted text is Base64 encoded for easy sharing
    """
    
    help_panel = Panel(
        help_text,
        title="[bold white]Help & Instructions[/bold white]",
        border_style="blue",
        box=box.DOUBLE,
        padding=(1, 3)
    )
    
    console.print(help_panel)
    console.print("\n[dim]Press Enter to return to menu...[/dim]")
    console.input()


def confirm_exit():
    """Confirm before exiting"""
    return Confirm.ask("\n[bold yellow]Are you sure you want to exit?[/bold yellow]", default=False)


def show_processing(message="Processing..."):
    """Show processing indicator"""
    console.print(f"\n[bold cyan]⏳ {message}[/bold cyan]")


def show_separator():
    """Show a visual separator"""
    console.print("\n" + "─" * 60 + "\n", style="dim")


def show_encryption_progress(duration_seconds):
    """Show progress bar for encryption with random duration"""
    messages = [
        "Generating encryption keys...",
        "Applying AES-256 encryption...",
        "Adding salt and padding...",
        "Finalizing secure encryption...",
        "Verifying encryption integrity..."
    ]
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=40),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Encrypting data...", total=100)
        
        steps = len(messages)
        step_duration = duration_seconds / steps
        
        for i, message in enumerate(messages):
            progress.update(task, description=f"[cyan]{message}")
            
            # Progress for this step
            step_progress = 100 / steps
            start_progress = i * step_progress
            
            # Smooth progress update
            for j in range(20):
                current = start_progress + (step_progress * j / 20)
                progress.update(task, completed=current)
                time.sleep(step_duration / 20)
        
        # Ensure we reach 100%
        progress.update(task, completed=100, description="[green]Encryption complete!")
        time.sleep(0.5)


def show_decryption_progress(duration_seconds):
    """Show progress bar for decryption with random duration"""
    messages = [
        "Initializing decryption engine...",
        "Validating encryption signature...",
        "Deriving decryption keys...",
        "Applying PBKDF2 iterations...",
        "Decrypting data blocks...",
        "Reconstructing original data...",
        "Verifying data integrity...",
        "Finalizing decryption process..."
    ]
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=40),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[yellow]Decrypting data...", total=100)
        
        steps = len(messages)
        step_duration = duration_seconds / steps
        
        for i, message in enumerate(messages):
            progress.update(task, description=f"[yellow]{message}")
            
            # Progress for this step
            step_progress = 100 / steps
            start_progress = i * step_progress
            
            # Smooth progress update with variable speed to seem more authentic
            for j in range(30):
                # Add some randomness to make it look more authentic
                if random.random() < 0.1:  # 10% chance of slight pause
                    time.sleep(step_duration / 25)
                
                current = start_progress + (step_progress * j / 30)
                progress.update(task, completed=current)
                time.sleep(step_duration / 30)
        
        # Ensure we reach 100%
        progress.update(task, completed=100, description="[green]Decryption complete!")
        time.sleep(0.5)