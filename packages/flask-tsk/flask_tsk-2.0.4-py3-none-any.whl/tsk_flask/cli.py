#!/usr/bin/env python3
"""
Flask-TSK CLI Tool
Command-line interface for managing Flask-TSK projects
"""

import argparse
import os
import sys
import logging
import sqlite3
import shutil
import datetime
from pathlib import Path
from typing import Optional

# Import ASCII art module
try:
    from .ascii_art import (
        show_success_banner,
        show_error_message,
        show_service_banner,
        show_peanut_operation,
        show_loading_animation,
        show_welcome_message
    )
    ASCII_ART_AVAILABLE = True
except ImportError:
    ASCII_ART_AVAILABLE = False
    def show_success_banner(): print("✅ Success!")
    def show_error_message(msg): print(f"❌ Error: {msg}")
    def show_service_banner(service, action=""): print(f"🔧 {service} - {action}")
    def show_peanut_operation(op): print(f"🥜 {op}")
    def show_loading_animation(msg): print(f"⏳ {msg}")
    def show_welcome_message(): print("🐘 Welcome to Flask-TSK!")

from .optimization_tools import get_asset_optimizer, get_layout_manager, optimize_project_assets

def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def create_project_structure(project_path: str, force: bool = False):
    """Create Flask-TSK project structure"""
    from . import FlaskTSK
    
    project_path = os.path.abspath(project_path)
    
    if not os.path.exists(project_path):
        os.makedirs(project_path)
        print(f"Created project directory: {project_path}")
    
    # Create a minimal Flask app to use FlaskTSK
    from flask import Flask
    
    app = Flask(__name__)
    tsk = FlaskTSK(app)
    
    # Setup project structure
    success = tsk.setup_project_structure(project_path)
    
    if success:
        show_success_banner()
        print(f"✅ Flask-TSK project structure created in: {project_path}")
        print("\n📁 Created folders:")
        folders = [
            'tsk/assets/css', 'tsk/assets/js', 'tsk/assets/images', 'tsk/assets/fonts', 'tsk/assets/icons',
            'tsk/layouts/headers', 'tsk/layouts/footers', 'tsk/layouts/navigation', 'tsk/layouts/sidebars', 'tsk/layouts/modals',
            'tsk/templates/base', 'tsk/templates/auth', 'tsk/templates/pages', 'tsk/templates/admin', 'tsk/templates/dashboard', 'tsk/templates/errors', 'tsk/templates/email',
            'tsk/components/navigation', 'tsk/components/forms', 'tsk/components/ui', 'tsk/components/layouts', 'tsk/components/ecommerce', 'tsk/components/blog', 'tsk/components/dashboard', 'tsk/components/cards', 'tsk/components/tables', 'tsk/components/buttons', 'tsk/components/alerts', 'tsk/components/modals', 'tsk/components/charts', 'tsk/components/widgets',
            'tsk/auth/templates', 'tsk/auth/components', 'tsk/auth/forms', 'tsk/auth/middleware',
            'tsk/menus/main', 'tsk/menus/sidebar', 'tsk/menus/user', 'tsk/menus/admin', 'tsk/menus/mobile',
            'tsk/navs/primary', 'tsk/navs/secondary', 'tsk/navs/breadcrumbs', 'tsk/navs/pagination', 'tsk/navs/tabs',
            'tsk/forms/auth', 'tsk/forms/user', 'tsk/forms/admin', 'tsk/forms/validation', 'tsk/forms/widgets',
            'tsk/ui/buttons', 'tsk/ui/inputs', 'tsk/ui/cards', 'tsk/ui/alerts', 'tsk/ui/modals', 'tsk/ui/tables', 'tsk/ui/charts', 'tsk/ui/progress', 'tsk/ui/badges', 'tsk/ui/tooltips',
            'tsk/optimization/scripts', 'tsk/optimization/tools',
            'tsk/config', 'tsk/config/themes', 'tsk/config/databases', 'tsk/config/security',
            'tsk/static/css', 'tsk/static/js', 'tsk/static/images', 'tsk/static/fonts', 'tsk/static/icons',
            'tsk/data', 'tsk/data/migrations', 'tsk/data/seeds', 'tsk/data/backups',
            'tsk/docs', 'tsk/docs/api', 'tsk/docs/components', 'tsk/docs/themes',
            'tsk/tests', 'tsk/tests/unit', 'tsk/tests/integration', 'tsk/tests/components',
            'tsk/logs', 'tsk/logs/access', 'tsk/logs/error', 'tsk/logs/debug',
            'tsk/build', 'tsk/cache'
        ]
        for folder in folders:
            print(f"   📂 {folder}")
        
        print("\n📄 Created files:")
        files = [
            'tsk/config/peanu.tsk',
            'tsk/templates/base/base.html',
            'tsk/templates/auth/login.html',
            'tsk/templates/auth/register.html',
            'tsk/layouts/navigation/default.html',
            'tsk/components/buttons/button.html',
            'tsk/components/cards/card.html',
            'tsk/assets/css/main.css',
            'tsk/assets/js/main.js',
            'tsk/docs/README.md'
        ]
        for file in files:
            print(f"   📄 {file}")
        
        print("\n🚀 Next steps:")
        print("   1. cd " + project_path)
        print("   2. flask-tsk db init")
        print("   3. python -m flask run")
        print("   4. Visit http://localhost:5000")
        print("\n📚 Documentation:")
        print("   - Check tsk/docs/README.md for project structure")
        print("   - Auth templates: tsk/templates/auth/")
        print("   - Components: tsk/components/")
        print("   - Base templates: tsk/templates/base/")
    else:
        show_error_message("Failed to create project structure")
        sys.exit(1)

def create_database(project_path: str, db_type: str = 'all', force: bool = False):
    """Create SQLite databases for Flask-TSK"""
    project_path = os.path.abspath(project_path)
    
    if not os.path.exists(project_path):
        show_error_message(f"Project path does not exist: {project_path}")
        sys.exit(1)
    
    # Create data directory
    data_dir = os.path.join(project_path, 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    databases = {
        'herd': {
            'file': 'herd_auth.db',
            'template': 'herd_auth.sql',
            'description': 'Herd Authentication Database'
        },
        'elephants': {
            'file': 'elephant_services.db',
            'template': 'elephant_services.sql',
            'description': 'Elephant Services Database'
        }
    }
    
    if db_type == 'all':
        db_list = databases.keys()
    elif db_type in databases:
        db_list = [db_type]
    else:
        show_error_message(f"Unknown database type: {db_type}")
        print(f"Available types: {', '.join(databases.keys())}, all")
        sys.exit(1)
    
    for db_name in db_list:
        db_config = databases[db_name]
        db_path = os.path.join(data_dir, db_config['file'])
        template_path = os.path.join(os.path.dirname(__file__), 'database_templates', db_config['template'])
        
        if os.path.exists(db_path) and not force:
            print(f"⚠️  Database {db_config['file']} already exists. Use --force to overwrite.")
            continue
        
        if not os.path.exists(template_path):
            show_error_message(f"Template file not found: {template_path}")
            continue
        
        try:
            show_loading_animation(f"Creating {db_config['description']}...")
            
            # Read SQL template
            with open(template_path, 'r') as f:
                sql_script = f.read()
            
            # Create database
            conn = sqlite3.connect(db_path)
            conn.executescript(sql_script)
            conn.close()
            
            print(f"✅ Created {db_config['description']}: {db_path}")
            
        except Exception as e:
            show_error_message(f"Failed to create {db_config['description']}: {e}")
            if os.path.exists(db_path):
                os.remove(db_path)
    
    print(f"\n📁 Databases created in: {data_dir}")
    print("\n🔧 Next steps:")
    print("   1. Update peanu.tsk with database paths")
    print("   2. Initialize Flask-TSK in your app")
    print("   3. Test authentication with admin@example.com / admin123")

def backup_database(project_path: str, db_name: str, backup_dir: str = None):
    """Backup SQLite database"""
    project_path = os.path.abspath(project_path)
    
    if not os.path.exists(project_path):
        show_error_message(f"Project path does not exist: {project_path}")
        sys.exit(1)
    
    data_dir = os.path.join(project_path, 'data')
    db_path = os.path.join(data_dir, f"{db_name}.db")
    
    if not os.path.exists(db_path):
        show_error_message(f"Database not found: {db_path}")
        sys.exit(1)
    
    if backup_dir is None:
        backup_dir = os.path.join(project_path, 'backups')
    
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backup_dir, f"{db_name}_{timestamp}.db")
    
    try:
        show_loading_animation(f"Backing up {db_name} database...")
        shutil.copy2(db_path, backup_path)
        print(f"✅ Database backed up to: {backup_path}")
    except Exception as e:
        show_error_message(f"Backup failed: {e}")
        sys.exit(1)

def restore_database(project_path: str, db_name: str, backup_file: str):
    """Restore SQLite database from backup"""
    project_path = os.path.abspath(project_path)
    
    if not os.path.exists(project_path):
        show_error_message(f"Project path does not exist: {project_path}")
        sys.exit(1)
    
    if not os.path.exists(backup_file):
        show_error_message(f"Backup file not found: {backup_file}")
        sys.exit(1)
    
    data_dir = os.path.join(project_path, 'data')
    db_path = os.path.join(data_dir, f"{db_name}.db")
    
    # Backup current database if it exists
    if os.path.exists(db_path):
        backup_database(project_path, db_name)
    
    try:
        show_loading_animation(f"Restoring {db_name} database...")
        shutil.copy2(backup_file, db_path)
        print(f"✅ Database restored from: {backup_file}")
    except Exception as e:
        show_error_message(f"Restore failed: {e}")
        sys.exit(1)

def list_databases(project_path: str):
    """List available databases"""
    project_path = os.path.abspath(project_path)
    
    if not os.path.exists(project_path):
        show_error_message(f"Project path does not exist: {project_path}")
        sys.exit(1)
    
    data_dir = os.path.join(project_path, 'data')
    
    if not os.path.exists(data_dir):
        print("📁 No data directory found")
        return
    
    print(f"📁 Databases in: {data_dir}")
    
    for file in os.listdir(data_dir):
        if file.endswith('.db'):
            db_path = os.path.join(data_dir, file)
            size = os.path.getsize(db_path)
            modified = os.path.getmtime(db_path)
            
            print(f"\n   📄 {file}")
            print(f"      Size: {size:,} bytes")
            print(f"      Modified: {datetime.datetime.fromtimestamp(modified)}")

def optimize_assets(project_path: str, minify: bool = True, obfuscate: bool = False,
                   compress_images: bool = True, gzip: bool = True, watch: bool = False):
    """Optimize project assets"""
    project_path = os.path.abspath(project_path)
    
    if not os.path.exists(project_path):
        show_error_message(f"Project path does not exist: {project_path}")
        sys.exit(1)
    
    show_service_banner('css', 'Asset Optimization')
    print(f"🔧 Optimizing assets in: {project_path}")
    
    if watch:
        print("👀 Starting asset watcher...")
        optimizer = get_asset_optimizer(project_path)
        observer = optimizer.watch_assets()
        
        if observer:
            try:
                print("Press Ctrl+C to stop watching")
                observer.join()
            except KeyboardInterrupt:
                observer.stop()
                observer.join()
                print("\n👋 Asset watching stopped")
        else:
            print("❌ Asset watching not available")
    else:
        results = optimize_project_assets(
            project_path,
            minify=minify,
            obfuscate=obfuscate,
            compress_images=compress_images,
            gzip=gzip
        )
        
        print("\n📊 Optimization Results:")
        for category, files in results.items():
            if files:
                print(f"   {category.title()}: {len(files)} files")
                for file in files:
                    print(f"     📄 {os.path.basename(file)}")

def generate_manifest(project_path: str, output_file: str = None):
    """Generate asset manifest"""
    project_path = os.path.abspath(project_path)
    
    if not os.path.exists(project_path):
        show_error_message(f"Project path does not exist: {project_path}")
        sys.exit(1)
    
    optimizer = get_asset_optimizer(project_path)
    manifest = optimizer.generate_asset_manifest()
    
    if output_file:
        import json
        with open(output_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        print(f"📄 Asset manifest saved to: {output_file}")
    else:
        print("📋 Asset Manifest:")
        for original, hashed in manifest.items():
            print(f"   {original} -> {hashed}")

def list_layouts(project_path: str):
    """List available layouts"""
    project_path = os.path.abspath(project_path)
    
    if not os.path.exists(project_path):
        show_error_message(f"Project path does not exist: {project_path}")
        sys.exit(1)
    
    layout_manager = get_layout_manager(project_path)
    layouts_path = os.path.join(project_path, 'tsk', 'layouts')
    
    print(f"📁 Available layouts in: {layouts_path}")
    
    for layout_type in ['headers', 'footers', 'navigation']:
        layout_dir = os.path.join(layouts_path, layout_type)
        if os.path.exists(layout_dir):
            print(f"\n   {layout_type.title()}:")
            for file in os.listdir(layout_dir):
                if file.endswith('.html'):
                    print(f"     📄 {file}")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Flask-TSK CLI Tool - Manage Flask-TSK projects and assets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  flask-tsk init my-project          # Create new Flask-TSK project
  flask-tsk db init my-project       # Initialize databases
  flask-tsk db backup my-project     # Backup databases
  flask-tsk optimize my-project      # Optimize all assets
  flask-tsk watch my-project         # Watch assets for changes
  flask-tsk manifest my-project      # Generate asset manifest
  flask-tsk layouts my-project       # List available layouts
        """
    )
    
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize new Flask-TSK project')
    init_parser.add_argument('project_path', help='Project directory path')
    init_parser.add_argument('--force', action='store_true',
                           help='Force creation even if directory exists')
    
    # Database commands
    db_parser = subparsers.add_parser('db', help='Database management commands')
    db_subparsers = db_parser.add_subparsers(dest='db_command', help='Database commands')
    
    # DB init command
    db_init_parser = db_subparsers.add_parser('init', help='Initialize databases')
    db_init_parser.add_argument('project_path', help='Project directory path')
    db_init_parser.add_argument('--type', choices=['herd', 'elephants', 'all'], default='all',
                               help='Database type to create')
    db_init_parser.add_argument('--force', action='store_true',
                               help='Force overwrite existing databases')
    
    # DB backup command
    db_backup_parser = db_subparsers.add_parser('backup', help='Backup databases')
    db_backup_parser.add_argument('project_path', help='Project directory path')
    db_backup_parser.add_argument('db_name', help='Database name (herd, elephants)')
    db_backup_parser.add_argument('--backup-dir', help='Backup directory')
    
    # DB restore command
    db_restore_parser = db_subparsers.add_parser('restore', help='Restore database from backup')
    db_restore_parser.add_argument('project_path', help='Project directory path')
    db_restore_parser.add_argument('db_name', help='Database name (herd, elephants)')
    db_restore_parser.add_argument('backup_file', help='Backup file path')
    
    # DB list command
    db_list_parser = db_subparsers.add_parser('list', help='List available databases')
    db_list_parser.add_argument('project_path', help='Project directory path')
    
    # Optimize command
    optimize_parser = subparsers.add_parser('optimize', help='Optimize project assets')
    optimize_parser.add_argument('project_path', help='Project directory path')
    optimize_parser.add_argument('--no-minify', action='store_true',
                               help='Skip minification')
    optimize_parser.add_argument('--obfuscate', action='store_true',
                               help='Obfuscate JavaScript')
    optimize_parser.add_argument('--no-compress-images', action='store_true',
                               help='Skip image compression')
    optimize_parser.add_argument('--no-gzip', action='store_true',
                               help='Skip gzip compression')
    
    # Watch command
    watch_parser = subparsers.add_parser('watch', help='Watch assets for changes')
    watch_parser.add_argument('project_path', help='Project directory path')
    
    # Manifest command
    manifest_parser = subparsers.add_parser('manifest', help='Generate asset manifest')
    manifest_parser.add_argument('project_path', help='Project directory path')
    manifest_parser.add_argument('--output', '-o', help='Output file path')
    
    # Layouts command
    layouts_parser = subparsers.add_parser('layouts', help='List available layouts')
    layouts_parser.add_argument('project_path', help='Project directory path')
    
    args = parser.parse_args()
    
    if not args.command:
        show_welcome_message()
        parser.print_help()
        sys.exit(1)
    
    setup_logging(args.verbose)
    
    try:
        if args.command == 'init':
            create_project_structure(args.project_path, args.force)
        elif args.command == 'db':
            if not args.db_command:
                db_parser.print_help()
                sys.exit(1)
            
            if args.db_command == 'init':
                create_database(args.project_path, args.type, args.force)
            elif args.db_command == 'backup':
                backup_database(args.project_path, args.db_name, args.backup_dir)
            elif args.db_command == 'restore':
                restore_database(args.project_path, args.db_name, args.backup_file)
            elif args.db_command == 'list':
                list_databases(args.project_path)
            else:
                show_error_message(f"Unknown database command: {args.db_command}")
                sys.exit(1)
        elif args.command == 'optimize':
            optimize_assets(
                args.project_path,
                minify=not args.no_minify,
                obfuscate=args.obfuscate,
                compress_images=not args.no_compress_images,
                gzip=not args.no_gzip
            )
        elif args.command == 'watch':
            optimize_assets(args.project_path, watch=True)
        elif args.command == 'manifest':
            generate_manifest(args.project_path, args.output)
        elif args.command == 'layouts':
            list_layouts(args.project_path)
        else:
            show_error_message(f"Unknown command: {args.command}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n👋 Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        show_error_message(str(e))
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main() 