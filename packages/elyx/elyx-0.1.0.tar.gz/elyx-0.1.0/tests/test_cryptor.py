"""
Tests for the Cryptor class
"""

import pytest
from elyx.cryptor import Cryptor
from elyx.utils import generate_password


class TestCryptor:
    
    def setup_method(self):
        """Set up test fixtures"""
        self.cryptor = Cryptor()
        self.test_data = "Hello, this is a secret message!"
        self.test_password = "MySecurePassword123!"
    
    def test_encrypt_decrypt_success(self):
        """Test successful encryption and decryption"""
        # Encrypt
        success, encrypted, _ = self.cryptor.encrypt(self.test_data, self.test_password)
        assert success is True
        assert encrypted != self.test_data
        assert len(encrypted) > 0
        
        # Decrypt
        success, decrypted = self.cryptor.decrypt(encrypted, self.test_password)
        assert success is True
        assert decrypted == self.test_data
    
    def test_encrypt_with_generated_password(self):
        """Test encryption with generated password"""
        password = generate_password()
        
        success, encrypted, _ = self.cryptor.encrypt(self.test_data, password)
        assert success is True
        
        success, decrypted = self.cryptor.decrypt(encrypted, password)
        assert success is True
        assert decrypted == self.test_data
    
    def test_decrypt_with_wrong_password(self):
        """Test decryption fails with wrong password"""
        success, encrypted, _ = self.cryptor.encrypt(self.test_data, self.test_password)
        assert success is True
        
        wrong_password = "WrongPassword123!"
        success, result = self.cryptor.decrypt(encrypted, wrong_password)
        assert success is False
        assert "Wrong password" in result
    
    def test_decrypt_invalid_data(self):
        """Test decryption with invalid encrypted data"""
        invalid_data = "ThisIsNotEncryptedData"
        
        success, result = self.cryptor.decrypt(invalid_data, self.test_password)
        assert success is False
        assert "Invalid encrypted data" in result
    
    def test_password_validation(self):
        """Test password validation"""
        # Too short
        valid, error = self.cryptor.validate_password("short")
        assert valid is False
        assert "at least 8 characters" in error
        
        # Valid password
        valid, error = self.cryptor.validate_password("ValidPass123")
        assert valid is True
        assert error is None
        
        # Too long
        long_password = "a" * 129
        valid, error = self.cryptor.validate_password(long_password)
        assert valid is False
        assert "less than 128 characters" in error
    
    def test_encrypt_empty_data(self):
        """Test encryption with empty data"""
        success, result, _ = self.cryptor.encrypt("", self.test_password)
        assert success is True  # Empty data can be encrypted
        
        success, decrypted = self.cryptor.decrypt(result, self.test_password)
        assert success is True
        assert decrypted == ""
    
    def test_encrypt_unicode_data(self):
        """Test encryption with Unicode characters"""
        unicode_data = "Hello 世界! 🔐 Encryption test"
        
        success, encrypted, _ = self.cryptor.encrypt(unicode_data, self.test_password)
        assert success is True
        
        success, decrypted = self.cryptor.decrypt(encrypted, self.test_password)
        assert success is True
        assert decrypted == unicode_data
    
    def test_different_encryptions_same_data(self):
        """Test that same data produces different encrypted outputs (due to random salt)"""
        success1, encrypted1, _ = self.cryptor.encrypt(self.test_data, self.test_password)
        success2, encrypted2, _ = self.cryptor.encrypt(self.test_data, self.test_password)
        
        assert success1 is True
        assert success2 is True
        assert encrypted1 != encrypted2  # Different due to random salt
        
        # But both should decrypt to same data
        _, decrypted1 = self.cryptor.decrypt(encrypted1, self.test_password)
        _, decrypted2 = self.cryptor.decrypt(encrypted2, self.test_password)
        
        assert decrypted1 == self.test_data
        assert decrypted2 == self.test_data