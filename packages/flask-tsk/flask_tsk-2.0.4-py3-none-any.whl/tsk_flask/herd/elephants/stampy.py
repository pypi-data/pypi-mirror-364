"""
<?tusk> TuskPython Stampy - The App Installer
==========================================

🐘 BACKSTORY: Stampy - The Simpsons' Elephant
--------------------------------------------
In The Simpsons episode "Bart Gets an Elephant," Bart wins Stampy from a
radio contest. Stampy quickly proves to be more than the family can handle -
eating enormous amounts of food, destroying fences, and generally causing
chaos. Despite the mayhem, Stampy is lovable and eventually finds a home
at an animal refuge. His brief stay with the Simpsons was memorable for
his size, appetite, and ability to "install" himself anywhere.

WHY THIS NAME: Like Stampy who could break through any barrier and make
himself at home anywhere, this installer helps you quickly "stomp" pre-built
apps into your project. Stampy was too big to ignore and changed everything
when he arrived - just like these powerful app installations that transform
your project instantly.

"Stampy! Stampy! Where are you boy?" - Bart Simpson

FEATURES:
- One-command app installations
- Pre-built application templates
- Dependency resolution
- Database migration handling
- Configuration wizards
- Rollback support
- App marketplace integration

@package TuskPython\Elephants
@author  TuskPython Team
@since   1.0.0
"""

import os
import json
import shutil
import zipfile
import tarfile
import hashlib
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import requests
from flask import current_app
import yaml


@dataclass
class AppInfo:
    """Represents an app in the catalog"""
    name: str
    description: str
    size: str
    features: List[str]
    requirements: Dict[str, Any]
    version: str
    package: str
    hash: Optional[str] = None
    config_prompts: Optional[Dict] = None
    post_install: Optional[str] = None


@dataclass
class InstalledApp:
    """Represents an installed app"""
    name: str
    version: str
    path: str
    installed_at: float
    size: str
    features: List[str]


class Stampy:
    """
    Stampy - The App Installer
    
    Like Stampy who could install himself anywhere, this class helps you
    quickly install pre-built applications into your Flask-TSK project.
    """
    
    def __init__(self, app=None):
        self.available_apps = {}
        self.installed_apps = {}
        self.app_repository = 'https://apps.tuskpython.com/'
        self.local_cache = Path('cache/stampy')
        self.install_path = Path('installed-apps')
        self.backup_path = Path('backups/stampy')
        
        # Initialize with Flask app if provided
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize Stampy with Flask app"""
        self.app = app
        
        # Create necessary directories
        self.ensure_directories()
        
        # Load configurations
        self.load_app_catalog()
        self.scan_installed_apps()
    
    def ensure_directories(self):
        """Ensure all required directories exist"""
        dirs = [
            self.local_cache,
            self.install_path,
            self.backup_path,
            self.local_cache / 'downloads',
            self.local_cache / 'temp'
        ]
        
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def install(self, app_name: str, options: Dict = None) -> bool:
        """Install an app - Stampy stomps it into place!"""
        options = options or {}
        
        print(f"🐘 STAMPY IS INSTALLING: {app_name}")
        print("Stand back! This elephant needs room to work!\n")
        
        try:
            # Check if app exists in catalog
            if app_name not in self.available_apps:
                raise Exception(f"D'oh! Stampy can't find '{app_name}' in the catalog!")
            
            # Check if already installed
            if self.is_installed(app_name) and not options.get('force'):
                raise Exception(f"Stampy already installed {app_name}! Use --force to reinstall.")
            
            app = self.available_apps[app_name]
            
            # Show installation plan
            self.show_installation_plan(app)
            
            # Check requirements
            print("📋 Checking requirements...")
            self.check_requirements(app)
            
            # Download app package
            print("\n📦 Downloading package...")
            package_path = self.download_package(app)
            
            # Extract and install
            print("\n🔨 Extracting package...")
            install_path = self.extract_package(package_path, app)
            
            # Run installation scripts
            print("\n🚀 Running installation scripts...")
            self.run_install_scripts(app, install_path)
            
            # Configure the app
            print("\n⚙️  Configuring the app...")
            self.configure_app(app, options)
            
            # Register as installed
            print("\n📝 Registering installation...")
            self.register_installation(app)
            
            print(f"\n✅ Stampy successfully installed {app_name}!")
            print("🎺 *triumphant elephant trumpet*\n")
            
            # Show post-install instructions
            self.show_post_install_instructions(app)
            
            return True
            
        except Exception as e:
            print(f"\n❌ Stampy encountered a problem: {e}")
            print("🐘 *sad elephant noises*")
            
            # Attempt rollback
            if 'install_path' in locals() and install_path.exists():
                print("\n🔄 Attempting rollback...")
                self.rollback_installation(app_name, install_path)
            
            return False
    
    def check_requirements(self, app: AppInfo):
        """Check if all requirements are met"""
        missing = []
        warnings = []
        
        # Check Python version
        if 'python' in app.requirements:
            required = app.requirements['python']
            if not self.check_python_version(required):
                missing.append(f"Python {required} or higher")
        
        # Check Python packages
        if 'packages' in app.requirements:
            for package in app.requirements['packages']:
                if not self.check_package_installed(package):
                    missing.append(f"Python package: {package}")
        
        # Check disk space
        if 'disk_space' in app.requirements:
            required_space = self.parse_size(app.requirements['disk_space'])
            free_space = shutil.disk_usage('.').free
            if free_space < required_space:
                missing.append(f"Disk space: {self.format_bytes(required_space)} required")
        
        # Report results
        if missing:
            print("❌ Missing requirements:")
            for req in missing:
                print(f"   - {req}")
            raise Exception("Requirements not met. Stampy can't proceed!")
        
        if warnings:
            print("⚠️  Warnings:")
            for warn in warnings:
                print(f"   - {warn}")
        
        print("✅ All requirements satisfied! Stampy is happy!")
    
    def download_package(self, app: AppInfo) -> Path:
        """Download the app package"""
        package_url = f"{self.app_repository}{app.package}"
        download_path = self.local_cache / 'downloads'
        file_name = app.package
        full_path = download_path / file_name
        
        # Check cache first
        cache_key = f"stampy_package_{hashlib.md5(package_url.encode()).hexdigest()}"
        cached_path = self.get_cache(cache_key)
        
        if cached_path and cached_path.exists():
            cache_age = time.time() - cached_path.stat().st_mtime
            if cache_age < 3600:  # 1 hour cache
                print(f"📦 Using cached package (saved {int(cache_age/60)} minutes ago)")
                return cached_path
        
        # Download with progress
        print(f"🌐 Downloading from: {package_url}")
        
        try:
            response = requests.get(package_url, stream=True)
            response.raise_for_status()
            
            with open(full_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Verify download
            if not full_path.exists() or full_path.stat().st_size < 100:
                raise Exception("Downloaded package appears to be invalid")
            
            # Verify package integrity if hash provided
            if app.hash:
                actual_hash = self.calculate_file_hash(full_path)
                if actual_hash != app.hash:
                    full_path.unlink()
                    raise Exception("Package integrity check failed! Stampy detected tampering!")
                print("🔒 Package integrity verified")
            
            # Cache the download path
            self.set_cache(cache_key, str(full_path), 3600)
            
            print(f"✅ Package downloaded successfully ({self.format_bytes(full_path.stat().st_size)})")
            
            return full_path
            
        except Exception as e:
            raise Exception(f"Failed to download package: {e}")
    
    def extract_package(self, package_path: Path, app: AppInfo) -> Path:
        """Extract the package to installation directory"""
        temp_dir = self.local_cache / 'temp' / f"stampy_{os.urandom(8).hex()}"
        final_dir = self.install_path / app.name
        
        # Create temp extraction directory
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Determine package type and extract
            if package_path.suffix == '.zip':
                self.extract_zip(package_path, temp_dir)
            elif package_path.suffix in ['.tar', '.gz', '.tgz']:
                self.extract_tar(package_path, temp_dir)
            else:
                raise Exception(f"Unsupported package format: {package_path.suffix}")
            
            # Find the app root
            app_root = self.find_app_root(temp_dir)
            
            # Move to final location
            if final_dir.exists():
                # Backup existing installation
                backup_name = f"{app.name}_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}"
                backup_dir = self.backup_path / backup_name
                shutil.move(str(final_dir), str(backup_dir))
                print(f"📦 Backed up existing installation to: {backup_name}")
            
            # Move extracted files to final location
            shutil.move(str(app_root), str(final_dir))
            
            # Set proper permissions
            self.set_permissions(final_dir)
            
            # Clean up temp directory
            shutil.rmtree(temp_dir)
            
            print(f"✅ Package extracted to: {final_dir}")
            
            return final_dir
            
        except Exception as e:
            # Clean up on failure
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            raise e
    
    def run_install_scripts(self, app: AppInfo, install_path: Path):
        """Run installation scripts"""
        scripts_run = 0
        
        # Look for installation scripts
        script_paths = [
            'install.py',
            'setup.py',
            'scripts/install.py',
            'bin/install.py',
            '.stampy/install.py'
        ]
        
        for script_path in script_paths:
            full_path = install_path / script_path
            if full_path.exists():
                print(f"🔧 Running installation script: {script_path}")
                
                try:
                    # Execute script
                    result = subprocess.run(
                        [sys.executable, str(full_path)],
                        cwd=install_path,
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode != 0:
                        raise Exception(f"Installation script failed: {result.stderr}")
                    
                    scripts_run += 1
                    
                except Exception as e:
                    raise Exception(f"Installation script error: {e}")
        
        # Run database migrations if present
        migration_dir = install_path / 'migrations'
        if migration_dir.exists():
            print("🗄️  Running database migrations...")
            self.run_migrations(migration_dir, app.name)
        
        # Install dependencies if requirements.txt exists
        requirements_file = install_path / 'requirements.txt'
        if requirements_file.exists():
            print("📚 Installing dependencies...")
            self.install_dependencies(install_path)
        
        # Create required directories
        self.create_app_directories(install_path, app)
        
        if scripts_run > 0:
            print("✅ Installation scripts completed successfully")
    
    def configure_app(self, app: AppInfo, options: Dict):
        """Configure the installed app"""
        config_path = install_path / '.peanuts'
        config = {}
        
        # Load default configuration
        default_config_path = install_path / '.peanuts.default'
        if default_config_path.exists():
            config = self.load_config_file(default_config_path)
        
        # Interactive configuration if not in quick mode
        if not options.get('quick'):
            print(f"\n🎯 Let's configure {app.name}:")
            
            # App-specific configuration
            if app.config_prompts:
                for key, prompt in app.config_prompts.items():
                    default = config.get(key, prompt.get('default', ''))
                    value = self.prompt(prompt['question'], default)
                    config[key] = value
        
        # Add app metadata
        config['_stampy'] = {
            'app_name': app.name,
            'version': app.version,
            'installed_at': datetime.now().isoformat(),
            'installed_by': os.getenv('USER', 'unknown')
        }
        
        # Save configuration
        self.save_config_file(config_path, config)
        
        print("✅ Configuration saved to .peanuts file")
    
    def register_installation(self, app: AppInfo):
        """Register the app as installed"""
        install_path = self.install_path / app.name
        
        # Update installed apps registry
        self.installed_apps[app.name] = InstalledApp(
            name=app.name,
            version=app.version,
            path=str(install_path),
            installed_at=time.time(),
            size=app.size,
            features=app.features
        )
        
        # Save to persistent storage
        registry_file = Path('storage/stampy/registry.peanuts')
        registry_file.parent.mkdir(parents=True, exist_ok=True)
        self.save_config_file(registry_file, {k: asdict(v) for k, v in self.installed_apps.items()})
        
        print("✅ App registered successfully")
    
    def scan_installed_apps(self):
        """Scan for already installed apps"""
        registry_file = Path('storage/stampy/registry.peanuts')
        if registry_file.exists():
            registry_data = self.load_config_file(registry_file)
            for name, data in registry_data.items():
                if Path(data['path']).exists():
                    self.installed_apps[name] = InstalledApp(**data)
    
    def is_installed(self, app_name: str) -> bool:
        """Check if Stampy has already installed an app"""
        return app_name in self.installed_apps
    
    def uninstall(self, app_name: str) -> bool:
        """Uninstall an app - Sometimes Stampy must leave"""
        if app_name not in self.installed_apps:
            raise Exception(f"Stampy hasn't installed {app_name} yet!")
        
        print(f"🐘 Stampy is sadly removing {app_name}...")
        
        # Confirm uninstallation
        if self.prompt(f"Are you sure you want to uninstall {app_name}?", 'no') != 'yes':
            print("Uninstallation cancelled. Stampy is relieved!")
            return False
        
        try:
            app = self.installed_apps[app_name]
            install_path = Path(app.path)
            
            # Run uninstall scripts
            self.run_uninstall_scripts(app_name)
            
            # Create backup before removal
            backup_name = f"{app_name}_final_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}"
            backup_dir = self.backup_path / backup_name
            
            if install_path.exists():
                shutil.move(str(install_path), str(backup_dir))
                print(f"📦 Final backup created: {backup_name}")
            
            # Update registry
            del self.installed_apps[app_name]
            
            # Save updated registry
            registry_file = Path('storage/stampy/registry.peanuts')
            self.save_config_file(registry_file, {k: asdict(v) for k, v in self.installed_apps.items()})
            
            print(f"😢 {app_name} has been uninstalled. Stampy will miss it.")
            
            return True
            
        except Exception as e:
            print(f"❌ Uninstall failed: {e}")
            return False
    
    def catalog(self):
        """List available apps - What can Stampy install?"""
        print("🐘 STAMPY'S APP CATALOG")
        print("======================\n")
        
        for key, app in self.available_apps.items():
            # Check if installed
            installed = self.is_installed(key)
            status = " ✅ INSTALLED" if installed else ""
            
            print(f"📦 stampy->{key}{status}")
            print(f"   Name: {app.name} v{app.version}")
            print(f"   Size: {app.size} ({self.get_elephant_size(app.size)})")
            print(f"   Description: {app.description}")
            print(f"   Features: {', '.join(app.features)}")
            
            if installed and key in self.installed_apps:
                info = self.installed_apps[key]
                print(f"   Installed: {datetime.fromtimestamp(info.installed_at).strftime('%Y-%m-%d %H:%M')}")
            
            print()
        
        print("Use: stampy->install('app-name') to install!")
        print("Use: stampy->stomp('app-name') for quick install!")
    
    def stomp(self, app_name: str) -> bool:
        """Quick install command - Stampy's rampage mode"""
        print("🐘 STAMPY STOMP MODE ACTIVATED!")
        print(f"Installing {app_name} with maximum elephant force!\n")
        
        return self.install(app_name, {'quick': True, 'force': True})
    
    # Helper methods
    def load_app_catalog(self):
        """Load available apps catalog"""
        self.available_apps = {
            'reddit': AppInfo(
                name='Reddit Clone',
                description='Full-featured Reddit-style community platform',
                size='XXL',
                features=['voting', 'comments', 'subreddits', 'karma'],
                requirements={'python': '3.8', 'packages': ['flask', 'sqlalchemy']},
                version='2.0.0',
                package='reddit-clone-v2.zip'
            ),
            'blog': AppInfo(
                name='Blog Platform',
                description='Simple but powerful blogging system',
                size='M',
                features=['posts', 'categories', 'comments', 'rss'],
                requirements={'python': '3.7'},
                version='1.0.0',
                package='blog-platform-v1.zip',
                post_install="Your blog is ready! Visit /admin to start writing."
            ),
            'shop': AppInfo(
                name='E-commerce Platform',
                description='Full shopping cart system',
                size='XL',
                features=['products', 'cart', 'checkout', 'payments'],
                requirements={'python': '3.8', 'packages': ['flask', 'stripe']},
                version='2.5.0',
                package='ecommerce-v2.5.zip',
                config_prompts={
                    'stripe_key': {
                        'question': 'Enter your Stripe publishable key (optional):',
                        'default': ''
                    }
                }
            )
        }
    
    def show_installation_plan(self, app: AppInfo):
        """Show installation plan before proceeding"""
        print("\n📋 INSTALLATION PLAN")
        print("═══════════════════════════════")
        print(f"App: {app.name}")
        print(f"Description: {app.description}")
        print(f"Size: {app.size} ({self.get_elephant_size(app.size)})")
        print(f"Features: {', '.join(app.features)}")
        print()
    
    def show_post_install_instructions(self, app: AppInfo):
        """Show post-installation instructions"""
        install_path = self.install_path / app.name
        
        print("📚 POST-INSTALLATION INSTRUCTIONS")
        print("═══════════════════════════════════")
        print(f"✅ {app.name} has been installed to:")
        print(f"   {install_path}\n")
        
        # Check for README
        readme_paths = ['README.md', 'readme.md', 'README.txt', 'docs/README.md']
        for readme_path in readme_paths:
            if (install_path / readme_path).exists():
                print("📖 Documentation available at:")
                print(f"   {install_path}/{readme_path}\n")
                break
        
        # App-specific instructions
        if app.post_install:
            print(f"{app.post_install}\n")
        
        print("🚀 Next steps:")
        print("   1. Review the configuration in .peanuts")
        print("   2. Set up your web server to point to the app")
        print("   3. Run any pending migrations")
        print("   4. Clear your cache if needed\n")
    
    def get_elephant_size(self, size: str) -> str:
        """Get elephant-sized descriptions"""
        sizes = {
            'M': 'Baby elephant - quick and easy',
            'L': 'Young elephant - moderate setup',
            'XL': 'Adult elephant - substantial app',
            'XXL': 'Stampy-sized - big installation!',
            'XXXL': 'Bigger than Stampy! Massive platform'
        }
        return sizes.get(size, 'Unknown size')
    
    def check_python_version(self, required: str) -> bool:
        """Check if Python version meets requirement"""
        import sys
        return sys.version_info >= tuple(map(int, required.split('.')))
    
    def check_package_installed(self, package: str) -> bool:
        """Check if a Python package is installed"""
        try:
            __import__(package)
            return True
        except ImportError:
            return False
    
    def parse_size(self, size_str: str) -> int:
        """Parse size string to bytes"""
        units = {'B': 1, 'KB': 1024, 'MB': 1048576, 'GB': 1073741824}
        import re
        match = re.match(r'^(\d+(?:\.\d+)?)\s*([KMGT]?B)?$', size_str, re.IGNORECASE)
        if match:
            number = float(match.group(1))
            unit = match.group(2) or 'B'
            return int(number * units.get(unit.upper(), 1))
        return 0
    
    def format_bytes(self, bytes_val: int) -> str:
        """Format bytes to human readable"""
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        for i, unit in enumerate(units):
            if bytes_val < 1024 or i == len(units) - 1:
                return f"{bytes_val:.1f} {unit}"
            bytes_val /= 1024
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def extract_zip(self, zip_file: Path, destination: Path):
        """Extract ZIP archives"""
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(destination)
    
    def extract_tar(self, tar_file: Path, destination: Path):
        """Extract TAR archives"""
        with tarfile.open(tar_file, 'r:*') as tar_ref:
            tar_ref.extractall(destination)
    
    def find_app_root(self, extract_dir: Path) -> Path:
        """Find the app root directory in extracted files"""
        # Check if files are directly in extract dir
        if any((extract_dir / f).exists() for f in ['requirements.txt', '.peanuts', 'app.py']):
            return extract_dir
        
        # Check first level subdirectories
        dirs = [d for d in extract_dir.iterdir() if d.is_dir()]
        if len(dirs) == 1:
            return dirs[0]
        
        # Look for directory with app files
        for dir_path in dirs:
            if any((dir_path / f).exists() for f in ['requirements.txt', '.peanuts', 'app.py']):
                return dir_path
        
        return extract_dir
    
    def set_permissions(self, dir_path: Path):
        """Set proper permissions on app directory"""
        for root, dirs, files in os.walk(dir_path):
            for d in dirs:
                os.chmod(os.path.join(root, d), 0o755)
            for f in files:
                os.chmod(os.path.join(root, f), 0o644)
    
    def run_migrations(self, migration_dir: Path, app_name: str):
        """Run database migrations"""
        # Implementation would depend on your migration system
        pass
    
    def install_dependencies(self, install_path: Path):
        """Install Python dependencies"""
        requirements_file = install_path / 'requirements.txt'
        if requirements_file.exists():
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)
            ], cwd=install_path, check=True)
    
    def create_app_directories(self, install_path: Path, app: AppInfo):
        """Create required app directories"""
        directories = [
            'storage', 'storage/cache', 'storage/logs', 'storage/uploads',
            'storage/temp', 'public/uploads', 'public/assets'
        ]
        
        for dir_name in directories:
            dir_path = install_path / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def run_uninstall_scripts(self, app_name: str):
        """Run uninstall scripts"""
        if app_name not in self.installed_apps:
            return
        
        app = self.installed_apps[app_name]
        install_path = Path(app.path)
        
        # Look for uninstall scripts
        script_paths = ['uninstall.py', 'remove.py', 'scripts/uninstall.py']
        
        for script_path in script_paths:
            full_path = install_path / script_path
            if full_path.exists():
                print(f"🔧 Running uninstall script: {script_path}")
                try:
                    subprocess.run([sys.executable, str(full_path)], cwd=install_path)
                except Exception as e:
                    print(f"⚠️  Uninstall script warning: {e}")
    
    def rollback_installation(self, app_name: str, install_path: Path):
        """Rollback a failed installation"""
        try:
            if install_path.exists():
                shutil.rmtree(install_path)
            
            if app_name in self.installed_apps:
                del self.installed_apps[app_name]
            
            print("✅ Rollback completed")
            
        except Exception as e:
            print(f"⚠️  Rollback warning: {e}")
    
    def prompt(self, question: str, default: str = '') -> str:
        """Simple prompt for user input"""
        default_text = f" [{default}]" if default else ""
        return input(f"{question}{default_text}: ").strip() or default
    
    def load_config_file(self, file_path: Path) -> Dict:
        """Load configuration file"""
        if file_path.suffix == '.peanuts':
            # Load as JSON
            with open(file_path, 'r') as f:
                return json.load(f)
        else:
            # Load as YAML
            with open(file_path, 'r') as f:
                return yaml.safe_load(f)
    
    def save_config_file(self, file_path: Path, data: Dict):
        """Save configuration file"""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        if file_path.suffix == '.peanuts':
            # Save as JSON
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        else:
            # Save as YAML
            with open(file_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False)
    
    def get_cache(self, key: str) -> Optional[Path]:
        """Get value from cache"""
        cache_file = self.local_cache / f"{key}.cache"
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                return Path(f.read().strip())
        return None
    
    def set_cache(self, key: str, value: str, ttl: int):
        """Set value in cache"""
        cache_file = self.local_cache / f"{key}.cache"
        with open(cache_file, 'w') as f:
            f.write(value)


# Flask extension registration
def init_stampy(app):
    """Initialize Stampy with Flask app"""
    stampy = Stampy(app)
    app.stampy = stampy
    return stampy 