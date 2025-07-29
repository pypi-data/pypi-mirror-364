"""
Session management utilities
"""

import random
import string
import time
from typing import Dict, Optional


class SessionManager:
    """Manages session codes and session data"""
    
    def __init__(self):
        self.sessions: Dict[str, dict] = {}
        self.session_timeout = 3600  # 1 hour
    
    def generate_session_code(self, length: int = 5) -> str:
        """Generate a unique session code"""
        while True:
            # Generate random alphanumeric code
            code = ''.join(random.choices(
                string.ascii_uppercase + string.digits, 
                k=length
            ))
            
            # Ensure uniqueness
            if code not in self.sessions:
                # Store session data
                self.sessions[code] = {
                    'created_at': time.time(),
                    'status': 'waiting'
                }
                return code
    
    def get_session(self, session_code: str) -> Optional[dict]:
        """Get session data by code"""
        self._cleanup_expired_sessions()
        return self.sessions.get(session_code)
    
    def update_session(self, session_code: str, data: dict) -> bool:
        """Update session data"""
        if session_code in self.sessions:
            self.sessions[session_code].update(data)
            return True
        return False
    
    def delete_session(self, session_code: str) -> bool:
        """Delete a session"""
        if session_code in self.sessions:
            del self.sessions[session_code]
            return True
        return False
    
    def _cleanup_expired_sessions(self) -> None:
        """Remove expired sessions"""
        current_time = time.time()
        expired_sessions = [
            code for code, data in self.sessions.items()
            if current_time - data['created_at'] > self.session_timeout
        ]
        
        for code in expired_sessions:
            del self.sessions[code]
    
    def is_valid_session_code(self, session_code: str) -> bool:
        """Check if session code is valid format"""
        if not session_code or len(session_code) != 5:
            return False
        
        return all(c.isalnum() and c.isupper() for c in session_code)
