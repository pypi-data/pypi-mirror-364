"""
Elyx - A secure terminal-based encryption/decryption tool
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .cryptor import Cryptor
from .utils import generate_password

__all__ = ["Cryptor", "generate_password"]