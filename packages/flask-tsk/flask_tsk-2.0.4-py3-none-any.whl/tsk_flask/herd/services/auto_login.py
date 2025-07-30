"""
Flask-TSK Herd AutoLogin Service
===============================
"Magic links for the herd - elephants never forget the way home"
Secure auto-login with magic links and enhanced tracking
Strong. Secure. Scalable. 🐘
"""

from flask import current_app, session, request
from typing import Dict, List, Optional, Any, Union
import secrets
import time
from datetime import datetime, timedelta
import json

from ... import get_tsk

class AutoLogin:
    """Auto-login service for Herd"""
    
    def __init__(self):
        self.default_expires_hours = 24
        self.max_uses_default = 1
        self.token_length = 64
    
    def generate_magic_link(self, user_id: int, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate magic link for user auto-login"""
        try:
            options = options or {}
            
            # Get user
            user = self.get_user_by_id(user_id)
            if not user:
                return {
                    'success': False,
                    'message': 'User not found'
                }
            
            if not self.is_user_active(user):
                return {
                    'success': False,
                    'message': 'User account is not active'
                }
            
            # Parse options
            purpose = options.get('purpose', 'login')
            redirect_url = options.get('redirect', '/dashboard/')
            valid_days = options.get('valid_days', 1)
            max_uses = options.get('max_uses', self.max_uses_default)
            
            # Generate secure token
            token = self.generate_secure_token()
            expires_at = datetime.now() + timedelta(days=valid_days)
            
            # Store magic link
            link_data = {
                'user_id': user_id,
                'token': token,
                'purpose': purpose,
                'redirect_url': redirect_url,
                'max_uses': max_uses,
                'uses_count': 0,
                'expires_at': expires_at.isoformat(),
                'created_at': datetime.now().isoformat()
            }
            
            tsk = get_tsk()
            link_id = tsk.execute_function('magic_links', 'create_link', [link_data])
            
            if not link_id:
                return {
                    'success': False,
                    'message': 'Failed to generate magic link'
                }
            
            # Build magic link URL
            magic_url = self.build_magic_url(token, redirect_url)
            
            return {
                'success': True,
                'magic_url': magic_url,
                'token': token,
                'expires_at': expires_at.isoformat(),
                'expires_in_hours': valid_days * 24,
                'max_uses': max_uses,
                'purpose': purpose,
                'link_id': link_id
            }
            
        except Exception as e:
            current_app.logger.error(f"Generate magic link error: {e}")
            return {
                'success': False,
                'message': 'Failed to generate magic link'
            }
    
    def verify_magic_link(self, token: str) -> Dict[str, Any]:
        """Verify magic link token"""
        try:
            tsk = get_tsk()
            
            # Find token
            links = tsk.execute_function('magic_links', 'get_by_token', [token])
            
            if not links:
                return {
                    'valid': False,
                    'message': 'Invalid magic link'
                }
            
            link = links[0]
            
            # Check if expired
            expires_at = datetime.fromisoformat(link['expires_at'])
            if datetime.now() > expires_at:
                return {
                    'valid': False,
                    'message': 'Magic link has expired'
                }
            
            # Check usage limits
            if link['uses_count'] >= link['max_uses']:
                return {
                    'valid': False,
                    'message': 'Magic link has been used maximum times'
                }
            
            # Get user
            user = self.get_user_by_id(link['user_id'])
            if not user or not self.is_user_active(user):
                return {
                    'valid': False,
                    'message': 'User account is not active'
                }
            
            return {
                'valid': True,
                'user_id': link['user_id'],
                'user': user,
                'purpose': link['purpose'],
                'redirect_url': link['redirect_url'],
                'link_id': link['id']
            }
            
        except Exception as e:
            current_app.logger.error(f"Verify magic link error: {e}")
            return {
                'valid': False,
                'message': 'An error occurred while verifying the magic link'
            }
    
    def login_with_magic_link(self, token: str) -> Dict[str, Any]:
        """Login user with magic link"""
        try:
            # Verify the token first
            verification = self.verify_magic_link(token)
            if not verification['valid']:
                return {
                    'success': False,
                    'message': verification['message']
                }
            
            user = verification['user']
            link_id = verification['link_id']
            redirect_url = verification['redirect_url']
            
            # Update usage tracking
            self.update_magic_link_usage(link_id)
            
            # Create user session
            session_created = self.create_magic_link_session(user)
            
            if not session_created:
                return {
                    'success': False,
                    'message': 'Failed to create user session'
                }
            
            # Update user's last login
            tsk = get_tsk()
            tsk.execute_function('users', 'update_last_login', [
                user['id'],
                datetime.now().isoformat(),
                request.remote_addr or 'unknown'
            ])
            
            return {
                'success': True,
                'user_id': user['id'],
                'redirect_url': redirect_url,
                'login_method': 'magic_link',
                'message': 'Successfully logged in with magic link'
            }
            
        except Exception as e:
            current_app.logger.error(f"Magic link login error: {e}")
            return {
                'success': False,
                'message': 'Login failed - please try again'
            }
    
    def send_magic_link_email(self, user_id: int, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send magic link via email"""
        try:
            options = options or {}
            
            # Generate magic link
            link_result = self.generate_magic_link(user_id, options)
            if not link_result['success']:
                return link_result
            
            user = self.get_user_by_id(user_id)
            if not user:
                return {
                    'success': False,
                    'message': 'User not found'
                }
            
            # Send email
            purpose = options.get('purpose', 'login')
            subject = options.get('subject', self.get_default_subject(purpose))
            
            email_data = {
                'to_email': user['email'],
                'to_name': user.get('first_name', 'User'),
                'subject': subject,
                'template': 'magic_link',
                'data': {
                    'user_name': user.get('first_name', 'User'),
                    'magic_url': link_result['magic_url'],
                    'purpose': purpose,
                    'expires_hours': link_result['expires_in_hours']
                }
            }
            
            tsk = get_tsk()
            tsk.execute_function('email', 'send_email', [email_data])
            
            return {
                'success': True,
                'message': 'Magic link sent successfully',
                'link_id': link_result['link_id'],
                'expires_at': link_result['expires_at']
            }
            
        except Exception as e:
            current_app.logger.error(f"Send magic link email error: {e}")
            return {
                'success': False,
                'message': 'Failed to send magic link email'
            }
    
    def generate_secure_token(self) -> str:
        """Generate secure token"""
        return secrets.token_urlsafe(self.token_length)
    
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
    
    def build_magic_url(self, token: str, redirect: str = '/dashboard/') -> str:
        """Build magic link URL"""
        base_url = request.host_url.rstrip('/')
        params = {
            'token': token,
            'redirect': redirect
        }
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}/magic-login?{query_string}"
    
    def create_magic_link_session(self, user: Dict[str, Any]) -> bool:
        """Create user session for magic link login"""
        try:
            # Regenerate session ID for security
            session.regenerate()
            
            # Set session data
            session['herd_authenticated'] = True
            session['user_id'] = user['id']
            session['user_email'] = user['email']
            session['login_time'] = time.time()
            session['login_method'] = 'magic_link'
            session['session_id'] = session.sid
            
            # Set session lifetime
            session.permanent = True
            session.modified = True
            
            return True
            
        except Exception as e:
            current_app.logger.error(f"Create magic link session error: {e}")
            return False
    
    def update_magic_link_usage(self, link_id: int) -> None:
        """Update magic link usage count"""
        try:
            tsk = get_tsk()
            tsk.execute_function('magic_links', 'increment_usage', [link_id])
        except Exception as e:
            current_app.logger.error(f"Update magic link usage error: {e}")
    
    def get_default_subject(self, purpose: str) -> str:
        """Get default email subject for purpose"""
        subjects = {
            'login': '🔐 Your Magic Login Link',
            'email_verification': '✅ Verify Your Email Address',
            'password_reset': '🔑 Reset Your Password',
            'welcome': '🎉 Welcome to the Herd!'
        }
        return subjects.get(purpose, '🐘 Your Secure Access Link') 