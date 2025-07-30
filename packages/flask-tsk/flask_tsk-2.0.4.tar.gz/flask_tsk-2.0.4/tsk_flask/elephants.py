"""
Flask-TSK Elephant Integration
=============================
"The elephant herd joins Flask-TSK"
Complete integration of all 12 elephants into Flask-TSK framework
Strong. Secure. Scalable. 🐘
"""

from flask import Flask, current_app, request, jsonify
from typing import Dict, List, Optional, Any, Union
import time
from datetime import datetime
import json

from . import get_tsk

# Import all elephants from the correct location
try:
    from .herd.elephants.babar import Babar, init_babar, get_babar
    from .herd.elephants.dumbo import Dumbo, init_dumbo, get_dumbo
    from .herd.elephants.elmer import Elmer, init_elmer, get_elmer
    from .herd.elephants.happy import Happy, init_happy, get_happy
    from .herd.elephants.heffalump import Heffalump, init_heffalump, get_heffalump
    from .herd.elephants.horton import Horton, init_horton, get_horton
    from .herd.elephants.jumbo import Jumbo, init_jumbo, get_jumbo
    from .herd.elephants.kaavan import Kaavan, init_kaavan, get_kaavan
    from .herd.elephants.koshik import Koshik, init_koshik, get_koshik
    from .herd.elephants.satao import Satao, init_satao
    from .herd.elephants.stampy import Stampy, init_stampy
    from .herd.elephants.tantor import Tantor, init_tantor, get_tantor
    
    ELEPHANTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some elephants not available: {e}")
    ELEPHANTS_AVAILABLE = False

class ElephantHerd:
    """Main elephant herd manager for Flask-TSK"""
    
    def __init__(self, app: Flask = None):
        self.app = app
        self.elephants = {}
        self.initialized = False
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize elephant herd with Flask app"""
        if not ELEPHANTS_AVAILABLE:
            app.logger.warning("Elephants not available - skipping initialization")
            return
        
        self.app = app
        
        # Initialize all elephants
        try:
            # Core elephants
            self.elephants['babar'] = init_babar(app)
            self.elephants['dumbo'] = init_dumbo(app)
            self.elephants['elmer'] = init_elmer(app)
            self.elephants['happy'] = init_happy(app)
            self.elephants['heffalump'] = init_heffalump(app)
            self.elephants['horton'] = init_horton(app)
            
            # Utility elephants
            self.elephants['jumbo'] = init_jumbo(app)
            self.elephants['kaavan'] = init_kaavan(app)
            self.elephants['koshik'] = init_koshik(app)
            self.elephants['satao'] = init_satao(app)
            self.elephants['stampy'] = init_stampy(app)
            self.elephants['tantor'] = init_tantor(app)
            
            self.initialized = True
            app.logger.info("🐘 Elephant herd initialized successfully!")
            
        except Exception as e:
            app.logger.error(f"Failed to initialize elephant herd: {e}")
            self.initialized = False
    
    def get_elephant(self, name: str):
        """Get specific elephant instance"""
        if not self.initialized:
            return None
        
        return self.elephants.get(name)
    
    def get_all_elephants(self) -> Dict[str, Any]:
        """Get all elephant instances"""
        if not self.initialized:
            return {}
        
        return self.elephants.copy()
    
    def get_herd_status(self) -> Dict[str, Any]:
        """Get status of all elephants"""
        if not self.initialized:
            return {
                'initialized': False,
                'elephants': {},
                'total_count': 0,
                'available_count': 0
            }
        
        status = {
            'initialized': True,
            'elephants': {},
            'total_count': len(self.elephants),
            'available_count': 0,
            'timestamp': datetime.now().isoformat()
        }
        
        for name, elephant in self.elephants.items():
            elephant_status = {
                'available': elephant is not None,
                'type': type(elephant).__name__ if elephant else None
            }
            
            if elephant:
                status['available_count'] += 1
                
                # Get specific elephant stats if available
                try:
                    if hasattr(elephant, 'get_stats'):
                        elephant_status['stats'] = elephant.get_stats()
                    elif hasattr(elephant, 'stats'):
                        elephant_status['stats'] = elephant.stats()
                except Exception:
                    elephant_status['stats'] = None
            
            status['elephants'][name] = elephant_status
        
        return status
    
    def run_herd_health_check(self) -> Dict[str, Any]:
        """Run health check on all elephants"""
        if not self.initialized:
            return {
                'healthy': False,
                'message': 'Elephant herd not initialized',
                'checks': {}
            }
        
        health_results = {
            'healthy': True,
            'timestamp': datetime.now().isoformat(),
            'checks': {}
        }
        
        for name, elephant in self.elephants.items():
            try:
                if elephant is None:
                    health_results['checks'][name] = {
                        'healthy': False,
                        'error': 'Elephant not available'
                    }
                    health_results['healthy'] = False
                    continue
                
                # Run elephant-specific health checks
                if hasattr(elephant, 'health_check'):
                    result = elephant.health_check()
                elif hasattr(elephant, 'watch'):
                    result = elephant.watch()
                elif hasattr(elephant, 'get_stats'):
                    result = elephant.get_stats()
                else:
                    result = {'status': 'unknown'}
                
                health_results['checks'][name] = {
                    'healthy': True,
                    'result': result
                }
                
            except Exception as e:
                health_results['checks'][name] = {
                    'healthy': False,
                    'error': str(e)
                }
                health_results['healthy'] = False
        
        return health_results

# Global herd instance
_herd = None

def init_elephant_herd(app: Flask) -> ElephantHerd:
    """Initialize elephant herd with Flask app"""
    global _herd
    _herd = ElephantHerd(app)
    return _herd

def get_elephant_herd() -> ElephantHerd:
    """Get global elephant herd instance"""
    global _herd
    if _herd is None:
        if current_app:
            _herd = ElephantHerd(current_app)
        else:
            raise RuntimeError("Flask app not available")
    return _herd

def get_elephant(name: str):
    """Get specific elephant by name"""
    herd = get_elephant_herd()
    return herd.get_elephant(name)

# Convenience functions for each elephant
def get_babar_cms():
    """Get Babar CMS elephant"""
    return get_elephant('babar')

def get_dumbo_http():
    """Get Dumbo HTTP elephant"""
    return get_elephant('dumbo')

def get_elmer_theme():
    """Get Elmer theme elephant"""
    return get_elephant('elmer')

def get_happy_image():
    """Get Happy image elephant"""
    return get_elephant('happy')

def get_heffalump_search():
    """Get Heffalump search elephant"""
    return get_elephant('heffalump')

def get_horton_jobs():
    """Get Horton jobs elephant"""
    return get_elephant('horton')

def get_jumbo_upload():
    """Get Jumbo upload elephant"""
    return get_elephant('jumbo')

def get_kaavan_monitor():
    """Get Kaavan monitor elephant"""
    return get_elephant('kaavan')

def get_koshik_audio():
    """Get Koshik audio elephant"""
    return get_elephant('koshik')

def get_satao_security():
    """Get Satao security elephant"""
    return get_elephant('satao')

def get_stampy_packages():
    """Get Stampy packages elephant"""
    return get_elephant('stampy')

def get_tantor_database():
    """Get Tantor database elephant"""
    return get_elephant('tantor')

# Elephant showcase functions
def showcase_elephant_capabilities() -> Dict[str, Any]:
    """Showcase all elephant capabilities"""
    if not ELEPHANTS_AVAILABLE:
        return {
            'available': False,
            'message': 'Elephants not available'
        }
    
    showcase = {
        'available': True,
        'timestamp': datetime.now().isoformat(),
        'elephants': {}
    }
    
    # Test each elephant's capabilities
    elephants_to_test = [
        ('babar', 'Content Management'),
        ('dumbo', 'HTTP Operations'),
        ('elmer', 'Theme Generation'),
        ('happy', 'Image Processing'),
        ('heffalump', 'Search & Discovery'),
        ('horton', 'Job Processing'),
        ('jumbo', 'File Upload'),
        ('kaavan', 'System Monitoring'),
        ('koshik', 'Audio & Notifications'),
        ('satao', 'Security & Protection'),
        ('stampy', 'Package Management'),
        ('tantor', 'Database Operations')
    ]
    
    for name, description in elephants_to_test:
        elephant = get_elephant(name)
        if elephant:
            try:
                # Test basic functionality
                if hasattr(elephant, 'get_stats'):
                    stats = elephant.get_stats()
                elif hasattr(elephant, 'stats'):
                    stats = elephant.stats()
                else:
                    stats = {'status': 'available'}
                
                showcase['elephants'][name] = {
                    'description': description,
                    'available': True,
                    'stats': stats
                }
            except Exception as e:
                showcase['elephants'][name] = {
                    'description': description,
                    'available': True,
                    'error': str(e)
                }
        else:
            showcase['elephants'][name] = {
                'description': description,
                'available': False,
                'error': 'Elephant not initialized'
            }
    
    return showcase

def run_elephant_demo(demo_type: str = 'all') -> Dict[str, Any]:
    """Run elephant demonstration"""
    if not ELEPHANTS_AVAILABLE:
        return {
            'success': False,
            'message': 'Elephants not available'
        }
    
    demo_results = {
        'success': True,
        'demo_type': demo_type,
        'timestamp': datetime.now().isoformat(),
        'results': {}
    }
    
    try:
        if demo_type in ['all', 'content']:
            # Babar demo
            babar = get_babar_cms()
            if babar:
                demo_results['results']['babar'] = {
                    'demo': 'Content creation',
                    'status': 'available'
                }
        
        if demo_type in ['all', 'network']:
            # Dumbo demo
            dumbo = get_dumbo_http()
            if dumbo:
                demo_results['results']['dumbo'] = {
                    'demo': 'HTTP operations',
                    'status': 'available'
                }
        
        if demo_type in ['all', 'themes']:
            # Elmer demo
            elmer = get_elmer_theme()
            if elmer:
                demo_results['results']['elmer'] = {
                    'demo': 'Theme generation',
                    'status': 'available'
                }
        
        if demo_type in ['all', 'images']:
            # Happy demo
            happy = get_happy_image()
            if happy:
                demo_results['results']['happy'] = {
                    'demo': 'Image processing',
                    'status': 'available'
                }
        
        if demo_type in ['all', 'search']:
            # Heffalump demo
            heffalump = get_heffalump_search()
            if heffalump:
                demo_results['results']['heffalump'] = {
                    'demo': 'Search operations',
                    'status': 'available'
                }
        
        if demo_type in ['all', 'jobs']:
            # Horton demo
            horton = get_horton_jobs()
            if horton:
                demo_results['results']['horton'] = {
                    'demo': 'Job processing',
                    'status': 'available'
                }
        
    except Exception as e:
        demo_results['success'] = False
        demo_results['error'] = str(e)
    
    return demo_results 