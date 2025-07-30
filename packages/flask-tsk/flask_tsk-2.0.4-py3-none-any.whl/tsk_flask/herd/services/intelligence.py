"""
Flask-TSK Herd Intelligence Service
==================================
"The herd's wisdom and insights"
Analytics, security intelligence, and behavioral analysis
Strong. Secure. Scalable. 🐘
"""

from flask import current_app, request
from typing import Dict, List, Optional, Any, Union
import time
from datetime import datetime, timedelta
import json

from ... import get_tsk

class Intelligence:
    """Intelligence and analytics service for Herd"""
    
    def __init__(self):
        self.anomaly_threshold = 3
        self.session_timeout = 1800  # 30 minutes
    
    def get_intelligence_report(self) -> Dict[str, Any]:
        """Get comprehensive intelligence report"""
        try:
            return {
                'security': self.get_security_intelligence(),
                'behavior': self.get_behavior_intelligence(),
                'realtime': self.get_realtime_metrics(),
                'insights': self.generate_insights(),
                'recommendations': self.get_recommendations(),
                'generated_at': datetime.now().isoformat()
            }
        except Exception as e:
            current_app.logger.error(f"Get intelligence report error: {e}")
            return {}
    
    def get_security_intelligence(self) -> Dict[str, Any]:
        """Get security intelligence"""
        try:
            tsk = get_tsk()
            
            return {
                'threat_level': self.calculate_threat_level(),
                'security_score': self.calculate_security_score(),
                'failed_attempts': self.get_failed_login_attempts(),
                'suspicious_ips': self.get_suspicious_ips(),
                'device_anomalies': self.get_device_anomalies(),
                'geographic_anomalies': self.get_geographic_anomalies(),
                'active_threats': self.get_active_threats(),
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            current_app.logger.error(f"Get security intelligence error: {e}")
            return {}
    
    def get_behavior_intelligence(self) -> Dict[str, Any]:
        """Get behavioral intelligence"""
        try:
            tsk = get_tsk()
            
            return {
                'login_patterns': self.get_login_patterns(),
                'session_patterns': self.get_session_patterns(),
                'page_analytics': self.get_page_analytics(),
                'user_journey': self.get_user_journey_data(),
                'engagement_metrics': self.get_engagement_metrics(),
                'conversion_funnel': self.get_conversion_funnel(),
                'device_usage': self.get_device_usage(),
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            current_app.logger.error(f"Get behavior intelligence error: {e}")
            return {}
    
    def get_realtime_metrics(self) -> Dict[str, Any]:
        """Get real-time metrics"""
        try:
            return {
                'active_users': self.get_active_users(),
                'recent_logins': self.get_recent_logins(5),
                'page_views_per_minute': self.get_page_views_per_minute(),
                'new_sessions': self.get_new_sessions_count(),
                'bounce_rate': self.calculate_current_bounce_rate(),
                'average_session_duration': self.get_average_session_duration(),
                'security_alerts': self.get_recent_security_alerts(),
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            current_app.logger.error(f"Get realtime metrics error: {e}")
            return {}
    
    def track_user_activity(self, user_id: int, action: str, data: Dict[str, Any] = None) -> None:
        """Track user activity"""
        try:
            tsk = get_tsk()
            
            activity_data = {
                'user_id': user_id,
                'action': action,
                'data': json.dumps(data or {}),
                'ip_address': request.remote_addr or 'unknown',
                'user_agent': request.headers.get('User-Agent', 'unknown'),
                'timestamp': datetime.now().isoformat()
            }
            
            tsk.execute_function('analytics', 'track_activity', [activity_data])
            
            # Update real-time stats
            self.update_real_time_stats(action, data or {})
            
        except Exception as e:
            current_app.logger.error(f"Track user activity error: {e}")
    
    def generate_insights(self) -> List[Dict[str, Any]]:
        """Generate insights from data"""
        try:
            insights = []
            
            # Security insights
            failed_attempts = self.get_failed_login_attempts()
            if failed_attempts > 10:
                insights.append({
                    'type': 'security',
                    'severity': 'high',
                    'message': f'High number of failed login attempts: {failed_attempts}',
                    'recommendation': 'Review security measures and consider rate limiting'
                })
            
            # Performance insights
            active_users = self.get_active_users()
            if active_users > 100:
                insights.append({
                    'type': 'performance',
                    'severity': 'medium',
                    'message': f'High concurrent users: {active_users}',
                    'recommendation': 'Monitor server performance and consider scaling'
                })
            
            return insights
            
        except Exception as e:
            current_app.logger.error(f"Generate insights error: {e}")
            return []
    
    def get_recommendations(self) -> List[Dict[str, Any]]:
        """Get security and performance recommendations"""
        try:
            recommendations = []
            
            # Security recommendations
            security_score = self.calculate_security_score()
            if security_score < 70:
                recommendations.append({
                    'type': 'security',
                    'priority': 'high',
                    'message': 'Security score is low. Review authentication and access controls.',
                    'action': 'Implement additional security measures'
                })
            
            # Performance recommendations
            avg_session = self.get_average_session_duration()
            if avg_session < 60:
                recommendations.append({
                    'type': 'performance',
                    'priority': 'medium',
                    'message': 'Low session duration. Consider improving user experience.',
                    'action': 'Analyze user journey and optimize engagement'
                })
            
            return recommendations
            
        except Exception as e:
            current_app.logger.error(f"Get recommendations error: {e}")
            return []
    
    def calculate_threat_level(self) -> str:
        """Calculate current threat level"""
        try:
            failed_attempts = self.get_failed_login_attempts()
            suspicious_ips = len(self.get_suspicious_ips())
            
            if failed_attempts > 20 or suspicious_ips > 5:
                return 'high'
            elif failed_attempts > 10 or suspicious_ips > 2:
                return 'medium'
            else:
                return 'low'
        except Exception as e:
            current_app.logger.error(f"Calculate threat level error: {e}")
            return 'unknown'
    
    def calculate_security_score(self) -> int:
        """Calculate security score (0-100)"""
        try:
            score = 100
            
            # Deduct for failed attempts
            failed_attempts = self.get_failed_login_attempts()
            score -= min(failed_attempts * 2, 30)
            
            # Deduct for suspicious activity
            suspicious_ips = len(self.get_suspicious_ips())
            score -= min(suspicious_ips * 5, 20)
            
            return max(score, 0)
        except Exception as e:
            current_app.logger.error(f"Calculate security score error: {e}")
            return 0
    
    def get_failed_login_attempts(self) -> int:
        """Get recent failed login attempts"""
        try:
            tsk = get_tsk()
            count = tsk.execute_function('analytics', 'get_failed_attempts', [60])  # Last hour
            return count or 0
        except Exception as e:
            current_app.logger.error(f"Get failed attempts error: {e}")
            return 0
    
    def get_suspicious_ips(self) -> List[str]:
        """Get suspicious IP addresses"""
        try:
            tsk = get_tsk()
            ips = tsk.execute_function('security', 'get_suspicious_ips', [])
            return ips or []
        except Exception as e:
            current_app.logger.error(f"Get suspicious IPs error: {e}")
            return []
    
    def get_device_anomalies(self) -> List[Dict[str, Any]]:
        """Get device anomalies"""
        try:
            tsk = get_tsk()
            anomalies = tsk.execute_function('security', 'get_device_anomalies', [])
            return anomalies or []
        except Exception as e:
            current_app.logger.error(f"Get device anomalies error: {e}")
            return []
    
    def get_geographic_anomalies(self) -> List[Dict[str, Any]]:
        """Get geographic anomalies"""
        try:
            tsk = get_tsk()
            anomalies = tsk.execute_function('security', 'get_geographic_anomalies', [])
            return anomalies or []
        except Exception as e:
            current_app.logger.error(f"Get geographic anomalies error: {e}")
            return []
    
    def get_active_users(self) -> int:
        """Get currently active users"""
        try:
            tsk = get_tsk()
            count = tsk.execute_function('analytics', 'get_active_users', [self.session_timeout])
            return count or 0
        except Exception as e:
            current_app.logger.error(f"Get active users error: {e}")
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
    
    def get_page_views_per_minute(self) -> float:
        """Get page views per minute"""
        try:
            tsk = get_tsk()
            views = tsk.execute_function('analytics', 'get_page_views_per_minute', [])
            return float(views) if views else 0.0
        except Exception as e:
            current_app.logger.error(f"Get page views per minute error: {e}")
            return 0.0
    
    def get_new_sessions_count(self) -> int:
        """Get new sessions count"""
        try:
            tsk = get_tsk()
            count = tsk.execute_function('analytics', 'get_new_sessions', [5])  # Last 5 minutes
            return count or 0
        except Exception as e:
            current_app.logger.error(f"Get new sessions count error: {e}")
            return 0
    
    def calculate_current_bounce_rate(self) -> float:
        """Calculate current bounce rate"""
        try:
            tsk = get_tsk()
            rate = tsk.execute_function('analytics', 'get_bounce_rate', [])
            return float(rate) if rate else 0.0
        except Exception as e:
            current_app.logger.error(f"Calculate bounce rate error: {e}")
            return 0.0
    
    def get_average_session_duration(self) -> int:
        """Get average session duration in seconds"""
        try:
            tsk = get_tsk()
            duration = tsk.execute_function('analytics', 'get_avg_session_duration', [])
            return int(duration) if duration else 0
        except Exception as e:
            current_app.logger.error(f"Get average session duration error: {e}")
            return 0
    
    def get_recent_security_alerts(self) -> int:
        """Get recent security alerts"""
        try:
            tsk = get_tsk()
            alerts = tsk.execute_function('security', 'get_recent_alerts', [60])  # Last hour
            return alerts or 0
        except Exception as e:
            current_app.logger.error(f"Get recent security alerts error: {e}")
            return 0
    
    def get_login_patterns(self) -> Dict[str, Any]:
        """Get login patterns"""
        try:
            tsk = get_tsk()
            patterns = tsk.execute_function('analytics', 'get_login_patterns', [])
            return patterns or {}
        except Exception as e:
            current_app.logger.error(f"Get login patterns error: {e}")
            return {}
    
    def get_session_patterns(self) -> Dict[str, Any]:
        """Get session patterns"""
        try:
            tsk = get_tsk()
            patterns = tsk.execute_function('analytics', 'get_session_patterns', [])
            return patterns or {}
        except Exception as e:
            current_app.logger.error(f"Get session patterns error: {e}")
            return {}
    
    def get_page_analytics(self) -> Dict[str, Any]:
        """Get page analytics"""
        try:
            tsk = get_tsk()
            analytics = tsk.execute_function('analytics', 'get_page_analytics', [])
            return analytics or {}
        except Exception as e:
            current_app.logger.error(f"Get page analytics error: {e}")
            return {}
    
    def get_user_journey_data(self) -> Dict[str, Any]:
        """Get user journey data"""
        try:
            tsk = get_tsk()
            journey = tsk.execute_function('analytics', 'get_user_journey', [])
            return journey or {}
        except Exception as e:
            current_app.logger.error(f"Get user journey data error: {e}")
            return {}
    
    def get_engagement_metrics(self) -> Dict[str, Any]:
        """Get engagement metrics"""
        try:
            tsk = get_tsk()
            metrics = tsk.execute_function('analytics', 'get_engagement_metrics', [])
            return metrics or {}
        except Exception as e:
            current_app.logger.error(f"Get engagement metrics error: {e}")
            return {}
    
    def get_conversion_funnel(self) -> Dict[str, Any]:
        """Get conversion funnel data"""
        try:
            tsk = get_tsk()
            funnel = tsk.execute_function('analytics', 'get_conversion_funnel', [])
            return funnel or {}
        except Exception as e:
            current_app.logger.error(f"Get conversion funnel error: {e}")
            return {}
    
    def get_device_usage(self) -> Dict[str, Any]:
        """Get device usage statistics"""
        try:
            tsk = get_tsk()
            usage = tsk.execute_function('analytics', 'get_device_usage', [])
            return usage or {}
        except Exception as e:
            current_app.logger.error(f"Get device usage error: {e}")
            return {}
    
    def get_active_threats(self) -> List[Dict[str, Any]]:
        """Get active threats"""
        try:
            tsk = get_tsk()
            threats = tsk.execute_function('security', 'get_active_threats', [])
            return threats or []
        except Exception as e:
            current_app.logger.error(f"Get active threats error: {e}")
            return []
    
    def update_real_time_stats(self, event: str, data: Dict[str, Any]) -> None:
        """Update real-time statistics"""
        try:
            tsk = get_tsk()
            tsk.execute_function('analytics', 'update_realtime_stats', [event, data])
        except Exception as e:
            current_app.logger.error(f"Update real-time stats error: {e}")
    
    def get_footprint_analytics(self) -> Dict[str, Any]:
        """Get footprint analytics (user behavior tracking)"""
        try:
            tsk = get_tsk()
            footprint = tsk.execute_function('analytics', 'get_footprint', [])
            return footprint or {}
        except Exception as e:
            current_app.logger.error(f"Get footprint analytics error: {e}")
            return {}
    
    def get_security_intelligence(self) -> Dict[str, Any]:
        """Get security intelligence (alias for get_security_intelligence)"""
        return self.get_security_intelligence() 