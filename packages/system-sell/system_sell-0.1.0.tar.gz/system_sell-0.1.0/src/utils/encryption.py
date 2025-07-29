"""
File encryption utilities using AES-256
"""

import os
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


class FileEncryption:
    """Handles file encryption and decryption using AES-256"""
    
    def __init__(self):
        pass
    
    def generate_key(self) -> bytes:
        """Generate a new encryption key"""
        return Fernet.generate_key()
    
    def encrypt_data(self, data: bytes, key: bytes) -> bytes:
        """Encrypt data using the provided key"""
        fernet = Fernet(key)
        return fernet.encrypt(data)
    
    def decrypt_data(self, encrypted_data: bytes, key: bytes) -> bytes:
        """Decrypt data using the provided key"""
        fernet = Fernet(key)
        return fernet.decrypt(encrypted_data)
    
    from typing import Optional

    def derive_key_from_password(self, password: str, salt: Optional[bytes] = None) -> tuple:
        """Derive an encryption key from a password"""
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt
    
    def generate_file_hash(self, file_path: str) -> str:
        """Generate SHA-256 hash of a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
