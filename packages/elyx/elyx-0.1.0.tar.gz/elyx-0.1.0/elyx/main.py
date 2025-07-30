"""
Main entry point for Elyx encryption tool
"""

import sys
import random
from .cryptor import Cryptor
from .utils import generate_password, validate_password_strength
from . import ui


def handle_encryption(cryptor: Cryptor):
    """Handle text encryption with improved UX"""
    ui.show_separator()
    ui.show_info("Encryption Mode - Secure your text with a password")
    
    # Get text to encrypt
    text = ui.get_text_input("Enter the text to encrypt", multiline=True)
    
    if not text:
        ui.show_error("No text provided!")
        return
    
    # Show processing
    ui.show_processing("Preparing encryption...")
    
    # Password options
    ui.console.print("\n[bold yellow]Password Options:[/bold yellow]")
    ui.console.print("1. Generate secure password (recommended)")
    ui.console.print("2. Enter custom password")
    
    password_choice = ui.Prompt.ask(
        "\n[bold cyan]Select password option[/bold cyan]",
        choices=["1", "2"],
        default="1"
    )
    
    if password_choice == "1":
        password = generate_password()
        ui.show_result("Generated Password", password, style="cyan")
        ui.show_info("⚠️  Save this password! You'll need it to decrypt your text.")
    else:
        ui.show_info("💡 Your password will be visible as you type for verification")
        while True:
            password = ui.get_password_input("Enter password (min 8 characters)", mask=False)
            valid, error = cryptor.validate_password(password)
            if valid:
                # Check password strength
                strength = validate_password_strength(password)
                if strength["score"] < 3:
                    ui.show_info(f"Password strength: {strength['strength']}")
                    if not ui.Confirm.ask("This password is weak. Continue anyway?", default=False):
                        continue
                break
            else:
                ui.show_error(error)
    
    # Encrypt with authentic delay
    encryption_delay = random.uniform(5, 10)  # Random 5-10 seconds
    
    # First encrypt the data (instant)
    success, result, _ = cryptor.encrypt(text, password)
    
    if success:
        # Show progress bar for authentic feel
        ui.show_encryption_progress(encryption_delay)
        
        ui.show_success("Text encrypted successfully!")
        ui.show_result("Encrypted Data", result, style="green")
        ui.show_info("💡 Your encrypted text has been copied to clipboard!")
    else:
        ui.show_error(f"Encryption failed: {result}")


def handle_decryption(cryptor: Cryptor):
    """Handle text decryption with improved UX"""
    ui.show_separator()
    ui.show_info("Decryption Mode - Recover your original text")
    
    # Get encrypted text
    encrypted_text = ui.get_text_input("Enter the encrypted text", multiline=True)
    
    if not encrypted_text:
        ui.show_error("No encrypted text provided!")
        return
    
    # Get password
    ui.show_info("💡 Your password will be visible as you type for verification")
    password = ui.get_password_input("Enter the password used for encryption", mask=False)
    
    # Decrypt with authentic delay
    decryption_delay = random.uniform(150, 180)  # Random 2.5-3 minutes (150-180 seconds)
    
    # First decrypt the data (instant)
    success, result = cryptor.decrypt(encrypted_text.strip(), password)
    
    if success:
        # Show progress bar for authentic feel
        ui.show_decryption_progress(decryption_delay)
        
        ui.show_success("Text decrypted successfully!")
        ui.show_result("Decrypted Text", result, style="blue", copyable=False)
        ui.show_info("💡 Select and copy the text above if needed")
    else:
        # Still show some progress before failing for authenticity
        ui.show_decryption_progress(random.uniform(3, 5))
        ui.show_error(f"Decryption failed: {result}")
        ui.show_info("Make sure you're using the correct password and the encrypted text is complete")


def handle_password_generation():
    """Handle password generation with improved UX"""
    ui.show_separator()
    ui.show_info("Password Generator - Create secure passwords")
    
    ui.show_processing("Generating secure password...")
    
    password = generate_password()
    strength = validate_password_strength(password)
    
    ui.show_result("Generated Password", password, style="cyan")
    ui.show_info(f"Password strength: {strength['strength']} (Score: {strength['score']}/5)")
    ui.show_success("Password copied to clipboard!")


def main():
    """Main application loop with improved UX"""
    # Initialize
    cryptor = Cryptor()
    
    # Clear screen and show banner
    ui.clear_screen()
    ui.show_banner()
    
    # Main loop
    while True:
        ui.show_menu()
        
        choice = ui.get_menu_choice()
        
        if choice == "1":  # Encrypt
            handle_encryption(cryptor)
            ui.console.print("\n[dim]Press Enter to continue...[/dim]")
            ui.console.input()
            ui.clear_screen()
            ui.show_banner()
            
        elif choice == "2":  # Decrypt
            handle_decryption(cryptor)
            ui.console.print("\n[dim]Press Enter to continue...[/dim]")
            ui.console.input()
            ui.clear_screen()
            ui.show_banner()
            
        elif choice == "3":  # Generate password
            handle_password_generation()
            ui.console.print("\n[dim]Press Enter to continue...[/dim]")
            ui.console.input()
            ui.clear_screen()
            ui.show_banner()
            
        elif choice == "4":  # Copy last result
            ui.show_separator()
            ui.copy_last_result()
            ui.console.print("\n[dim]Press Enter to continue...[/dim]")
            ui.console.input()
            ui.clear_screen()
            ui.show_banner()
            
        elif choice == "5":  # Help
            ui.clear_screen()
            ui.show_help()
            ui.clear_screen()
            ui.show_banner()
            
        elif choice == "6":  # Exit
            if ui.confirm_exit():
                ui.show_info("Thank you for using Elyx! Stay secure! 🔐")
                sys.exit(0)
            else:
                ui.clear_screen()
                ui.show_banner()
        
        else:
            ui.show_error("Invalid option! Please try again.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        ui.console.print("\n\n[yellow]Interrupted by user. Exiting...[/yellow]")
        sys.exit(0)
    except Exception as e:
        ui.console.print(f"\n[red]An error occurred: {str(e)}[/red]")
        sys.exit(1)