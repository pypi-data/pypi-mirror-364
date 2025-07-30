"""
Flask-TSK Herd Password Changed Event
====================================
"The herd strengthens its defenses"
Password changed event for Herd authentication system
Strong. Secure. Scalable. 🐘
"""

from typing import Dict, Any
import time

class PasswordChangedEvent:
    """Password changed event for Herd authentication system"""
    
    def __init__(self, user: Dict[str, Any], method: str):
        self.user = user
        self.method = method  # 'reset', 'update', etc.
        self.timestamp = time.time()
        self.event_type = 'password_changed'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            'event_type': self.event_type,
            'user_id': self.user.get('id'),
            'user_email': self.user.get('email'),
            'method': self.method,
            'timestamp': self.timestamp,
            'user_data': self.user
        } 