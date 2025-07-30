"""
Flask-TSK Herd Login Event
=========================
"The herd celebrates a new member's arrival"
Login event for Herd authentication system
Strong. Secure. Scalable. 🐘
"""

from typing import Dict, Any
import time

class LoginEvent:
    """Login event for Herd authentication system"""
    
    def __init__(self, user: Dict[str, Any]):
        self.user = user
        self.timestamp = time.time()
        self.event_type = 'login'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            'event_type': self.event_type,
            'user_id': self.user.get('id'),
            'user_email': self.user.get('email'),
            'timestamp': self.timestamp,
            'user_data': self.user
        } 