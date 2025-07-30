"""
<?tusk> TuskPython Satao - The Security Guardian
============================================

🐘 BACKSTORY: Satao - The Legendary Tusker
------------------------------------------
Satao was one of Kenya's last great "tuskers" - elephants whose tusks were
so large they touched the ground. He lived in Tsavo East National Park and
was known for his incredible intelligence, often hiding his massive tusks
behind bushes when humans approached, aware that they made him a target.
Despite constant protection efforts, poachers killed him in 2014 for his ivory.

WHY THIS NAME: Satao spent his life evading poachers, developing an acute
awareness of threats and danger. This security system embodies Satao's
vigilance - constantly watching for "poachers" (hackers/attackers) trying
to steal what's valuable. Like Satao who could sense danger from miles away,
this system detects threats before they strike.

Satao's legacy lives on in this guardian that protects your application's
"ivory" - your precious data, user information, and system integrity.

FEATURES:
- Real-time threat detection and monitoring
- Intrusion prevention system (IPS)
- DDoS attack mitigation
- SQL injection and XSS prevention
- Brute force attack protection
- Security audit logging
- Automated threat response

"In memory of Satao - may his wisdom protect what cannot be replaced"

@package TuskPython\Elephants
@author  TuskPython Team
@since   1.0.0
"""

import re
import time
import json
import hashlib
import logging
import ipaddress
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from flask import request, current_app, g
from werkzeug.exceptions import Forbidden, TooManyRequests
import redis
import sqlite3
import os
import threading
from collections import defaultdict, deque


@dataclass
class ThreatEvent:
    """Represents a detected security threat"""
    type: str
    ip: str
    reason: str
    user_agent: str
    uri: str
    timestamp: float
    threat_level: str
    details: Dict[str, Any] = None


@dataclass
class BlockedIP:
    """Represents a blocked IP address"""
    ip: str
    time: float
    reason: str
    attempts: int
    expires: float


class Satao:
    """
    Satao - The Security Guardian
    
    Like Satao who protected his herd from poachers, this class protects
    your Flask application from various security threats.
    """
    
    def __init__(self, app=None):
        self.threat_level = 'low'
        self.detected_threats = []
        self.blocked_ips = {}
        self.alert_threshold = 5
        self.emergency_mode = False
        self.trusted_ips = set()
        self.rate_limits = defaultdict(lambda: deque(maxlen=50))
        self.login_attempts = defaultdict(lambda: {'count': 0, 'window_start': time.time()})
        
        # Security patterns
        self.sql_patterns = [
            r'union\s+select',
            r'drop\s+table',
            r';\s*delete\s+from',
            r'or\s+1\s*=\s*1',
            r"'\s*or\s*'\s*'",
            r'exec\s+xp_',
            r'information_schema'
        ]
        
        self.xss_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe',
            r'<embed',
            r'<object',
            r'document\.(cookie|write)',
            r'window\.(location|open)',
            r'<svg.*?onload='
        ]
        
        self.suspicious_agents = [
            'sqlmap', 'nikto', 'scanner', 'nessus', 'havij',
            'acunetix', 'nmap', 'grab', 'harvest', 'bot'
        ]
        
        self.dangerous_extensions = {
            'php', 'php3', 'php4', 'php5', 'phtml', 'phar',
            'exe', 'bat', 'cmd', 'sh', 'cgi', 'htaccess',
            'py', 'pl', 'asp', 'aspx', 'jsp', 'jspx'
        }
        
        # Initialize with Flask app if provided
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize Satao with Flask app"""
        self.app = app
        
        # Load configuration
        self.load_security_config()
        
        # Initialize threat database
        self.initialize_threat_database()
        
        # Set up logging
        self.setup_logging()
        
        # Register Flask hooks
        self.register_hooks()
        
        # Add trusted IPs
        self.add_trusted_ips([
            '127.0.0.1',
            '::1',
            '10.0.0.0/8',
            '172.16.0.0/12',
            '192.168.0.0/16'
        ])
    
    def load_security_config(self):
        """Load security configuration from app config"""
        config = getattr(self.app, 'config', {})
        
        self.alert_threshold = config.get('SATAO_ALERT_THRESHOLD', 5)
        self.emergency_mode = config.get('SATAO_EMERGENCY_MODE', False)
        
        # Load from .peanuts file if available
        peanuts_file = config.get('SATAO_PEANUTS_FILE', '.peanuts')
        if os.path.exists(peanuts_file):
            try:
                with open(peanuts_file, 'r') as f:
                    peanuts_config = json.load(f)
                    security_config = peanuts_config.get('security', {})
                    self.alert_threshold = security_config.get('alert_threshold', self.alert_threshold)
                    self.emergency_mode = security_config.get('emergency_mode', self.emergency_mode)
            except Exception as e:
                logging.warning(f"Satao: Could not load .peanuts config: {e}")
    
    def initialize_threat_database(self):
        """Initialize threat database and load blocked IPs"""
        self.db_path = getattr(self.app, 'config', {}).get('SATAO_DB_PATH', 'satao_security.db')
        
        # Create database if it doesn't exist
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS blocked_ips (
                    ip TEXT PRIMARY KEY,
                    time REAL,
                    reason TEXT,
                    attempts INTEGER,
                    expires REAL
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS security_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT,
                    ip TEXT,
                    reason TEXT,
                    user_agent TEXT,
                    uri TEXT,
                    time REAL,
                    threat_level TEXT,
                    details TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS security_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level TEXT,
                    reason TEXT,
                    ip TEXT,
                    created_at TEXT
                )
            ''')
        
        # Load blocked IPs from database
        self.load_blocked_ips()
    
    def setup_logging(self):
        """Set up security logging"""
        log_file = getattr(self.app, 'config', {}).get('SATAO_LOG_FILE', 'logs/satao_security.log')
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        self.logger = logging.getLogger('satao')
        self.logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def register_hooks(self):
        """Register Flask request hooks"""
        @self.app.before_request
        def before_request():
            self.monitor_request()
        
        @self.app.after_request
        def after_request(response):
            self.log_request(response)
            return response
    
    def monitor_request(self):
        """Monitor incoming request for threats - Satao's eternal vigilance"""
        if self.emergency_mode:
            raise Forbidden("Emergency lockdown active - Access denied")
        
        # Get client IP
        ip = self.get_client_ip()
        
        # Check if IP is blocked
        if self.is_ip_blocked(ip):
            raise Forbidden("IP address blocked due to security violations")
        
        # Check if IP is trusted
        if self.is_trusted(ip):
            return  # Trusted IPs bypass most checks
        
        # Detect threats
        threats = {
            'sql_injection': self.detect_sql_injection(),
            'xss_attempts': self.detect_xss(),
            'brute_force': self.detect_brute_force(),
            'ddos': self.detect_ddos(),
            'file_upload': self.detect_malicious_uploads(),
            'suspicious_activity': self.detect_anomalies()
        }
        
        # Assess threat level
        self.assess_threat_level(threats)
        
        # Respond to threats
        self.respond_to_threats(threats, ip)
    
    def get_client_ip(self):
        """Get the real client IP address"""
        # Check for forwarded headers
        for header in ['X-Forwarded-For', 'X-Real-IP', 'X-Client-IP']:
            ip = request.headers.get(header)
            if ip:
                # Take the first IP if multiple are present
                return ip.split(',')[0].strip()
        
        # Fallback to remote address
        return request.remote_addr or 'unknown'
    
    def detect_sql_injection(self):
        """Detect SQL injection attempts - Poachers trying to steal data"""
        inputs = self.get_all_inputs()
        
        for key, value in inputs.items():
            if isinstance(value, str):
                for pattern in self.sql_patterns:
                    if re.search(pattern, value, re.IGNORECASE):
                        self.detected_threats.append({
                            'type': 'sql_injection',
                            'pattern': pattern,
                            'input': key,
                            'value': value[:100],
                            'time': time.time()
                        })
                        return True
        return False
    
    def detect_xss(self):
        """Detect XSS attempts - Script injections trying to poison the watering hole"""
        inputs = self.get_all_inputs()
        
        for key, value in inputs.items():
            if isinstance(value, str):
                for pattern in self.xss_patterns:
                    if re.search(pattern, value, re.IGNORECASE):
                        self.detected_threats.append({
                            'type': 'xss',
                            'pattern': pattern,
                            'input': key,
                            'value': value[:100],
                            'time': time.time()
                        })
                        return True
        return False
    
    def detect_brute_force(self):
        """Detect brute force attempts - Relentless poachers trying every path"""
        ip = self.get_client_ip()
        current_path = request.path
        
        # Check for login-related endpoints
        login_endpoints = ['/login', '/api/login', '/admin', '/wp-login', '/auth']
        
        for endpoint in login_endpoints:
            if endpoint in current_path:
                # Track attempts in 5-minute windows
                now = time.time()
                attempts = self.login_attempts[ip]
                
                # Reset window if more than 5 minutes passed
                if now - attempts['window_start'] > 300:
                    attempts['count'] = 0
                    attempts['window_start'] = now
                
                attempts['count'] += 1
                
                # More than 5 attempts in 5 minutes = brute force
                if attempts['count'] > 5:
                    self.detected_threats.append({
                        'type': 'brute_force',
                        'ip': ip,
                        'attempts': attempts['count'],
                        'endpoint': current_path,
                        'time': now
                    })
                    return True
        return False
    
    def detect_ddos(self):
        """Detect DDoS attempts - The stampede attack"""
        ip = self.get_client_ip()
        now = time.time()
        
        # Track requests per second
        self.rate_limits[ip].append(now)
        
        # Keep only requests from last 10 seconds
        recent_requests = [req_time for req_time in self.rate_limits[ip] 
                          if now - req_time < 10]
        
        # More than 50 requests in 10 seconds = potential DDoS
        if len(recent_requests) > 50:
            self.detected_threats.append({
                'type': 'ddos',
                'ip': ip,
                'requests_per_10s': len(recent_requests),
                'time': now
            })
            return True
        return False
    
    def detect_malicious_uploads(self):
        """Detect malicious file uploads - Trojan elephants at the gates"""
        if not request.files:
            return False
        
        for file_key, file_obj in request.files.items():
            if file_obj and file_obj.filename:
                filename = file_obj.filename.lower()
                extension = filename.split('.')[-1] if '.' in filename else ''
                
                # Check file extension
                if extension in self.dangerous_extensions:
                    self.detected_threats.append({
                        'type': 'malicious_upload',
                        'filename': filename,
                        'extension': extension,
                        'time': time.time()
                    })
                    return True
                
                # Check MIME type
                if file_obj.content_type:
                    dangerous_mimes = [
                        'application/x-httpd-php',
                        'application/x-php',
                        'application/x-executable',
                        'application/x-shellscript'
                    ]
                    if file_obj.content_type in dangerous_mimes:
                        self.detected_threats.append({
                            'type': 'malicious_upload',
                            'filename': filename,
                            'mime_type': file_obj.content_type,
                            'time': time.time()
                        })
                        return True
        return False
    
    def detect_anomalies(self):
        """Detect anomalies - Satao's sixth sense for danger"""
        anomalies = []
        
        # Check for suspicious user agents
        user_agent = request.headers.get('User-Agent', '')
        for agent in self.suspicious_agents:
            if agent.lower() in user_agent.lower():
                anomalies.append('suspicious_user_agent')
                break
        
        # Check for missing user agent
        if not user_agent:
            anomalies.append('missing_user_agent')
        
        # Check for direct access to sensitive files
        uri = request.path
        sensitive_patterns = [
            r'\.env', r'\.git', r'\.peanuts', r'\.shell',
            r'wp-config', r'config\.php', r'database\.php'
        ]
        
        for pattern in sensitive_patterns:
            if re.search(pattern, uri):
                anomalies.append('sensitive_file_access')
                break
        
        # Check for unusual request methods
        method = request.method
        if method not in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']:
            anomalies.append('unusual_request_method')
        
        if anomalies:
            self.detected_threats.append({
                'type': 'anomaly',
                'anomalies': anomalies,
                'ip': self.get_client_ip(),
                'time': time.time()
            })
            return True
        return False
    
    def get_all_inputs(self):
        """Get all input data from request"""
        inputs = {}
        
        # GET parameters
        inputs.update(request.args.to_dict())
        
        # POST parameters
        if request.is_json:
            inputs.update(request.get_json() or {})
        else:
            inputs.update(request.form.to_dict())
        
        # Cookies
        inputs.update(request.cookies.to_dict())
        
        # Headers
        for key, value in request.headers.items():
            inputs[f'header_{key.lower()}'] = value
        
        return inputs
    
    def assess_threat_level(self, threats):
        """Assess overall threat level - Satao's intuition"""
        active_threats = [t for t in threats.values() if t]
        threat_count = len(active_threats)
        
        if threat_count == 0:
            self.threat_level = 'low'
        elif threat_count <= 2:
            self.threat_level = 'medium'
        elif threat_count <= 4:
            self.threat_level = 'high'
        else:
            self.threat_level = 'critical'
            # Satao's wisdom: When surrounded, call for help
            self.emergency_lockdown('Multiple simultaneous threats detected')
    
    def respond_to_threats(self, threats, ip):
        """Respond to detected threats - Satao's defensive actions"""
        active_threats = [threat_type for threat_type, detected in threats.items() if detected]
        
        if not active_threats:
            return
        
        # Different responses based on threat type
        for threat_type in active_threats:
            if threat_type in ['sql_injection', 'xss_attempts']:
                # Immediate block for injection attempts
                self.block_attacker(ip, f"Detected {threat_type}")
            elif threat_type == 'brute_force':
                # Temporary block with increasing duration
                attempt_count = self.get_attempt_count(ip)
                block_duration = attempt_count * 3600  # 1hr per attempt
                self.temp_block_ip(ip, block_duration)
            elif threat_type == 'ddos':
                # Rate limiting
                self.enable_rate_limiting(ip)
            elif threat_type == 'file_upload':
                # Log and reject
                self.log_security_event('malicious_upload_blocked', ip, 'Dangerous file detected')
        
        # Alert admins if threat level is high
        if self.threat_level in ['high', 'critical']:
            self.notify_administrators(f"High threat level detected: {self.threat_level}")
    
    def emergency_lockdown(self, reason):
        """Emergency lockdown - When poachers are at the gates"""
        self.emergency_mode = True
        self.threat_level = 'critical'
        
        # Satao's final defense - hide everything valuable
        self.block_all_access()
        self.notify_administrators(reason)
        self.enable_maximum_logging()
        
        # Store emergency state
        self.store_emergency_state(reason)
        
        self.logger.critical(f"EMERGENCY LOCKDOWN ACTIVATED: {reason}")
    
    def block_all_access(self):
        """Block all access - Emergency shutdown"""
        # Create emergency lockfile
        lock_file = '/tmp/satao_emergency_lock'
        lock_data = {
            'time': time.time(),
            'reason': 'Emergency lockdown activated',
            'ip': self.get_client_ip()
        }
        
        with open(lock_file, 'w') as f:
            json.dump(lock_data, f)
    
    def block_attacker(self, ip, reason):
        """Block attacker - Satao's defensive charge"""
        block_duration = 86400  # 24 hours
        expires = time.time() + block_duration
        
        blocked_ip = BlockedIP(
            ip=ip,
            time=time.time(),
            reason=reason,
            attempts=self.get_attempt_count(ip),
            expires=expires
        )
        
        self.blocked_ips[ip] = blocked_ip
        
        # Store in database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO blocked_ips 
                (ip, time, reason, attempts, expires) 
                VALUES (?, ?, ?, ?, ?)
            ''', (ip, blocked_ip.time, reason, blocked_ip.attempts, expires))
        
        # Like Satao's trumpet warning the herd
        self.log_security_event('ip_blocked', ip, reason)
    
    def temp_block_ip(self, ip, duration):
        """Temporarily block an IP"""
        expires = time.time() + duration
        
        blocked_ip = BlockedIP(
            ip=ip,
            time=time.time(),
            reason='Temporary block',
            attempts=self.get_attempt_count(ip),
            expires=expires
        )
        
        self.blocked_ips[ip] = blocked_ip
    
    def is_ip_blocked(self, ip):
        """Check if IP is currently blocked"""
        if ip in self.blocked_ips:
            blocked = self.blocked_ips[ip]
            if time.time() < blocked.expires:
                return True
            else:
                # Remove expired block
                del self.blocked_ips[ip]
        
        return False
    
    def is_trusted(self, ip):
        """Check if IP is trusted - Satao knew friend from foe"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            
            # Check against trusted IPs
            for trusted in self.trusted_ips:
                if isinstance(trusted, str):
                    if trusted == ip:
                        return True
                else:
                    if ip_obj in trusted:
                        return True
            
            return False
        except ValueError:
            return False
    
    def add_trusted_ips(self, ips):
        """Add trusted IP addresses"""
        for ip in ips:
            try:
                if '/' in ip:
                    # CIDR notation
                    self.trusted_ips.add(ipaddress.ip_network(ip, strict=False))
                else:
                    # Single IP
                    self.trusted_ips.add(ip)
            except ValueError:
                self.logger.warning(f"Invalid trusted IP: {ip}")
    
    def get_attempt_count(self, ip):
        """Get attempt count for an IP"""
        return self.login_attempts[ip]['count']
    
    def enable_rate_limiting(self, ip):
        """Enable rate limiting for an IP"""
        # This would integrate with Flask-Limiter or similar
        pass
    
    def log_security_event(self, event_type, ip, reason):
        """Log security event - Satao's memory never forgets"""
        event = ThreatEvent(
            type=event_type,
            ip=ip,
            reason=reason,
            user_agent=request.headers.get('User-Agent', 'unknown'),
            uri=request.path,
            timestamp=time.time(),
            threat_level=self.threat_level
        )
        
        # Store in database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO security_events 
                (type, ip, reason, user_agent, uri, time, threat_level, details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.type, event.ip, event.reason, event.user_agent,
                event.uri, event.timestamp, event.threat_level,
                json.dumps(event.details or {})
            ))
        
        # Log to file
        self.logger.info(f"Security event: {event_type} from {ip} - {reason}")
    
    def notify_administrators(self, reason):
        """Notify administrators - Sound the alarm"""
        # Log critical security event
        self.logger.critical(f"CRITICAL SECURITY ALERT: {reason}")
        
        # Store in database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO security_alerts (level, reason, ip, created_at)
                VALUES (?, ?, ?, ?)
            ''', ('critical', reason, self.get_client_ip(), datetime.now().isoformat()))
        
        # Could integrate with email/notification systems here
        if hasattr(self.app, 'extensions') and 'mail' in self.app.extensions:
            # Send email notification
            pass
    
    def enable_maximum_logging(self):
        """Enable maximum logging - Record everything"""
        # Set up detailed request logging
        log_data = {
            'time': datetime.now().isoformat(),
            'ip': self.get_client_ip(),
            'method': request.method,
            'uri': request.path,
            'user_agent': request.headers.get('User-Agent', ''),
            'referrer': request.headers.get('Referer', ''),
            'post_data': dict(request.form),
            'get_data': dict(request.args),
            'headers': dict(request.headers)
        }
        
        self.logger.critical(f"EMERGENCY LOG: {json.dumps(log_data)}")
    
    def store_emergency_state(self, reason):
        """Store emergency state for recovery"""
        emergency_data = {
            'time': time.time(),
            'reason': reason,
            'ip': self.get_client_ip()
        }
        
        # Store in database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO security_alerts (level, reason, ip, created_at)
                VALUES (?, ?, ?, ?)
            ''', ('emergency', reason, self.get_client_ip(), datetime.now().isoformat()))
    
    def load_blocked_ips(self):
        """Load blocked IPs from database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT ip, time, reason, attempts, expires 
                FROM blocked_ips 
                WHERE expires > ?
            ''', (time.time(),))
            
            for row in cursor:
                ip, block_time, reason, attempts, expires = row
                self.blocked_ips[ip] = BlockedIP(
                    ip=ip,
                    time=block_time,
                    reason=reason,
                    attempts=attempts,
                    expires=expires
                )
    
    def log_request(self, response):
        """Log request details"""
        if self.threat_level in ['high', 'critical']:
            self.logger.info(f"Request: {request.method} {request.path} - {response.status_code}")
    
    def audit(self):
        """Security audit - Learning from every encounter"""
        return {
            'threat_level': self.threat_level,
            'active_threats': len(self.detected_threats),
            'blocked_ips': len(self.blocked_ips),
            'emergency_mode': self.emergency_mode,
            'last_attack': self.get_last_attack_time(),
            'protection_status': self.get_protection_status()
        }
    
    def get_last_attack_time(self):
        """Get last attack time"""
        if not self.detected_threats:
            return None
        return max(threat['time'] for threat in self.detected_threats)
    
    def get_protection_status(self):
        """Get protection status - Satao's current state"""
        if self.emergency_mode:
            return 'emergency_lockdown'
        
        status_map = {
            'critical': 'maximum_alert',
            'high': 'heightened_security',
            'medium': 'elevated_watch',
            'low': 'active_monitoring'
        }
        
        return status_map.get(self.threat_level, 'unknown')
    
    def get_threat_intelligence(self):
        """Get threat intelligence - Shared knowledge saves lives"""
        return {
            'known_attackers': self.get_known_attackers(),
            'attack_patterns': self.get_attack_patterns(),
            'vulnerabilities': self.get_known_vulnerabilities(),
            'recommendations': self.get_security_recommendations()
        }
    
    def get_known_attackers(self):
        """Get known attackers from threat intelligence"""
        attackers = {}
        
        # Add recently blocked IPs
        for ip, blocked in self.blocked_ips.items():
            attackers[ip] = {
                'ip': ip,
                'first_seen': blocked.time,
                'attacks': blocked.attempts,
                'status': 'blocked'
            }
        
        return attackers
    
    def get_attack_patterns(self):
        """Get common attack patterns"""
        return {
            'sql_injection': {
                'patterns': self.sql_patterns,
                'severity': 'critical',
                'response': 'immediate_block'
            },
            'xss': {
                'patterns': self.xss_patterns,
                'severity': 'high',
                'response': 'sanitize_and_block'
            },
            'path_traversal': {
                'patterns': [
                    r'\.\./', r'\.\.\\', r'%2e%2e/',
                    r'/etc/passwd', r'C:\\Windows'
                ],
                'severity': 'high',
                'response': 'block_request'
            }
        }
    
    def get_known_vulnerabilities(self):
        """Get known vulnerabilities"""
        vulnerabilities = []
        
        # Check for common misconfigurations
        if self.app.debug:
            vulnerabilities.append({
                'type': 'configuration',
                'issue': 'Debug mode enabled in production',
                'severity': 'medium',
                'fix': 'Set debug = False in production'
            })
        
        return vulnerabilities
    
    def get_security_recommendations(self):
        """Get security recommendations - Satao's wisdom"""
        recommendations = [
            'Use HTTPS for all connections',
            'Enable Content Security Policy (CSP) headers',
            'Implement rate limiting on all endpoints',
            'Regular security audits and penetration testing',
            'Keep all software and dependencies updated',
            'Use prepared statements for all database queries',
            'Implement proper session management',
            'Enable two-factor authentication for admin accounts',
            'Regular backup and disaster recovery testing',
            'Monitor and analyze security logs regularly'
        ]
        
        # Add specific recommendations based on current threats
        if self.threat_level in ['high', 'critical']:
            recommendations.insert(0, f'URGENT: Address current {self.threat_level} threat level')
            recommendations.insert(1, 'Review recent security events in the audit log')
            recommendations.insert(2, 'Consider enabling emergency lockdown mode')
        
        return recommendations
    
    def scan(self, server=None, get=None, post=None):
        """Simple scan method for basic security checking"""
        # Basic security scan - always return safe for now
        # This can be enhanced later with real threat detection
        return {
            'safe': True,
            'threat_level': 'low',
            'threats': []
        }
    
    @staticmethod
    def handle_threat(security_check):
        """Handle security threats"""
        if not security_check['safe']:
            raise Forbidden("Access Denied - Security threat detected")
    
    def cleanup_expired_blocks(self):
        """Clean up expired IP blocks"""
        current_time = time.time()
        expired_ips = [
            ip for ip, blocked in self.blocked_ips.items()
            if current_time >= blocked.expires
        ]
        
        for ip in expired_ips:
            del self.blocked_ips[ip]
        
        # Clean up database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('DELETE FROM blocked_ips WHERE expires <= ?', (current_time,))
    
    def reset_emergency_mode(self):
        """Reset emergency mode - Satao stands down"""
        self.emergency_mode = False
        self.threat_level = 'low'
        
        # Remove emergency lockfile
        lock_file = '/tmp/satao_emergency_lock'
        if os.path.exists(lock_file):
            os.remove(lock_file)
        
        self.logger.info("Emergency mode deactivated - Satao stands down")


# Flask extension registration
def init_satao(app):
    """Initialize Satao with Flask app"""
    satao = Satao(app)
    app.satao = satao
    return satao 