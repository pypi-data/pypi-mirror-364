"""
TuskPHP Peanuts - The Configuration & Performance Elephant (Python Edition)
==========================================================================

🥜 BACKSTORY: Peanuts - The Performance Elephant
-----------------------------------------------
Peanuts is the elephant who manages the configuration and performance
of the entire TuskPHP ecosystem. Like a wise elephant who knows exactly
how much food to eat and when to conserve energy, Peanuts monitors system
performance and adapts the configuration accordingly.

WHY THIS NAME: Just as elephants love peanuts and know how to manage
their energy efficiently, this system manages configuration "peanuts"
and optimizes performance based on system conditions.

FEATURES:
- Encrypted configuration management (.pnt, peanu.tsk, .peanuts files)
- Adaptive performance optimization
- Four performance modes: Feast, Balanced, Diet, Survival
- Real-time performance monitoring
- Automatic resource management
- Elephant service coordination
- Binary and source configuration formats

@package TuskPHP\Elephants
@author  TuskPHP Team
@since   1.0.0
"""

import os
import json
import time
import gzip
import hashlib
import configparser
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import threading
import logging

# Flask-TSK imports
try:
    from tsk_flask.memory import Memory
    from tsk_flask.database import TuskDb
except ImportError:
    # Fallback for standalone usage
    Memory = None
    TuskDb = None


class PerformanceMode(Enum):
    """Performance modes"""
    FEAST = 'feast'      # High performance, all features enabled
    BALANCED = 'balanced'  # Standard operation
    DIET = 'diet'        # Conservation mode, reduced features
    SURVIVAL = 'survival'  # Emergency mode, minimal features only


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    response_times: List[float]
    memory_usage: List[int]
    db_query_times: List[float]
    error_rate: float
    concurrent_users: int
    cache_hit_rate: float
    last_updated: int
    performance_score: float


class Peanuts:
    """Peanuts - The Configuration & Performance Elephant (Python Edition)"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __init__(self):
        self.metrics = PerformanceMetrics(
            response_times=[],
            memory_usage=[],
            db_query_times=[],
            error_rate=0.0,
            concurrent_users=0,
            cache_hit_rate=0.0,
            last_updated=int(time.time()),
            performance_score=1.0
        )
        self.performance_mode = PerformanceMode.BALANCED
        self.last_optimization = 0
        self.reward_threshold = 0.8
        self.diet_threshold = 0.4
        self.config = {}
        
        # Encrypted environment handling
        self.env_cache = {}
        self.peanuts_file = None
        self.encryption_key = None
        
        # Setup logging
        self.logger = logging.getLogger('peanuts')
        self.logger.setLevel(logging.INFO)
        
        self.initialize_metrics()
        self.start_performance_monitoring()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def get_instance(cls) -> 'Peanuts':
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = Peanuts()
        return cls._instance
    
    def initialize_metrics(self):
        """Initialize performance metrics"""
        self.metrics = PerformanceMetrics(
            response_times=[],
            memory_usage=[],
            db_query_times=[],
            error_rate=0.0,
            concurrent_users=0,
            cache_hit_rate=0.0,
            last_updated=int(time.time()),
            performance_score=1.0
        )
    
    def start_performance_monitoring(self):
        """Start performance monitoring"""
        # In Python, we'll use a different approach for request monitoring
        # This would typically be integrated with Flask middleware
        self.logger.info("🥜 Performance monitoring started")
    
    def give_peanuts(self, reason: str = 'good_performance'):
        """Give performance rewards"""
        current_score = self.calculate_performance_score()
        if current_score >= self.reward_threshold:
            self.enable_performance_rewards(reason)
            self.log_peanut_reward(reason, current_score)
    
    def start_diet(self, reason: str = 'poor_performance'):
        """Start conservation mode"""
        current_score = self.calculate_performance_score()
        if current_score <= self.diet_threshold:
            self.enable_conservation_mode(reason)
            self.log_diet_mode(reason, current_score)
    
    def calculate_performance_score(self) -> float:
        """Calculate overall performance score"""
        factors = {
            'response_time': self.score_response_time(),
            'memory_usage': self.score_memory_usage(),
            'error_rate': self.score_error_rate(),
            'db_performance': self.score_database_performance(),
            'cache_efficiency': self.score_cache_efficiency()
        }
        
        # Weighted average
        weights = {
            'response_time': 0.3,
            'memory_usage': 0.2,
            'error_rate': 0.2,
            'db_performance': 0.2,
            'cache_efficiency': 0.1
        }
        
        score = sum(factors[factor] * weights[factor] for factor in factors)
        self.metrics.performance_score = score
        return score
    
    def adaptive_optimize(self):
        """Adaptive performance optimization"""
        score = self.calculate_performance_score()
        current_mode = self.performance_mode
        
        # Determine optimal mode based on performance score
        if score >= 0.9:
            new_mode = PerformanceMode.FEAST
        elif score >= 0.7:
            new_mode = PerformanceMode.BALANCED
        elif score >= 0.4:
            new_mode = PerformanceMode.DIET
        else:
            new_mode = PerformanceMode.SURVIVAL
        
        # Only change mode if necessary
        if new_mode != current_mode:
            self.switch_performance_mode(new_mode, score)
        
        # Apply mode-specific optimizations
        self.apply_mode_optimizations(new_mode)
    
    def switch_performance_mode(self, mode: PerformanceMode, score: float):
        """Switch performance mode"""
        old_mode = self.performance_mode
        self.performance_mode = mode
        
        if mode == PerformanceMode.FEAST:
            self.enable_feast_mode()
        elif mode == PerformanceMode.BALANCED:
            self.enable_balanced_mode()
        elif mode == PerformanceMode.DIET:
            self.enable_diet_mode()
        elif mode == PerformanceMode.SURVIVAL:
            self.enable_survival_mode()
        
        self.log_mode_switch(old_mode, mode, score)
    
    def enable_feast_mode(self):
        """Enable feast mode (high performance)"""
        # Enable aggressive caching
        if Memory:
            Memory.set_default_ttl(7200)  # 2 hours
            Memory.enable_aggressive_caching(True)
        
        # Enable parallel processing
        # In Python, this would involve thread pool configuration
        
        # Optimize database connections
        if TuskDb:
            TuskDb.enable_connection_pooling(True)
            TuskDb.set_query_cache(True)
        
        # Enable all elephant services
        self.enable_all_elephant_services()
    
    def enable_diet_mode(self):
        """Enable diet mode (conservation)"""
        # Reduce cache TTL
        if Memory:
            Memory.set_default_ttl(300)  # 5 minutes
            Memory.enable_aggressive_caching(False)
        
        # Limit execution time
        # In Python, this would involve signal handlers or threading
        
        # Optimize database for conservation
        if TuskDb:
            TuskDb.enable_connection_pooling(False)
            TuskDb.limit_concurrent_queries(5)
        
        # Disable non-essential elephant services
        self.disable_non_essential_services()
    
    def enable_survival_mode(self):
        """Enable survival mode (emergency)"""
        # Minimal caching
        if Memory:
            Memory.set_default_ttl(60)  # 1 minute
            Memory.enable_aggressive_caching(False)
        
        # Strict execution limits
        # In Python, this would involve resource limits
        
        # Emergency database settings
        if TuskDb:
            TuskDb.enable_emergency_mode(True)
            TuskDb.limit_concurrent_queries(2)
        
        # Only essential services
        self.enable_only_essential_services()
    
    def enable_balanced_mode(self):
        """Enable balanced mode (standard)"""
        # Reset to balanced defaults
        if Memory:
            Memory.enable_aggressive_caching(False)
            Memory.set_default_ttl(1800)  # 30 minutes
        
        # Standard database settings
        if TuskDb:
            TuskDb.enable_connection_pooling(True)
            TuskDb.set_query_cache(True)
            TuskDb.set_max_connections(10)
        
        # Resume background jobs if paused
        if Memory:
            Memory.forget('horton_paused')
        
        self.logger.info("⚖️ Balanced mode activated")
    
    def capture_request_metrics(self, response_time: float = None, memory_usage: int = None):
        """Capture request metrics"""
        if response_time is None:
            response_time = 0.1  # Default
        
        if memory_usage is None:
            memory_usage = 0  # Default
        
        # Store metrics
        self.metrics.response_times.append(response_time)
        self.metrics.memory_usage.append(memory_usage)
        self.metrics.last_updated = int(time.time())
        
        # Keep only last 100 entries
        if len(self.metrics.response_times) > 100:
            self.metrics.response_times = self.metrics.response_times[-100:]
            self.metrics.memory_usage = self.metrics.memory_usage[-100:]
        
        # Trigger adaptive optimization every 10 requests
        if len(self.metrics.response_times) % 10 == 0:
            self.adaptive_optimize()
    
    def get_performance_status(self) -> Dict[str, Any]:
        """Get current performance status"""
        return {
            'mode': self.performance_mode.value,
            'score': self.calculate_performance_score(),
            'metrics': asdict(self.metrics),
            'avg_response_time': self.get_average_response_time(),
            'avg_memory_usage': self.get_average_memory_usage(),
            'recommendations': self.get_optimization_recommendations()
        }
    
    # Configuration Management Methods
    @staticmethod
    def load_peanuts_env(file_path: str = None) -> bool:
        """Load encrypted .peanuts environment"""
        instance = Peanuts.get_instance()
        
        if not file_path:
            possible_paths = [
                Path(__file__).parent.parent.parent / 'config' / 'tusk' / '.peanuts',
                Path(__file__).parent.parent.parent / '.peanuts',
                Path(__file__).parent.parent.parent.parent / '.peanuts',
                Path(__file__).parent.parent.parent.parent.parent / '.peanuts',
                Path.cwd() / '.peanuts'
            ]
            
            for path in possible_paths:
                if path.exists():
                    file_path = str(path)
                    break
        
        if not file_path or not Path(file_path).exists():
            return False
        
        instance.peanuts_file = file_path
        
        try:
            with open(file_path, 'rb') as f:
                encrypted_content = f.read()
            
            decrypted_content = instance.decrypt_peanuts(encrypted_content)
            if decrypted_content:
                instance.parse_peanuts_env(decrypted_content)
                return True
        except Exception as e:
            instance.logger.error(f"🥜 Failed to load .peanuts file: {e}")
        
        return False
    
    @staticmethod
    def save_peanuts_env(env_vars: Dict[str, Any], file_path: str = None) -> bool:
        """Save encrypted .peanuts environment"""
        instance = Peanuts.get_instance()
        
        if not file_path:
            file_path = instance.peanuts_file or str(Path.cwd() / '.peanuts')
        
        try:
            content = instance.generate_peanuts_content(env_vars)
            encrypted_content = instance.encrypt_peanuts(content)
            
            with open(file_path, 'wb') as f:
                f.write(encrypted_content)
            
            instance.peanuts_file = file_path
            instance.env_cache.update(env_vars)
            return True
        except Exception as e:
            instance.logger.error(f"🥜 Failed to save .peanuts file: {e}")
        
        return False
    
    @staticmethod
    def get_peanuts_env(key: str, default: Any = None) -> Any:
        """Get environment variable from .peanuts"""
        instance = Peanuts.get_instance()
        
        # First try cache
        if key in instance.env_cache:
            return instance.env_cache[key]
        
        # Try to load if not already loaded
        if not instance.env_cache and Peanuts.load_peanuts_env():
            return instance.env_cache.get(key, default)
        
        return default
    
    @staticmethod
    def set_peanuts_env(key: str, value: Any) -> bool:
        """Set environment variable in .peanuts"""
        instance = Peanuts.get_instance()
        instance.env_cache[key] = value
        
        # If we have a file loaded, update it
        if instance.peanuts_file:
            return Peanuts.save_peanuts_env(instance.env_cache)
        
        return True  # Cached for now
    
    def encrypt_peanuts(self, content: str) -> bytes:
        """Encrypt peanuts content"""
        key = self.get_peanuts_encryption_key()
        
        # Simple encryption using XOR (in production, use proper encryption)
        content_bytes = content.encode('utf-8')
        key_bytes = key.encode('utf-8')[:len(content_bytes)]
        
        encrypted = bytes(a ^ b for a, b in zip(content_bytes, key_bytes))
        
        # Add header and compress
        header = b'PNUT' + len(encrypted).to_bytes(4, 'big')
        compressed = gzip.compress(encrypted, 9)
        
        return header + compressed
    
    def decrypt_peanuts(self, encrypted_content: bytes) -> Optional[str]:
        """Decrypt peanuts content"""
        try:
            # Check header
            if len(encrypted_content) < 8 or encrypted_content[:4] != b'PNUT':
                return None
            
            # Extract length and data
            length = int.from_bytes(encrypted_content[4:8], 'big')
            compressed_data = encrypted_content[8:]
            
            # Decompress
            encrypted = gzip.decompress(compressed_data)
            
            # Decrypt
            key = self.get_peanuts_encryption_key()
            key_bytes = key.encode('utf-8')[:len(encrypted)]
            
            decrypted = bytes(a ^ b for a, b in zip(encrypted, key_bytes))
            return decrypted.decode('utf-8')
        except Exception as e:
            self.logger.error(f"Failed to decrypt peanuts: {e}")
            return None
    
    def get_peanuts_encryption_key(self) -> str:
        """Get encryption key for peanuts"""
        if self.encryption_key:
            return self.encryption_key
        
        # Try various sources for the key
        key_sources = [
            os.environ.get('PEANUTS_KEY'),
            os.uname().sysname + __file__ + 'PeanutsAreDelicious'
        ]
        
        for source in key_sources:
            if source:
                self.encryption_key = hashlib.sha256(source.encode()).hexdigest()
                return self.encryption_key
        
        # Fallback key
        self.encryption_key = hashlib.sha256('ElephantsPeanutsSecret'.encode()).hexdigest()
        return self.encryption_key
    
    def parse_peanuts_env(self, content: str):
        """Parse peanuts environment content"""
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Parse KEY=VALUE format
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Remove quotes if present
                if len(value) >= 2 and value[0] in ['"', "'"] and value[-1] == value[0]:
                    value = value[1:-1]
                
                self.env_cache[key] = value
                
                # Also set as environment variable
                os.environ[key] = value
    
    def generate_peanuts_content(self, env_vars: Dict[str, Any]) -> str:
        """Generate peanuts content from environment variables"""
        content = "# 🥜 TuskPHP Encrypted Environment Configuration\n"
        content += "# Even elephants have trouble finding encrypted peanuts!\n"
        content += f"# Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        for key, value in env_vars.items():
            # Escape values that contain special characters
            if isinstance(value, str) and (' ' in value or '"' in value):
                value = f'"{value.replace('"', '\\"')}"'
            content += f"{key}={value}\n"
        
        return content
    
    # Configuration File Methods
    @staticmethod
    def eat(config_file: str = None) -> bool:
        """Load configuration file (priority: .pnt → peanu.tsk → .peanuts → .shell)"""
        instance = Peanuts.get_instance()
        
        if not config_file:
            # Check priority order
            for filename in ['.pnt', 'peanu.tsk', '.peanuts', '.shell']:
                if Path(filename).exists():
                    config_file = filename
                    break
        
        if not config_file:
            instance.logger.error("🥜 No configuration file found - run 'tusk init'")
            return False
        
        # Try binary files first
        if Peanuts.is_binary_file(config_file):
            return instance.crack_binary(config_file)
        
        # Try source files
        if config_file.endswith('.tsk') or 'peanu.tsk' in config_file:
            return instance.load_source(config_file)
        
        # Legacy fallback
        if config_file.endswith('.shell'):
            return instance.crack_shell(config_file)
        
        return False
    
    def crack_binary(self, binary_file: str) -> bool:
        """Crack binary configuration file"""
        try:
            with open(binary_file, 'rb') as f:
                data = f.read()
            
            # Check magic header
            if len(data) < 8 or data[:4] != b'PNUT':
                self.logger.error(f"Invalid binary magic header in {binary_file}")
                return False
            
            # Extract configuration data
            length = int.from_bytes(data[4:8], 'big')
            config_data = data[8:8+length]
            
            # Decompress
            decompressed = gzip.decompress(config_data)
            
            # Parse as JSON
            self.config = json.loads(decompressed.decode('utf-8'))
            self.apply_configuration()
            return True
            
        except Exception as e:
            self.logger.error(f"Error cracking binary file {binary_file}: {e}")
            return False
    
    def load_source(self, source_file: str) -> bool:
        """Load source configuration file"""
        try:
            with open(source_file, 'r') as f:
                content = f.read()
            
            # Parse as INI format
            config = configparser.ConfigParser()
            config.read_string(content)
            
            # Convert to dictionary
            self.config = {}
            for section in config.sections():
                self.config[section] = dict(config[section])
            
            self.apply_configuration()
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading source file {source_file}: {e}")
            return False
    
    def crack_shell(self, shell_file: str) -> bool:
        """Crack shell configuration file (legacy)"""
        try:
            with open(shell_file, 'rb') as f:
                data = f.read()
            
            # Check magic header
            if len(data) < 8 or data[:4] != b'SHEL':
                self.logger.error("Invalid .shell magic header")
                return False
            
            # Extract configuration data
            length = int.from_bytes(data[4:8], 'big')
            config_data = data[8:8+length]
            
            # Decompress
            decompressed = gzip.decompress(config_data)
            
            # Parse as JSON
            self.config = json.loads(decompressed.decode('utf-8'))
            self.apply_configuration()
            return True
            
        except Exception as e:
            self.logger.error(f"Error cracking .shell: {e}")
            return False
    
    def apply_configuration(self):
        """Apply configuration to environment"""
        # Set environment variables
        for section, values in self.config.items():
            if isinstance(values, dict):
                for key, value in values.items():
                    env_key = f"{section.upper()}_{key.upper()}"
                    os.environ[env_key] = str(value)
            else:
                env_key = section.upper()
                os.environ[env_key] = str(values)
        
        # Set specific constants for TuskPHP
        self.set_tusk_constants()
    
    def set_tusk_constants(self):
        """Set TuskPHP-specific constants"""
        mappings = {
            'database.host': 'DB_HOST',
            'database.name': 'DB_NAME',
            'database.user': 'DB_USER',
            'database.password': 'DB_PASS',
            'database.port': 'DB_PORT',
            'app.name': 'PROJECT_NAME',
            'app.url': 'APP_URL',
            'app.env': 'APP_ENV',
            'app.debug': 'APP_DEBUG',
            'mail.host': 'SMTP_SERVER',
            'mail.port': 'SMTP_PORT',
            'mail.username': 'SMTP_USERNAME',
            'mail.password': 'SMTP_PASSWORD',
            'mail.from': 'MAIL_DEFAULT_SENDER',
            'tusk.version': 'TUSK_VERSION',
            'tusk.elder_path': 'ELDER_PATH',
            'tusk.api_key': 'TUSK_API_KEY',
        }
        
        for config_path, constant_name in mappings.items():
            value = self.get_config_value(config_path)
            if value is not None:
                # In Python, we'd typically use environment variables instead of constants
                os.environ[constant_name] = str(value)
    
    def get_config_value(self, path: str, default: Any = None) -> Any:
        """Get configuration value by path"""
        keys = path.split('.')
        value = self.config
        
        for key in keys:
            if not isinstance(value, dict) or key not in value:
                return default
            value = value[key]
        
        return value
    
    @staticmethod
    def compile(source_file: str = 'peanu.tsk', output_file: str = None) -> bool:
        """Compile source configuration to binary format"""
        if not output_file:
            output_file = '.pnt' if 'peanu.tsk' in source_file else source_file.replace('.tsk', '.pnt')
        
        instance = Peanuts.get_instance()
        if not instance.load_source(source_file):
            return False
        
        try:
            # Compress config for binary format
            config_json = json.dumps(instance.config, separators=(',', ':'))
            compressed = gzip.compress(config_json.encode('utf-8'), 9)
            
            # Create binary header
            header = b'PNUT' + len(compressed).to_bytes(4, 'big')
            
            # Write binary file
            with open(output_file, 'wb') as f:
                f.write(header + compressed)
            
            # Make it read-only for security
            os.chmod(output_file, 0o644)
            return True
            
        except Exception as e:
            instance.logger.error(f"Error compiling to binary format: {e}")
        
        return False
    
    @staticmethod
    def shell(source_file: str = '.peanuts', output_file: str = None) -> bool:
        """Compile to shell format (legacy)"""
        if not output_file:
            output_file = source_file.replace('.peanuts', '.shell')
        
        instance = Peanuts.get_instance()
        if not instance.load_source(source_file):
            return False
        
        try:
            # Compress config for shell format
            config_json = json.dumps(instance.config, separators=(',', ':'))
            compressed = gzip.compress(config_json.encode('utf-8'), 9)
            
            # Create shell header
            header = b'SHEL' + len(compressed).to_bytes(4, 'big')
            
            # Write shell file
            with open(output_file, 'wb') as f:
                f.write(header + compressed)
            
            # Make it read-only for security
            os.chmod(output_file, 0o644)
            return True
            
        except Exception as e:
            instance.logger.error(f"Error shelling .peanuts: {e}")
        
        return False
    
    @staticmethod
    def is_binary_file(file_path: str) -> bool:
        """Check if file is binary format"""
        if not Path(file_path).exists():
            return False
        
        try:
            with open(file_path, 'rb') as f:
                magic = f.read(4)
            
            return magic in [b'PNUT', b'SHEL']
        except Exception:
            return False
    
    # Performance scoring methods
    def score_response_time(self) -> float:
        """Score response time performance"""
        if not self.metrics.response_times:
            return 1.0
        
        avg_time = sum(self.metrics.response_times) / len(self.metrics.response_times)
        
        # Score based on response time (lower is better)
        if avg_time <= 0.1:
            return 1.0  # Excellent
        elif avg_time <= 0.5:
            return 0.8  # Good
        elif avg_time <= 1.0:
            return 0.6  # Acceptable
        elif avg_time <= 2.0:
            return 0.4  # Poor
        else:
            return 0.2  # Very poor
    
    def score_memory_usage(self) -> float:
        """Score memory usage performance"""
        if not self.metrics.memory_usage:
            return 1.0
        
        avg_memory = sum(self.metrics.memory_usage) / len(self.metrics.memory_usage)
        
        # Simple memory scoring (in production, check actual limits)
        if avg_memory < 50 * 1024 * 1024:  # 50MB
            return 1.0
        elif avg_memory < 100 * 1024 * 1024:  # 100MB
            return 0.8
        elif avg_memory < 200 * 1024 * 1024:  # 200MB
            return 0.6
        elif avg_memory < 500 * 1024 * 1024:  # 500MB
            return 0.4
        else:
            return 0.2
    
    def score_error_rate(self) -> float:
        """Score error rate performance"""
        # Track errors over the last 100 requests
        error_count = Memory.recall('peanuts_error_count') if Memory else 0
        total_requests = len(self.metrics.response_times)
        
        if total_requests == 0:
            return 1.0  # No requests yet, assume perfect
        
        # Calculate error rate
        error_rate = error_count / total_requests
        
        # Convert to score (inverse relationship)
        if error_rate <= 0.01:
            return 1.0  # Less than 1% errors = perfect
        elif error_rate <= 0.05:
            return 0.8  # Less than 5% = good
        elif error_rate <= 0.10:
            return 0.6  # Less than 10% = acceptable
        elif error_rate <= 0.20:
            return 0.4  # Less than 20% = poor
        else:
            return 0.2  # More than 20% = critical
    
    def score_database_performance(self) -> float:
        """Score database performance"""
        if not self.metrics.db_query_times:
            return 0.8  # Assume good performance
        
        avg_query_time = sum(self.metrics.db_query_times) / len(self.metrics.db_query_times)
        
        # Score based on average query time (in milliseconds)
        if avg_query_time <= 10:
            return 1.0  # Excellent (< 10ms)
        elif avg_query_time <= 50:
            return 0.8  # Good (< 50ms)
        elif avg_query_time <= 100:
            return 0.6  # Acceptable (< 100ms)
        elif avg_query_time <= 500:
            return 0.4  # Poor (< 500ms)
        else:
            return 0.2  # Very poor (> 500ms)
    
    def score_cache_efficiency(self) -> float:
        """Score cache efficiency"""
        # Get cache statistics from Memory
        cache_hits = Memory.recall('peanuts_cache_hits') if Memory else 0
        cache_misses = Memory.recall('peanuts_cache_misses') if Memory else 0
        total_attempts = cache_hits + cache_misses
        
        if total_attempts == 0:
            return 0.8  # No cache usage yet, assume good
        
        hit_rate = cache_hits / total_attempts
        self.metrics.cache_hit_rate = hit_rate
        
        # Score based on cache hit rate
        if hit_rate >= 0.90:
            return 1.0  # 90%+ hit rate = excellent
        elif hit_rate >= 0.75:
            return 0.8  # 75%+ = good
        elif hit_rate >= 0.60:
            return 0.6  # 60%+ = acceptable
        elif hit_rate >= 0.40:
            return 0.4  # 40%+ = poor
        else:
            return 0.2  # Less than 40% = needs improvement
    
    # Helper methods
    def get_average_response_time(self) -> float:
        """Get average response time"""
        if not self.metrics.response_times:
            return 0.0
        return sum(self.metrics.response_times) / len(self.metrics.response_times)
    
    def get_average_memory_usage(self) -> int:
        """Get average memory usage"""
        if not self.metrics.memory_usage:
            return 0
        return int(sum(self.metrics.memory_usage) / len(self.metrics.memory_usage))
    
    def get_optimization_recommendations(self) -> List[str]:
        """Get optimization recommendations"""
        recommendations = []
        score = self.calculate_performance_score()
        
        if score < 0.6:
            recommendations.append("Consider enabling caching for database queries")
            recommendations.append("Review slow database queries and add indexes")
            recommendations.append("Optimize image sizes and enable compression")
        
        if self.get_average_response_time() > 1.0:
            recommendations.append("Response times are high - consider code optimization")
        
        return recommendations
    
    def log_peanut_reward(self, reason: str, score: float):
        """Log peanut reward"""
        self.logger.info(f"🥜 Peanuts reward given! Reason: {reason}, Score: {score:.3f}")
    
    def log_diet_mode(self, reason: str, score: float):
        """Log diet mode activation"""
        self.logger.info(f"🥗 Diet mode activated. Reason: {reason}, Score: {score:.3f}")
    
    def log_mode_switch(self, old_mode: PerformanceMode, new_mode: PerformanceMode, score: float):
        """Log performance mode switch"""
        self.logger.info(f"🐘 Performance mode switch: {old_mode.value} → {new_mode.value} (Score: {score:.3f})")
    
    # Elephant service management
    def enable_all_elephant_services(self):
        """Enable all elephant services for feast mode"""
        elephant_services = {
            'Satao': {'security_monitoring': True, 'threat_detection': True},
            'Horton': {'job_processing': True, 'async_jobs': True},
            'Jumbo': {'large_uploads': True, 'chunked_processing': True},
            'Tantor': {'websocket': True, 'realtime_updates': True},
            'Heffalump': {'search_indexing': True, 'fuzzy_search': True},
            'Koshik': {'audio_processing': True, 'speech_synthesis': True},
            'Happy': {'image_processing': True, 'filters': True},
            'Tai': {'video_embedding': True, 'streaming': True},
            'Elmer': {'theme_generation': True, 'dynamic_styling': True},
            'Babar': {'cms_features': True, 'content_management': True},
            'Dumbo': {'http_client': True, 'parallel_requests': True},
            'Stampy': {'app_installation': True, 'package_management': True},
            'Kaavan': {'monitoring': True, 'analytics': True, 'backups': True}
        }
        
        if Memory:
            for elephant, features in elephant_services.items():
                for feature, enabled in features.items():
                    Memory.remember(f"elephant_{elephant}_{feature}", enabled, 7200)
            
            Memory.remember('all_elephants_active', True, 7200)
        
        self.logger.info("🐘 All elephant services enabled for FEAST mode")
    
    def disable_non_essential_services(self):
        """Disable non-essential services for diet mode"""
        # Essential services that remain active
        essential_services = {
            'Satao': {'security_monitoring': True},
            'Memory': {'basic_caching': True},
            'TuskDb': {'database_access': True},
            'Herd': {'authentication': True}
        }
        
        # Non-essential services to disable
        non_essential_services = {
            'Horton': {'async_jobs': False},
            'Jumbo': {'large_uploads': False},
            'Tantor': {'websocket': False},
            'Heffalump': {'search_indexing': False},
            'Koshik': {'audio_processing': False},
            'Happy': {'image_processing': False},
            'Tai': {'video_embedding': False},
            'Elmer': {'theme_generation': False},
            'Stampy': {'app_installation': False},
            'Kaavan': {'backups': False}
        }
        
        if Memory:
            # Apply essential services
            for elephant, features in essential_services.items():
                for feature, enabled in features.items():
                    Memory.remember(f"elephant_{elephant}_{feature}", enabled, 1800)
            
            # Disable non-essential services
            for elephant, features in non_essential_services.items():
                for feature, enabled in features.items():
                    Memory.remember(f"elephant_{elephant}_{feature}", enabled, 1800)
            
            Memory.remember('horton_paused', True, 1800)
        
        self.logger.info("🥗 Non-essential elephant services disabled for DIET mode")
    
    def enable_only_essential_services(self):
        """Enable only essential services for survival mode"""
        # Only the most critical services
        critical_services = {
            'Satao': {'basic_security': True},
            'Memory': {'emergency_cache': True},
            'TuskDb': {'read_only': True},
            'Herd': {'basic_auth': True}
        }
        
        # Disable ALL non-critical elephants
        all_elephants = [
            'Horton', 'Jumbo', 'Tantor', 'Heffalump', 'Koshik',
            'Happy', 'Tai', 'Elmer', 'Babar', 'Dumbo', 'Stampy', 'Kaavan'
        ]
        
        if Memory:
            for elephant in all_elephants:
                Memory.remember(f"elephant_{elephant}_disabled", True, 300)
            
            # Apply critical services only
            for elephant, features in critical_services.items():
                for feature, enabled in features.items():
                    Memory.remember(f"elephant_{elephant}_{feature}", enabled, 300)
            
            Memory.remember('emergency_mode_active', True, 300)
            Memory.remember('read_only_mode', True, 300)
        
        self.logger.info("🚨 SURVIVAL MODE: Only critical elephant services active")
    
    def apply_mode_optimizations(self, mode: PerformanceMode):
        """Apply mode-specific optimizations"""
        if mode == PerformanceMode.FEAST:
            self.enable_async_processing()
            self.enable_output_compression()
            self.optimize_autoloading()
        elif mode == PerformanceMode.BALANCED:
            self.enable_output_compression()
            self.optimize_autoloading()
        elif mode == PerformanceMode.DIET:
            self.disable_non_essential_autoloading()
            self.limit_output_buffering()
        elif mode == PerformanceMode.SURVIVAL:
            self.disable_all_non_critical()
            self.enable_emergency_mode()
    
    def enable_async_processing(self):
        """Enable async processing features"""
        if Memory:
            Memory.remember('peanuts_async_enabled', True)
    
    def enable_output_compression(self):
        """Enable output compression"""
        if Memory:
            Memory.remember('peanuts_compression_enabled', True)
    
    def optimize_autoloading(self):
        """Optimize autoloading"""
        if Memory:
            Memory.remember('peanuts_autoload_optimized', True)
    
    def disable_non_essential_autoloading(self):
        """Disable non-essential autoloading"""
        if Memory:
            Memory.remember('peanuts_minimal_autoload', True)
    
    def limit_output_buffering(self):
        """Limit output buffering"""
        if Memory:
            Memory.remember('peanuts_limited_buffering', True)
    
    def disable_all_non_critical(self):
        """Disable all non-critical features"""
        if Memory:
            Memory.remember('peanuts_critical_only', True)
    
    def enable_emergency_mode(self):
        """Enable emergency mode"""
        if Memory:
            Memory.remember('peanuts_emergency', True, 300)
        
        self.logger.error("🚨 PEANUTS EMERGENCY MODE ACTIVATED")
    
    def enable_performance_rewards(self, reason: str):
        """Enable performance rewards"""
        self.logger.info(f"🥜 Performance reward enabled: {reason}")
        
        if Memory:
            Memory.remember('peanuts_rewards_active', {
                'reason': reason,
                'enabled_at': int(time.time()),
                'features': ['aggressive_caching', 'connection_pooling', 'extended_execution']
            }, 3600)
    
    def enable_conservation_mode(self, reason: str):
        """Enable conservation mode"""
        self.logger.info(f"🥗 Conservation mode enabled: {reason}")
        
        if Memory:
            Memory.remember('peanuts_conservation_active', {
                'reason': reason,
                'enabled_at': int(time.time()),
                'restrictions': ['limited_memory', 'no_pooling', 'jobs_paused']
            }, 1800)
    
    # Configuration methods
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        return self.config.copy()
    
    def set_config(self, path: str, value: Any):
        """Set configuration value"""
        keys = path.split('.')
        config = self.config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
    
    # Cache management methods
    @staticmethod
    def should_use_cache(route: Dict[str, str]) -> bool:
        """Determine if caching should be used based on route and performance mode"""
        instance = Peanuts.get_instance()
        
        # Never cache in survival mode
        if instance.performance_mode == PerformanceMode.SURVIVAL:
            return False
        
        # Check if route contains admin or dynamic elements
        h1 = route.get('h1', '')
        h2 = route.get('h2', '')
        
        # Don't cache admin pages, API endpoints, or dynamic content
        if h1 in ['admin', 'api', 'cron', 'logout']:
            return False
        
        # Don't cache pages with query parameters (likely dynamic)
        # In Python, this would be checked differently
        
        return True
    
    @staticmethod
    def get_cache_ttl(h1: str = '') -> int:
        """Get cache TTL based on current performance mode and content type"""
        instance = Peanuts.get_instance()
        
        # Base TTL by performance mode
        if instance.performance_mode == PerformanceMode.FEAST:
            base_ttl = 7200  # 2 hours
        elif instance.performance_mode == PerformanceMode.BALANCED:
            base_ttl = 1800  # 30 minutes
        elif instance.performance_mode == PerformanceMode.DIET:
            base_ttl = 300   # 5 minutes
        elif instance.performance_mode == PerformanceMode.SURVIVAL:
            base_ttl = 60    # 1 minute
        else:
            base_ttl = 1800  # 30 minutes default
        
        # Adjust TTL based on content type
        if h1 in ['home', '']:
            return base_ttl  # Full TTL for home page
        elif h1 in ['about', 'contact']:
            return base_ttl * 2  # Static pages cache longer
        elif h1 in ['dashboard', 'profile']:
            return min(base_ttl // 2, 300)  # Dynamic user pages cache shorter
        else:
            return base_ttl
    
    @staticmethod
    def cleanup():
        """Cleanup method for end-of-request optimizations"""
        instance = Peanuts.get_instance()
        
        # Capture final metrics
        instance.capture_request_metrics()
        
        # Perform any end-of-request optimizations
        if instance.performance_mode == PerformanceMode.FEAST:
            # In feast mode, we can do more expensive cleanup
            pass
        
        # Clear temporary data
        if Memory:
            Memory.forget('peanuts_temp_data')
        
        # Log performance summary if debug mode is enabled
        score = instance.calculate_performance_score()
        instance.logger.info(f"🥜 Request completed - Performance score: {score:.3f} Mode: {instance.performance_mode.value}")


# Global functions for easy access
def peanuts() -> Peanuts:
    """Get Peanuts instance"""
    return Peanuts.get_instance()


def peanuts_env(key: str, default: Any = None) -> Any:
    """Get environment variable from .peanuts"""
    return Peanuts.get_peanuts_env(key, default)


def peanuts_set(key: str, value: Any) -> bool:
    """Set environment variable in .peanuts"""
    return Peanuts.set_peanuts_env(key, value)


# Flask-TSK integration
def init_peanuts(app, claude_api_key: str = None):
    """Initialize Peanuts with Flask app"""
    peanuts_instance = peanuts()
    app.peanuts = peanuts_instance
    return peanuts_instance


def get_peanuts() -> Peanuts:
    """Get Peanuts instance from Flask app context"""
    from flask import current_app
    return current_app.peanuts 