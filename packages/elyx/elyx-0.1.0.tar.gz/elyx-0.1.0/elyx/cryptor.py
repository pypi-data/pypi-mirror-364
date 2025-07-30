"""
Core encryption and decryption functionality using Fernet symmetric encryption
"""

import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Optional, Tuple


class Cryptor:
    """Handles encryption and decryption operations"""
    
    def __init__(self):
        self.iterations = 100000  # PBKDF2 iterations for key derivation
        
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """Derive encryption key from password using PBKDF2"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=self.iterations,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def encrypt(self, data: str, password: str) -> Tuple[bool, str, Optional[str]]:
        """
        Encrypt data with password
        
        Returns:
            Tuple of (success, encrypted_data or error_message, salt_for_debugging)
        """
        try:
            # Generate random salt
            salt = os.urandom(16)
            
            # Derive key from password
            key = self._derive_key(password, salt)
            
            # Create Fernet instance and encrypt
            f = Fernet(key)
            encrypted_data = f.encrypt(data.encode())
            
            # Combine salt and encrypted data for storage
            combined = salt + encrypted_data
            
            # Encode to base64 for easy copying
            encoded = base64.urlsafe_b64encode(combined).decode()
            
            return True, encoded, None
            
        except Exception as e:
            return False, f"Encryption failed: {str(e)}", None
    
    def decrypt(self, encrypted_data: str, password: str) -> Tuple[bool, str]:
        """
        Decrypt data with password
        
        Returns:
            Tuple of (success, decrypted_data or error_message)
        """
        try:
            # Decode from base64
            try:
                combined = base64.urlsafe_b64decode(encrypted_data.encode())
            except Exception:
                return False, "Invalid encrypted data format. Please check your input."
            
            # Extract salt and encrypted data
            if len(combined) < 16:
                return False, "Invalid encrypted data. Data too short."
                
            salt = combined[:16]
            encrypted = combined[16:]
            
            # Derive key from password
            key = self._derive_key(password, salt)
            
            # Decrypt
            try:
                f = Fernet(key)
                decrypted = f.decrypt(encrypted)
                return True, decrypted.decode()
            except Exception:
                return False, "Decryption failed. Wrong password or corrupted data."
                
        except Exception as e:
            return False, f"Decryption error: {str(e)}"
    
    def validate_password(self, password: str) -> Tuple[bool, Optional[str]]:
        """
        Validate password strength
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if len(password) > 128:
            return False, "Password must be less than 128 characters"
            
        return True, None