"""
Flask-TSK Herd Two-Factor Authentication Service
===============================================
"Double protection for the herd"
Two-factor authentication with TOTP support
Strong. Secure. Scalable. 🐘
"""

from flask import current_app
from typing import Dict, List, Optional, Any, Union
import pyotp
import secrets
import time
from datetime import datetime, timedelta
import json

from ... import get_tsk

class TwoFactor:
    """Two-factor authentication service for Herd"""
    
    def __init__(self):
        self.totp_issuer = "Flask-TSK Herd"
        self.backup_code_count = 10
    
    def enable(self, user_id: int) -> Dict[str, Any]:
        """Enable 2FA for user"""
        try:
            # Generate secret key
            secret = pyotp.random_base32()
            
            # Generate backup codes
            backup_codes = self.generate_backup_codes()
            
            # Store 2FA data
            twofa_data = {
                'user_id': user_id,
                'secret': secret,
                'backup_codes': json.dumps(backup_codes),
                'enabled': False,  # Will be enabled after verification
                'created_at': datetime.now().isoformat()
            }
            
            tsk = get_tsk()
            twofa_id = tsk.execute_function('two_factor', 'create_twofa', [twofa_data])
            
            if not twofa_id:
                return {
                    'success': False,
                    'message': 'Failed to enable 2FA'
                }
            
            # Generate QR code URL
            qr_url = self.generate_qr_url(secret, user_id)
            
            return {
                'success': True,
                'secret': secret,
                'qr_url': qr_url,
                'backup_codes': backup_codes,
                'message': '2FA setup initiated. Please verify with your authenticator app.'
            }
            
        except Exception as e:
            current_app.logger.error(f"Enable 2FA error: {e}")
            return {
                'success': False,
                'message': 'An error occurred while enabling 2FA'
            }
    
    def disable(self, user_id: int) -> Dict[str, Any]:
        """Disable 2FA for user"""
        try:
            tsk = get_tsk()
            success = tsk.execute_function('two_factor', 'disable_twofa', [user_id])
            
            return {
                'success': success,
                'message': '2FA disabled successfully' if success else 'Failed to disable 2FA'
            }
            
        except Exception as e:
            current_app.logger.error(f"Disable 2FA error: {e}")
            return {
                'success': False,
                'message': 'An error occurred while disabling 2FA'
            }
    
    def verify(self, code: str, user_id: int) -> bool:
        """Verify 2FA code"""
        try:
            # Get 2FA data
            tsk = get_tsk()
            twofa_data = tsk.execute_function('two_factor', 'get_by_user_id', [user_id])
            
            if not twofa_data:
                return False
            
            # Check if 2FA is enabled
            if not twofa_data.get('enabled', False):
                return False
            
            secret = twofa_data['secret']
            
            # Verify TOTP code
            totp = pyotp.TOTP(secret)
            if totp.verify(code):
                return True
            
            # Check backup codes
            backup_codes = json.loads(twofa_data.get('backup_codes', '[]'))
            if code in backup_codes:
                # Remove used backup code
                backup_codes.remove(code)
                tsk.execute_function('two_factor', 'update_backup_codes', [user_id, json.dumps(backup_codes)])
                return True
            
            return False
            
        except Exception as e:
            current_app.logger.error(f"Verify 2FA error: {e}")
            return False
    
    def generate_backup_codes(self) -> List[str]:
        """Generate backup codes"""
        codes = []
        for _ in range(self.backup_code_count):
            code = secrets.token_hex(4).upper()
            codes.append(code)
        return codes
    
    def generate_qr_url(self, secret: str, user_id: int) -> str:
        """Generate QR code URL for authenticator app"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return ""
            
            email = user.get('email', '')
            name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
            
            totp = pyotp.TOTP(secret)
            return totp.provisioning_uri(
                name=name,
                issuer_name=self.totp_issuer
            )
            
        except Exception as e:
            current_app.logger.error(f"Generate QR URL error: {e}")
            return ""
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            tsk = get_tsk()
            users = tsk.execute_function('users', 'get_by_id', [user_id])
            return users[0] if users else None
        except Exception as e:
            current_app.logger.error(f"Get user by ID error: {e}")
            return None 