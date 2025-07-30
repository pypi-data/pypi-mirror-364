"""
Flask-TSK Herd Password Reset Event
==================================
"The herd guides the lost back to the path"
Password reset event for Herd authentication system
Strong. Secure. Scalable. 🐘
"""

from typing import Dict, Any
import time

class PasswordResetEvent:
    """Password reset event for Herd authentication system"""
    
    def __init__(self, user: Dict[str, Any], token: str):
        self.user = user
        self.token = token
        self.timestamp = time.time()
        self.event_type = 'password_reset'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            'event_type': self.event_type,
            'user_id': self.user.get('id'),
            'user_email': self.user.get('email'),
            'token': self.token,
            'timestamp': self.timestamp,
            'user_data': self.user
        } 