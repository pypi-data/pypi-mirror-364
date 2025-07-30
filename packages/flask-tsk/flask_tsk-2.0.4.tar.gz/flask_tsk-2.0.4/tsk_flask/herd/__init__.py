"""
Flask-TSK Herd Authentication System
===================================
"The herd protects itself from threats"
Scalable, secure authentication with TuskLang integration
Strong. Secure. Scalable. 🐘
"""

from flask import current_app, session, request
from typing import Dict, List, Optional, Any, Union
import hashlib
import secrets
import time
from datetime import datetime, timedelta
import json

from .. import get_tsk

class Herd:
    """Main Herd authentication class for Flask-TSK"""
    
    _instance = None
    _user = None
    _guard = 'web'
    _guards = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Herd, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialize_services()
            self.load_configuration()
            self.initialized = True
    
    @classmethod
    def get_instance(cls) -> 'Herd':
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def initialize_services(self):
        """Initialize Herd services"""
        from .services import (
            HerdManager, Primary, Registration, Password, 
            TwoFactor, Guard, Session, Token, Audit, 
            Intelligence, AutoLogin
        )
        
        self.herd_manager = HerdManager()
        self.primary = Primary()
        self.registration = Registration()
        self.password = Password()
        self.two_factor = TwoFactor()
        self.guard_service = Guard()
        self.session_service = Session()
        self.token_service = Token()
        self.audit = Audit()
        self.intelligence = Intelligence()
        self.auto_login = AutoLogin()
    
    def load_configuration(self):
        """Load Herd configuration from TuskLang"""
        try:
            tsk = get_tsk()
            config = tsk.get_config('herd', 'config', self.get_default_config())
            if isinstance(config, str):
                config = json.loads(config)
            self._guards = config.get('guards', ['web', 'api', 'admin'])
        except Exception as e:
            # Use logging instead of current_app to avoid context issues
            import logging
            logging.warning(f"Failed to load Herd config: {e}")
            self._guards = ['web', 'api', 'admin']
    
    # ==========================================
    # 1. PRIMARY LOGIN FLOW
    # ==========================================
    
    @classmethod
    def login(cls, email: str, password: str, remember: bool = False) -> bool:
        """Attempt user login"""
        return cls.get_instance().primary.attempt_login(email, password, remember)
    
    @classmethod
    def once(cls, credentials: Dict[str, Any]) -> bool:
        """Single-use login attempt"""
        return cls.get_instance().primary.attempt_once(credentials)
    
    @classmethod
    def logout(cls) -> bool:
        """Perform user logout"""
        result = cls.get_instance().primary.perform_logout()
        cls._user = None
        return result
    
    @classmethod
    def user(cls) -> Optional[Dict[str, Any]]:
        """Get current authenticated user"""
        if cls._user is None:
            cls._user = cls.get_instance().primary.get_current_user()
        return cls._user
    
    @classmethod
    def id(cls) -> Optional[int]:
        """Get current user ID"""
        user = cls.user()
        return user.get('id') if user else None
    
    @classmethod
    def check(cls) -> bool:
        """Check if user is authenticated"""
        return cls.user() is not None
    
    @classmethod
    def guest(cls) -> bool:
        """Check if user is a guest (not authenticated)"""
        return not cls.check()
    
    @classmethod
    def guard(cls, guard_name: str) -> 'Herd':
        """Switch to different guard"""
        instance = cls.get_instance()
        instance.guard_service.switch_guard(guard_name)
        cls._guard = guard_name
        return instance
    
    # ==========================================
    # 2. REGISTRATION & ACCOUNT LIFECYCLE
    # ==========================================
    
    @classmethod
    def create_user(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new user account"""
        return cls.get_instance().registration.create_user(data)
    
    @classmethod
    def invite(cls, email: str, role: str = 'user') -> bool:
        """Invite user to join"""
        return cls.get_instance().registration.invite_user(email, role)
    
    @classmethod
    def activate(cls, token: str) -> Dict[str, Any]:
        """Activate user account with token"""
        return cls.get_instance().registration.verify_email(token)
    
    @classmethod
    def deactivate(cls, user_id: int) -> bool:
        """Deactivate user account"""
        return cls.get_instance().registration.deactivate_user(user_id)
    
    @classmethod
    def restore(cls, user_id: int) -> bool:
        """Restore deactivated user account"""
        return cls.get_instance().registration.restore_user(user_id)
    
    @classmethod
    def purge(cls, user_id: int) -> bool:
        """Permanently delete user account"""
        return cls.get_instance().registration.purge_user(user_id)
    
    # ==========================================
    # 3. PASSWORD MANAGEMENT
    # ==========================================
    
    @classmethod
    def request_password_reset(cls, email: str) -> Dict[str, Any]:
        """Request password reset"""
        return cls.get_instance().password.request_reset(email)
    
    @classmethod
    def validate_reset_token(cls, token: str) -> Dict[str, Any]:
        """Validate password reset token"""
        return cls.get_instance().password.validate_reset_token(token)
    
    @classmethod
    def reset_password(cls, token: str, new_password: str) -> Dict[str, Any]:
        """Reset password with token"""
        return cls.get_instance().password.reset_password(token, new_password)
    
    @classmethod
    def update_password(cls, current: str, new: str) -> Dict[str, Any]:
        """Update user password"""
        user_id = cls.id()
        if not user_id:
            return {
                'success': False,
                'errors': {'auth': 'User not authenticated'}
            }
        return cls.get_instance().password.update_password(user_id, current, new)
    
    @classmethod
    def force_password_change(cls, user_id: int) -> Dict[str, Any]:
        """Force user to change password"""
        return cls.get_instance().password.force_password_change(user_id)
    
    # ==========================================
    # 4. INTELLIGENCE & ANALYTICS
    # ==========================================
    
    @classmethod
    def analytics(cls) -> Dict[str, Any]:
        """Get comprehensive analytics"""
        return cls.get_instance().intelligence.get_intelligence_report()
    
    @classmethod
    def live_stats(cls) -> Dict[str, Any]:
        """Get live statistics"""
        return cls.get_instance().herd_manager.get_live_stats()
    
    @classmethod
    def footprint(cls) -> Dict[str, Any]:
        """Get user behavior analytics"""
        return cls.get_instance().intelligence.get_footprint_analytics()
    
    @classmethod
    def eye(cls) -> Dict[str, Any]:
        """Get security intelligence"""
        return cls.get_instance().intelligence.get_security_intelligence()
    
    @classmethod
    def track(cls, action: str, data: Dict[str, Any] = None) -> None:
        """Track user activity"""
        user_id = cls.id()
        if user_id:
            cls.get_instance().intelligence.track_user_activity(user_id, action, data or {})
    
    @classmethod
    def wisdom(cls) -> Dict[str, Any]:
        """Get comprehensive herd wisdom"""
        instance = cls.get_instance()
        return {
            'herd_stats': instance.herd_manager.get_stats(),
            'intelligence': instance.intelligence.get_intelligence_report(),
            'insights': instance.intelligence.generate_insights(),
            'recommendations': instance.intelligence.get_recommendations(),
            'elephant_wisdom': cls.herd_wisdom()
        }
    
    @classmethod
    def herd_wisdom(cls) -> Dict[str, Any]:
        """Get basic herd statistics"""
        try:
            tsk = get_tsk()
            total_users = tsk.execute_function('database', 'count_users', [])
            return {
                'total_members': total_users or 0,
                'active_sessions': len(session) if session else 0,
                'guard': cls._guard,
                'last_activity': datetime.now().isoformat()
            }
        except Exception as e:
            current_app.logger.error(f"Herd wisdom error: {e}")
            return {
                'total_members': 0,
                'active_sessions': 0,
                'guard': cls._guard,
                'last_activity': datetime.now().isoformat()
            }
    
    # ==========================================
    # 5. MAGIC LINKS & AUTO-LOGIN
    # ==========================================
    
    @classmethod
    def generate_magic_link(cls, user_id: int, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate magic link for user"""
        return cls.get_instance().auto_login.generate_magic_link(user_id, options or {})
    
    @classmethod
    def send_magic_link(cls, user_id: int, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send magic link via email"""
        return cls.get_instance().auto_login.send_magic_link_email(user_id, options or {})
    
    @classmethod
    def verify_magic_link(cls, token: str) -> Dict[str, Any]:
        """Verify magic link token"""
        return cls.get_instance().auto_login.verify_magic_link(token)
    
    @classmethod
    def login_with_magic_link(cls, token: str) -> Dict[str, Any]:
        """Login user with magic link"""
        return cls.get_instance().auto_login.login_with_magic_link(token)
    
    @classmethod
    def generate_auto_login(cls, user_id: int, redirect: str = '/dashboard/', valid_days: int = 3) -> Dict[str, Any]:
        """Generate auto-login link"""
        options = {
            'purpose': 'auto_login',
            'redirect': redirect,
            'valid_days': valid_days,
            'max_uses': 1
        }
        return cls.generate_magic_link(user_id, options)
    
    @classmethod
    def verify_auto_login(cls, token: str) -> Dict[str, Any]:
        """Verify auto-login token"""
        return cls.verify_magic_link(token)
    
    @classmethod
    def login_with_token(cls, token: str) -> bool:
        """Login with token"""
        result = cls.login_with_magic_link(token)
        return result.get('success', False)
    
    # ==========================================
    # HELPER METHODS
    # ==========================================
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default Herd configuration"""
        return {
            'guards': {
                'web': {
                    'driver': 'session',
                    'provider': 'users'
                },
                'api': {
                    'driver': 'token',
                    'provider': 'users'
                },
                'admin': {
                    'driver': 'session',
                    'provider': 'admins'
                }
            },
            'providers': {
                'users': {
                    'driver': 'tusk',
                    'model': 'User'
                }
            },
            'passwords': {
                'users': {
                    'provider': 'users',
                    'table': 'password_resets',
                    'expire': 60
                }
            },
            'session': {
                'lifetime': 120,
                'expire_on_close': False,
                'encrypt': False,
                'cookie': 'herd_session',
                'path': '/',
                'domain': None,
                'secure': False,
                'http_only': True,
                'same_site': 'lax'
            }
        }
    
    @classmethod
    def get_current_guard(cls) -> str:
        """Get current guard name"""
        return cls._guard

# Global Herd instance
herd = Herd.get_instance()

# Convenience functions
def get_herd() -> Herd:
    """Get global Herd instance"""
    return Herd.get_instance()

def herd_user() -> Optional[Dict[str, Any]]:
    """Get current authenticated user"""
    return Herd.user()

def herd_id() -> Optional[int]:
    """Get current user ID"""
    return Herd.id()

def herd_check() -> bool:
    """Check if user is authenticated"""
    return Herd.check()

def herd_guest() -> bool:
    """Check if user is a guest"""
    return Herd.guest() 