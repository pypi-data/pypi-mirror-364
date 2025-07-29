"""
Configuration loader for SYSTEM-SELL
"""

import os
import json

class Config:
    """Loads configuration from file or environment"""
    def __init__(self, config_path=None):
        self.config = {}
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        # Load environment variables as fallback
        self.config.setdefault('stun_server', os.environ.get('STUN_SERVER', 'stun.l.google.com:19302'))
        self.config.setdefault('encryption', {'algorithm': 'AES-256'})
    
    def get(self, key, default=None):
        return self.config.get(key, default)
