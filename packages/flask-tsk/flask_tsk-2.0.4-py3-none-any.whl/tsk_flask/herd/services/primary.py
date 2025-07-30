"""
Flask-TSK Herd Primary Authentication Service
============================================
"The matriarch leads the primary authentication"
Primary login/logout functionality with TuskLang integration
Strong. Secure. Scalable. 🐘
"""

from flask import current_app, session, request
from typing import Dict, List, Optional, Any, Union
import hashlib
import secrets
import time
from datetime import datetime, timedelta
import json

from ... import get_tsk

class Primary:
    """Primary authentication service for Herd"""
    
    def __init__(self):
        self.max_attempts = 5
        self.lockout_duration = 900  # 15 minutes
        self.session_lifetime = 7200  # 2 hours
    
    def attempt_login(self, email: str, password: str, remember: bool = False) -> bool:
        """Attempt user login with email and password"""
        try:
            tsk = get_tsk()
            
            # Check if account is locked
            if self.is_account_locked(email):
                current_app.logger.warning(f"Login attempt for locked account: {email}")
                return False
            
            # Get user by email
            user = self.get_user_by_email(email)
            if not user:
                self.increment_failed_attempts(email)
                self.log_failed_attempt(email, "User not found")
                return False
            
            # Check if user is active
            if not self.is_user_active(user):
                self.increment_failed_attempts(email)
                self.log_failed_attempt(email, "Account not active")
                return False
            
            # Verify password
            if not self.verify_password(password, user.get('password_hash', '')):
                self.increment_failed_attempts(email)
                self.log_failed_attempt(email, "Invalid password")
                return False
            
            # Reset failed attempts on successful login
            self.reset_failed_attempts(email)
            
            # Create user session
            self.create_user_session(user, remember)
            
            # Log successful login
            self.log_successful_login(user)
            
            # Fire login event
            self.fire_login_event(user)
            
            # Send login notification
            self.send_login_notification(user)
            
            return True
            
        except Exception as e:
            current_app.logger.error(f"Login error: {e}")
            return False
    
    def attempt_once(self, credentials: Dict[str, Any]) -> bool:
        """Single-use login attempt (no session creation)"""
        try:
            email = credentials.get('email')
            password = credentials.get('password')
            
            if not email or not password:
                return False
            
            # Get user by email
            user = self.get_user_by_email(email)
            if not user or not self.is_user_active(user):
                return False
            
            # Verify password
            if not self.verify_password(password, user.get('password_hash', '')):
                return False
            
            return True
            
        except Exception as e:
            current_app.logger.error(f"Once login error: {e}")
            return False
    
    def perform_logout(self) -> bool:
        """Perform user logout"""
        try:
            user = self.get_current_user()
            if user:
                # Fire logout event
                self.fire_logout_event(user)
                
                # Log successful logout
                self.log_successful_logout(user)
            
            # Destroy user session
            self.destroy_user_session()
            
            return True
            
        except Exception as e:
            current_app.logger.error(f"Logout error: {e}")
            return False
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get current authenticated user"""
        try:
            # Check session first
            if session.get('herd_authenticated') and session.get('user_id'):
                user_id = session['user_id']
                user = self.get_user_by_id(user_id)
                if user and self.is_user_active(user):
                    return user
            
            # Check remember token
            user_id = self.get_user_from_remember_token()
            if user_id:
                user = self.get_user_by_id(user_id)
                if user and self.is_user_active(user):
                    # Recreate session
                    self.create_user_session(user, True)
                    return user
            
            return None
            
        except Exception as e:
            current_app.logger.error(f"Get current user error: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email address"""
        try:
            tsk = get_tsk()
            users = tsk.execute_function('users', 'get_by_email', [email])
            return users[0] if users else None
        except Exception as e:
            current_app.logger.error(f"Get user by email error: {e}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            tsk = get_tsk()
            users = tsk.execute_function('users', 'get_by_id', [user_id])
            return users[0] if users else None
        except Exception as e:
            current_app.logger.error(f"Get user by ID error: {e}")
            return None
    
    def verify_password(self, password: str, hash_value: str) -> bool:
        """Verify password against hash"""
        try:
            # Use TuskLang password verification
            tsk = get_tsk()
            result = tsk.execute_function('auth', 'verify_password', [password, hash_value])
            return result.get('valid', False)
        except Exception as e:
            current_app.logger.error(f"Password verification error: {e}")
            return False
    
    def is_user_active(self, user: Dict[str, Any]) -> bool:
        """Check if user account is active"""
        return (
            user.get('is_active', True) and 
            user.get('deleted_at') is None and
            user.get('email_verified_at') is not None
        )
    
    def is_account_locked(self, email: str) -> bool:
        """Check if account is locked due to failed attempts"""
        try:
            tsk = get_tsk()
            lock_data = tsk.execute_function('auth', 'get_account_lock', [email])
            
            if not lock_data:
                return False
            
            lock_time = lock_data.get('locked_at')
            if not lock_time:
                return False
            
            # Check if lockout period has expired
            lock_datetime = datetime.fromisoformat(lock_time)
            if datetime.now() - lock_datetime > timedelta(seconds=self.lockout_duration):
                # Clear expired lock
                tsk.execute_function('auth', 'clear_account_lock', [email])
                return False
            
            return True
            
        except Exception as e:
            current_app.logger.error(f"Check account lock error: {e}")
            return False
    
    def increment_failed_attempts(self, email: str) -> None:
        """Increment failed login attempts"""
        try:
            tsk = get_tsk()
            attempts = tsk.execute_function('auth', 'increment_failed_attempts', [email])
            
            # Lock account if max attempts reached
            if attempts >= self.max_attempts:
                self.lock_account(email)
                
        except Exception as e:
            current_app.logger.error(f"Increment failed attempts error: {e}")
    
    def reset_failed_attempts(self, email: str) -> None:
        """Reset failed login attempts"""
        try:
            tsk = get_tsk()
            tsk.execute_function('auth', 'reset_failed_attempts', [email])
        except Exception as e:
            current_app.logger.error(f"Reset failed attempts error: {e}")
    
    def lock_account(self, email: str) -> None:
        """Lock user account"""
        try:
            tsk = get_tsk()
            lock_data = {
                'email': email,
                'locked_at': datetime.now().isoformat(),
                'reason': 'Too many failed login attempts'
            }
            tsk.execute_function('auth', 'lock_account', [email, lock_data])
            
            # Fire lock event
            self.fire_lock_event(email, lock_data)
            
            # Log account lock
            self.log_account_lock(email)
            
        except Exception as e:
            current_app.logger.error(f"Lock account error: {e}")
    
    def create_user_session(self, user: Dict[str, Any], remember: bool = False) -> None:
        """Create user session"""
        try:
            # Regenerate session ID for security
            session.regenerate()
            
            # Set session data
            session['herd_authenticated'] = True
            session['user_id'] = user['id']
            session['user_email'] = user['email']
            session['login_time'] = time.time()
            session['login_method'] = 'password'
            session['session_id'] = session.sid
            
            # Set session lifetime
            session.permanent = True
            session.modified = True
            
            # Create remember token if requested
            if remember:
                self.create_remember_token(user['id'])
            
            # Update user's last login
            tsk = get_tsk()
            tsk.execute_function('users', 'update_last_login', [
                user['id'], 
                datetime.now().isoformat(),
                request.remote_addr or 'unknown'
            ])
            
            # Increment active session count
            self.increment_active_session_count()
            
        except Exception as e:
            current_app.logger.error(f"Create user session error: {e}")
    
    def destroy_user_session(self) -> None:
        """Destroy user session"""
        try:
            # Clear remember token
            user_id = session.get('user_id')
            if user_id:
                self.clear_remember_token(user_id)
            
            # Clear session data
            session.clear()
            
            # Decrement active session count
            self.decrement_active_session_count()
            
        except Exception as e:
            current_app.logger.error(f"Destroy user session error: {e}")
    
    def create_remember_token(self, user_id: int) -> None:
        """Create remember me token"""
        try:
            token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(days=30)
            
            tsk = get_tsk()
            tsk.execute_function('auth', 'create_remember_token', [
                user_id, 
                token, 
                expires_at.isoformat()
            ])
            
            # Set remember cookie
            session['remember_token'] = token
            
        except Exception as e:
            current_app.logger.error(f"Create remember token error: {e}")
    
    def clear_remember_token(self, user_id: int) -> None:
        """Clear remember me token"""
        try:
            tsk = get_tsk()
            tsk.execute_function('auth', 'clear_remember_token', [user_id])
            
            # Clear remember cookie
            session.pop('remember_token', None)
            
        except Exception as e:
            current_app.logger.error(f"Clear remember token error: {e}")
    
    def get_user_from_remember_token(self) -> Optional[int]:
        """Get user ID from remember token"""
        try:
            token = session.get('remember_token')
            if not token:
                return None
            
            tsk = get_tsk()
            result = tsk.execute_function('auth', 'get_user_from_remember_token', [token])
            
            if result and result.get('valid'):
                return result.get('user_id')
            
            return None
            
        except Exception as e:
            current_app.logger.error(f"Get user from remember token error: {e}")
            return None
    
    def fire_login_event(self, user: Dict[str, Any]) -> None:
        """Fire login event"""
        try:
            from ..events import LoginEvent
            
            event = LoginEvent(user)
            
            # Store event in TuskLang
            tsk = get_tsk()
            tsk.execute_function('events', 'store_event', [
                'login',
                user['id'],
                event.__dict__
            ])
            
        except Exception as e:
            current_app.logger.error(f"Fire login event error: {e}")
    
    def fire_logout_event(self, user: Dict[str, Any]) -> None:
        """Fire logout event"""
        try:
            from ..events import LogoutEvent
            
            event = LogoutEvent(user)
            
            # Store event in TuskLang
            tsk = get_tsk()
            tsk.execute_function('events', 'store_event', [
                'logout',
                user['id'],
                event.__dict__
            ])
            
        except Exception as e:
            current_app.logger.error(f"Fire logout event error: {e}")
    
    def fire_lock_event(self, email: str, lock_data: Dict[str, Any]) -> None:
        """Fire account lock event"""
        try:
            from ..events import LockEvent
            
            event = LockEvent(email, lock_data)
            
            # Store event in TuskLang
            tsk = get_tsk()
            tsk.execute_function('events', 'store_event', [
                'account_locked',
                None,
                event.__dict__
            ])
            
        except Exception as e:
            current_app.logger.error(f"Fire lock event error: {e}")
    
    def increment_active_session_count(self) -> None:
        """Increment active session count"""
        try:
            tsk = get_tsk()
            current_count = tsk.execute_function('stats', 'get_active_sessions', [])
            tsk.execute_function('stats', 'set_active_sessions', [current_count + 1])
        except Exception as e:
            current_app.logger.error(f"Increment session count error: {e}")
    
    def decrement_active_session_count(self) -> None:
        """Decrement active session count"""
        try:
            tsk = get_tsk()
            current_count = tsk.execute_function('stats', 'get_active_sessions', [])
            tsk.execute_function('stats', 'set_active_sessions', [max(0, current_count - 1)])
        except Exception as e:
            current_app.logger.error(f"Decrement session count error: {e}")
    
    def log_successful_login(self, user: Dict[str, Any]) -> None:
        """Log successful login"""
        try:
            tsk = get_tsk()
            tsk.execute_function('logs', 'log_auth_event', [
                'login_success',
                user['id'],
                {
                    'email': user['email'],
                    'ip_address': request.remote_addr or 'unknown',
                    'user_agent': request.headers.get('User-Agent', 'unknown'),
                    'timestamp': datetime.now().isoformat()
                }
            ])
        except Exception as e:
            current_app.logger.error(f"Log successful login error: {e}")
    
    def log_successful_logout(self, user: Dict[str, Any]) -> None:
        """Log successful logout"""
        try:
            tsk = get_tsk()
            tsk.execute_function('logs', 'log_auth_event', [
                'logout_success',
                user['id'],
                {
                    'email': user['email'],
                    'ip_address': request.remote_addr or 'unknown',
                    'timestamp': datetime.now().isoformat()
                }
            ])
        except Exception as e:
            current_app.logger.error(f"Log successful logout error: {e}")
    
    def log_failed_attempt(self, email: str, reason: str) -> None:
        """Log failed login attempt"""
        try:
            tsk = get_tsk()
            tsk.execute_function('logs', 'log_auth_event', [
                'login_failed',
                None,
                {
                    'email': email,
                    'reason': reason,
                    'ip_address': request.remote_addr or 'unknown',
                    'user_agent': request.headers.get('User-Agent', 'unknown'),
                    'timestamp': datetime.now().isoformat()
                }
            ])
        except Exception as e:
            current_app.logger.error(f"Log failed attempt error: {e}")
    
    def log_account_lock(self, email: str) -> None:
        """Log account lock"""
        try:
            tsk = get_tsk()
            tsk.execute_function('logs', 'log_auth_event', [
                'account_locked',
                None,
                {
                    'email': email,
                    'ip_address': request.remote_addr or 'unknown',
                    'timestamp': datetime.now().isoformat()
                }
            ])
        except Exception as e:
            current_app.logger.error(f"Log account lock error: {e}")
    
    def send_login_notification(self, user: Dict[str, Any]) -> None:
        """Send login notification"""
        try:
            # Check if notification should be sent
            tsk = get_tsk()
            should_notify = tsk.execute_function('notifications', 'should_send_login_notification', [
                user['id']
            ])
            
            if should_notify:
                # Send email notification
                tsk.execute_function('email', 'send_login_notification', [
                    user['email'],
                    {
                        'user_name': user.get('first_name', 'User'),
                        'login_time': datetime.now().isoformat(),
                        'ip_address': request.remote_addr or 'unknown',
                        'user_agent': request.headers.get('User-Agent', 'unknown')
                    }
                ])
                
        except Exception as e:
            current_app.logger.error(f"Send login notification error: {e}")
    
    def parse_user_agent(self, user_agent: str) -> str:
        """Parse user agent string"""
        try:
            if 'Mobile' in user_agent or 'Android' in user_agent or 'iPhone' in user_agent:
                return 'mobile'
            elif 'iPad' in user_agent:
                return 'tablet'
            elif 'Windows' in user_agent or 'Mac' in user_agent or 'Linux' in user_agent:
                return 'desktop'
            else:
                return 'unknown'
        except Exception:
            return 'unknown' 