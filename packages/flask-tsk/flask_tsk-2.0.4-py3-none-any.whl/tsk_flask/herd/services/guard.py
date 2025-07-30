"""
Flask-TSK Herd Guard Service
===========================
"Different herds for different lands"
Guard switching for web, api, admin authentication
Strong. Secure. Scalable. 🐘
"""

from flask import current_app
from typing import Dict, List, Optional, Any, Union
import time
from datetime import datetime

from ... import get_tsk

class Guard:
    """Guard service for Herd"""
    
    def __init__(self):
        self.current_guard = 'web'
        self.guards = self.initialize_guards()
    
    def switch_guard(self, guard_name: str) -> None:
        """Switch to a different guard"""
        if guard_name not in self.guards:
            raise ValueError(f"Guard '{guard_name}' is not configured")
        
        self.current_guard = guard_name
        self.log_guard_switch(guard_name)
    
    def get_current_guard(self) -> str:
        """Get current guard name"""
        return self.current_guard
    
    def get_guard_config(self, guard_name: str) -> Dict[str, Any]:
        """Get guard configuration"""
        return self.guards.get(guard_name, {})
    
    def has_guard(self, guard_name: str) -> bool:
        """Check if guard exists"""
        return guard_name in self.guards
    
    def get_guards(self) -> List[str]:
        """Get all available guards"""
        return list(self.guards.keys())
    
    def initialize_guards(self) -> Dict[str, Dict[str, Any]]:
        """Initialize guard configurations"""
        return {
            'web': {
                'driver': 'session',
                'provider': 'users',
                'session_key': 'herd_user_id',
                'remember_key': 'herd_remember',
                'timeout': 7200,  # 2 hours
            },
            'api': {
                'driver': 'token',
                'provider': 'users',
                'token_key': 'api_token',
                'timeout': 86400,  # 24 hours
            },
            'admin': {
                'driver': 'session',
                'provider': 'admins',
                'session_key': 'herd_admin_id',
                'remember_key': 'herd_admin_remember',
                'timeout': 3600,  # 1 hour
                'require_2fa': True,
            }
        }
    
    def log_guard_switch(self, guard_name: str) -> None:
        """Log guard switch"""
        try:
            tsk = get_tsk()
            tsk.execute_function('logs', 'log_auth_event', [
                'guard_switched',
                None,
                {
                    'guard': guard_name,
                    'previous_guard': self.current_guard,
                    'timestamp': datetime.now().isoformat()
                }
            ])
        except Exception as e:
            current_app.logger.error(f"Log guard switch error: {e}") 