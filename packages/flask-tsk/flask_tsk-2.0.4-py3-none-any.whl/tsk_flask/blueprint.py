#!/usr/bin/env python3
"""
Flask Blueprint for TuskLang API endpoints
Provides REST API for TuskLang configuration and operations
Includes FULL TuskLang SDK capabilities
"""

from flask import Blueprint, request, jsonify, current_app, g
from typing import Any, Dict, List, Optional
import logging

tsk_blueprint = Blueprint('tsk', __name__, url_prefix='/tsk')


@tsk_blueprint.route('/status', methods=['GET'])
def get_status():
    """Get TuskLang integration status"""
    try:
        from . import get_tsk
        tsk = get_tsk()
        if tsk:
            return jsonify({
                'success': True,
                'data': tsk.get_status()
            })
        else:
            return jsonify({
                'success': False,
                'data': {},
                'error': 'Flask-TSK not initialized'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'data': {},
            'error': str(e)
        }), 500


@tsk_blueprint.route('/config/<section>', methods=['GET'])
def get_config_section(section: str):
    """Get entire configuration section"""
    try:
        from . import get_tsk
        tsk = get_tsk()
        if tsk:
            data = tsk.get_section(section)
            return jsonify({
                'success': True,
                'data': {
                    'section': section,
                    'data': data
                }
            })
        else:
            return jsonify({
                'success': False,
                'data': {},
                'error': 'Flask-TSK not initialized'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'data': {},
            'error': str(e)
        }), 500


@tsk_blueprint.route('/config/<section>/<key>', methods=['GET'])
def get_config_value(section: str, key: str):
    """Get specific configuration value"""
    try:
        from . import get_tsk
        tsk = get_tsk()
        if tsk:
            value = tsk.get_config(section, key)
            return jsonify({
                'success': True,
                'data': {
                    'section': section,
                    'key': key,
                    'value': value
                }
            })
        else:
            return jsonify({
                'success': False,
                'data': {},
                'error': 'Flask-TSK not initialized'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'data': {},
            'error': str(e)
        }), 500


@tsk_blueprint.route('/config/<section>/<key>', methods=['POST'])
def set_config_value(section: str, key: str):
    """Set configuration value"""
    try:
        from . import get_tsk
        tsk = get_tsk()
        if tsk:
            value = request.get_json()
            success = tsk.set_config(section, key, value)
            return jsonify({
                'success': success,
                'data': {
                    'section': section,
                    'key': key,
                    'value': value,
                    'set': success
                }
            })
        else:
            return jsonify({
                'success': False,
                'data': {},
                'error': 'Flask-TSK not initialized'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'data': {},
            'error': str(e)
        }), 500


@tsk_blueprint.route('/function', methods=['POST'])
def execute_function():
    """Execute TuskLang function"""
    try:
        from . import get_tsk
        tsk = get_tsk()
        if not tsk:
            return jsonify({
                'success': False,
                'data': {},
                'error': 'Flask-TSK not initialized'
            })
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'data': {},
                'error': 'No data provided'
            }), 400
        
        section = data.get('section')
        key = data.get('key')
        args = data.get('args', [])
        kwargs = data.get('kwargs', {})
        
        if not section or not key:
            return jsonify({
                'success': False,
                'data': {},
                'error': 'Section and key are required'
            }), 400
        
        result = tsk.execute_function(section, key, *args, **kwargs)
        return jsonify({
            'success': True,
            'data': {
                'section': section,
                'key': key,
                'args': args,
                'kwargs': kwargs,
                'result': result
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'data': {},
            'error': str(e)
        }), 500


# ===== ADVANCED TUSKLANG SDK ENDPOINTS =====

@tsk_blueprint.route('/parse', methods=['POST'])
def parse_tsk_content():
    """Parse TuskLang content"""
    try:
        from . import get_tsk
        tsk = get_tsk()
        if not tsk:
            return jsonify({
                'success': False,
                'data': {},
                'error': 'Flask-TSK not initialized'
            })
        
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({
                'success': False,
                'data': {},
                'error': 'Content is required'
            }), 400
        
        content = data['content']
        enhanced = data.get('enhanced', False)
        with_comments = data.get('with_comments', False)
        
        result = tsk.parse_tsk(content, enhanced, with_comments)
        return jsonify({
            'success': True,
            'data': {
                'content': content,
                'enhanced': enhanced,
                'with_comments': with_comments,
                'parsed': result
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'data': {},
            'error': str(e)
        }), 500


@tsk_blueprint.route('/stringify', methods=['POST'])
def stringify_tsk_data():
    """Stringify data to TuskLang format"""
    try:
        from . import get_tsk
        tsk = get_tsk()
        if not tsk:
            return jsonify({
                'success': False,
                'data': {},
                'error': 'Flask-TSK not initialized'
            })
        
        data = request.get_json()
        if not data or 'data' not in data:
            return jsonify({
                'success': False,
                'data': {},
                'error': 'Data is required'
            }), 400
        
        tsk_data = data['data']
        result = tsk.stringify_tsk(tsk_data)
        return jsonify({
            'success': True,
            'data': {
                'input_data': tsk_data,
                'stringified': result
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'data': {},
            'error': str(e)
        }), 500


@tsk_blueprint.route('/save-data', methods=['POST'])
def save_tsk_data():
    """Save TuskLang data to file"""
    try:
        from . import get_tsk
        tsk = get_tsk()
        if not tsk:
            return jsonify({
                'success': False,
                'data': {},
                'error': 'Flask-TSK not initialized'
            })
        
        data = request.get_json()
        if not data or 'data' not in data or 'filepath' not in data:
            return jsonify({
                'success': False,
                'data': {},
                'error': 'Data and filepath are required'
            }), 400
        
        tsk_data = data['data']
        filepath = data['filepath']
        success = tsk.save_tsk(tsk_data, filepath)
        
        return jsonify({
            'success': success,
            'data': {
                'filepath': filepath,
                'saved': success
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'data': {},
            'error': str(e)
        }), 500


@tsk_blueprint.route('/load-data', methods=['POST'])
def load_tsk_data():
    """Load TuskLang data from file"""
    try:
        from . import get_tsk
        tsk = get_tsk()
        if not tsk:
            return jsonify({
                'success': False,
                'data': {},
                'error': 'Flask-TSK not initialized'
            })
        
        data = request.get_json()
        if not data or 'filepath' not in data:
            return jsonify({
                'success': False,
                'data': {},
                'error': 'Filepath is required'
            }), 400
        
        filepath = data['filepath']
        result = tsk.load_tsk(filepath)
        
        return jsonify({
            'success': True,
            'data': {
                'filepath': filepath,
                'loaded_data': result
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'data': {},
            'error': str(e)
        }), 500


@tsk_blueprint.route('/sections', methods=['GET'])
def list_sections():
    """List all available configuration sections"""
    try:
        from . import get_tsk
        tsk = get_tsk()
        if tsk and tsk.tsk_instance:
            sections = tsk.get_all_sections()
            return jsonify({
                'success': True,
                'data': {
                    'sections': sections
                }
            })
        else:
            return jsonify({
                'success': False,
                'data': {},
                'error': 'TuskLang not initialized'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'data': {},
            'error': str(e)
        }), 500


@tsk_blueprint.route('/sections/<section>', methods=['DELETE'])
def delete_section(section: str):
    """Delete a configuration section"""
    try:
        from . import get_tsk
        tsk = get_tsk()
        if not tsk:
            return jsonify({
                'success': False,
                'data': {},
                'error': 'Flask-TSK not initialized'
            })
        
        success = tsk.delete_section(section)
        return jsonify({
            'success': success,
            'data': {
                'section': section,
                'deleted': success
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'data': {},
            'error': str(e)
        }), 500


@tsk_blueprint.route('/sections/<section>/keys', methods=['GET'])
def get_section_keys(section: str):
    """Get all keys in a section"""
    try:
        from . import get_tsk
        tsk = get_tsk()
        if not tsk:
            return jsonify({
                'success': False,
                'data': {},
                'error': 'Flask-TSK not initialized'
            })
        
        keys = tsk.get_all_keys(section)
        return jsonify({
            'success': True,
            'data': {
                'section': section,
                'keys': keys
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'data': {},
            'error': str(e)
        }), 500


@tsk_blueprint.route('/sections/<section>/exists', methods=['GET'])
def check_section_exists(section: str):
    """Check if section exists"""
    try:
        from . import get_tsk
        tsk = get_tsk()
        if not tsk:
            return jsonify({
                'success': False,
                'data': {},
                'error': 'Flask-TSK not initialized'
            })
        
        exists = tsk.has_section(section)
        return jsonify({
            'success': True,
            'data': {
                'section': section,
                'exists': exists
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'data': {},
            'error': str(e)
        }), 500


# ===== SPECIALIZED CONFIGURATION ENDPOINTS =====

@tsk_blueprint.route('/database', methods=['GET'])
def get_database_config():
    """Get database configuration from TuskLang"""
    try:
        from . import get_tsk
        tsk = get_tsk()
        if tsk:
            db_config = tsk.get_database_config()
            return jsonify({
                'success': True,
                'data': {
                    'database_config': db_config
                }
            })
        else:
            return jsonify({
                'success': False,
                'data': {},
                'error': 'Flask-TSK not initialized'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'data': {},
            'error': str(e)
        }), 500


@tsk_blueprint.route('/security', methods=['GET'])
def get_security_config():
    """Get security configuration from TuskLang"""
    try:
        from . import get_tsk
        tsk = get_tsk()
        if tsk:
            security_config = tsk.get_security_config()
            return jsonify({
                'success': True,
                'data': {
                    'security_config': security_config
                }
            })
        else:
            return jsonify({
                'success': False,
                'data': {},
                'error': 'Flask-TSK not initialized'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'data': {},
            'error': str(e)
        }), 500


@tsk_blueprint.route('/ui', methods=['GET'])
def get_ui_config():
    """Get UI configuration from TuskLang"""
    try:
        from . import get_tsk
        tsk = get_tsk()
        if tsk:
            ui_config = tsk.get_ui_config()
            return jsonify({
                'success': True,
                'data': {
                    'ui_config': ui_config
                }
            })
        else:
            return jsonify({
                'success': False,
                'data': {},
                'error': 'Flask-TSK not initialized'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'data': {},
            'error': str(e)
        }), 500


# ===== FILE OPERATIONS =====

@tsk_blueprint.route('/save', methods=['POST'])
def save_config():
    """Save TuskLang configuration to file"""
    try:
        from . import get_tsk
        tsk = get_tsk()
        if not tsk:
            return jsonify({
                'success': False,
                'data': {},
                'error': 'Flask-TSK not initialized'
            })
        
        data = request.get_json()
        if not data or 'filepath' not in data:
            return jsonify({
                'success': False,
                'data': {},
                'error': 'Filepath is required'
            }), 400
        
        filepath = data['filepath']
        success = tsk.save_config(filepath)
        return jsonify({
            'success': success,
            'data': {
                'filepath': filepath,
                'saved': success
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'data': {},
            'error': str(e)
        }), 500


@tsk_blueprint.route('/load', methods=['POST'])
def load_config():
    """Load TuskLang configuration from file"""
    try:
        from . import get_tsk
        tsk = get_tsk()
        if not tsk:
            return jsonify({
                'success': False,
                'data': {},
                'error': 'Flask-TSK not initialized'
            })
        
        data = request.get_json()
        if not data or 'filepath' not in data:
            return jsonify({
                'success': False,
                'data': {},
                'error': 'Filepath is required'
            }), 400
        
        filepath = data['filepath']
        success = tsk.load_config(filepath)
        return jsonify({
            'success': success,
            'data': {
                'filepath': filepath,
                'loaded': success
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'data': {},
            'error': str(e)
        }), 500


@tsk_blueprint.route('/health', methods=['GET'])
def health_check():
    """Health check for TuskLang integration"""
    try:
        from . import get_tsk
        tsk = get_tsk()
        if tsk:
            status = tsk.get_status()
            is_healthy = status.get('available', False) and status.get('initialized', False)
            
            return jsonify({
                'success': is_healthy,
                'data': {
                    'status': 'healthy' if is_healthy else 'unhealthy',
                    'tsk_status': status
                }
            })
        else:
            return jsonify({
                'success': False,
                'data': {
                    'status': 'unhealthy'
                },
                'error': 'Flask-TSK not initialized'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'data': {
                'status': 'error'
            },
            'error': str(e)
        }), 500


@tsk_blueprint.route('/capabilities', methods=['GET'])
def get_capabilities():
    """Get all available TuskLang capabilities"""
    try:
        from . import get_tsk, TUSK_AVAILABLE, TUSK_VERSION
        tsk = get_tsk()
        
        capabilities = {
            'tusk_available': TUSK_AVAILABLE,
            'tusk_version': TUSK_VERSION,
            'flask_tsk_initialized': tsk is not None,
            'features': {
                'configuration_management': True,
                'function_execution': True,
                'template_integration': True,
                'rest_api': True,
                'database_integration': True,
                'security_features': True,
                'ui_configuration': True,
                'performance_engine': True,
                'advanced_parsing': TUSK_AVAILABLE,
                'data_serialization': TUSK_AVAILABLE,
                'file_operations': TUSK_AVAILABLE,
                'section_management': TUSK_AVAILABLE,
                'parser_creation': TUSK_AVAILABLE,
                'shell_storage': TUSK_AVAILABLE
            },
            'endpoints': [
                '/tsk/status',
                '/tsk/config/{section}',
                '/tsk/config/{section}/{key}',
                '/tsk/function',
                '/tsk/parse',
                '/tsk/stringify',
                '/tsk/save-data',
                '/tsk/load-data',
                '/tsk/sections',
                '/tsk/sections/{section}',
                '/tsk/sections/{section}/keys',
                '/tsk/sections/{section}/exists',
                '/tsk/database',
                '/tsk/security',
                '/tsk/ui',
                '/tsk/save',
                '/tsk/load',
                '/tsk/health',
                '/tsk/capabilities'
            ]
        }
        
        return jsonify({
            'success': True,
            'data': capabilities
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'data': {},
            'error': str(e)
        }), 500 