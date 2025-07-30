#!/usr/bin/env python3
"""
Flask-TSK - Flask Extension for TuskLang Integration
Provides seamless TuskLang configuration and function execution in Flask applications
Includes FULL TuskLang SDK capabilities for maximum power and flexibility
"""

from flask import Flask, current_app, g, request, jsonify
from typing import Any, Dict, List, Optional, Union
import logging
import os

# Type annotations for conditional imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from tusktsk import TSKParser, ShellStorage

try:
    import tusktsk
    from tusktsk import (
        TSK, parse, stringify, save, load
    )
    # Import these separately to handle potential missing attributes
    try:
        from tusktsk import TSKParser, ShellStorage
    except ImportError:
        TSKParser = None
        ShellStorage = None
    TUSK_AVAILABLE = True
    TUSK_VERSION = getattr(tusktsk, '__version__', '2.0.4')
except ImportError:
    TUSK_AVAILABLE = False
    TUSK_VERSION = None
    TSKParser = None
    ShellStorage = None
    logging.warning("tusktsk package not available. Install with: pip install tusktsk")

# Import performance engine
try:
    from .performance_engine import (
        TurboTemplateEngine, 
        render_turbo_template, 
        render_turbo_template_async,
        optimize_flask_app,
        get_performance_stats
    )
    PERFORMANCE_ENGINE_AVAILABLE = True
except ImportError:
    PERFORMANCE_ENGINE_AVAILABLE = False
    logging.warning("Performance engine not available")

# Elephant integration
try:
    from .elephants import init_elephant_herd, get_elephant_herd
    from .elephant_routes import elephant_bp
    from .elephant_showcase import init_elephant_showcase
    
    def init_elephants(app):
        """Initialize elephant herd with Flask app"""
        init_elephant_herd(app)
        app.register_blueprint(elephant_bp)
        init_elephant_showcase(app)
        app.logger.info("🐘 Elephant integration complete!")
    
    ELEPHANTS_ENABLED = True
except ImportError as e:
    # Don't use current_app at module level
    ELEPHANTS_ENABLED = False
    
    def init_elephants(app):
        """Placeholder for elephant initialization"""
        app.logger.info("Elephants not available - skipping initialization")


# Global TSK instance for herd integration
_global_tsk_instance = None

def get_tsk():
    """Get the global TSK instance"""
    global _global_tsk_instance
    if _global_tsk_instance is None:
        if TUSK_AVAILABLE:
            _global_tsk_instance = TSK()
        else:
            _global_tsk_instance = None
    return _global_tsk_instance


class FlaskTSK:
    """Flask extension for TuskLang integration with FULL SDK capabilities"""
    
    def __init__(self, app: Optional[Flask] = None):
        self.app = app
        self.tsk_instance: Optional[TSK] = None
        self.peanut_loaded = False
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize the Flask extension"""
        self.app = app
        
        # Set default configuration
        app.config.setdefault('TSK_CONFIG_PATH', None)
        app.config.setdefault('TSK_AUTO_LOAD', True)
        app.config.setdefault('TSK_ENABLE_BLUEPRINT', True)
        app.config.setdefault('TSK_ENABLE_CONTEXT', True)
        app.config.setdefault('TSK_ENABLE_FULL_SDK', True)  # Enable full TuskLang SDK
        
        # Initialize TuskLang if available
        if TUSK_AVAILABLE and app.config.get('TSK_AUTO_LOAD', True):
            self._initialize_tusk()
        
        # Register blueprint if enabled
        if app.config.get('TSK_ENABLE_BLUEPRINT', True):
            from .blueprint import tsk_blueprint
            app.register_blueprint(tsk_blueprint)
        
        # Register context processor if enabled
        if app.config.get('TSK_ENABLE_CONTEXT', True):
            app.context_processor(self._context_processor)
        
        # Register before_request handler
        app.before_request(self._before_request)
        
        # Register teardown_appcontext handler
        app.teardown_appcontext(self._teardown_appcontext)
        
        # Add extension to app
        app.extensions['flask-tsk'] = self
        
        # Apply performance optimizations if available
        if PERFORMANCE_ENGINE_AVAILABLE:
            optimize_flask_app(app)
            if hasattr(self, 'app') and self.app:
                self.app.logger.info("Flask-TSK: Performance optimizations applied")
    
    def _initialize_tusk(self):
        """Initialize TuskLang integration"""
        try:
            # Create TSK instance - load_from_peanut may not be available
            self.tsk_instance = TSK()
            self.peanut_loaded = True
            if hasattr(self, 'app') and self.app:
                self.app.logger.info(f"Flask-TSK: Successfully initialized TuskLang (tusktsk v{TUSK_VERSION})")
        except Exception as e:
            if hasattr(self, 'app') and self.app:
                self.app.logger.warning(f"Flask-TSK: Failed to initialize TuskLang: {e}")
            self.tsk_instance = None
    
    def _context_processor(self):
        """Context processor to make TSK available in templates"""
        return {
            'tsk': self,
            'tsk_available': TUSK_AVAILABLE,
            'tsk_version': TUSK_VERSION,
            'tsk_full_sdk': TUSK_AVAILABLE
        }
    
    def _before_request(self):
        """Before request handler to set up TSK context"""
        if TUSK_AVAILABLE and self.tsk_instance:
            g.tsk = self.tsk_instance
        else:
            g.tsk = None
    
    def _teardown_appcontext(self, exception=None):
        """Teardown app context handler"""
        if hasattr(g, 'tsk'):
            del g.tsk
    
    # ===== CORE TUSKLANG SDK METHODS =====
    
    def get_config(self, section: str, key: str, default: Any = None) -> Any:
        """Get configuration value from TuskLang"""
        if not TUSK_AVAILABLE or not self.tsk_instance:
            return default
        
        try:
            return self.tsk_instance.get_value(section, key)
        except Exception as e:
            if hasattr(self, 'app') and self.app:
                self.app.logger.warning(f"Flask-TSK: Failed to get config {section}.{key}: {e}")
            return default
    
    def set_config(self, section: str, key: str, value: Any) -> bool:
        """Set configuration value in TuskLang"""
        if not TUSK_AVAILABLE or not self.tsk_instance:
            return False
        
        try:
            self.tsk_instance.set_value(section, key, value)
            return True
        except Exception as e:
            if hasattr(self, 'app') and self.app:
                self.app.logger.error(f"Flask-TSK: Failed to set config {section}.{key}: {e}")
            return False
    
    def get_section(self, section: str) -> Optional[Dict[str, Any]]:
        """Get entire section from TuskLang"""
        if not TUSK_AVAILABLE or not self.tsk_instance:
            return None
        
        try:
            return self.tsk_instance.get_section(section)
        except Exception as e:
            current_app.logger.warning(f"Flask-TSK: Failed to get section {section}: {e}")
            return None
    
    def execute_function(self, section: str, key: str, *args, **kwargs) -> Any:
        """Execute a TuskLang function"""
        if not TUSK_AVAILABLE or not self.tsk_instance:
            return None
        
        try:
            return self.tsk_instance.execute_fujsen(section, key, *args, **kwargs)
        except Exception as e:
            current_app.logger.error(f"Flask-TSK: Failed to execute function {section}.{key}: {e}")
            return None
    
    # ===== ADVANCED TUSKLANG SDK METHODS =====
    
    def parse_tsk(self, content: str, enhanced: bool = False, with_comments: bool = False) -> Dict[str, Any]:
        """Parse TuskLang content with advanced options"""
        if not TUSK_AVAILABLE:
            return {}
        
        try:
            # Use regular parse for all cases since enhanced/comment parsing may not be available
            return parse(content)
        except Exception as e:
            current_app.logger.error(f"Flask-TSK: Failed to parse TuskLang content: {e}")
            return {}
    
    def stringify_tsk(self, data: Dict[str, Any]) -> str:
        """Convert data back to TuskLang format"""
        if not TUSK_AVAILABLE:
            return ""
        
        try:
            return stringify(data)
        except Exception as e:
            current_app.logger.error(f"Flask-TSK: Failed to stringify data: {e}")
            return ""
    
    def save_tsk(self, data: Dict[str, Any], filepath: str) -> bool:
        """Save TuskLang data to file"""
        if not TUSK_AVAILABLE:
            return False
        
        try:
            save(data, filepath)
            return True
        except Exception as e:
            current_app.logger.error(f"Flask-TSK: Failed to save TuskLang data: {e}")
            return False
    
    def load_tsk(self, filepath: str) -> Dict[str, Any]:
        """Load TuskLang data from file"""
        if not TUSK_AVAILABLE:
            return {}
        
        try:
            return load(filepath)
        except Exception as e:
            current_app.logger.error(f"Flask-TSK: Failed to load TuskLang data: {e}")
            return {}
    
    def create_parser(self) -> Optional[TSKParser]:
        """Create a TuskLang parser instance"""
        if not TUSK_AVAILABLE:
            return None
        
        try:
            return TSKParser()
        except Exception as e:
            current_app.logger.error(f"Flask-TSK: Failed to create parser: {e}")
            return None
    
    def create_shell_storage(self) -> Optional[ShellStorage]:
        """Create a TuskLang shell storage instance"""
        if not TUSK_AVAILABLE:
            return None
        
        try:
            return ShellStorage()
        except Exception as e:
            current_app.logger.error(f"Flask-TSK: Failed to create shell storage: {e}")
            return None
    
    # ===== CONFIGURATION MANAGEMENT =====
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration from TuskLang"""
        db_config = self.get_section('database')
        if db_config:
            return db_config
        
        # Fallback to Flask config
        return {
            'type': 'sqlite',
            'host': current_app.config.get('DB_HOST', 'localhost'),
            'port': current_app.config.get('DB_PORT', 5432),
            'name': current_app.config.get('DB_NAME', 'app.db'),
            'username': current_app.config.get('DB_USERNAME', ''),
            'password': current_app.config.get('DB_PASSWORD', ''),
            'charset': 'utf8mb4',
            'pool_size': 10
        }
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration from TuskLang"""
        security_config = self.get_section('security')
        if security_config:
            return security_config
        
        # Fallback to Flask config
        return {
            'encryption_key': current_app.config.get('SECRET_KEY', ''),
            'jwt_secret': current_app.config.get('JWT_SECRET_KEY', ''),
            'app_key': current_app.config.get('APP_KEY', '')
        }
    
    def get_ui_config(self) -> Dict[str, Any]:
        """Get UI configuration from TuskLang"""
        ui_config = self.get_section('ui')
        if ui_config:
            return ui_config
        
        # Fallback to Flask config
        return {
            'theme': current_app.config.get('UI_THEME', 'default'),
            'component_cache': current_app.config.get('UI_COMPONENT_CACHE', True),
            'minify_assets': current_app.config.get('UI_MINIFY_ASSETS', True),
            'responsive_design': current_app.config.get('UI_RESPONSIVE_DESIGN', True)
        }
    
    # ===== UTILITY METHODS =====
    
    def is_available(self) -> bool:
        """Check if TuskLang is available"""
        return TUSK_AVAILABLE and self.tsk_instance is not None
    
    def get_status(self) -> Dict[str, Any]:
        """Get TuskLang integration status"""
        status = {
            'available': TUSK_AVAILABLE,
            'version': TUSK_VERSION,
            'initialized': self.tsk_instance is not None,
            'peanut_loaded': self.peanut_loaded,
            'package_source': 'PyPI' if TUSK_AVAILABLE else 'None',
            'performance_engine': PERFORMANCE_ENGINE_AVAILABLE,
            'full_sdk_enabled': TUSK_AVAILABLE
        }
        
        # Add performance stats if available
        if PERFORMANCE_ENGINE_AVAILABLE:
            try:
                status['performance_stats'] = get_performance_stats()
            except Exception as e:
                status['performance_error'] = str(e)
        
        return status
    
    def save_config(self, filepath: str) -> bool:
        """Save TuskLang configuration to file"""
        if not TUSK_AVAILABLE or not self.tsk_instance:
            return False
        
        try:
            self.tsk_instance.to_file(filepath)
            return True
        except Exception as e:
            current_app.logger.error(f"Flask-TSK: Failed to save config to {filepath}: {e}")
            return False
    
    def load_config(self, filepath: str) -> bool:
        """Load TuskLang configuration from file"""
        if not TUSK_AVAILABLE:
            return False
        
        try:
            self.tsk_instance = TSK.from_file(filepath)
            return True
        except Exception as e:
            current_app.logger.error(f"Flask-TSK: Failed to load config from {filepath}: {e}")
            return False
    
    # ===== ADVANCED FEATURES =====
    
    def get_all_sections(self) -> List[str]:
        """Get all available sections"""
        if not TUSK_AVAILABLE or not self.tsk_instance:
            return []
        
        try:
            return list(self.tsk_instance.data.keys())
        except Exception as e:
            current_app.logger.error(f"Flask-TSK: Failed to get sections: {e}")
            return []
    
    def has_section(self, section: str) -> bool:
        """Check if section exists"""
        if not TUSK_AVAILABLE or not self.tsk_instance:
            return False
        
        try:
            return section in self.tsk_instance.data
        except Exception as e:
            current_app.logger.error(f"Flask-TSK: Failed to check section {section}: {e}")
            return False
    
    def delete_section(self, section: str) -> bool:
        """Delete a section"""
        if not TUSK_AVAILABLE or not self.tsk_instance:
            return False
        
        try:
            if section in self.tsk_instance.data:
                del self.tsk_instance.data[section]
                return True
            return False
        except Exception as e:
            current_app.logger.error(f"Flask-TSK: Failed to delete section {section}: {e}")
            return False
    
    def get_all_keys(self, section: str) -> List[str]:
        """Get all keys in a section"""
        section_data = self.get_section(section)
        if section_data:
            return list(section_data.keys())
        return []

    def setup_project_structure(self, project_path: str = None):
        """
        Create Flask-TSK comprehensive folder structure for asset management, layouts, and optimization.
        
        Creates:
        - tsk/assets/ (CSS, JS, images, fonts)
        - tsk/layouts/ (HTML templates, headers, footers)
        - tsk/templates/ (Jinja2 templates - auth, base, pages)
        - tsk/components/ (Ready-to-use Flask components)
        - tsk/optimization/ (minification, obfuscation scripts)
        - tsk/config/ (TuskLang configuration files)
        - tsk/static/ (Flask static files)
        - tsk/auth/ (Authentication templates and components)
        - tsk/menus/ (Navigation menus and dropdowns)
        - tsk/navs/ (Navigation components)
        - tsk/forms/ (Form components and validation)
        - tsk/ui/ (UI components and widgets)
        - tsk/examples/ (Example applications showcasing elephant services)
        """
        if project_path is None:
            project_path = os.getcwd()
        
        # Define the comprehensive folder structure
        folders = [
            # Core Flask-TSK structure
            'tsk/assets/css',
            'tsk/assets/js', 
            'tsk/assets/images',
            'tsk/assets/fonts',
            'tsk/assets/icons',
            
            # Layout system
            'tsk/layouts/headers',
            'tsk/layouts/footers',
            'tsk/layouts/navigation',
            'tsk/layouts/sidebars',
            'tsk/layouts/modals',
            
            # Template system
            'tsk/templates/base',
            'tsk/templates/auth',
            'tsk/templates/pages',
            'tsk/templates/admin',
            'tsk/templates/dashboard',
            'tsk/templates/errors',
            'tsk/templates/email',
            
            # Component system
            'tsk/components/navigation',
            'tsk/components/forms',
            'tsk/components/ui',
            'tsk/components/layouts',
            'tsk/components/ecommerce',
            'tsk/components/blog',
            'tsk/components/dashboard',
            'tsk/components/cards',
            'tsk/components/tables',
            'tsk/components/buttons',
            'tsk/components/alerts',
            'tsk/components/modals',
            'tsk/components/charts',
            'tsk/components/widgets',
            
            # Authentication system
            'tsk/auth/templates',
            'tsk/auth/components',
            'tsk/auth/forms',
            'tsk/auth/middleware',
            
            # Menu system
            'tsk/menus/main',
            'tsk/menus/sidebar',
            'tsk/menus/user',
            'tsk/menus/admin',
            'tsk/menus/mobile',
            
            # Navigation system
            'tsk/navs/primary',
            'tsk/navs/secondary',
            'tsk/navs/breadcrumbs',
            'tsk/navs/pagination',
            'tsk/navs/tabs',
            
            # Form system
            'tsk/forms/auth',
            'tsk/forms/user',
            'tsk/forms/admin',
            'tsk/forms/validation',
            'tsk/forms/widgets',
            
            # UI system
            'tsk/ui/buttons',
            'tsk/ui/inputs',
            'tsk/ui/cards',
            'tsk/ui/alerts',
            'tsk/ui/modals',
            'tsk/ui/tables',
            'tsk/ui/charts',
            'tsk/ui/progress',
            'tsk/ui/badges',
            'tsk/ui/tooltips',
            
            # Optimization system
            'tsk/optimization/scripts',
            'tsk/optimization/tools',
            
            # Configuration system
            'tsk/config',
            'tsk/config/themes',
            'tsk/config/databases',
            'tsk/config/security',
            
            # Static files
            'tsk/static/css',
            'tsk/static/js',
            'tsk/static/images',
            'tsk/static/fonts',
            'tsk/static/icons',
            
            # Data system
            'tsk/data',
            'tsk/data/migrations',
            'tsk/data/seeds',
            'tsk/data/backups',
            
            # Documentation
            'tsk/docs',
            'tsk/docs/api',
            'tsk/docs/components',
            'tsk/docs/themes',
            'tsk/docs/examples',
            
            # Testing
            'tsk/tests',
            'tsk/tests/unit',
            'tsk/tests/integration',
            'tsk/tests/components',
            
            # Logging
            'tsk/logs',
            'tsk/logs/access',
            'tsk/logs/error',
            'tsk/logs/debug',
            
            # Build system
            'tsk/build',
            'tsk/cache',
            
            # Examples showcase
            'tsk/examples',
            'tsk/examples/basic_auth',
            'tsk/examples/blog_system',
            'tsk/examples/ecommerce',
            'tsk/examples/dashboard',
            'tsk/examples/api_service',
            'tsk/examples/social_network',
            'tsk/examples/portfolio',
            'tsk/examples/saas_app',
            
            # Example templates
            'tsk/examples/templates',
            'tsk/examples/templates/auth',
            'tsk/examples/templates/blog',
            'tsk/examples/templates/shop',
            'tsk/examples/templates/admin',
            'tsk/examples/templates/social',
            'tsk/examples/templates/portfolio',
            'tsk/examples/templates/saas',
            
            # Example static files
            'tsk/examples/static',
            'tsk/examples/static/css',
            'tsk/examples/static/js',
            'tsk/examples/static/images',
        ]
        
        # Create all folders
        for folder in folders:
            folder_path = os.path.join(project_path, folder)
            os.makedirs(folder_path, exist_ok=True)
        
        # Create default files
        self._create_comprehensive_default_files(project_path)
        
        # Create example showcase
        self._create_example_showcase(project_path)
        
        return True
    
    def _create_default_files(self, project_path: str):
        """Create default configuration and template files."""
        
        # Default peanu.tsk configuration
        peanu_content = '''[flask_tsk]
# Flask-TSK Configuration
version = "1.0.1"
auto_setup = true
optimization_enabled = true

[database]
# Database configuration
type = "sqlite"
herd_db = "data/herd_auth.db"
elephants_db = "data/elephant_services.db"
auto_create = true
migrations = true

[herd]
# Herd authentication configuration
guards = ["web", "api", "admin"]
session_lifetime = 7200
max_attempts = 5
lockout_duration = 900

[users]
# User management configuration
table = "users"
provider = "tusk"
default_role = "user"
require_email_verification = true

[auth]
# Authentication configuration
table = "auth_attempts"
provider = "tusk"
password_min_length = 8
require_special_chars = true

[assets]
# Asset management configuration
css_dir = "tsk/assets/css"
js_dir = "tsk/assets/js"
images_dir = "tsk/assets/images"
fonts_dir = "tsk/assets/fonts"

[optimization]
# Optimization settings
minify_css = true
minify_js = true
obfuscate_js = false
compress_images = true
cache_enabled = true

[layouts]
# Layout configuration
default_header = "tsk/layouts/headers/default.html"
default_footer = "tsk/layouts/footers/default.html"
default_nav = "tsk/layouts/navigation/default.html"

[components]
# Component configuration
auto_include = true
component_dir = "tsk/components"
default_theme = "modern"
responsive = true

[build]
# Build settings
output_dir = "tsk/build"
source_maps = true
watch_mode = false
'''
        
        # Default header template
        header_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title|default('Flask-TSK App') }}</title>
    
    <!-- Flask-TSK Asset Management -->
    {% if tsk_available %}
        <link rel="stylesheet" href="{{ tsk_asset('css', 'main.css') }}">
        <link rel="stylesheet" href="{{ tsk_asset('css', 'components.css') }}">
        <script src="{{ tsk_asset('js', 'main.js') }}" defer></script>
    {% else %}
        <link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}">
        <link rel="stylesheet" href="{{ url_for('static', filename='css/components.css') }}">
        <script src="{{ url_for('static', filename='js/main.js') }}" defer></script>
    {% endif %}
    
    <!-- Meta tags -->
    <meta name="description" content="{{ description|default('Flask-TSK Application') }}">
    <meta name="keywords" content="{{ keywords|default('flask, tusk, python') }}">
    
    <!-- Favicon -->
    <link rel="icon" type="image/x-icon" href="{{ url_for('static', filename='favicon.ico') }}">
</head>
<body>
    <!-- Navigation -->
    {% include 'tsk/layouts/navigation/default.html' %}
    
    <!-- Main content wrapper -->
    <main class="main-content">
'''
        
        # Default footer template
        footer_content = '''    </main>
    
    <!-- Footer -->
    <footer class="footer">
        <div class="container">
            <p>&copy; {{ current_year|default(2024) }} Flask-TSK Application. Powered by <a href="https://github.com/cyber-boost/tusktsk" target="_blank">TuskLang</a>.</p>
        </div>
    </footer>
    
    <!-- Flask-TSK Asset Management -->
    {% if tsk_available %}
        <script src="{{ tsk_asset('js', 'footer.js') }}"></script>
    {% else %}
        <script src="{{ url_for('static', filename='js/footer.js') }}"></script>
    {% endif %}
</body>
</html>
'''
        
        # Default navigation template
        nav_content = '''<nav class="navbar">
    <div class="container">
        <div class="navbar-brand">
            <a href="{{ url_for('index') }}" class="navbar-item">
                Flask-TSK
            </a>
        </div>
        
        <div class="navbar-menu">
            <a href="{{ url_for('index') }}" class="navbar-item">Home</a>
            <a href="{{ url_for('about') }}" class="navbar-item">About</a>
            <a href="{{ url_for('contact') }}" class="navbar-item">Contact</a>
        </div>
    </div>
</nav>
'''
        
        # Default CSS
        css_content = '''/* Flask-TSK Default Styles */
:root {
    --primary-color: #4ECDC4;
    --secondary-color: #FF6B6B;
    --accent-color: #FFE66D;
    --text-color: #1A1A1A;
    --background-color: #F8F9FA;
    --border-radius: 8px;
    --transition: all 0.3s ease;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    line-height: 1.6;
    color: var(--text-color);
    background-color: var(--background-color);
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

/* Navigation */
.navbar {
    background: white;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    padding: 1rem 0;
}

.navbar-brand {
    font-weight: bold;
    font-size: 1.5rem;
}

.navbar-item {
    color: var(--text-color);
    text-decoration: none;
    padding: 0.5rem 1rem;
    border-radius: var(--border-radius);
    transition: var(--transition);
}

.navbar-item:hover {
    background-color: var(--primary-color);
    color: white;
}

/* Main content */
.main-content {
    min-height: calc(100vh - 200px);
    padding: 2rem 0;
}

/* Footer */
.footer {
    background: var(--text-color);
    color: white;
    padding: 2rem 0;
    text-align: center;
}

.footer a {
    color: var(--primary-color);
    text-decoration: none;
}

.footer a:hover {
    text-decoration: underline;
}
'''
        
        # Default JavaScript
        js_content = '''// Flask-TSK Default JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('Flask-TSK Application Loaded');
    
    // Initialize navigation
    initNavigation();
    
    // Initialize any TuskLang features
    if (typeof tsk !== 'undefined') {
        initTuskFeatures();
    }
});

function initNavigation() {
    // Add active class to current page
    const currentPath = window.location.pathname;
    const navItems = document.querySelectorAll('.navbar-item');
    
    navItems.forEach(item => {
        if (item.getAttribute('href') === currentPath) {
            item.classList.add('active');
        }
    });
}

function initTuskFeatures() {
    // Initialize TuskLang-specific features
    console.log('TuskLang features initialized');
    
    // Example: Dynamic configuration loading
    if (tsk && tsk.getConfig) {
        const theme = tsk.getConfig('ui', 'theme', 'light');
        document.body.setAttribute('data-theme', theme);
    }
}

// Utility functions
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}
'''
        
        # Files to create
        files = {
            'tsk/config/peanu.tsk': peanu_content,
            'tsk/layouts/headers/default.html': header_content,
            'tsk/layouts/footers/default.html': footer_content,
            'tsk/layouts/navigation/default.html': nav_content,
            'tsk/assets/css/main.css': css_content,
            'tsk/assets/js/main.js': js_content,
            'tsk/static/css/main.css': css_content,
            'tsk/static/js/main.js': js_content,
        }
        
        # Create files
        for file_path, content in files.items():
            full_path = os.path.join(project_path, file_path)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            current_app.logger.info(f"Created Flask-TSK file: {file_path}")

    def _create_comprehensive_default_files(self, project_path: str):
        """Create comprehensive default configuration and template files."""
        
        # Enhanced peanu.tsk configuration
        peanu_content = '''[flask_tsk]
# Flask-TSK Comprehensive Configuration
version = "1.0.1"
auto_setup = true
optimization_enabled = true
theme_system = true
auth_system = true
component_system = true

[database]
# Database configuration
type = "sqlite"
herd_db = "tsk/data/herd_auth.db"
elephants_db = "tsk/data/elephant_services.db"
auto_create = true
migrations = true
backup_enabled = true

[herd]
# Herd authentication configuration
guards = ["web", "api", "admin", "mobile"]
session_lifetime = 7200
max_attempts = 5
lockout_duration = 900
password_reset_enabled = true
email_verification = true

[users]
# User management configuration
table = "users"
provider = "tusk"
default_role = "user"
require_email_verification = true
profile_fields = ["first_name", "last_name", "avatar", "bio"]
roles = ["user", "admin", "moderator", "premium"]

[auth]
# Authentication configuration
table = "auth_attempts"
provider = "tusk"
password_min_length = 8
require_special_chars = true
two_factor_enabled = false
social_login = ["google", "github", "facebook"]

[assets]
# Asset management configuration
css_dir = "tsk/assets/css"
js_dir = "tsk/assets/js"
images_dir = "tsk/assets/images"
fonts_dir = "tsk/assets/fonts"
icons_dir = "tsk/assets/icons"

[optimization]
# Optimization settings
minify_css = true
minify_js = true
obfuscate_js = false
compress_images = true
cache_enabled = true
gzip_enabled = true

[layouts]
# Layout configuration
default_header = "tsk/layouts/headers/default.html"
default_footer = "tsk/layouts/footers/default.html"
default_nav = "tsk/layouts/navigation/default.html"
default_sidebar = "tsk/layouts/sidebars/default.html"
responsive = true

[components]
# Component configuration
auto_include = true
component_dir = "tsk/components"
default_theme = "modern"
responsive = true
lazy_loading = true

[themes]
# Theme configuration
default_theme = "modern"
available_themes = ["modern", "dark", "classic", "custom"]
theme_switcher = true
custom_css_enabled = true

[build]
# Build settings
output_dir = "tsk/build"
source_maps = true
watch_mode = false
hot_reload = true

[security]
# Security configuration
csrf_enabled = true
xss_protection = true
content_security_policy = true
rate_limiting = true
session_secure = true

[logging]
# Logging configuration
level = "INFO"
file_logging = true
log_dir = "tsk/logs"
max_file_size = "10MB"
backup_count = 5
'''
        
        # Base template
        base_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}{{ title|default('Flask-TSK App') }}{% endblock %}</title>
    
    <!-- Flask-TSK Asset Management -->
    {% if tsk_available %}
        <link rel="stylesheet" href="{{ tsk_asset('css', 'main.css') }}">
        <link rel="stylesheet" href="{{ tsk_asset('css', 'components.css') }}">
        <link rel="stylesheet" href="{{ tsk_asset('css', 'themes/' + theme|default('modern') + '.css') }}">
        <script src="{{ tsk_asset('js', 'main.js') }}" defer></script>
    {% else %}
        <link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}">
        <link rel="stylesheet" href="{{ url_for('static', filename='css/components.css') }}">
        <script src="{{ url_for('static', filename='js/main.js') }}" defer></script>
    {% endif %}
    
    <!-- Meta tags -->
    <meta name="description" content="{% block description %}{{ description|default('Flask-TSK Application') }}{% endblock %}">
    <meta name="keywords" content="{% block keywords %}{{ keywords|default('flask, tusk, python') }}{% endblock %}">
    
    <!-- Open Graph -->
    <meta property="og:title" content="{% block og_title %}{{ title|default('Flask-TSK App') }}{% endblock %}">
    <meta property="og:description" content="{% block og_description %}{{ description|default('Flask-TSK Application') }}{% endblock %}">
    <meta property="og:type" content="website">
    <meta property="og:url" content="{{ request.url }}">
    
    <!-- Favicon -->
    <link rel="icon" type="image/x-icon" href="{{ url_for('static', filename='favicon.ico') }}">
    
    {% block extra_head %}{% endblock %}
</head>
<body class="theme-{{ theme|default('modern') }}">
    <!-- Flash Messages -->
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            <div class="flash-messages">
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }} alert-dismissible">
                        {{ message }}
                        <button type="button" class="close" data-dismiss="alert">&times;</button>
                    </div>
                {% endfor %}
            </div>
        {% endif %}
    {% endwith %}
    
    <!-- Navigation -->
    {% include 'tsk/layouts/navigation/default.html' %}
    
    <!-- Main content wrapper -->
    <main class="main-content">
        {% block content %}{% endblock %}
    </main>
    
    <!-- Footer -->
    {% include 'tsk/layouts/footers/default.html' %}
    
    <!-- Flask-TSK Asset Management -->
    {% if tsk_available %}
        <script src="{{ tsk_asset('js', 'footer.js') }}"></script>
        <script src="{{ tsk_asset('js', 'components.js') }}"></script>
    {% else %}
        <script src="{{ url_for('static', filename='js/footer.js') }}"></script>
        <script src="{{ url_for('static', filename='js/components.js') }}"></script>
    {% endif %}
    
    {% block extra_scripts %}{% endblock %}
</body>
</html>
'''
        
        # Auth templates
        login_template = '''{% extends "tsk/templates/base/base.html" %}

{% block title %}Login - Flask-TSK{% endblock %}

{% block content %}
<div class="auth-container">
    <div class="auth-card">
        <div class="auth-header">
            <h1>Welcome Back</h1>
            <p>Sign in to your account</p>
        </div>
        
        <form method="POST" action="{{ url_for('auth.login') }}" class="auth-form">
            {{ form.hidden_tag() }}
            
            <div class="form-group">
                <label for="email">Email</label>
                <input type="email" id="email" name="email" required class="form-control">
            </div>
            
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required class="form-control">
            </div>
            
            <div class="form-group">
                <label class="checkbox-label">
                    <input type="checkbox" name="remember" id="remember">
                    <span class="checkmark"></span>
                    Remember me
                </label>
            </div>
            
            <button type="submit" class="btn btn-primary btn-block">Sign In</button>
        </form>
        
        <div class="auth-footer">
            <a href="{{ url_for('auth.forgot_password') }}">Forgot password?</a>
            <span class="divider">|</span>
            <a href="{{ url_for('auth.register') }}">Create account</a>
        </div>
        
        <div class="social-login">
            <p>Or sign in with</p>
            <div class="social-buttons">
                <a href="{{ url_for('auth.google_login') }}" class="btn btn-social btn-google">
                    <i class="fab fa-google"></i> Google
                </a>
                <a href="{{ url_for('auth.github_login') }}" class="btn btn-social btn-github">
                    <i class="fab fa-github"></i> GitHub
                </a>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''
        
        register_template = '''{% extends "tsk/templates/base/base.html" %}

{% block title %}Register - Flask-TSK{% endblock %}

{% block content %}
<div class="auth-container">
    <div class="auth-card">
        <div class="auth-header">
            <h1>Create Account</h1>
            <p>Join our community</p>
        </div>
        
        <form method="POST" action="{{ url_for('auth.register') }}" class="auth-form">
            {{ form.hidden_tag() }}
            
            <div class="form-row">
                <div class="form-group">
                    <label for="first_name">First Name</label>
                    <input type="text" id="first_name" name="first_name" required class="form-control">
                </div>
                <div class="form-group">
                    <label for="last_name">Last Name</label>
                    <input type="text" id="last_name" name="last_name" required class="form-control">
                </div>
            </div>
            
            <div class="form-group">
                <label for="email">Email</label>
                <input type="email" id="email" name="email" required class="form-control">
            </div>
            
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required class="form-control">
                <div class="password-strength" id="password-strength"></div>
            </div>
            
            <div class="form-group">
                <label for="confirm_password">Confirm Password</label>
                <input type="password" id="confirm_password" name="confirm_password" required class="form-control">
            </div>
            
            <div class="form-group">
                <label class="checkbox-label">
                    <input type="checkbox" name="terms" id="terms" required>
                    <span class="checkmark"></span>
                    I agree to the <a href="{{ url_for('terms') }}">Terms of Service</a>
                </label>
            </div>
            
            <button type="submit" class="btn btn-primary btn-block">Create Account</button>
        </form>
        
        <div class="auth-footer">
            <span>Already have an account?</span>
            <a href="{{ url_for('auth.login') }}">Sign in</a>
        </div>
    </div>
</div>
{% endblock %}
'''
        
        # Enhanced navigation template
        enhanced_nav = '''<nav class="navbar navbar-expand-lg">
    <div class="container">
        <div class="navbar-brand">
            <a href="{{ url_for('index') }}" class="brand-logo">
                <span class="brand-icon">🐘</span>
                <span class="brand-text">Flask-TSK</span>
            </a>
        </div>
        
        <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav">
            <span class="navbar-toggler-icon"></span>
        </button>
        
        <div class="collapse navbar-collapse" id="navbarNav">
            <ul class="navbar-nav ml-auto">
                <li class="nav-item">
                    <a href="{{ url_for('index') }}" class="nav-link {{ 'active' if request.endpoint == 'index' else '' }}">
                        <i class="fas fa-home"></i> Home
                    </a>
                </li>
                <li class="nav-item">
                    <a href="{{ url_for('about') }}" class="nav-link {{ 'active' if request.endpoint == 'about' else '' }}">
                        <i class="fas fa-info-circle"></i> About
                    </a>
                </li>
                <li class="nav-item">
                    <a href="{{ url_for('contact') }}" class="nav-link {{ 'active' if request.endpoint == 'contact' else '' }}">
                        <i class="fas fa-envelope"></i> Contact
                    </a>
                </li>
                
                {% if current_user.is_authenticated %}
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" id="userDropdown" role="button" data-toggle="dropdown">
                            <img src="{{ current_user.avatar or url_for('static', filename='images/default-avatar.png') }}" 
                                 alt="{{ current_user.name }}" class="user-avatar">
                            {{ current_user.name }}
                        </a>
                        <div class="dropdown-menu">
                            <a class="dropdown-item" href="{{ url_for('profile') }}">
                                <i class="fas fa-user"></i> Profile
                            </a>
                            <a class="dropdown-item" href="{{ url_for('settings') }}">
                                <i class="fas fa-cog"></i> Settings
                            </a>
                            <div class="dropdown-divider"></div>
                            <a class="dropdown-item" href="{{ url_for('auth.logout') }}">
                                <i class="fas fa-sign-out-alt"></i> Logout
                            </a>
                        </div>
                    </li>
                {% else %}
                    <li class="nav-item">
                        <a href="{{ url_for('auth.login') }}" class="nav-link">
                            <i class="fas fa-sign-in-alt"></i> Login
                        </a>
                    </li>
                    <li class="nav-item">
                        <a href="{{ url_for('auth.register') }}" class="btn btn-primary">
                            <i class="fas fa-user-plus"></i> Register
                        </a>
                    </li>
                {% endif %}
            </ul>
        </div>
    </div>
</nav>
'''
        
        # Enhanced CSS with components
        enhanced_css = '''/* Flask-TSK Enhanced Styles */
:root {
    --primary-color: #4ECDC4;
    --secondary-color: #FF6B6B;
    --accent-color: #FFE66D;
    --success-color: #28a745;
    --warning-color: #ffc107;
    --danger-color: #dc3545;
    --info-color: #17a2b8;
    --text-color: #1A1A1A;
    --text-muted: #6c757d;
    --background-color: #F8F9FA;
    --border-color: #dee2e6;
    --border-radius: 8px;
    --border-radius-lg: 12px;
    --transition: all 0.3s ease;
    --shadow: 0 2px 10px rgba(0,0,0,0.1);
    --shadow-lg: 0 4px 20px rgba(0,0,0,0.15);
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    line-height: 1.6;
    color: var(--text-color);
    background-color: var(--background-color);
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

/* Navigation */
.navbar {
    background: white;
    box-shadow: var(--shadow);
    padding: 1rem 0;
    position: sticky;
    top: 0;
    z-index: 1000;
}

.navbar-brand {
    font-weight: bold;
    font-size: 1.5rem;
}

.brand-logo {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    text-decoration: none;
    color: var(--text-color);
}

.brand-icon {
    font-size: 1.8rem;
}

.navbar-nav {
    display: flex;
    list-style: none;
    gap: 1rem;
    align-items: center;
}

.nav-link {
    color: var(--text-color);
    text-decoration: none;
    padding: 0.5rem 1rem;
    border-radius: var(--border-radius);
    transition: var(--transition);
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.nav-link:hover,
.nav-link.active {
    background-color: var(--primary-color);
    color: white;
}

/* Auth Components */
.auth-container {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
}

.auth-card {
    background: white;
    border-radius: var(--border-radius-lg);
    box-shadow: var(--shadow-lg);
    padding: 2rem;
    width: 100%;
    max-width: 400px;
}

.auth-header {
    text-align: center;
    margin-bottom: 2rem;
}

.auth-header h1 {
    color: var(--text-color);
    margin-bottom: 0.5rem;
}

.auth-header p {
    color: var(--text-muted);
}

.auth-form .form-group {
    margin-bottom: 1.5rem;
}

.form-control {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    font-size: 1rem;
    transition: var(--transition);
}

.form-control:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(78, 205, 196, 0.1);
}

.btn {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: var(--border-radius);
    font-size: 1rem;
    font-weight: 500;
    text-decoration: none;
    cursor: pointer;
    transition: var(--transition);
}

.btn-primary {
    background-color: var(--primary-color);
    color: white;
}

.btn-primary:hover {
    background-color: #3db8b0;
    transform: translateY(-1px);
}

.btn-block {
    width: 100%;
    justify-content: center;
}

/* Flash Messages */
.flash-messages {
    position: fixed;
    top: 1rem;
    right: 1rem;
    z-index: 1001;
    max-width: 400px;
}

.alert {
    padding: 1rem;
    border-radius: var(--border-radius);
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.alert-success {
    background-color: var(--success-color);
    color: white;
}

.alert-warning {
    background-color: var(--warning-color);
    color: var(--text-color);
}

.alert-danger {
    background-color: var(--danger-color);
    color: white;
}

.alert-info {
    background-color: var(--info-color);
    color: white;
}

/* Main content */
.main-content {
    min-height: calc(100vh - 200px);
    padding: 2rem 0;
}

/* Footer */
.footer {
    background: var(--text-color);
    color: white;
    padding: 2rem 0;
    text-align: center;
}

.footer a {
    color: var(--primary-color);
    text-decoration: none;
}

.footer a:hover {
    text-decoration: underline;
}

/* Responsive */
@media (max-width: 768px) {
    .navbar-nav {
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .auth-card {
        margin: 1rem;
        padding: 1.5rem;
    }
}
'''
        
        # Enhanced JavaScript
        enhanced_js = '''// Flask-TSK Enhanced JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('Flask-TSK Enhanced Application Loaded');
    
    // Initialize all components
    initNavigation();
    initAuthComponents();
    initFlashMessages();
    initFormValidation();
    
    // Initialize any TuskLang features
    if (typeof tsk !== 'undefined') {
        initTuskFeatures();
    }
});

function initNavigation() {
    // Add active class to current page
    const currentPath = window.location.pathname;
    const navItems = document.querySelectorAll('.nav-link');
    
    navItems.forEach(item => {
        if (item.getAttribute('href') === currentPath) {
            item.classList.add('active');
        }
    });
    
    // Initialize dropdowns
    const dropdowns = document.querySelectorAll('.dropdown-toggle');
    dropdowns.forEach(dropdown => {
        dropdown.addEventListener('click', function(e) {
            e.preventDefault();
            const menu = this.nextElementSibling;
            menu.classList.toggle('show');
        });
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.dropdown')) {
            document.querySelectorAll('.dropdown-menu').forEach(menu => {
                menu.classList.remove('show');
            });
        }
    });
}

function initAuthComponents() {
    // Password strength indicator
    const passwordInput = document.getElementById('password');
    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            const strength = calculatePasswordStrength(this.value);
            updatePasswordStrength(strength);
        });
    }
    
    // Password confirmation
    const confirmPassword = document.getElementById('confirm_password');
    if (confirmPassword) {
        confirmPassword.addEventListener('input', function() {
            const password = document.getElementById('password').value;
            if (this.value !== password) {
                this.setCustomValidity('Passwords do not match');
            } else {
                this.setCustomValidity('');
            }
        });
    }
}

function initFlashMessages() {
    // Auto-dismiss flash messages
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
    
    // Manual dismiss
    const closeButtons = document.querySelectorAll('.alert .close');
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            this.parentElement.remove();
        });
    });
}

function initFormValidation() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!this.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            this.classList.add('was-validated');
        });
    });
}

function calculatePasswordStrength(password) {
    let strength = 0;
    
    if (password.length >= 8) strength += 1;
    if (/[a-z]/.test(password)) strength += 1;
    if (/[A-Z]/.test(password)) strength += 1;
    if (/[0-9]/.test(password)) strength += 1;
    if (/[^A-Za-z0-9]/.test(password)) strength += 1;
    
    return strength;
}

function updatePasswordStrength(strength) {
    const indicator = document.getElementById('password-strength');
    if (!indicator) return;
    
    const messages = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong'];
    const colors = ['#dc3545', '#ffc107', '#fd7e14', '#28a745', '#20c997'];
    
    indicator.textContent = messages[strength - 1] || '';
    indicator.style.color = colors[strength - 1] || '#6c757d';
}

function initTuskFeatures() {
    // Initialize TuskLang-specific features
    console.log('TuskLang features initialized');
    
    // Example: Dynamic configuration loading
    if (tsk && tsk.getConfig) {
        const theme = tsk.getConfig('ui', 'theme', 'light');
        document.body.setAttribute('data-theme', theme);
    }
}

// Utility functions
function showNotification(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="close" data-dismiss="alert">&times;</button>
    `;
    
    // Add to flash messages container or create one
    let container = document.querySelector('.flash-messages');
    if (!container) {
        container = document.createElement('div');
        container.className = 'flash-messages';
        document.body.appendChild(container);
    }
    
    container.appendChild(notification);
    
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, duration);
}

// Form helpers
function validateEmail(email) {
    const re = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
    return re.test(email);
}

function validatePassword(password) {
    return password.length >= 8;
}

// API helpers
async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}
'''
        
        # Component templates
        button_component = '''<!-- Button Component -->
<button class="btn btn-{{ style|default('primary') }} {{ size|default('') }} {{ 'btn-block' if block else '' }}"
        {% if disabled %}disabled{% endif %}
        {% if onclick %}onclick="{{ onclick }}"{% endif %}
        {% if type %}type="{{ type }}"{% endif %}>
    {% if icon %}<i class="{{ icon }}"></i>{% endif %}
    {{ text }}
</button>
'''
        
        card_component = '''<!-- Card Component -->
<div class="card {{ 'card-' + style if style else '' }}">
    {% if header %}
        <div class="card-header">
            {% if header_icon %}<i class="{{ header_icon }}"></i>{% endif %}
            {{ header }}
        </div>
    {% endif %}
    
    <div class="card-body">
        {{ content|safe }}
    </div>
    
    {% if footer %}
        <div class="card-footer">
            {{ footer|safe }}
        </div>
    {% endif %}
</div>
'''
        
        # Create comprehensive file structure
        files = {
            # Configuration
            'tsk/config/peanu.tsk': peanu_content,
            
            # Base templates
            'tsk/templates/base/base.html': base_template,
            
            # Auth templates
            'tsk/templates/auth/login.html': login_template,
            'tsk/templates/auth/register.html': register_template,
            'tsk/templates/auth/forgot_password.html': '{% extends "tsk/templates/base/base.html" %}\n{% block content %}<h1>Forgot Password</h1>{% endblock %}',
            'tsk/templates/auth/reset_password.html': '{% extends "tsk/templates/base/base.html" %}\n{% block content %}<h1>Reset Password</h1>{% endblock %}',
            
            # Layout templates
            'tsk/layouts/headers/default.html': base_template,
            'tsk/layouts/footers/default.html': '    </main>\n    <footer class="footer">\n        <div class="container">\n            <p>&copy; {{ current_year|default(2024) }} Flask-TSK Application. Powered by <a href="https://github.com/cyber-boost/tusktsk" target="_blank">TuskLang</a>.</p>\n        </div>\n    </footer>',
            'tsk/layouts/navigation/default.html': enhanced_nav,
            
            # Component templates
            'tsk/components/buttons/button.html': button_component,
            'tsk/components/cards/card.html': card_component,
            
            # Assets
            'tsk/assets/css/main.css': enhanced_css,
            'tsk/assets/js/main.js': enhanced_js,
            'tsk/static/css/main.css': enhanced_css,
            'tsk/static/js/main.js': enhanced_js,
            
            # Documentation
            'tsk/docs/README.md': '# Flask-TSK Project Documentation\n\nThis project uses Flask-TSK for enhanced functionality.\n\n## Structure\n- `tsk/templates/` - Jinja2 templates\n- `tsk/components/` - Reusable components\n- `tsk/assets/` - Source assets\n- `tsk/static/` - Compiled assets\n\n## Getting Started\n1. Run `flask-tsk db init`\n2. Start development server\n3. Visit http://localhost:5000',
            
            # Sample pages
            'tsk/templates/pages/index.html': '{% extends "tsk/templates/base/base.html" %}\n{% block content %}<h1>Welcome to Flask-TSK</h1>{% endblock %}',
            'tsk/templates/pages/about.html': '{% extends "tsk/templates/base/base.html" %}\n{% block content %}<h1>About Flask-TSK</h1>{% endblock %}',
            'tsk/templates/pages/contact.html': '{% extends "tsk/templates/base/base.html" %}\n{% block content %}<h1>Contact Us</h1>{% endblock %}',
            
            # Error pages
            'tsk/templates/errors/404.html': '{% extends "tsk/templates/base/base.html" %}\n{% block content %}<h1>404 - Page Not Found</h1>{% endblock %}',
            'tsk/templates/errors/500.html': '{% extends "tsk/templates/base/base.html" %}\n{% block content %}<h1>500 - Server Error</h1>{% endblock %}',
        }
        
        # Create files
        for file_path, content in files.items():
            full_path = os.path.join(project_path, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            current_app.logger.info(f"Created Flask-TSK file: {file_path}") 

    def _create_example_showcase(self, project_path: str):
        """
        Creates example applications and showcases within the project structure.
        """
        examples_path = os.path.join(project_path, 'tsk/examples')
        os.makedirs(examples_path, exist_ok=True)

        # Create a simple README for examples
        readme_path = os.path.join(examples_path, 'README.md')
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write('''# Flask-TSK Examples

This directory contains comprehensive examples showcasing Flask-TSK capabilities.

## Available Examples

- **Basic Authentication**: Simple authentication example with Herd
- **Blog System**: Complete blog with content management
- **E-commerce**: Full e-commerce system with products
- **Dashboard**: Admin dashboard with monitoring
- **API Service**: REST API with authentication
- **Social Network**: Social features with user profiles
- **Portfolio**: Portfolio website with admin panel
- **SaaS App**: Software-as-a-Service application

## Running Examples

Use the example runner:

```bash
# List all examples
python -m tsk_flask.example_runner list

# Run a specific example
python -m tsk_flask.example_runner run basic-auth

# Run all examples
python -m tsk_flask.example_runner run-all
```

## Elephant Services

Each example demonstrates the integration of elephant services:
- Babar (Content Management)
- Dumbo (HTTP Client)
- Elmer (Theme Generator)
- Happy (Image Processing)
- Heffalump (Search)
- Horton (Background Jobs)
- Jumbo (File Upload)
- Kaavan (System Monitoring)
- Koshik (Audio & Notifications)
- Peanuts (Performance)
- Satao (Security)
- Stampy (Package Management)
- Tantor (Database)

For more information, visit the elephant showcase page in each example.
''')

        # Create example configuration file
        config_path = os.path.join(examples_path, 'examples.tsk')
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write('''[examples]
# Flask-TSK Examples Configuration
version = "1.0.0"
auto_setup = true

[basic_auth]
enabled = true
port = 5000
description = "Simple authentication example showcasing Herd with elephant services"

[blog_system]
enabled = true
port = 5001
description = "Complete blog system with content management and elephant services"

[ecommerce]
enabled = true
port = 5002
description = "Complete e-commerce system with product management and elephant services"

[dashboard]
enabled = true
port = 5003
description = "Comprehensive admin dashboard with elephant services monitoring"

[api_service]
enabled = true
port = 5004
description = "REST API service with authentication and elephant services"

[social_network]
enabled = true
port = 5005
description = "Social network with user profiles and content sharing"

[portfolio]
enabled = true
port = 5006
description = "Personal portfolio website with project showcase and admin panel"

[saas_app]
enabled = true
port = 5007
description = "Software-as-a-Service application with subscription management"
''')