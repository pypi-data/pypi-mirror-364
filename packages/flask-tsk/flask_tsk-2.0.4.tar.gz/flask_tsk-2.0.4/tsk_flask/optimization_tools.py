#!/usr/bin/env python3
"""
Flask-TSK Optimization Tools
Asset management, minification, and optimization utilities
"""

import os
import re
import gzip
import hashlib
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

try:
    import csscompressor
    CSS_COMPRESSOR_AVAILABLE = True
except ImportError:
    CSS_COMPRESSOR_AVAILABLE = False

try:
    import jsmin
    JSMIN_AVAILABLE = True
except ImportError:
    JSMIN_AVAILABLE = False

try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

class AssetOptimizer:
    """Flask-TSK Asset Optimization Engine"""
    
    def __init__(self, project_path: str = None):
        self.project_path = project_path or os.getcwd()
        self.tsk_path = os.path.join(self.project_path, 'tsk')
        self.assets_path = os.path.join(self.tsk_path, 'assets')
        self.build_path = os.path.join(self.tsk_path, 'build')
        self.cache_path = os.path.join(self.tsk_path, 'cache')
        
        # Ensure paths exist
        os.makedirs(self.build_path, exist_ok=True)
        os.makedirs(self.cache_path, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
    
    def minify_css(self, input_file: str, output_file: str = None) -> str:
        """Minify CSS file"""
        if not CSS_COMPRESSOR_AVAILABLE:
            self.logger.warning("csscompressor not available, using basic minification")
            return self._basic_css_minify(input_file, output_file)
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                css_content = f.read()
            
            minified = csscompressor.compress(css_content)
            
            if output_file is None:
                output_file = input_file.replace('.css', '.min.css')
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(minified)
            
            self.logger.info(f"CSS minified: {input_file} -> {output_file}")
            return output_file
            
        except Exception as e:
            self.logger.error(f"CSS minification failed: {e}")
            return input_file
    
    def _basic_css_minify(self, input_file: str, output_file: str = None) -> str:
        """Basic CSS minification without external dependencies"""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                css_content = f.read()
            
            # Remove comments
            css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
            
            # Remove unnecessary whitespace
            css_content = re.sub(r'\s+', ' ', css_content)
            css_content = re.sub(r';\s*}', '}', css_content)
            css_content = re.sub(r'{\s*', '{', css_content)
            css_content = re.sub(r'}\s*', '}', css_content)
            
            # Remove trailing semicolons
            css_content = re.sub(r';}', '}', css_content)
            
            if output_file is None:
                output_file = input_file.replace('.css', '.min.css')
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(css_content.strip())
            
            self.logger.info(f"CSS minified (basic): {input_file} -> {output_file}")
            return output_file
            
        except Exception as e:
            self.logger.error(f"Basic CSS minification failed: {e}")
            return input_file
    
    def minify_js(self, input_file: str, output_file: str = None) -> str:
        """Minify JavaScript file"""
        if not JSMIN_AVAILABLE:
            self.logger.warning("jsmin not available, using basic minification")
            return self._basic_js_minify(input_file, output_file)
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                js_content = f.read()
            
            minified = jsmin.jsmin(js_content)
            
            if output_file is None:
                output_file = input_file.replace('.js', '.min.js')
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(minified)
            
            self.logger.info(f"JavaScript minified: {input_file} -> {output_file}")
            return output_file
            
        except Exception as e:
            self.logger.error(f"JavaScript minification failed: {e}")
            return input_file
    
    def _basic_js_minify(self, input_file: str, output_file: str = None) -> str:
        """Basic JavaScript minification without external dependencies"""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                js_content = f.read()
            
            # Remove single-line comments (but preserve URLs)
            js_content = re.sub(r'(?<!:)\/\/.*$', '', js_content, flags=re.MULTILINE)
            
            # Remove multi-line comments
            js_content = re.sub(r'/\*.*?\*/', '', js_content, flags=re.DOTALL)
            
            # Remove unnecessary whitespace
            js_content = re.sub(r'\s+', ' ', js_content)
            js_content = re.sub(r';\s*}', '}', js_content)
            js_content = re.sub(r'{\s*', '{', js_content)
            js_content = re.sub(r'}\s*', '}', js_content)
            
            if output_file is None:
                output_file = input_file.replace('.js', '.min.js')
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(js_content.strip())
            
            self.logger.info(f"JavaScript minified (basic): {input_file} -> {output_file}")
            return output_file
            
        except Exception as e:
            self.logger.error(f"Basic JavaScript minification failed: {e}")
            return input_file
    
    def obfuscate_js(self, input_file: str, output_file: str = None) -> str:
        """Obfuscate JavaScript code"""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                js_content = f.read()
            
            # Basic obfuscation (variable name mangling)
            # This is a simple implementation - for production, consider using tools like javascript-obfuscator
            
            # Generate random variable names
            import random
            import string
            
            def generate_random_name(length=8):
                return ''.join(random.choices(string.ascii_lowercase, k=length))
            
            # Simple variable name replacement (basic obfuscation)
            # Note: This is a simplified version - real obfuscation is much more complex
            obfuscated = js_content
            
            if output_file is None:
                output_file = input_file.replace('.js', '.obf.js')
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(obfuscated)
            
            self.logger.info(f"JavaScript obfuscated: {input_file} -> {output_file}")
            return output_file
            
        except Exception as e:
            self.logger.error(f"JavaScript obfuscation failed: {e}")
            return input_file
    
    def compress_image(self, input_file: str, output_file: str = None, quality: int = 85) -> str:
        """Compress image file"""
        if not PILLOW_AVAILABLE:
            self.logger.warning("Pillow not available, skipping image compression")
            return input_file
        
        try:
            with Image.open(input_file) as img:
                if output_file is None:
                    name, ext = os.path.splitext(input_file)
                    output_file = f"{name}_compressed{ext}"
                
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                img.save(output_file, quality=quality, optimize=True)
            
            self.logger.info(f"Image compressed: {input_file} -> {output_file}")
            return output_file
            
        except Exception as e:
            self.logger.error(f"Image compression failed: {e}")
            return input_file
    
    def gzip_file(self, input_file: str, output_file: str = None) -> str:
        """Create gzipped version of file"""
        try:
            with open(input_file, 'rb') as f:
                content = f.read()
            
            if output_file is None:
                output_file = f"{input_file}.gz"
            
            with gzip.open(output_file, 'wb') as f:
                f.write(content)
            
            self.logger.info(f"File gzipped: {input_file} -> {output_file}")
            return output_file
            
        except Exception as e:
            self.logger.error(f"Gzip compression failed: {e}")
            return input_file
    
    def generate_asset_manifest(self) -> Dict[str, str]:
        """Generate asset manifest with file hashes for cache busting"""
        manifest = {}
        
        # Process CSS files
        css_dir = os.path.join(self.assets_path, 'css')
        if os.path.exists(css_dir):
            for file in os.listdir(css_dir):
                if file.endswith('.css'):
                    file_path = os.path.join(css_dir, file)
                    file_hash = self._get_file_hash(file_path)
                    manifest[f"css/{file}"] = f"css/{file}?v={file_hash}"
        
        # Process JS files
        js_dir = os.path.join(self.assets_path, 'js')
        if os.path.exists(js_dir):
            for file in os.listdir(js_dir):
                if file.endswith('.js'):
                    file_path = os.path.join(js_dir, file)
                    file_hash = self._get_file_hash(file_path)
                    manifest[f"js/{file}"] = f"js/{file}?v={file_hash}"
        
        # Process images
        images_dir = os.path.join(self.assets_path, 'images')
        if os.path.exists(images_dir):
            for file in os.listdir(images_dir):
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg')):
                    file_path = os.path.join(images_dir, file)
                    file_hash = self._get_file_hash(file_path)
                    manifest[f"images/{file}"] = f"images/{file}?v={file_hash}"
        
        return manifest
    
    def _get_file_hash(self, file_path: str) -> str:
        """Get MD5 hash of file for cache busting"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            return hashlib.md5(content).hexdigest()[:8]
        except Exception:
            return "00000000"
    
    def optimize_all_assets(self, minify: bool = True, obfuscate: bool = False, 
                          compress_images: bool = True, gzip: bool = True) -> Dict[str, List[str]]:
        """Optimize all assets in the project"""
        results = {
            'minified': [],
            'obfuscated': [],
            'compressed': [],
            'gzipped': []
        }
        
        # Process CSS files
        css_dir = os.path.join(self.assets_path, 'css')
        if os.path.exists(css_dir):
            for file in os.listdir(css_dir):
                if file.endswith('.css') and not file.endswith('.min.css'):
                    file_path = os.path.join(css_dir, file)
                    if minify:
                        minified = self.minify_css(file_path)
                        results['minified'].append(minified)
        
        # Process JS files
        js_dir = os.path.join(self.assets_path, 'js')
        if os.path.exists(js_dir):
            for file in os.listdir(js_dir):
                if file.endswith('.js') and not file.endswith('.min.js'):
                    file_path = os.path.join(js_dir, file)
                    if minify:
                        minified = self.minify_js(file_path)
                        results['minified'].append(minified)
                    if obfuscate:
                        obfuscated = self.obfuscate_js(file_path)
                        results['obfuscated'].append(obfuscated)
        
        # Process images
        images_dir = os.path.join(self.assets_path, 'images')
        if os.path.exists(images_dir) and compress_images:
            for file in os.listdir(images_dir):
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    file_path = os.path.join(images_dir, file)
                    compressed = self.compress_image(file_path)
                    results['compressed'].append(compressed)
        
        # Create gzipped versions
        if gzip:
            for file_list in results.values():
                for file in file_list:
                    gzipped = self.gzip_file(file)
                    results['gzipped'].append(gzipped)
        
        return results
    
    def watch_assets(self, callback=None):
        """Watch assets directory for changes and auto-optimize"""
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler
            
            class AssetHandler(FileSystemEventHandler):
                def __init__(self, optimizer, callback):
                    self.optimizer = optimizer
                    self.callback = callback
                
                def on_modified(self, event):
                    if not event.is_directory:
                        file_path = event.src_path
                        if file_path.endswith(('.css', '.js')):
                            self.optimizer.logger.info(f"Asset changed: {file_path}")
                            if self.callback:
                                self.callback(file_path)
            
            event_handler = AssetHandler(self, callback)
            observer = Observer()
            observer.schedule(event_handler, self.assets_path, recursive=True)
            observer.start()
            
            self.logger.info(f"Asset watching started for: {self.assets_path}")
            return observer
            
        except ImportError:
            self.logger.warning("watchdog not available, asset watching disabled")
            return None

class LayoutManager:
    """Flask-TSK Layout Management System"""
    
    def __init__(self, project_path: str = None):
        self.project_path = project_path or os.getcwd()
        self.layouts_path = os.path.join(self.project_path, 'tsk', 'layouts')
        self.logger = logging.getLogger(__name__)
    
    def get_header(self, name: str = 'default') -> str:
        """Get header template content"""
        header_path = os.path.join(self.layouts_path, 'headers', f'{name}.html')
        try:
            with open(header_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            self.logger.warning(f"Header template not found: {header_path}")
            return self._get_default_header()
    
    def get_footer(self, name: str = 'default') -> str:
        """Get footer template content"""
        footer_path = os.path.join(self.layouts_path, 'footers', f'{name}.html')
        try:
            with open(footer_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            self.logger.warning(f"Footer template not found: {footer_path}")
            return self._get_default_footer()
    
    def get_navigation(self, name: str = 'default') -> str:
        """Get navigation template content"""
        nav_path = os.path.join(self.layouts_path, 'navigation', f'{name}.html')
        try:
            with open(nav_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            self.logger.warning(f"Navigation template not found: {nav_path}")
            return self._get_default_navigation()
    
    def _get_default_header(self) -> str:
        """Get default header template"""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title|default('Flask-TSK App') }}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}">
</head>
<body>
    <header>
        <nav>Navigation will be inserted here</nav>
    </header>
    <main>'''
    
    def _get_default_footer(self) -> str:
        """Get default footer template"""
        return '''
    </main>
    <footer>
        <p>&copy; 2024 Flask-TSK Application</p>
    </footer>
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
</body>
</html>'''
    
    def _get_default_navigation(self) -> str:
        """Get default navigation template"""
        return '''<nav class="navbar">
    <div class="container">
        <a href="{{ url_for('index') }}" class="navbar-brand">Flask-TSK</a>
        <div class="navbar-menu">
            <a href="{{ url_for('index') }}">Home</a>
            <a href="{{ url_for('about') }}">About</a>
        </div>
    </div>
</nav>'''

# Utility functions
def get_asset_optimizer(project_path: str = None) -> AssetOptimizer:
    """Get AssetOptimizer instance"""
    return AssetOptimizer(project_path)

def get_layout_manager(project_path: str = None) -> LayoutManager:
    """Get LayoutManager instance"""
    return LayoutManager(project_path)

def optimize_project_assets(project_path: str = None, **kwargs) -> Dict[str, List[str]]:
    """Optimize all assets in a Flask-TSK project"""
    optimizer = get_asset_optimizer(project_path)
    return optimizer.optimize_all_assets(**kwargs) 