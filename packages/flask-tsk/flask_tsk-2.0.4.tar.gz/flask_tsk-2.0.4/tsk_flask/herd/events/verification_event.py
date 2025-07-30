"""
Flask-TSK Herd Verification Event
================================
"The herd confirms a member's identity"
Email verification event for Herd authentication system
Strong. Secure. Scalable. 🐘
"""

from typing import Dict, Any
import time

class VerificationEvent:
    """Email verification event for Herd authentication system"""
    
    def __init__(self, user: Dict[str, Any]):
        self.user = user
        self.timestamp = time.time()
        self.event_type = 'verification'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            'event_type': self.event_type,
            'user_id': self.user.get('id'),
            'user_email': self.user.get('email'),
            'timestamp': self.timestamp,
            'user_data': self.user
        } 