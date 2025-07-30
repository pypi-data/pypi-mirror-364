"""
Flask-TSK Herd Registration Service
==================================
"A new calf joins the herd"
User registration and account lifecycle management
Strong. Secure. Scalable. 🐘
"""

from flask import current_app, request
from typing import Dict, List, Optional, Any, Union
import secrets
import time
from datetime import datetime, timedelta
import json

from ... import get_tsk

class Registration:
    """Registration service for Herd"""
    
    def __init__(self):
        self.verification_expires_hours = 24
        self.invitation_expires_days = 7
    
    def create_user(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new user account"""
        try:
            # Validate registration data
            validation = self.validate_registration_data(data)
            if not validation['valid']:
                return {
                    'success': False,
                    'errors': validation['errors']
                }
            
            # Check if user already exists
            if self.user_exists(data['email']):
                return {
                    'success': False,
                    'errors': {'email': 'User with this email already exists'}
                }
            
            # Check if username exists (if provided)
            if 'username' in data and self.username_exists(data['username']):
                return {
                    'success': False,
                    'errors': {'username': 'Username already taken'}
                }
            
            # Hash password
            password_hash = self.hash_password(data['password'])
            
            # Generate verification token
            verification_token = self.generate_verification_token()
            
            # Prepare user data
            user_data = {
                'email': data['email'],
                'password_hash': password_hash,
                'first_name': data.get('first_name', ''),
                'last_name': data.get('last_name', ''),
                'username': data.get('username', ''),
                'verification_token': verification_token,
                'verification_expires_at': (datetime.now() + timedelta(hours=self.verification_expires_hours)).isoformat(),
                'is_active': False,
                'email_verified_at': None,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Create user in database
            tsk = get_tsk()
            user_id = tsk.execute_function('users', 'create_user', [user_data])
            
            if not user_id:
                return {
                    'success': False,
                    'errors': {'database': 'Failed to create user account'}
                }
            
            # Get created user
            user = self.get_user_by_id(user_id)
            
            # Send verification email
            self.send_verification_email(user)
            
            # Fire registration event
            self.fire_registration_event(user)
            
            # Log registration
            self.log_registration(user)
            
            return {
                'success': True,
                'user_id': user_id,
                'message': 'User account created successfully. Please check your email to verify your account.',
                'user': user
            }
            
        except Exception as e:
            current_app.logger.error(f"Create user error: {e}")
            return {
                'success': False,
                'errors': {'system': 'An error occurred while creating your account'}
            }
    
    def invite_user(self, email: str, role: str = 'user') -> bool:
        """Invite user to join the system"""
        try:
            # Check if user already exists
            if self.user_exists(email):
                current_app.logger.warning(f"Invitation sent to existing user: {email}")
                return False
            
            # Generate invitation token
            invitation_token = self.generate_verification_token()
            
            # Create invitation record
            invitation_data = {
                'email': email,
                'role': role,
                'token': invitation_token,
                'expires_at': (datetime.now() + timedelta(days=self.invitation_expires_days)).isoformat(),
                'created_at': datetime.now().isoformat()
            }
            
            tsk = get_tsk()
            invitation_id = tsk.execute_function('invitations', 'create_invitation', [invitation_data])
            
            if not invitation_id:
                return False
            
            # Send invitation email
            self.send_invitation_email(email, invitation_token, role)
            
            return True
            
        except Exception as e:
            current_app.logger.error(f"Invite user error: {e}")
            return False
    
    def verify_email(self, token: str) -> Dict[str, Any]:
        """Verify user email with token"""
        try:
            tsk = get_tsk()
            
            # Find user by verification token
            users = tsk.execute_function('users', 'get_by_verification_token', [token])
            
            if not users:
                return {
                    'success': False,
                    'errors': {'token': 'Invalid verification token'}
                }
            
            user = users[0]
            
            # Check if token is expired
            expires_at = datetime.fromisoformat(user['verification_expires_at'])
            if datetime.now() > expires_at:
                return {
                    'success': False,
                    'errors': {'token': 'Verification token has expired'}
                }
            
            # Check if already verified
            if user['email_verified_at']:
                return {
                    'success': False,
                    'errors': {'token': 'Email already verified'}
                }
            
            # Update user verification status
            update_data = {
                'email_verified_at': datetime.now().isoformat(),
                'is_active': True,
                'verification_token': None,
                'verification_expires_at': None,
                'updated_at': datetime.now().isoformat()
            }
            
            success = tsk.execute_function('users', 'update_user', [user['id'], update_data])
            
            if not success:
                return {
                    'success': False,
                    'errors': {'database': 'Failed to verify email'}
                }
            
            # Get updated user
            updated_user = self.get_user_by_id(user['id'])
            
            # Fire verification event
            self.fire_verification_event(updated_user)
            
            # Log email verification
            self.log_email_verification(updated_user)
            
            return {
                'success': True,
                'message': 'Email verified successfully. Your account is now active.',
                'user': updated_user
            }
            
        except Exception as e:
            current_app.logger.error(f"Verify email error: {e}")
            return {
                'success': False,
                'errors': {'system': 'An error occurred while verifying your email'}
            }
    
    def resend_verification(self, email: str) -> Dict[str, Any]:
        """Resend verification email"""
        try:
            # Get user by email
            user = self.get_user_by_email(email)
            if not user:
                return {
                    'success': False,
                    'errors': {'email': 'User not found'}
                }
            
            # Check if already verified
            if user['email_verified_at']:
                return {
                    'success': False,
                    'errors': {'email': 'Email already verified'}
                }
            
            # Generate new verification token
            verification_token = self.generate_verification_token()
            
            # Update user with new token
            update_data = {
                'verification_token': verification_token,
                'verification_expires_at': (datetime.now() + timedelta(hours=self.verification_expires_hours)).isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            tsk = get_tsk()
            success = tsk.execute_function('users', 'update_user', [user['id'], update_data])
            
            if not success:
                return {
                    'success': False,
                    'errors': {'database': 'Failed to update verification token'}
                }
            
            # Get updated user
            updated_user = self.get_user_by_id(user['id'])
            
            # Send verification email
            self.send_verification_email(updated_user)
            
            return {
                'success': True,
                'message': 'Verification email sent successfully'
            }
            
        except Exception as e:
            current_app.logger.error(f"Resend verification error: {e}")
            return {
                'success': False,
                'errors': {'system': 'An error occurred while sending verification email'}
            }
    
    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate user account"""
        try:
            tsk = get_tsk()
            
            # Update user status
            update_data = {
                'is_active': False,
                'deactivated_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            success = tsk.execute_function('users', 'update_user', [user_id, update_data])
            
            if success:
                # Log deactivation
                self.log_user_deactivation(user_id)
            
            return success
            
        except Exception as e:
            current_app.logger.error(f"Deactivate user error: {e}")
            return False
    
    def restore_user(self, user_id: int) -> bool:
        """Restore deactivated user account"""
        try:
            tsk = get_tsk()
            
            # Update user status
            update_data = {
                'is_active': True,
                'deactivated_at': None,
                'updated_at': datetime.now().isoformat()
            }
            
            success = tsk.execute_function('users', 'update_user', [user_id, update_data])
            
            if success:
                # Log restoration
                self.log_user_restoration(user_id)
            
            return success
            
        except Exception as e:
            current_app.logger.error(f"Restore user error: {e}")
            return False
    
    def purge_user(self, user_id: int) -> bool:
        """Permanently delete user account"""
        try:
            tsk = get_tsk()
            
            # Soft delete user
            update_data = {
                'deleted_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            success = tsk.execute_function('users', 'update_user', [user_id, update_data])
            
            if success:
                # Log purging
                self.log_user_purge(user_id)
            
            return success
            
        except Exception as e:
            current_app.logger.error(f"Purge user error: {e}")
            return False
    
    def validate_registration_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate user registration data"""
        errors = {}
        
        # Required fields
        required_fields = ['email', 'password']
        for field in required_fields:
            if field not in data or not data[field]:
                errors[field] = f'{field.title()} is required'
        
        # Email validation
        if 'email' in data and data['email']:
            if not self.is_valid_email(data['email']):
                errors['email'] = 'Invalid email format'
        
        # Password validation
        if 'password' in data and data['password']:
            password_validation = self.validate_password_strength(data['password'])
            if not password_validation['valid']:
                errors['password'] = password_validation['message']
        
        # Username validation (if provided)
        if 'username' in data and data['username']:
            if not self.is_valid_username(data['username']):
                errors['username'] = 'Username must be 3-20 characters, alphanumeric and underscores only'
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validate password strength"""
        if len(password) < 8:
            return {
                'valid': False,
                'message': 'Password must be at least 8 characters long'
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
    
    def is_valid_email(self, email: str) -> bool:
        """Check if email is valid"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def is_valid_username(self, username: str) -> bool:
        """Check if username is valid"""
        import re
        pattern = r'^[a-zA-Z0-9_]{3,20}$'
        return re.match(pattern, username) is not None
    
    def user_exists(self, email: str) -> bool:
        """Check if user exists by email"""
        try:
            tsk = get_tsk()
            users = tsk.execute_function('users', 'get_by_email', [email])
            return len(users) > 0
        except Exception as e:
            current_app.logger.error(f"Check user exists error: {e}")
            return False
    
    def username_exists(self, username: str) -> bool:
        """Check if username exists"""
        try:
            tsk = get_tsk()
            users = tsk.execute_function('users', 'get_by_username', [username])
            return len(users) > 0
        except Exception as e:
            current_app.logger.error(f"Check username exists error: {e}")
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
    
    def generate_verification_token(self) -> str:
        """Generate verification token"""
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
    
    def send_verification_email(self, user: Dict[str, Any]) -> None:
        """Send verification email"""
        try:
            tsk = get_tsk()
            
            verification_url = self.build_verification_url(user['verification_token'])
            
            email_data = {
                'to_email': user['email'],
                'to_name': user.get('first_name', 'User'),
                'subject': 'Verify Your Email Address',
                'template': 'email_verification',
                'data': {
                    'user_name': user.get('first_name', 'User'),
                    'verification_url': verification_url,
                    'expires_hours': self.verification_expires_hours
                }
            }
            
            tsk.execute_function('email', 'send_email', [email_data])
            
            # Log email sent
            self.log_email_sent(user['id'], 'verification')
            
        except Exception as e:
            current_app.logger.error(f"Send verification email error: {e}")
    
    def send_invitation_email(self, email: str, token: str, role: str) -> None:
        """Send invitation email"""
        try:
            tsk = get_tsk()
            
            invitation_url = self.build_invitation_url(token)
            
            email_data = {
                'to_email': email,
                'to_name': 'Friend',
                'subject': 'You\'re Invited to Join',
                'template': 'invitation',
                'data': {
                    'invitation_url': invitation_url,
                    'role': role,
                    'expires_days': self.invitation_expires_days
                }
            }
            
            tsk.execute_function('email', 'send_email', [email_data])
            
        except Exception as e:
            current_app.logger.error(f"Send invitation email error: {e}")
    
    def build_verification_url(self, token: str) -> str:
        """Build verification URL"""
        base_url = request.host_url.rstrip('/')
        return f"{base_url}/verify-email?token={token}"
    
    def build_invitation_url(self, token: str) -> str:
        """Build invitation URL"""
        base_url = request.host_url.rstrip('/')
        return f"{base_url}/accept-invitation?token={token}"
    
    def fire_registration_event(self, user: Dict[str, Any]) -> None:
        """Fire registration event"""
        try:
            from ..events import RegistrationEvent
            
            event = RegistrationEvent(user)
            
            tsk = get_tsk()
            tsk.execute_function('events', 'store_event', [
                'registration',
                user['id'],
                event.__dict__
            ])
            
        except Exception as e:
            current_app.logger.error(f"Fire registration event error: {e}")
    
    def fire_verification_event(self, user: Dict[str, Any]) -> None:
        """Fire verification event"""
        try:
            from ..events import VerificationEvent
            
            event = VerificationEvent(user)
            
            tsk = get_tsk()
            tsk.execute_function('events', 'store_event', [
                'verification',
                user['id'],
                event.__dict__
            ])
            
        except Exception as e:
            current_app.logger.error(f"Fire verification event error: {e}")
    
    def log_registration(self, user: Dict[str, Any]) -> None:
        """Log user registration"""
        try:
            tsk = get_tsk()
            tsk.execute_function('logs', 'log_user_event', [
                'registration',
                user['id'],
                {
                    'email': user['email'],
                    'ip_address': request.remote_addr or 'unknown',
                    'user_agent': request.headers.get('User-Agent', 'unknown'),
                    'timestamp': datetime.now().isoformat()
                }
            ])
        except Exception as e:
            current_app.logger.error(f"Log registration error: {e}")
    
    def log_email_verification(self, user: Dict[str, Any]) -> None:
        """Log email verification"""
        try:
            tsk = get_tsk()
            tsk.execute_function('logs', 'log_user_event', [
                'email_verification',
                user['id'],
                {
                    'email': user['email'],
                    'ip_address': request.remote_addr or 'unknown',
                    'timestamp': datetime.now().isoformat()
                }
            ])
        except Exception as e:
            current_app.logger.error(f"Log email verification error: {e}")
    
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
    
    def log_user_deactivation(self, user_id: int) -> None:
        """Log user deactivation"""
        try:
            tsk = get_tsk()
            tsk.execute_function('logs', 'log_user_event', [
                'deactivation',
                user_id,
                {
                    'timestamp': datetime.now().isoformat()
                }
            ])
        except Exception as e:
            current_app.logger.error(f"Log user deactivation error: {e}")
    
    def log_user_restoration(self, user_id: int) -> None:
        """Log user restoration"""
        try:
            tsk = get_tsk()
            tsk.execute_function('logs', 'log_user_event', [
                'restoration',
                user_id,
                {
                    'timestamp': datetime.now().isoformat()
                }
            ])
        except Exception as e:
            current_app.logger.error(f"Log user restoration error: {e}")
    
    def log_user_purge(self, user_id: int) -> None:
        """Log user purge"""
        try:
            tsk = get_tsk()
            tsk.execute_function('logs', 'log_user_event', [
                'purge',
                user_id,
                {
                    'timestamp': datetime.now().isoformat()
                }
            ])
        except Exception as e:
            current_app.logger.error(f"Log user purge error: {e}") 