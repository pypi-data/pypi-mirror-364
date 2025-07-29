"""Encryption utilities for cache entries."""

import base64
import os
from typing import Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class CacheEncryption:
    """Handle encryption/decryption of cache entries."""
    
    def __init__(self, passphrase: Optional[str] = None):
        """
        Initialize encryption with optional passphrase.
        
        Args:
            passphrase: Encryption passphrase from environment or config
        """
        self.passphrase = passphrase or os.getenv("LLMCACHE_ENCRYPTION_KEY")
        self._fernet: Optional[Fernet] = None
        
        if self.passphrase:
            self._fernet = self._create_fernet(self.passphrase)
    
    def _create_fernet(self, passphrase: str) -> Fernet:
        """Create Fernet instance from passphrase."""
        # Generate salt and key
        salt = b"llm_cache_salt"  # Fixed salt for deterministic key derivation
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))
        return Fernet(key)
    
    def encrypt(self, data: str) -> str:
        """
        Encrypt data string.
        
        Args:
            data: String data to encrypt
            
        Returns:
            Base64 encoded encrypted data
        """
        if not self._fernet:
            return data
        
        encrypted = self._fernet.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt data string.
        
        Args:
            encrypted_data: Base64 encoded encrypted data
            
        Returns:
            Decrypted string data
        """
        if not self._fernet:
            return encrypted_data
        
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self._fernet.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            raise ValueError(f"Failed to decrypt data: {e}")
    
    def is_encrypted(self, data: str) -> bool:
        """
        Check if data appears to be encrypted.
        
        Args:
            data: Data to check
            
        Returns:
            True if data appears encrypted
        """
        if not self._fernet:
            return False
        
        try:
            # Try to decode as base64
            base64.urlsafe_b64decode(data.encode())
            return True
        except Exception:
            return False 