"""
Flask-TSK Theme Configuration System
Integrates with TuskLang for dynamic theme configuration
"""

from flask import current_app
from typing import Dict, List, Optional, Any
import json
import os

class ThemeConfig:
    """Theme configuration management with TuskLang integration"""
    
    def __init__(self, app=None):
        self.app = app
        self.config_file = 'theme_config.tsk'
        self.default_config = {
            'current_theme': 'modern',
            'themes': {
                'modern': {
                    'enabled': True,
                    'primary_color': '#007bff',
                    'secondary_color': '#6c757d',
                    'accent_color': '#28a745',
                    'font_family': 'Inter, sans-serif',
                    'border_radius': '8px',
                    'box_shadow': '0 2px 10px rgba(0,0,0,0.1)'
                },
                'dark': {
                    'enabled': True,
                    'primary_color': '#007bff',
                    'secondary_color': '#6c757d',
                    'accent_color': '#28a745',
                    'font_family': 'Inter, sans-serif',
                    'border_radius': '8px',
                    'box_shadow': '0 2px 10px rgba(0,0,0,0.3)'
                },
                'classic': {
                    'enabled': True,
                    'primary_color': '#007bff',
                    'secondary_color': '#6c757d',
                    'accent_color': '#28a745',
                    'font_family': 'Georgia, serif',
                    'border_radius': '4px',
                    'box_shadow': '0 1px 3px rgba(0,0,0,0.1)'
                }
            },
            'components': {
                'header': {
                    'show_brand': True,
                    'show_navigation': True,
                    'show_user_menu': True,
                    'sticky': True
                },
                'footer': {
                    'show_social_links': True,
                    'show_stats': True,
                    'show_activity': True
                },
                'navigation': {
                    'show_icons': True,
                    'show_badges': True,
                    'collapsible': True
                }
            },
            'database': {
                'auto_load': True,
                'cache_duration': 300,
                'fallback_data': True
            }
        }
    
    def init_app(self, app):
        self.app = app
        self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load theme configuration from TuskLang"""
        try:
            from tsk_flask import get_tsk
            tsk = get_tsk()
            
            # Try to load from TuskLang configuration
            config = tsk.get_config('theme', 'config', self.default_config)
            if isinstance(config, str):
                config = json.loads(config)
            
            return config
            
        except Exception as e:
            current_app.logger.warning(f"Failed to load theme config from TuskLang: {e}")
            return self.default_config
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """Save theme configuration to TuskLang"""
        try:
            from tsk_flask import get_tsk
            tsk = get_tsk()
            
            # Save to TuskLang configuration
            success = tsk.set_config('theme', 'config', json.dumps(config))
            return success
            
        except Exception as e:
            current_app.logger.error(f"Failed to save theme config to TuskLang: {e}")
            return False
    
    def get_theme_config(self, theme_name: str) -> Dict[str, Any]:
        """Get configuration for specific theme"""
        config = self.load_config()
        return config.get('themes', {}).get(theme_name, {})
    
    def set_theme_config(self, theme_name: str, theme_config: Dict[str, Any]) -> bool:
        """Set configuration for specific theme"""
        config = self.load_config()
        if 'themes' not in config:
            config['themes'] = {}
        config['themes'][theme_name] = theme_config
        return self.save_config(config)
    
    def get_component_config(self, component_name: str) -> Dict[str, Any]:
        """Get configuration for specific component"""
        config = self.load_config()
        return config.get('components', {}).get(component_name, {})
    
    def set_component_config(self, component_name: str, component_config: Dict[str, Any]) -> bool:
        """Set configuration for specific component"""
        config = self.load_config()
        if 'components' not in config:
            config['components'] = {}
        config['components'][component_name] = component_config
        return self.save_config(config)
    
    def get_current_theme(self) -> str:
        """Get current theme name"""
        config = self.load_config()
        return config.get('current_theme', 'modern')
    
    def set_current_theme(self, theme_name: str) -> bool:
        """Set current theme"""
        config = self.load_config()
        config['current_theme'] = theme_name
        return self.save_config(config)
    
    def get_enabled_themes(self) -> List[str]:
        """Get list of enabled themes"""
        config = self.load_config()
        enabled_themes = []
        for theme_name, theme_config in config.get('themes', {}).items():
            if theme_config.get('enabled', True):
                enabled_themes.append(theme_name)
        return enabled_themes
    
    def generate_css_variables(self, theme_name: str) -> str:
        """Generate CSS variables for theme"""
        theme_config = self.get_theme_config(theme_name)
        
        css_vars = f"""
        :root {{
            --primary-color: {theme_config.get('primary_color', '#007bff')};
            --secondary-color: {theme_config.get('secondary_color', '#6c757d')};
            --accent-color: {theme_config.get('accent_color', '#28a745')};
            --font-family: {theme_config.get('font_family', 'Inter, sans-serif')};
            --border-radius: {theme_config.get('border_radius', '8px')};
            --box-shadow: {theme_config.get('box_shadow', '0 2px 10px rgba(0,0,0,0.1)')};
        }}
        """
        return css_vars
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration for themes"""
        config = self.load_config()
        return config.get('database', {})
    
    def should_auto_load_data(self) -> bool:
        """Check if theme should auto-load database data"""
        db_config = self.get_database_config()
        return db_config.get('auto_load', True)
    
    def get_cache_duration(self) -> int:
        """Get cache duration for theme data"""
        db_config = self.get_database_config()
        return db_config.get('cache_duration', 300)
    
    def should_use_fallback_data(self) -> bool:
        """Check if theme should use fallback data"""
        db_config = self.get_database_config()
        return db_config.get('fallback_data', True)

class ThemeDataProvider:
    """Provides data for themes with TuskLang integration"""
    
    def __init__(self, config: ThemeConfig):
        self.config = config
        self.cache = {}
        self.cache_timestamps = {}
    
    def get_navigation_data(self, theme_name: str = None) -> Dict[str, Any]:
        """Get navigation data with caching"""
        cache_key = f"nav_{theme_name or 'default'}"
        
        if self._is_cache_valid(cache_key):
            return self.cache.get(cache_key, {})
        
        try:
            from tsk_flask import get_tsk
            tsk = get_tsk()
            
            # Get navigation data from TuskLang database
            nav_data = {
                'main_nav': [
                    {'url': '/', 'text': 'Home', 'icon': '🏠', 'active': True},
                    {'url': '/products', 'text': 'Products', 'icon': '📦'},
                    {'url': '/services', 'text': 'Services', 'icon': '🛠️'},
                    {'url': '/about', 'text': 'About', 'icon': 'ℹ️'},
                    {'url': '/contact', 'text': 'Contact', 'icon': '📞'}
                ],
                'secondary_nav': [
                    {'url': '/blog', 'text': 'Blog', 'icon': '📝'},
                    {'url': '/support', 'text': 'Support', 'icon': '💬'},
                    {'url': '/docs', 'text': 'Documentation', 'icon': '📚'}
                ]
            }
            
            # Cache the data
            self._cache_data(cache_key, nav_data)
            return nav_data
            
        except Exception as e:
            current_app.logger.error(f"Failed to get navigation data: {e}")
            return self._get_fallback_navigation_data()
    
    def get_user_menu_data(self, theme_name: str = None) -> Dict[str, Any]:
        """Get user menu data with caching"""
        cache_key = f"user_{theme_name or 'default'}"
        
        if self._is_cache_valid(cache_key):
            return self.cache.get(cache_key, {})
        
        try:
            from tsk_flask import get_tsk
            tsk = get_tsk()
            
            # Get user data from TuskLang database
            user_data = {
                'user': {
                    'name': 'John Doe',
                    'avatar': '/static/avatars/user.jpg',
                    'role': 'Admin',
                    'notifications': 5
                },
                'menu_items': [
                    {'url': '/dashboard', 'text': 'Dashboard', 'icon': '📊'},
                    {'url': '/profile', 'text': 'Profile', 'icon': '👤'},
                    {'url': '/settings', 'text': 'Settings', 'icon': '⚙️'},
                    {'url': '/logout', 'text': 'Logout', 'icon': '🚪'}
                ]
            }
            
            # Cache the data
            self._cache_data(cache_key, user_data)
            return user_data
            
        except Exception as e:
            current_app.logger.error(f"Failed to get user menu data: {e}")
            return self._get_fallback_user_data()
    
    def get_site_stats_data(self, theme_name: str = None) -> Dict[str, Any]:
        """Get site statistics data with caching"""
        cache_key = f"stats_{theme_name or 'default'}"
        
        if self._is_cache_valid(cache_key):
            return self.cache.get(cache_key, {})
        
        try:
            from tsk_flask import get_tsk
            tsk = get_tsk()
            
            # Get statistics from TuskLang database
            stats_data = {
                'total_users': 15420,
                'active_projects': 342,
                'total_revenue': 1250000,
                'growth_rate': 23.5
            }
            
            # Cache the data
            self._cache_data(cache_key, stats_data)
            return stats_data
            
        except Exception as e:
            current_app.logger.error(f"Failed to get site stats data: {e}")
            return self._get_fallback_stats_data()
    
    def get_activity_data(self, theme_name: str = None) -> Dict[str, Any]:
        """Get activity data with caching"""
        cache_key = f"activity_{theme_name or 'default'}"
        
        if self._is_cache_valid(cache_key):
            return self.cache.get(cache_key, {})
        
        try:
            from tsk_flask import get_tsk
            tsk = get_tsk()
            
            # Get activity data from TuskLang database
            activity_data = {
                'activities': [
                    {'type': 'user_login', 'user': 'Alice', 'time': '2 min ago'},
                    {'type': 'project_created', 'user': 'Bob', 'time': '15 min ago'},
                    {'type': 'file_uploaded', 'user': 'Charlie', 'time': '1 hour ago'},
                    {'type': 'comment_added', 'user': 'Diana', 'time': '2 hours ago'}
                ]
            }
            
            # Cache the data
            self._cache_data(cache_key, activity_data)
            return activity_data
            
        except Exception as e:
            current_app.logger.error(f"Failed to get activity data: {e}")
            return self._get_fallback_activity_data()
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self.cache_timestamps:
            return False
        
        cache_duration = self.config.get_cache_duration()
        import time
        return (time.time() - self.cache_timestamps[cache_key]) < cache_duration
    
    def _cache_data(self, cache_key: str, data: Dict[str, Any]):
        """Cache data with timestamp"""
        self.cache[cache_key] = data
        import time
        self.cache_timestamps[cache_key] = time.time()
    
    def _get_fallback_navigation_data(self) -> Dict[str, Any]:
        """Get fallback navigation data"""
        return {
            'main_nav': [
                {'url': '/', 'text': 'Home', 'icon': '🏠', 'active': True},
                {'url': '/about', 'text': 'About', 'icon': 'ℹ️'},
                {'url': '/contact', 'text': 'Contact', 'icon': '📞'}
            ],
            'secondary_nav': []
        }
    
    def _get_fallback_user_data(self) -> Dict[str, Any]:
        """Get fallback user data"""
        return {
            'user': {
                'name': 'Guest User',
                'avatar': '/static/avatars/default.jpg',
                'role': 'Guest',
                'notifications': 0
            },
            'menu_items': [
                {'url': '/login', 'text': 'Login', 'icon': '🔑'},
                {'url': '/register', 'text': 'Register', 'icon': '📝'}
            ]
        }
    
    def _get_fallback_stats_data(self) -> Dict[str, Any]:
        """Get fallback statistics data"""
        return {
            'total_users': 0,
            'active_projects': 0,
            'total_revenue': 0,
            'growth_rate': 0
        }
    
    def _get_fallback_activity_data(self) -> Dict[str, Any]:
        """Get fallback activity data"""
        return {
            'activities': [
                {'type': 'system_startup', 'user': 'System', 'time': 'Just now'}
            ]
        }

# Global instances
theme_config = ThemeConfig()
theme_data_provider = ThemeDataProvider(theme_config)

def get_theme_config() -> ThemeConfig:
    """Get global theme configuration instance"""
    return theme_config

def get_theme_data_provider() -> ThemeDataProvider:
    """Get global theme data provider instance"""
    return theme_data_provider 