"""
Flask-TSK Herd Password Service
==============================
"The herd strengthens its defenses"
Password management and reset functionality
Strong. Secure. Scalable. 🐘
"""

from flask import current_app, request
from typing import Dict, List, Optional, Any, Union
import secrets
import time
from datetime import datetime, timedelta
import json

from ... import get_tsk

class Password:
    """Password management service for Herd"""
    
    def __init__(self):
        self.reset_expires_hours = 1
        self.password_history_count = 5
        self.min_password_length = 8
    
    def request_reset(self, email: str) -> Dict[str, Any]:
        """Request password reset"""
        try:
            # Get user by email
            user = self.get_user_by_email(email)
            if not user:
                return {
                    'success': False,
                    'message': 'If a user with this email exists, a reset link has been sent.'
                }
            
            # Check if user is active
            if not self.is_user_active(user):
                return {
                    'success': False,
                    'message': 'If a user with this email exists, a reset link has been sent.'
                }
            
            # Generate reset token
            reset_token = self.generate_reset_token()
            
            # Store reset token
            reset_data = {
                'user_id': user['id'],
                'token': reset_token,
                'expires_at': (datetime.now() + timedelta(hours=self.reset_expires_hours)).isoformat(),
                'created_at': datetime.now().isoformat()
            }
            
            tsk = get_tsk()
            token_id = tsk.execute_function('password_resets', 'create_reset_token', [reset_data])
            
            if not token_id:
                return {
                    'success': False,
                    'message': 'Failed to create reset token'
                }
            
            # Send reset email
            self.send_reset_email(user, reset_token)
            
            # Fire password reset event
            self.fire_password_reset_event(user, reset_token)
            
            # Log password reset request
            self.log_password_reset_request(user)
            
            return {
                'success': True,
                'message': 'If a user with this email exists, a reset link has been sent.'
            }
            
        except Exception as e:
            current_app.logger.error(f"Request password reset error: {e}")
            return {
                'success': False,
                'message': 'An error occurred while processing your request.'
            }
    
    def validate_reset_token(self, token: str) -> Dict[str, Any]:
        """Validate password reset token"""
        try:
            tsk = get_tsk()
            
            # Find reset token
            tokens = tsk.execute_function('password_resets', 'get_by_token', [token])
            
            if not tokens:
                return {
                    'valid': False,
                    'message': 'Invalid reset token'
                }
            
            reset_data = tokens[0]
            
            # Check if token is expired
            expires_at = datetime.fromisoformat(reset_data['expires_at'])
            if datetime.now() > expires_at:
                return {
                    'valid': False,
                    'message': 'Reset token has expired'
                }
            
            # Check if token is used
            if reset_data.get('used', False):
                return {
                    'valid': False,
                    'message': 'Reset token has already been used'
                }
            
            # Get user
            user = self.get_user_by_id(reset_data['user_id'])
            if not user or not self.is_user_active(user):
                return {
                    'valid': False,
                    'message': 'User account is not active'
                }
            
            return {
                'valid': True,
                'user_id': user['id'],
                'user': user,
                'token': token
            }
            
        except Exception as e:
            current_app.logger.error(f"Validate reset token error: {e}")
            return {
                'valid': False,
                'message': 'An error occurred while validating the token'
            }
    
    def reset_password(self, token: str, new_password: str) -> Dict[str, Any]:
        """Reset password with token"""
        try:
            # Validate token
            validation = self.validate_reset_token(token)
            if not validation['valid']:
                return {
                    'success': False,
                    'errors': {'token': validation['message']}
                }
            
            user = validation['user']
            user_id = validation['user_id']
            
            # Validate new password
            password_validation = self.validate_password(new_password)
            if not password_validation['valid']:
                return {
                    'success': False,
                    'errors': {'password': password_validation['message']}
                }
            
            # Check password history
            if self.is_password_in_history(user_id, new_password):
                return {
                    'success': False,
                    'errors': {'password': 'Password has been used recently. Please choose a different password.'}
                }
            
            # Hash new password
            password_hash = self.hash_password(new_password)
            
            # Update user password
            update_data = {
                'password_hash': password_hash,
                'password_changed_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            tsk = get_tsk()
            success = tsk.execute_function('users', 'update_user', [user_id, update_data])
            
            if not success:
                return {
                    'success': False,
                    'errors': {'database': 'Failed to update password'}
                }
            
            # Mark token as used
            tsk.execute_function('password_resets', 'mark_token_used', [token])
            
            # Add to password history
            self.add_to_password_history(user_id, password_hash)
            
            # Fire password changed event
            self.fire_password_changed_event(user, 'reset')
            
            # Log password change
            self.log_password_change(user, 'reset')
            
            return {
                'success': True,
                'message': 'Password has been reset successfully'
            }
            
        except Exception as e:
            current_app.logger.error(f"Reset password error: {e}")
            return {
                'success': False,
                'errors': {'system': 'An error occurred while resetting your password'}
            }
    
    def update_password(self, user_id: int, current_password: str, new_password: str) -> Dict[str, Any]:
        """Update user password"""
        try:
            # Get user
            user = self.get_user_by_id(user_id)
            if not user:
                return {
                    'success': False,
                    'errors': {'user': 'User not found'}
                }
            
            # Verify current password
            if not self.verify_password(current_password, user.get('password_hash', '')):
                return {
                    'success': False,
                    'errors': {'current_password': 'Current password is incorrect'}
                }
            
            # Validate new password
            password_validation = self.validate_password(new_password)
            if not password_validation['valid']:
                return {
                    'success': False,
                    'errors': {'new_password': password_validation['message']}
                }
            
            # Check password history
            if self.is_password_in_history(user_id, new_password):
                return {
                    'success': False,
                    'errors': {'new_password': 'Password has been used recently. Please choose a different password.'}
                }
            
            # Hash new password
            password_hash = self.hash_password(new_password)
            
            # Update user password
            update_data = {
                'password_hash': password_hash,
                'password_changed_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            tsk = get_tsk()
            success = tsk.execute_function('users', 'update_user', [user_id, update_data])
            
            if not success:
                return {
                    'success': False,
                    'errors': {'database': 'Failed to update password'}
                }
            
            # Add to password history
            self.add_to_password_history(user_id, password_hash)
            
            # Fire password changed event
            self.fire_password_changed_event(user, 'update')
            
            # Log password change
            self.log_password_change(user, 'update')
            
            return {
                'success': True,
                'message': 'Password updated successfully'
            }
            
        except Exception as e:
            current_app.logger.error(f"Update password error: {e}")
            return {
                'success': False,
                'errors': {'system': 'An error occurred while updating your password'}
            }
    
    def force_password_change(self, user_id: int) -> Dict[str, Any]:
        """Force user to change password on next login"""
        try:
            # Update user to require password change
            update_data = {
                'force_password_change': True,
                'updated_at': datetime.now().isoformat()
            }
            
            tsk = get_tsk()
            success = tsk.execute_function('users', 'update_user', [user_id, update_data])
            
            if success:
                # Log force password change
                self.log_password_force(user_id)
            
            return {
                'success': success,
                'message': 'User will be required to change password on next login' if success else 'Failed to force password change'
            }
            
        except Exception as e:
            current_app.logger.error(f"Force password change error: {e}")
            return {
                'success': False,
                'message': 'An error occurred while forcing password change'
            }
    
    def must_change_password(self, user_id: int) -> bool:
        """Check if user must change password"""
        try:
            user = self.get_user_by_id(user_id)
            return user.get('force_password_change', False) if user else False
        except Exception as e:
            current_app.logger.error(f"Check must change password error: {e}")
            return False
    
    def validate_password(self, password: str) -> Dict[str, Any]:
        """Validate password strength"""
        if len(password) < self.min_password_length:
            return {
                'valid': False,
                'message': f'Password must be at least {self.min_password_length} characters long'
            }
        
        if not any(c.isupper() for c in password):
            return {
                'valid': False,
                'message': 'Password must contain at least one uppercase letter'
            }
        
        if not any(c.islower() for c in password):
            return {
                'valid': False,
                'message': 'Password must contain at least one lowercase letter'
            }
        
        if not any(c.isdigit() for c in password):
            return {
                'valid': False,
                'message': 'Password must contain at least one number'
            }
        
        return {
            'valid': True,
            'message': 'Password meets strength requirements'
        }
    
    def is_password_in_history(self, user_id: int, password: str) -> bool:
        """Check if password is in history"""
        try:
            tsk = get_tsk()
            history = tsk.execute_function('password_history', 'get_user_history', [user_id, self.password_history_count])
            
            for entry in history:
                if self.verify_password(password, entry['password_hash']):
                    return True
            
            return False
            
        except Exception as e:
            current_app.logger.error(f"Check password history error: {e}")
            return False
    
    def add_to_password_history(self, user_id: int, password_hash: str) -> None:
        """Add password to history"""
        try:
            history_data = {
                'user_id': user_id,
                'password_hash': password_hash,
                'created_at': datetime.now().isoformat()
            }
            
            tsk = get_tsk()
            tsk.execute_function('password_history', 'add_to_history', [history_data])
            
        except Exception as e:
            current_app.logger.error(f"Add to password history error: {e}")
    
    def generate_reset_token(self) -> str:
        """Generate password reset token"""
        return secrets.token_urlsafe(32)
    
    def hash_password(self, password: str) -> str:
        """Hash password"""
        try:
            tsk = get_tsk()
            result = tsk.execute_function('auth', 'hash_password', [password])
            return result.get('hash', '')
        except Exception as e:
            current_app.logger.error(f"Hash password error: {e}")
            return ''
    
    def verify_password(self, password: str, hash_value: str) -> bool:
        """Verify password against hash"""
        try:
            tsk = get_tsk()
            result = tsk.execute_function('auth', 'verify_password', [password, hash_value])
            return result.get('valid', False)
        except Exception as e:
            current_app.logger.error(f"Verify password error: {e}")
            return False
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
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
    
    def is_user_active(self, user: Dict[str, Any]) -> bool:
        """Check if user is active"""
        return (
            user.get('is_active', True) and 
            user.get('deleted_at') is None
        )
    
    def send_reset_email(self, user: Dict[str, Any], token: str) -> None:
        """Send password reset email"""
        try:
            tsk = get_tsk()
            
            reset_url = self.build_reset_url(token)
            
            email_data = {
                'to_email': user['email'],
                'to_name': user.get('first_name', 'User'),
                'subject': 'Reset Your Password',
                'template': 'password_reset',
                'data': {
                    'user_name': user.get('first_name', 'User'),
                    'reset_url': reset_url,
                    'expires_hours': self.reset_expires_hours
                }
            }
            
            tsk.execute_function('email', 'send_email', [email_data])
            
            # Log email sent
            self.log_email_sent(user['id'], 'password_reset')
            
        except Exception as e:
            current_app.logger.error(f"Send reset email error: {e}")
    
    def build_reset_url(self, token: str) -> str:
        """Build password reset URL"""
        base_url = request.host_url.rstrip('/')
        return f"{base_url}/reset-password?token={token}"
    
    def fire_password_reset_event(self, user: Dict[str, Any], token: str) -> None:
        """Fire password reset event"""
        try:
            from ..events import PasswordResetEvent
            
            event = PasswordResetEvent(user, token)
            
            tsk = get_tsk()
            tsk.execute_function('events', 'store_event', [
                'password_reset',
                user['id'],
                event.__dict__
            ])
            
        except Exception as e:
            current_app.logger.error(f"Fire password reset event error: {e}")
    
    def fire_password_changed_event(self, user: Dict[str, Any], method: str) -> None:
        """Fire password changed event"""
        try:
            from ..events import PasswordChangedEvent
            
            event = PasswordChangedEvent(user, method)
            
            tsk = get_tsk()
            tsk.execute_function('events', 'store_event', [
                'password_changed',
                user['id'],
                event.__dict__
            ])
            
        except Exception as e:
            current_app.logger.error(f"Fire password changed event error: {e}")
    
    def log_password_reset_request(self, user: Dict[str, Any]) -> None:
        """Log password reset request"""
        try:
            tsk = get_tsk()
            tsk.execute_function('logs', 'log_user_event', [
                'password_reset_request',
                user['id'],
                {
                    'email': user['email'],
                    'ip_address': request.remote_addr or 'unknown',
                    'user_agent': request.headers.get('User-Agent', 'unknown'),
                    'timestamp': datetime.now().isoformat()
                }
            ])
        except Exception as e:
            current_app.logger.error(f"Log password reset request error: {e}")
    
    def log_password_change(self, user: Dict[str, Any], method: str) -> None:
        """Log password change"""
        try:
            tsk = get_tsk()
            tsk.execute_function('logs', 'log_user_event', [
                'password_change',
                user['id'],
                {
                    'method': method,
                    'ip_address': request.remote_addr or 'unknown',
                    'timestamp': datetime.now().isoformat()
                }
            ])
        except Exception as e:
            current_app.logger.error(f"Log password change error: {e}")
    
    def log_password_force(self, user_id: int) -> None:
        """Log password force change"""
        try:
            tsk = get_tsk()
            tsk.execute_function('logs', 'log_user_event', [
                'password_force',
                user_id,
                {
                    'timestamp': datetime.now().isoformat()
                }
            ])
        except Exception as e:
            current_app.logger.error(f"Log password force error: {e}")
    
    def log_email_sent(self, user_id: int, email_type: str) -> None:
        """Log email sent"""
        try:
            tsk = get_tsk()
            tsk.execute_function('logs', 'log_email_sent', [
                user_id,
                email_type,
                datetime.now().isoformat()
            ])
        except Exception as e:
            current_app.logger.error(f"Log email sent error: {e}") 