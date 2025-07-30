"""
Flask-TSK Herd Audit Service
===========================
"The herd never forgets its history"
Audit logging with elephant memory
Strong. Secure. Scalable. 🐘
"""

from flask import current_app, request
from typing import Dict, List, Optional, Any, Union
import time
from datetime import datetime
import json

from ... import get_tsk

class Audit:
    """Audit logging service for Herd"""
    
    def __init__(self):
        self.audit_levels = ['info', 'warning', 'error', 'critical']
    
    def log_event(self, event_type: str, user_id: Optional[int], data: Dict[str, Any], level: str = 'info') -> bool:
        """Log audit event"""
        try:
            if level not in self.audit_levels:
                level = 'info'
            
            audit_data = {
                'event_type': event_type,
                'user_id': user_id,
                'level': level,
                'ip_address': request.remote_addr or 'unknown',
                'user_agent': request.headers.get('User-Agent', 'unknown'),
                'data': json.dumps(data),
                'timestamp': datetime.now().isoformat()
            }
            
            tsk = get_tsk()
            return tsk.execute_function('audit', 'log_event', [audit_data])
            
        except Exception as e:
            current_app.logger.error(f"Audit log error: {e}")
            return False
    
    def get_audit_logs(self, user_id: Optional[int] = None, event_type: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit logs"""
        try:
            tsk = get_tsk()
            filters = {}
            if user_id:
                filters['user_id'] = user_id
            if event_type:
                filters['event_type'] = event_type
            
            logs = tsk.execute_function('audit', 'get_logs', [filters, limit])
            return logs or []
            
        except Exception as e:
            current_app.logger.error(f"Get audit logs error: {e}")
            return []
    
    def cleanup_old_logs(self, days: int = 90) -> int:
        """Clean up old audit logs"""
        try:
            tsk = get_tsk()
            count = tsk.execute_function('audit', 'cleanup_old_logs', [days])
            return count or 0
        except Exception as e:
            current_app.logger.error(f"Cleanup audit logs error: {e}")
            return 0 