"""
Flask-TSK Herd Manager Service
=============================
"The matriarch leads the herd"
Central management for herd operations
Strong. Secure. Scalable. 🐘
"""

from flask import current_app
from typing import Dict, List, Optional, Any, Union
import time
from datetime import datetime, timedelta

from ... import get_tsk

class HerdManager:
    """Herd management service"""
    
    def __init__(self):
        self.session_timeout = 1800  # 30 minutes
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive herd statistics"""
        try:
            return {
                'realtime': self.get_realtime_stats(),
                'users': self.get_user_stats(),
                'sessions': self.get_session_stats(),
                'activity': self.get_activity_stats(),
                'security': self.get_security_stats(),
                'performance': self.get_performance_stats(),
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            current_app.logger.error(f"Get stats error: {e}")
            return {}
    
    def get_realtime_stats(self) -> Dict[str, Any]:
        """Get real-time statistics"""
        try:
            return {
                'currently_online': self.get_currently_online(),
                'active_sessions': self.get_active_sessions(),
                'recent_logins': self.get_recent_logins(5),
                'failed_attempts': self.get_recent_failed_attempts(5),
                'security_events': self.get_recent_security_events(5),
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            current_app.logger.error(f"Get realtime stats error: {e}")
            return {}
    
    def get_user_stats(self) -> Dict[str, Any]:
        """Get user statistics"""
        try:
            tsk = get_tsk()
            
            return {
                'total_users': tsk.execute_function('users', 'count_users', []),
                'verified_users': tsk.execute_function('users', 'count_verified_users', []),
                'active_users': {
                    'today': self.get_active_users(1),
                    'this_week': self.get_active_users(7),
                    'this_month': self.get_active_users(30)
                },
                'new_registrations': {
                    'today': self.get_new_registrations(1),
                    'this_week': self.get_new_registrations(7),
                    'this_month': self.get_new_registrations(30)
                }
            }
        except Exception as e:
            current_app.logger.error(f"Get user stats error: {e}")
            return {}
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        try:
            return {
                'total_active': self.get_total_active_sessions(),
                'average_duration': self.get_average_session_duration(),
                'concurrent_peak': self.get_peak_concurrent_sessions(),
                'session_distribution': self.get_session_distribution()
            }
        except Exception as e:
            current_app.logger.error(f"Get session stats error: {e}")
            return {}
    
    def get_activity_stats(self) -> Dict[str, Any]:
        """Get activity statistics"""
        try:
            return {
                'login_patterns': self.get_login_patterns(),
                'popular_times': self.get_popular_login_times(),
                'device_distribution': self.get_device_distribution(),
                'geographic_distribution': self.get_geographic_distribution()
            }
        except Exception as e:
            current_app.logger.error(f"Get activity stats error: {e}")
            return {}
    
    def get_security_stats(self) -> Dict[str, Any]:
        """Get security statistics"""
        try:
            return {
                'failed_logins': {
                    'last_hour': self.get_failed_attempts(1, 'hour'),
                    'today': self.get_failed_attempts(1, 'day'),
                    'this_week': self.get_failed_attempts(7, 'day')
                },
                'locked_accounts': self.get_locked_accounts(),
                'suspicious_activity': self.get_suspicious_activity(),
                'password_resets': {
                    'today': self.get_password_resets(1),
                    'this_week': self.get_password_resets(7)
                }
            }
        except Exception as e:
            current_app.logger.error(f"Get security stats error: {e}")
            return {}
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        try:
            return {
                'authentication_speed': self.get_authentication_performance(),
                'session_creation_time': self.get_session_creation_performance(),
                'database_performance': self.get_database_performance(),
                'response_times': self.get_response_time_metrics()
            }
        except Exception as e:
            current_app.logger.error(f"Get performance stats error: {e}")
            return {}
    
    def get_currently_online(self) -> int:
        """Get currently online users"""
        try:
            tsk = get_tsk()
            count = tsk.execute_function('analytics', 'get_currently_online', [self.session_timeout])
            return count or 0
        except Exception as e:
            current_app.logger.error(f"Get currently online error: {e}")
            return 0
    
    def get_active_sessions(self) -> int:
        """Get active sessions count"""
        try:
            tsk = get_tsk()
            count = tsk.execute_function('sessions', 'count_active', [])
            return count or 0
        except Exception as e:
            current_app.logger.error(f"Get active sessions error: {e}")
            return 0
    
    def get_recent_logins(self, minutes: int) -> int:
        """Get recent logins"""
        try:
            tsk = get_tsk()
            count = tsk.execute_function('analytics', 'get_recent_logins', [minutes])
            return count or 0
        except Exception as e:
            current_app.logger.error(f"Get recent logins error: {e}")
            return 0
    
    def get_recent_failed_attempts(self, minutes: int) -> int:
        """Get recent failed attempts"""
        try:
            tsk = get_tsk()
            count = tsk.execute_function('analytics', 'get_recent_failed_attempts', [minutes])
            return count or 0
        except Exception as e:
            current_app.logger.error(f"Get recent failed attempts error: {e}")
            return 0
    
    def get_recent_security_events(self, minutes: int) -> int:
        """Get recent security events"""
        try:
            tsk = get_tsk()
            count = tsk.execute_function('security', 'get_recent_events', [minutes])
            return count or 0
        except Exception as e:
            current_app.logger.error(f"Get recent security events error: {e}")
            return 0
    
    def get_active_users(self, days: int) -> int:
        """Get active users for period"""
        try:
            tsk = get_tsk()
            count = tsk.execute_function('analytics', 'get_active_users_period', [days])
            return count or 0
        except Exception as e:
            current_app.logger.error(f"Get active users error: {e}")
            return 0
    
    def get_new_registrations(self, days: int) -> int:
        """Get new registrations for period"""
        try:
            tsk = get_tsk()
            count = tsk.execute_function('users', 'count_new_registrations', [days])
            return count or 0
        except Exception as e:
            current_app.logger.error(f"Get new registrations error: {e}")
            return 0
    
    def get_total_active_sessions(self) -> int:
        """Get total active sessions"""
        return self.get_active_sessions()
    
    def get_average_session_duration(self) -> float:
        """Get average session duration"""
        try:
            tsk = get_tsk()
            duration = tsk.execute_function('analytics', 'get_avg_session_duration', [])
            return float(duration) if duration else 0.0
        except Exception as e:
            current_app.logger.error(f"Get average session duration error: {e}")
            return 0.0
    
    def get_peak_concurrent_sessions(self) -> int:
        """Get peak concurrent sessions"""
        try:
            tsk = get_tsk()
            peak = tsk.execute_function('analytics', 'get_peak_concurrent_sessions', [])
            return peak or 0
        except Exception as e:
            current_app.logger.error(f"Get peak concurrent sessions error: {e}")
            return 0
    
    def get_session_distribution(self) -> Dict[str, int]:
        """Get session distribution by device type"""
        try:
            tsk = get_tsk()
            distribution = tsk.execute_function('analytics', 'get_session_distribution', [])
            return distribution or {}
        except Exception as e:
            current_app.logger.error(f"Get session distribution error: {e}")
            return {}
    
    def get_login_patterns(self) -> Dict[str, int]:
        """Get login patterns by hour"""
        try:
            tsk = get_tsk()
            patterns = tsk.execute_function('analytics', 'get_login_patterns', [])
            return patterns or {}
        except Exception as e:
            current_app.logger.error(f"Get login patterns error: {e}")
            return {}
    
    def get_popular_login_times(self) -> Dict[str, Any]:
        """Get popular login times"""
        try:
            tsk = get_tsk()
            times = tsk.execute_function('analytics', 'get_popular_login_times', [])
            return times or {}
        except Exception as e:
            current_app.logger.error(f"Get popular login times error: {e}")
            return {}
    
    def get_device_distribution(self) -> Dict[str, int]:
        """Get device distribution"""
        try:
            tsk = get_tsk()
            distribution = tsk.execute_function('analytics', 'get_device_distribution', [])
            return distribution or {}
        except Exception as e:
            current_app.logger.error(f"Get device distribution error: {e}")
            return {}
    
    def get_geographic_distribution(self) -> Dict[str, int]:
        """Get geographic distribution"""
        try:
            tsk = get_tsk()
            distribution = tsk.execute_function('analytics', 'get_geographic_distribution', [])
            return distribution or {}
        except Exception as e:
            current_app.logger.error(f"Get geographic distribution error: {e}")
            return {}
    
    def get_failed_attempts(self, count: int, unit: str) -> int:
        """Get failed attempts for period"""
        try:
            tsk = get_tsk()
            attempts = tsk.execute_function('analytics', 'get_failed_attempts', [count, unit])
            return attempts or 0
        except Exception as e:
            current_app.logger.error(f"Get failed attempts error: {e}")
            return 0
    
    def get_locked_accounts(self) -> List[Dict[str, Any]]:
        """Get locked accounts"""
        try:
            tsk = get_tsk()
            accounts = tsk.execute_function('security', 'get_locked_accounts', [])
            return accounts or []
        except Exception as e:
            current_app.logger.error(f"Get locked accounts error: {e}")
            return []
    
    def get_suspicious_activity(self) -> List[Dict[str, Any]]:
        """Get suspicious activity"""
        try:
            tsk = get_tsk()
            activity = tsk.execute_function('security', 'get_suspicious_activity', [])
            return activity or []
        except Exception as e:
            current_app.logger.error(f"Get suspicious activity error: {e}")
            return []
    
    def get_password_resets(self, days: int) -> int:
        """Get password resets for period"""
        try:
            tsk = get_tsk()
            resets = tsk.execute_function('analytics', 'get_password_resets', [days])
            return resets or 0
        except Exception as e:
            current_app.logger.error(f"Get password resets error: {e}")
            return 0
    
    def get_authentication_performance(self) -> Dict[str, float]:
        """Get authentication performance metrics"""
        try:
            tsk = get_tsk()
            performance = tsk.execute_function('performance', 'get_auth_performance', [])
            return performance or {}
        except Exception as e:
            current_app.logger.error(f"Get authentication performance error: {e}")
            return {}
    
    def get_session_creation_performance(self) -> Dict[str, float]:
        """Get session creation performance metrics"""
        try:
            tsk = get_tsk()
            performance = tsk.execute_function('performance', 'get_session_performance', [])
            return performance or {}
        except Exception as e:
            current_app.logger.error(f"Get session creation performance error: {e}")
            return {}
    
    def get_database_performance(self) -> Dict[str, float]:
        """Get database performance metrics"""
        try:
            tsk = get_tsk()
            performance = tsk.execute_function('performance', 'get_database_performance', [])
            return performance or {}
        except Exception as e:
            current_app.logger.error(f"Get database performance error: {e}")
            return {}
    
    def get_response_time_metrics(self) -> Dict[str, float]:
        """Get response time metrics"""
        try:
            tsk = get_tsk()
            metrics = tsk.execute_function('performance', 'get_response_times', [])
            return metrics or {}
        except Exception as e:
            current_app.logger.error(f"Get response time metrics error: {e}")
            return {}
    
    def get_live_stats(self) -> Dict[str, Any]:
        """Get live statistics (alias for get_realtime_stats)"""
        return self.get_realtime_stats() 