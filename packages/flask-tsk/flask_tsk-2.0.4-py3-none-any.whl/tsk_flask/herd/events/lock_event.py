"""
Flask-TSK Herd Lock Event
========================
"The herd protects itself from threats"
Account lock event for Herd authentication system
Strong. Secure. Scalable. 🐘
"""

from typing import Dict, Any
import time

class LockEvent:
    """Account lock event for Herd authentication system"""
    
    def __init__(self, email: str, lock_data: Dict[str, Any]):
        self.email = email
        self.lock_data = lock_data
        self.timestamp = time.time()
        self.event_type = 'account_locked'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            'event_type': self.event_type,
            'email': self.email,
            'lock_data': self.lock_data,
            'timestamp': self.timestamp
        } 