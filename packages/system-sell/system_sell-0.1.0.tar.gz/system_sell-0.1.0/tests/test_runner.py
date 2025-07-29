"""
Test Runner - Runs automated tests for SYSTEM-SELL
"""

import unittest
import asyncio
import tempfile
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.encryption import FileEncryption
from src.utils.session import SessionManager
from src.utils.config import Config
from src.utils.logger import setup_logger


class TestEncryption(unittest.TestCase):
    """Test encryption functionality"""
    
    def setUp(self):
        self.encryption = FileEncryption()
    
    def test_key_generation(self):
        """Test encryption key generation"""
        key1 = self.encryption.generate_key()
        key2 = self.encryption.generate_key()
        
        self.assertIsInstance(key1, bytes)
        self.assertIsInstance(key2, bytes)
        self.assertNotEqual(key1, key2)  # Should be unique
    
    def test_encrypt_decrypt(self):
        """Test data encryption and decryption"""
        key = self.encryption.generate_key()
        test_data = b"Hello, World! This is test data."
        
        # Encrypt
        encrypted = self.encryption.encrypt_data(test_data, key)
        self.assertNotEqual(encrypted, test_data)
        
        # Decrypt
        decrypted = self.encryption.decrypt_data(encrypted, key)
        self.assertEqual(decrypted, test_data)
    
    def test_file_hash(self):
        """Test file hash generation"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("Test content for hashing")
            temp_file = f.name
        
        try:
            hash1 = self.encryption.generate_file_hash(temp_file)
            hash2 = self.encryption.generate_file_hash(temp_file)
            
            self.assertEqual(hash1, hash2)  # Should be consistent
            self.assertEqual(len(hash1), 64)  # SHA-256 is 64 chars
            
        finally:
            os.unlink(temp_file)


class TestSessionManager(unittest.TestCase):
    """Test session management functionality"""
    
    def setUp(self):
        self.session_manager = SessionManager()
    
    def test_session_code_generation(self):
        """Test session code generation"""
        code1 = self.session_manager.generate_session_code()
        code2 = self.session_manager.generate_session_code()
        
        self.assertEqual(len(code1), 5)
        self.assertEqual(len(code2), 5)
        self.assertNotEqual(code1, code2)  # Should be unique
        self.assertTrue(code1.isupper())
        self.assertTrue(code1.isalnum())
    
    def test_session_validation(self):
        """Test session code validation"""
        valid_codes = ["ABC12", "XYZ99", "TEST1"]
        invalid_codes = ["abc12", "AB12", "ABCDEF", "AB@12", ""]
        
        for code in valid_codes:
            self.assertTrue(self.session_manager.is_valid_session_code(code))
        
        for code in invalid_codes:
            self.assertFalse(self.session_manager.is_valid_session_code(code))
    
    def test_session_operations(self):
        """Test session CRUD operations"""
        code = self.session_manager.generate_session_code()
        
        # Get session
        session = self.session_manager.get_session(code)
        self.assertIsNotNone(session)
        if session is not None:
            self.assertEqual(session['status'], 'waiting')
        
        # Update session
        success = self.session_manager.update_session(code, {'status': 'active'})
        self.assertTrue(success)
        
        updated_session = self.session_manager.get_session(code)
        self.assertIsNotNone(updated_session)
        if updated_session is not None:
            self.assertEqual(updated_session['status'], 'active')
        
        # Delete session
        success = self.session_manager.delete_session(code)
        self.assertTrue(success)
        
        deleted_session = self.session_manager.get_session(code)
        self.assertIsNone(deleted_session)


class TestConfig(unittest.TestCase):
    """Test configuration functionality"""
    
    def test_default_config(self):
        """Test default configuration loading"""
        config = Config()
        
        self.assertIsNotNone(config.get('stun_server'))
        self.assertIsNotNone(config.get('encryption'))
    
    def test_config_file_loading(self):
        """Test loading configuration from file"""
        test_config = {
            'stun_server': 'test.stun.server:3478',
            'encryption': {'algorithm': 'AES-256'}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            import json
            json.dump(test_config, f)
            config_file = f.name
        
        try:
            config = Config(config_file)
            self.assertEqual(config.get('stun_server'), 'test.stun.server:3478')
            
        finally:
            os.unlink(config_file)


class TestLogger(unittest.TestCase):
    """Test logger functionality"""
    
    def test_logger_setup(self):
        """Test logger setup"""
        logger = setup_logger()
        self.assertIsNotNone(logger)
        
        verbose_logger = setup_logger(verbose=True)
        self.assertIsNotNone(verbose_logger)


def run_tests():
    """Run all tests"""
    print("🧪 Running SYSTEM-SELL Test Suite")
    print("=" * 50)
    
    # Discover and run tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ All tests passed!")
    else:
        print(f"❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
        
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
