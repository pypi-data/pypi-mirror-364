"""
Flask-TSK ASCII Art Module
==========================
Beautiful ASCII art for CLI interactions
"""

import os
from pathlib import Path

def load_ascii_art(filename):
    """Load ASCII art from file"""
    ascii_dir = Path(__file__).parent / "ascii"
    art_file = ascii_dir / filename
    
    if art_file.exists():
        with open(art_file, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

def get_tusk_banner():
    """Get the main Tusk banner for success messages"""
    return load_ascii_art("tusk.txt")

def get_error_art():
    """Get error art (turd-sm.txt)"""
    return load_ascii_art("turd-sm.txt")

def get_peanut_art():
    """Get peanut art for peanut-related operations"""
    return load_ascii_art("peanut.txt")

def get_elephant_art(service_name):
    """Get elephant art for specific services"""
    art_map = {
        'herd': 'heard.txt',
        'babar': 'create.txt',  # Using create.txt since buddy.txt was deleted
        'horton': 'horton.txt',
        'satao': 'eli.txt',
        'koshik': 'koshik.txt',
        'jumbo': 'dumbo.txt',
        'kaavan': 'elder.txt',
        'tantor': 'circus.txt',
        'peanuts': 'peanut.txt',
        'css': 'css.txt',
        'cron': 'cron.txt',
        'create': 'create.txt',
        'loading': 'loading.txt',
        'alert': 'alert.txt',
        'box': 'box.txt',
        'happy': 'happy.txt',
        'love': 'love.txt',
        'peace': 'peace.txt',
        'squirt': 'squirt.txt'
    }
    
    filename = art_map.get(service_name.lower(), 'tusk.txt')
    return load_ascii_art(filename)

def show_success_banner():
    """Show success banner with Tusk art"""
    print(get_tusk_banner())
    print("\n🐘 Flask-TSK - Revolutionary Flask Extension")
    print("===============================================")
    print("✅ Installation successful!")
    print("🚀 Ready to build amazing applications")

def show_error_message(message):
    """Show error message with turd art"""
    print(get_error_art())
    print(f"\n❌ Error: {message}")
    print("🔧 Please check the configuration and try again")

def show_service_banner(service_name, action=""):
    """Show service-specific banner"""
    art = get_elephant_art(service_name)
    if art:
        print(art)
    
    service_names = {
        'herd': '🐘 Herd Authentication',
        'babar': '📝 Babar CMS',
        'horton': '⚙️ Horton Job Queue',
        'satao': '🛡️ Satao Security',
        'koshik': '🔊 Koshik Audio',
        'jumbo': '📤 Jumbo Upload',
        'kaavan': '📊 Kaavan Monitoring',
        'tantor': '🔌 Tantor WebSocket',
        'peanuts': '🥜 Peanuts Performance'
    }
    
    service_display = service_names.get(service_name.lower(), service_name.title())
    if action:
        print(f"\n{service_display} - {action}")
    else:
        print(f"\n{service_display}")

def show_peanut_operation(operation):
    """Show peanut-related operation with peanut art"""
    print(get_peanut_art())
    print(f"\n🥜 Peanut Operation: {operation}")
    print("🌱 Growing your application...")

def show_loading_animation(message="Loading..."):
    """Show loading animation"""
    print(get_elephant_art('loading'))
    print(f"\n⏳ {message}")
    print("🔄 Please wait...")

def show_welcome_message():
    """Show welcome message for first-time CLI usage"""
    print(get_tusk_banner())
    print("\n🐘 Welcome to Flask-TSK!")
    print("===============================================")
    print("The strength of the elephant, the wisdom of the herd")
    print("\n🚀 Available commands:")
    print("  flask-tsk init <project>     - Create new project")
    print("  flask-tsk db init <project>  - Initialize databases")
    print("  flask-tsk optimize <project> - Optimize assets")
    print("  flask-tsk --help             - Show all commands") 