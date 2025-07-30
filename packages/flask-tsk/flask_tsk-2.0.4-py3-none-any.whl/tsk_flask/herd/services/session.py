"""
Flask-TSK Herd Session Service
=============================
"Managing the herd's gatherings"
Session management and tracking
Strong. Secure. Scalable. 🐘
"""

from flask import current_app, session
from typing import Dict, List, Optional, Any, Union
import time
from datetime import datetime, timedelta
import json

from ... import get_tsk

class Session:
    """Session management service for Herd"""
    
    def __init__(self):
        self.session_lifetime = 7200  # 2 hours
        self.cleanup_interval = 3600  # 1 hour
    
    def create_session(self, user_id: int, data: Dict[str, Any] = None) -> str:
        """Create new session"""
        try:
            session_id = self.generate_session_id()
            
            session_data = {
                'session_id': session_id,
                'user_id': user_id,
                'ip_address': data.get('ip_address', 'unknown'),
                'user_agent': data.get('user_agent', 'unknown'),
                'created_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(seconds=self.session_lifetime)).isoformat(),
                'data': json.dumps(data or {})
            }
            
            tsk = get_tsk()
            tsk.execute_function('sessions', 'create_session', [session_data])
            
            return session_id
            
        except Exception as e:
            current_app.logger.error(f"Create session error: {e}")
            return ""
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID"""
        try:
            tsk = get_tsk()
            sessions = tsk.execute_function('sessions', 'get_by_id', [session_id])
            
            if not sessions:
                return None
            
            session_data = sessions[0]
            
            # Check if expired
            expires_at = datetime.fromisoformat(session_data['expires_at'])
            if datetime.now() > expires_at:
                self.destroy_session(session_id)
                return None
            
            return session_data
            
        except Exception as e:
            current_app.logger.error(f"Get session error: {e}")
            return None
    
    def update_session(self, session_id: str, data: Dict[str, Any]) -> bool:
        """Update session data"""
        try:
            tsk = get_tsk()
            return tsk.execute_function('sessions', 'update_session', [session_id, data])
        except Exception as e:
            current_app.logger.error(f"Update session error: {e}")
            return False
    
    def destroy_session(self, session_id: str) -> bool:
        """Destroy session"""
        try:
            tsk = get_tsk()
            return tsk.execute_function('sessions', 'destroy_session', [session_id])
        except Exception as e:
            current_app.logger.error(f"Destroy session error: {e}")
            return False
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        try:
            tsk = get_tsk()
            count = tsk.execute_function('sessions', 'cleanup_expired', [])
            return count or 0
        except Exception as e:
            current_app.logger.error(f"Cleanup sessions error: {e}")
            return 0
    
    def generate_session_id(self) -> str:
        """Generate unique session ID"""
        import secrets
        return secrets.token_urlsafe(32) 