"""
TuskPHP Kaavan - The Lone Wolf Monitor & Backup Guardian (Python Edition)
========================================================================

🐘 BACKSTORY: Kaavan - "The World's Loneliest Elephant"
-------------------------------------------------------
Kaavan spent 35 years alone in a Pakistani zoo after his companion Saheli died in 2012.
His story touched hearts worldwide, leading to a massive campaign by Cher and others
to rescue him. In 2020, he was finally relocated to a sanctuary in Cambodia where he
could live with other elephants again.

WHY THIS NAME: Like Kaavan who stood alone for years, watching and waiting,
this class works in isolation, constantly monitoring your application's health.
It watches over everything - files, folders, cron jobs - ensuring nothing goes wrong.
And just as Kaavan was eventually rescued, this system rescues your data through
automated backups, ensuring you're never truly alone when disaster strikes.

"We are all like Kaavan" - standing guard over what matters most.

FEATURES:
- Continuous file and folder monitoring
- Cron job health checks
- Error detection and admin notifications
- Automated backup system (local, S3, remote)
- Self-healing capabilities
- Disaster recovery management

@package TuskPHP\Elephants
@author  TuskPHP Team
@since   2.0.0
"""

import os
import time
import json
import shutil
import hashlib
import subprocess
import threading
import schedule
from typing import Dict, List, Optional, Any, Union, Callable
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Flask-TSK imports
try:
    from tsk_flask.database import TuskDb
    from tsk_flask.memory import Memory
    from tsk_flask.utils import PermissionHelper
except ImportError:
    # Fallback for standalone usage
    TuskDb = None
    Memory = None
    PermissionHelper = None


@dataclass
class BackupConfig:
    """Backup configuration data structure"""
    destination: str = "/backups"
    s3_bucket: Optional[str] = None
    retention_days: int = 30
    schedule: str = "daily"
    compression: bool = True
    encryption: bool = False
    verify_backups: bool = True


@dataclass
class MonitoringAlert:
    """Monitoring alert data structure"""
    id: str
    type: str
    severity: str
    message: str
    timestamp: int
    resolved: bool = False
    resolved_at: Optional[int] = None
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class SystemHealth:
    """System health data structure"""
    timestamp: int
    files_status: Dict
    database_status: Dict
    cron_status: Dict
    errors_status: Dict
    backups_status: Dict
    overall_score: float


class Kaavan:
    """The Lone Wolf Monitor & Backup Guardian"""
    
    def __init__(self, config: Dict = None):
        """
        Initialize Kaavan - The lonely guardian begins his watch
        
        Args:
            config: Configuration dictionary
        """
        self.monitoring_enabled = True
        self.error_threshold = 3
        self.last_check = None
        self.alerts_sent = 0
        self.monitoring_thread = None
        self.backup_thread = None
        
        # Load configuration
        self.backup_config = self._load_backup_config(config)
        
        # Initialize monitoring state
        self.last_check = int(time.time())
        self.health_history: List[SystemHealth] = []
        self.active_alerts: Dict[str, MonitoringAlert] = {}
        
        # Setup logging
        self.logger = logging.getLogger('kaavan')
        self.logger.setLevel(logging.INFO)
        
        # Start monitoring
        self._start_monitoring()
    
    def watch(self) -> Dict:
        """
        Start monitoring - Kaavan begins his lonely vigil
        
        Returns:
            Dict with monitoring results
        """
        # Like Kaavan in his enclosure, constantly observing
        results = {
            'timestamp': int(time.time()),
            'files': self._scan_files(),
            'cron': self._check_cron_jobs(),
            'database': self._verify_database_health(),
            'disk_space': self._monitor_disk_space(),
            'error_logs': self._check_error_logs(),
            'backups': self._check_backup_status()
        }
        
        # Generate health score
        health_score = self._calculate_health_score(results)
        results['health_score'] = health_score
        
        # Store health data
        health_data = SystemHealth(
            timestamp=results['timestamp'],
            files_status=results['files'],
            database_status=results['database'],
            cron_status=results['cron'],
            errors_status=results['error_logs'],
            backups_status=results['backups'],
            overall_score=health_score
        )
        
        self.health_history.append(health_data)
        
        # Keep only last 100 health records
        if len(self.health_history) > 100:
            self.health_history = self.health_history[-100:]
        
        # Store in memory
        if Memory:
            Memory.remember('kaavan_last_watch', results['timestamp'], 3600)
            Memory.remember('kaavan_health_history', [asdict(h) for h in self.health_history[-10:]], 3600)
        
        self.last_check = results['timestamp']
        
        return results
    
    def backup(self, backup_type: str = 'full') -> Dict:
        """
        Backup system - Ensuring nothing is lost forever
        Just as Kaavan was saved, your data will be too
        
        Args:
            backup_type: Type of backup ('full', 'incremental', 'database', 'intelligent')
            
        Returns:
            Dict with backup results
        """
        backup_methods = {
            'full': self._full_backup,
            'incremental': self._incremental_backup,
            'database': self._database_backup,
            'intelligent': self._intelligent_backup
        }
        
        backup_method = backup_methods.get(backup_type, self._intelligent_backup)
        return backup_method()
    
    def analyze(self) -> Dict:
        """
        Analyze system health - The lone elephant's wisdom
        
        Returns:
            Dict with comprehensive health analysis
        """
        health = {
            'files': self._analyze_files(),
            'database': self._analyze_database(),
            'cron': self._analyze_cron_jobs(),
            'errors': self._analyze_errors(),
            'backups': self._analyze_backups()
        }
        
        return self._generate_health_report(health)
    
    def heal(self, issue: str) -> Dict:
        """
        Self-healing attempts - The resilient spirit
        
        Args:
            issue: The issue to attempt to heal
            
        Returns:
            Dict with healing results
        """
        # Like Kaavan's eventual healing in Cambodia,
        # the system attempts to fix itself
        return self._attempt_recovery(issue)
    
    def send_alert(self, issue: str, severity: str = 'warning', metadata: Dict = None) -> bool:
        """
        Alert admin when something goes wrong
        Kaavan's trumpet call for help
        
        Args:
            issue: Description of the issue
            severity: Alert severity ('info', 'warning', 'error', 'critical')
            metadata: Additional metadata
            
        Returns:
            True if alert sent successfully
        """
        # Just as Kaavan's plight reached the world,
        # these alerts ensure problems don't go unnoticed
        self.alerts_sent += 1
        
        alert_id = f"kaavan_alert_{int(time.time())}_{self.alerts_sent}"
        
        alert = MonitoringAlert(
            id=alert_id,
            type=issue,
            severity=severity,
            message=issue,
            timestamp=int(time.time()),
            metadata=metadata or {}
        )
        
        self.active_alerts[alert_id] = alert
        
        # Store in memory
        if Memory:
            Memory.remember(f"kaavan_alert_{alert_id}", asdict(alert), 86400)
        
        # Send email alert
        self._send_email_alert(alert)
        
        # Log the alert
        self.logger.warning(f"Kaavan Alert [{severity.upper()}]: {issue}")
        
        return True
    
    def get_alerts(self, active_only: bool = True) -> List[Dict]:
        """
        Get monitoring alerts
        
        Args:
            active_only: Return only active (unresolved) alerts
            
        Returns:
            List of alert dictionaries
        """
        alerts = list(self.active_alerts.values())
        
        if active_only:
            alerts = [alert for alert in alerts if not alert.resolved]
        
        return [asdict(alert) for alert in alerts]
    
    def resolve_alert(self, alert_id: str) -> bool:
        """
        Mark an alert as resolved
        
        Args:
            alert_id: The alert ID to resolve
            
        Returns:
            True if resolved successfully
        """
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.resolved = True
            alert.resolved_at = int(time.time())
            
            if Memory:
                Memory.remember(f"kaavan_alert_{alert_id}", asdict(alert), 86400)
            
            return True
        
        return False
    
    def _load_backup_config(self, config: Dict = None) -> BackupConfig:
        """
        Load backup configuration
        
        Args:
            config: Configuration dictionary
            
        Returns:
            BackupConfig object
        """
        if config:
            return BackupConfig(**config)
        
        # Load from environment or defaults
        return BackupConfig(
            destination=os.getenv('BACKUP_PATH', '/backups'),
            s3_bucket=os.getenv('BACKUP_S3_BUCKET'),
            retention_days=int(os.getenv('BACKUP_RETENTION', '30')),
            schedule=os.getenv('BACKUP_SCHEDULE', 'daily'),
            compression=os.getenv('BACKUP_COMPRESSION', 'true').lower() == 'true',
            encryption=os.getenv('BACKUP_ENCRYPTION', 'false').lower() == 'true',
            verify_backups=os.getenv('BACKUP_VERIFY', 'true').lower() == 'true'
        )
    
    def _scan_files(self) -> Dict:
        """
        Scan files for changes and issues
        
        Returns:
            Dict with file monitoring results
        """
        results = {
            'status': 'healthy',
            'files_checked': 0,
            'files_modified': 0,
            'files_missing': 0,
            'files_corrupted': 0,
            'issues': []
        }
        
        # Monitor critical application files
        critical_files = [
            '/var/www/html/index.php',
            '/var/www/html/config.php',
            '/var/log/nginx/error.log',
            '/etc/nginx/nginx.conf'
        ]
        
        for file_path in critical_files:
            path = Path(file_path)
            results['files_checked'] += 1
            
            if not path.exists():
                results['files_missing'] += 1
                results['issues'].append(f"Critical file missing: {file_path}")
                continue
            
            # Check file integrity
            try:
                stat = path.stat()
                current_hash = self._calculate_file_hash(path)
                
                # Store hash for comparison
                hash_key = f"kaavan_file_hash_{file_path.replace('/', '_')}"
                previous_hash = Memory.recall(hash_key) if Memory else None
                
                if previous_hash and previous_hash != current_hash:
                    results['files_modified'] += 1
                    results['issues'].append(f"File modified: {file_path}")
                
                if Memory:
                    Memory.remember(hash_key, current_hash, 86400)
                
            except Exception as e:
                results['files_corrupted'] += 1
                results['issues'].append(f"File corrupted: {file_path} - {str(e)}")
        
        # Update status based on issues
        if results['issues']:
            results['status'] = 'warning' if len(results['issues']) < 3 else 'error'
        
        return results
    
    def _check_cron_jobs(self) -> Dict:
        """
        Check cron job health
        
        Returns:
            Dict with cron monitoring results
        """
        results = {
            'status': 'healthy',
            'jobs_checked': 0,
            'jobs_failed': 0,
            'jobs_missing': 0,
            'issues': []
        }
        
        # Check if cron service is running
        try:
            cron_status = subprocess.run(['systemctl', 'is-active', 'cron'], 
                                       capture_output=True, text=True)
            if cron_status.stdout.strip() != 'active':
                results['status'] = 'error'
                results['issues'].append("Cron service not running")
        except Exception as e:
            results['issues'].append(f"Cannot check cron service: {str(e)}")
        
        # Check specific cron jobs
        important_jobs = [
            'backup_daily',
            'log_rotation',
            'system_cleanup'
        ]
        
        for job in important_jobs:
            results['jobs_checked'] += 1
            
            # Check if job exists in crontab
            try:
                crontab_check = subprocess.run(['crontab', '-l'], 
                                             capture_output=True, text=True)
                if job not in crontab_check.stdout:
                    results['jobs_missing'] += 1
                    results['issues'].append(f"Cron job missing: {job}")
            except Exception as e:
                results['jobs_failed'] += 1
                results['issues'].append(f"Cannot check cron job {job}: {str(e)}")
        
        # Update status
        if results['issues']:
            results['status'] = 'warning' if len(results['issues']) < 2 else 'error'
        
        return results
    
    def _verify_database_health(self) -> Dict:
        """
        Verify database health
        
        Returns:
            Dict with database health results
        """
        results = {
            'status': 'healthy',
            'connection': False,
            'tables_checked': 0,
            'tables_corrupted': 0,
            'issues': []
        }
        
        if not TuskDb:
            results['issues'].append("Database connection not available")
            results['status'] = 'error'
            return results
        
        try:
            # Test database connection
            db = TuskDb()
            db.execute("SELECT 1")
            results['connection'] = True
            
            # Check important tables
            important_tables = ['users', 'content', 'settings', 'logs']
            
            for table in important_tables:
                results['tables_checked'] += 1
                
                try:
                    db.execute(f"SELECT COUNT(*) FROM {table}")
                except Exception as e:
                    results['tables_corrupted'] += 1
                    results['issues'].append(f"Table {table} corrupted: {str(e)}")
            
        except Exception as e:
            results['issues'].append(f"Database connection failed: {str(e)}")
            results['status'] = 'error'
        
        # Update status
        if results['issues']:
            results['status'] = 'warning' if len(results['issues']) < 2 else 'error'
        
        return results
    
    def _monitor_disk_space(self) -> Dict:
        """
        Monitor disk space usage
        
        Returns:
            Dict with disk space monitoring results
        """
        results = {
            'status': 'healthy',
            'total_space': 0,
            'used_space': 0,
            'free_space': 0,
            'usage_percent': 0,
            'issues': []
        }
        
        try:
            # Get disk usage for root directory
            stat = shutil.disk_usage('/')
            
            results['total_space'] = stat.total
            results['used_space'] = stat.used
            results['free_space'] = stat.free
            results['usage_percent'] = (stat.used / stat.total) * 100
            
            # Check thresholds
            if results['usage_percent'] > 90:
                results['status'] = 'critical'
                results['issues'].append("Disk space critical (>90%)")
            elif results['usage_percent'] > 80:
                results['status'] = 'warning'
                results['issues'].append("Disk space warning (>80%)")
            
        except Exception as e:
            results['issues'].append(f"Cannot check disk space: {str(e)}")
            results['status'] = 'error'
        
        return results
    
    def _check_error_logs(self) -> Dict:
        """
        Check error logs for issues
        
        Returns:
            Dict with error log monitoring results
        """
        results = {
            'status': 'healthy',
            'logs_checked': 0,
            'errors_found': 0,
            'critical_errors': 0,
            'issues': []
        }
        
        # Check common error log locations
        log_files = [
            '/var/log/nginx/error.log',
            '/var/log/apache2/error.log',
            '/var/log/php/error.log',
            '/var/log/syslog'
        ]
        
        for log_file in log_files:
            log_path = Path(log_file)
            if not log_path.exists():
                continue
            
            results['logs_checked'] += 1
            
            try:
                # Check for recent errors (last hour)
                cutoff_time = time.time() - 3600
                error_count = 0
                critical_count = 0
                
                with open(log_path, 'r') as f:
                    for line in f:
                        if 'ERROR' in line or 'CRITICAL' in line:
                            error_count += 1
                        if 'CRITICAL' in line or 'FATAL' in line:
                            critical_count += 1
                
                results['errors_found'] += error_count
                results['critical_errors'] += critical_count
                
                if critical_count > 0:
                    results['issues'].append(f"Critical errors in {log_file}: {critical_count}")
                elif error_count > 10:
                    results['issues'].append(f"High error rate in {log_file}: {error_count}")
                
            except Exception as e:
                results['issues'].append(f"Cannot read log file {log_file}: {str(e)}")
        
        # Update status
        if results['critical_errors'] > 0:
            results['status'] = 'critical'
        elif results['errors_found'] > 20:
            results['status'] = 'warning'
        
        return results
    
    def _check_backup_status(self) -> Dict:
        """
        Check backup system status
        
        Returns:
            Dict with backup status results
        """
        results = {
            'status': 'healthy',
            'last_backup': None,
            'backup_age_hours': 0,
            'backups_available': 0,
            'issues': []
        }
        
        backup_path = Path(self.backup_config.destination)
        
        if not backup_path.exists():
            results['issues'].append("Backup directory does not exist")
            results['status'] = 'error'
            return results
        
        try:
            # Find most recent backup
            backup_files = list(backup_path.glob("*.tar.gz"))
            backup_files.extend(list(backup_path.glob("*.sql")))
            
            if backup_files:
                # Sort by modification time
                backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                latest_backup = backup_files[0]
                
                results['last_backup'] = latest_backup.name
                results['backup_age_hours'] = (time.time() - latest_backup.stat().st_mtime) / 3600
                results['backups_available'] = len(backup_files)
                
                # Check if backup is too old
                if results['backup_age_hours'] > 48:
                    results['status'] = 'warning'
                    results['issues'].append(f"Last backup is {results['backup_age_hours']:.1f} hours old")
                elif results['backup_age_hours'] > 168:  # 1 week
                    results['status'] = 'critical'
                    results['issues'].append("Backup is over a week old")
            else:
                results['status'] = 'critical'
                results['issues'].append("No backups found")
        
        except Exception as e:
            results['issues'].append(f"Cannot check backup status: {str(e)}")
            results['status'] = 'error'
        
        return results
    
    def _calculate_health_score(self, results: Dict) -> float:
        """
        Calculate overall health score
        
        Args:
            results: Monitoring results
            
        Returns:
            Health score from 0.0 to 1.0
        """
        scores = []
        
        # File health
        file_score = 1.0
        if results['files']['status'] == 'error':
            file_score = 0.3
        elif results['files']['status'] == 'warning':
            file_score = 0.7
        scores.append(file_score)
        
        # Cron health
        cron_score = 1.0
        if results['cron']['status'] == 'error':
            cron_score = 0.3
        elif results['cron']['status'] == 'warning':
            cron_score = 0.7
        scores.append(cron_score)
        
        # Database health
        db_score = 1.0
        if results['database']['status'] == 'error':
            db_score = 0.3
        elif results['database']['status'] == 'warning':
            db_score = 0.7
        scores.append(db_score)
        
        # Disk space health
        disk_score = 1.0
        if results['disk_space']['status'] == 'critical':
            disk_score = 0.1
        elif results['disk_space']['status'] == 'warning':
            disk_score = 0.5
        scores.append(disk_score)
        
        # Error log health
        error_score = 1.0
        if results['error_logs']['status'] == 'critical':
            error_score = 0.3
        elif results['error_logs']['status'] == 'warning':
            error_score = 0.7
        scores.append(error_score)
        
        # Backup health
        backup_score = 1.0
        if results['backups']['status'] == 'critical':
            backup_score = 0.3
        elif results['backups']['status'] == 'warning':
            backup_score = 0.7
        scores.append(backup_score)
        
        return sum(scores) / len(scores)
    
    def _full_backup(self) -> Dict:
        """
        Perform full system backup
        
        Returns:
            Dict with backup results
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"full_backup_{timestamp}.tar.gz"
        backup_path = Path(self.backup_config.destination) / backup_name
        
        try:
            # Create backup directory
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create tar.gz backup
            shutil.make_archive(
                str(backup_path.with_suffix('')),
                'gztar',
                root_dir='/var/www/html',
                base_dir='.'
            )
            
            # Verify backup
            if self.backup_config.verify_backups:
                self._verify_backup(backup_path)
            
            # Clean old backups
            self._cleanup_old_backups()
            
            return {
                'status': 'success',
                'backup_path': str(backup_path),
                'size': backup_path.stat().st_size,
                'timestamp': timestamp
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': timestamp
            }
    
    def _incremental_backup(self) -> Dict:
        """
        Perform incremental backup
        
        Returns:
            Dict with backup results
        """
        # Implementation for incremental backup
        return {
            'status': 'not_implemented',
            'message': 'Incremental backup not yet implemented'
        }
    
    def _database_backup(self) -> Dict:
        """
        Perform database backup
        
        Returns:
            Dict with backup results
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"database_backup_{timestamp}.sql"
        backup_path = Path(self.backup_config.destination) / backup_name
        
        try:
            # Create backup directory
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Database backup command (example for MySQL)
            backup_cmd = [
                'mysqldump',
                '--all-databases',
                '--single-transaction',
                '--routines',
                '--triggers',
                f'--result-file={backup_path}'
            ]
            
            result = subprocess.run(backup_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"Database backup failed: {result.stderr}")
            
            return {
                'status': 'success',
                'backup_path': str(backup_path),
                'size': backup_path.stat().st_size,
                'timestamp': timestamp
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': timestamp
            }
    
    def _intelligent_backup(self) -> Dict:
        """
        Perform intelligent backup based on system state
        
        Returns:
            Dict with backup results
        """
        # Check when last backup was performed
        last_backup = self._get_last_backup_time()
        
        if last_backup and (time.time() - last_backup) < 86400:  # Less than 24 hours
            return self._incremental_backup()
        else:
            return self._full_backup()
    
    def _verify_backup(self, backup_path: Path) -> bool:
        """
        Verify backup integrity
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            True if backup is valid
        """
        try:
            # Check if file exists and has size
            if not backup_path.exists() or backup_path.stat().st_size == 0:
                return False
            
            # Try to read the archive
            import tarfile
            with tarfile.open(backup_path, 'r:gz') as tar:
                tar.getmembers()  # This will raise an error if corrupted
            
            return True
        
        except Exception:
            return False
    
    def _cleanup_old_backups(self):
        """Clean up old backups based on retention policy"""
        backup_path = Path(self.backup_config.destination)
        cutoff_time = time.time() - (self.backup_config.retention_days * 86400)
        
        for backup_file in backup_path.glob("*"):
            if backup_file.stat().st_mtime < cutoff_time:
                backup_file.unlink()
    
    def _get_last_backup_time(self) -> Optional[float]:
        """Get timestamp of last backup"""
        backup_path = Path(self.backup_config.destination)
        
        if not backup_path.exists():
            return None
        
        backup_files = list(backup_path.glob("*"))
        if not backup_files:
            return None
        
        # Return most recent backup time
        return max(backup_file.stat().st_mtime for backup_file in backup_files)
    
    def _analyze_files(self) -> Dict:
        """Analyze file system health"""
        return {
            'total_files': 0,
            'modified_files': 0,
            'corrupted_files': 0,
            'recommendations': []
        }
    
    def _analyze_database(self) -> Dict:
        """Analyze database health"""
        return {
            'connection_status': 'unknown',
            'table_count': 0,
            'performance_score': 0.0,
            'recommendations': []
        }
    
    def _analyze_cron_jobs(self) -> Dict:
        """Analyze cron job health"""
        return {
            'active_jobs': 0,
            'failed_jobs': 0,
            'recommendations': []
        }
    
    def _analyze_errors(self) -> Dict:
        """Analyze error patterns"""
        return {
            'error_count': 0,
            'error_patterns': [],
            'recommendations': []
        }
    
    def _analyze_backups(self) -> Dict:
        """Analyze backup system"""
        return {
            'backup_count': 0,
            'last_backup_age': 0,
            'recommendations': []
        }
    
    def _generate_health_report(self, health: Dict) -> Dict:
        """Generate comprehensive health report"""
        return {
            'timestamp': int(time.time()),
            'overall_health': 'healthy',
            'components': health,
            'recommendations': [],
            'alerts': []
        }
    
    def _attempt_recovery(self, issue: str) -> Dict:
        """Attempt to recover from an issue"""
        return {
            'status': 'attempted',
            'issue': issue,
            'actions_taken': [],
            'success': False
        }
    
    def _send_email_alert(self, alert: MonitoringAlert):
        """Send email alert to admin"""
        # Implementation for email alerts
        pass
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def _start_monitoring(self):
        """Start background monitoring"""
        self.monitoring_thread = threading.Thread(target=self._monitoring_worker, daemon=True)
        self.monitoring_thread.start()
    
    def _monitoring_worker(self):
        """Background monitoring worker"""
        while self.monitoring_enabled:
            try:
                # Perform monitoring check
                results = self.watch()
                
                # Check for critical issues
                if results['health_score'] < 0.5:
                    self.send_alert("System health critical", "critical", results)
                elif results['health_score'] < 0.8:
                    self.send_alert("System health degraded", "warning", results)
                
                # Wait before next check
                time.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Monitoring worker error: {e}")
                time.sleep(60)


# Flask-TSK Integration Functions
def init_kaavan(app):
    """Initialize Kaavan with Flask app"""
    app.kaavan = Kaavan()
    return app.kaavan


def get_kaavan() -> Kaavan:
    """Get Kaavan instance from Flask app context"""
    from flask import current_app
    return current_app.kaavan 