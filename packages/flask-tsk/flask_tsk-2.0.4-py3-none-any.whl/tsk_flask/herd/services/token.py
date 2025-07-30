"""
Flask-TSK Herd Token Service
===========================
"Secure tokens for the herd"
Token management for API authentication
Strong. Secure. Scalable. 🐘
"""

from flask import current_app
from typing import Dict, List, Optional, Any, Union
import secrets
import time
from datetime import datetime, timedelta

from ... import get_tsk

class Token:
    """Token management service for Herd"""
    
    def __init__(self):
        self.token_length = 64
        self.default_expires_hours = 24
    
    def create_token(self, user_id: int, purpose: str = 'api', expires_hours: int = None) -> str:
        """Create new token"""
        try:
            token = self.generate_token()
            expires_at = datetime.now() + timedelta(hours=expires_hours or self.default_expires_hours)
            
            token_data = {
                'token': token,
                'user_id': user_id,
                'purpose': purpose,
                'created_at': datetime.now().isoformat(),
                'expires_at': expires_at.isoformat(),
                'last_used_at': None
            }
            
            tsk = get_tsk()
            tsk.execute_function('tokens', 'create_token', [token_data])
            
            return token
            
        except Exception as e:
            current_app.logger.error(f"Create token error: {e}")
            return ""
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate token"""
        try:
            tsk = get_tsk()
            tokens = tsk.execute_function('tokens', 'get_by_token', [token])
            
            if not tokens:
                return None
            
            token_data = tokens[0]
            
            # Check if expired
            expires_at = datetime.fromisoformat(token_data['expires_at'])
            if datetime.now() > expires_at:
                self.revoke_token(token)
                return None
            
            # Update last used
            tsk.execute_function('tokens', 'update_last_used', [token])
            
            return token_data
            
        except Exception as e:
            current_app.logger.error(f"Validate token error: {e}")
            return None
    
    def revoke_token(self, token: str) -> bool:
        """Revoke token"""
        try:
            tsk = get_tsk()
            return tsk.execute_function('tokens', 'revoke_token', [token])
        except Exception as e:
            current_app.logger.error(f"Revoke token error: {e}")
            return False
    
    def revoke_user_tokens(self, user_id: int, purpose: str = None) -> int:
        """Revoke all tokens for user"""
        try:
            tsk = get_tsk()
            count = tsk.execute_function('tokens', 'revoke_user_tokens', [user_id, purpose])
            return count or 0
        except Exception as e:
            current_app.logger.error(f"Revoke user tokens error: {e}")
            return 0
    
    def generate_token(self) -> str:
        """Generate secure token"""
        return secrets.token_urlsafe(self.token_length) 