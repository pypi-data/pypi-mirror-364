"""
Utility functions for password generation and validation
"""

import string
import secrets
from typing import Optional


def generate_password(length: int = 10) -> str:
    """
    Generate a secure random password
    
    Args:
        length: Password length (default: 10)
        
    Returns:
        Generated password string
    """
    # Define character sets
    uppercase = string.ascii_uppercase
    lowercase = string.ascii_lowercase
    digits = string.digits
    symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    # Ensure at least one character from each set
    password = [
        secrets.choice(uppercase),
        secrets.choice(lowercase),
        secrets.choice(digits),
        secrets.choice(symbols)
    ]
    
    # Fill the rest randomly from all characters
    all_chars = uppercase + lowercase + digits + symbols
    for _ in range(length - 4):
        password.append(secrets.choice(all_chars))
    
    # Shuffle the password
    secrets.SystemRandom().shuffle(password)
    
    return ''.join(password)


def mask_password(password: str, show_chars: int = 2) -> str:
    """
    Mask password for display purposes
    
    Args:
        password: Password to mask
        show_chars: Number of characters to show at start and end
        
    Returns:
        Masked password string
    """
    if len(password) <= show_chars * 2:
        return "*" * len(password)
    
    masked_middle = "*" * (len(password) - show_chars * 2)
    return password[:show_chars] + masked_middle + password[-show_chars:]


def validate_input(text: str, max_length: int = 10000) -> tuple[bool, Optional[str]]:
    """
    Validate user input
    
    Args:
        text: Input text to validate
        max_length: Maximum allowed length
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not text or not text.strip():
        return False, "Input cannot be empty"
    
    if len(text) > max_length:
        return False, f"Input too long (max {max_length} characters)"
    
    return True, None


def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncate text for display
    
    Args:
        text: Text to truncate
        max_length: Maximum length before truncation
        suffix: Suffix to add when truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def validate_password_strength(password: str) -> dict:
    """
    Validate password strength and return detailed analysis
    
    Args:
        password: Password to analyze
        
    Returns:
        Dictionary with score, strength, and feedback
    """
    score = 0
    feedback = []
    
    # Length check
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    
    # Character variety
    if any(c.isupper() for c in password):
        score += 1
    else:
        feedback.append("Add uppercase letters")
    
    if any(c.islower() for c in password):
        score += 1
    else:
        feedback.append("Add lowercase letters")
    
    if any(c.isdigit() for c in password):
        score += 1
    else:
        feedback.append("Add numbers")
    
    if any(c in string.punctuation for c in password):
        score += 1
    else:
        feedback.append("Add special characters")
    
    # Determine strength
    if score <= 2:
        strength = "Weak"
    elif score <= 4:
        strength = "Moderate"
    else:
        strength = "Strong"
    
    return {
        "score": min(score, 5),
        "strength": strength,
        "feedback": feedback
    }