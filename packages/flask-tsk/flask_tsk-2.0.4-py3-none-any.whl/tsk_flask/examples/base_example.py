"""
Base Example Class for Flask-TSK Examples

This provides a foundation for all examples with elephant services integration
and Herd authentication setup.
"""

import os
import json
from typing import Dict, Any, Optional
from flask import Flask, render_template, request, jsonify, redirect, url_for
from tsk_flask import FlaskTSK

# Simplified herd import - will be None if not available
try:
    from tsk_flask.herd import get_herd, Herd
    HERD_AVAILABLE = True
except ImportError:
    HERD_AVAILABLE = False
    get_herd = None
    Herd = None

# Elephant imports with error handling
try:
    from tsk_flask.herd.elephants.babar import get_babar
    from tsk_flask.herd.elephants.dumbo import get_dumbo
    from tsk_flask.herd.elephants.elmer import get_elmer
    from tsk_flask.herd.elephants.happy import get_happy
    from tsk_flask.herd.elephants.heffalump import get_heffalump
    from tsk_flask.herd.elephants.horton import get_horton
    from tsk_flask.herd.elephants.jumbo import get_jumbo
    from tsk_flask.herd.elephants.kaavan import get_kaavan
    from tsk_flask.herd.elephants.koshik import get_koshik
    from tsk_flask.herd.elephants.peanuts import get_peanuts
    from tsk_flask.herd.elephants.satao import init_satao
    from tsk_flask.herd.elephants.stampy import get_stampy
    from tsk_flask.herd.elephants.tantor import get_tantor
    ELEPHANTS_AVAILABLE = True
except ImportError:
    ELEPHANTS_AVAILABLE = False
    # Create dummy functions
    def get_babar(): return None
    def get_dumbo(): return None
    def get_elmer(): return None
    def get_happy(): return None
    def get_heffalump(): return None
    def get_horton(): return None
    def get_jumbo(): return None
    def get_kaavan(): return None
    def get_koshik(): return None
    def get_peanuts(): return None
    def init_satao(app): pass
    def get_stampy(): return None
    def get_tantor(): return None


class BaseExample:
    """Base class for all Flask-TSK examples"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.app = None
        self.tsk = None
        self.herd = None
        self.elephants = {}

    def create_app(self, config: Dict[str, Any] = None) -> Flask:
        """Create and configure Flask app with Flask-TSK and elephants"""

        # Create Flask app
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'your-secret-key-change-this'

        # Initialize Flask-TSK
        self.tsk = FlaskTSK(self.app)

        # Initialize Herd authentication
        if HERD_AVAILABLE:
            self.herd = get_herd()
        else:
            self.herd = None

        # Initialize all elephant services
        self._init_elephants()

        # Setup routes
        self._setup_routes()

        return self.app

    def _init_elephants(self):
        """Initialize all elephant services"""
        if not ELEPHANTS_AVAILABLE:
            print("Warning: Elephant services not available")
            return
            
        try:
            # Content Management Elephant
            self.elephants['babar'] = get_babar()

            # HTTP Client Elephant
            self.elephants['dumbo'] = get_dumbo()

            # Theme Generator Elephant
            self.elephants['elmer'] = get_elmer()

            # Image Processing Elephant
            self.elephants['happy'] = get_happy()

            # Search Elephant
            self.elephants['heffalump'] = get_heffalump()

            # Background Jobs Elephant
            self.elephants['horton'] = get_horton()

            # File Upload Elephant
            self.elephants['jumbo'] = get_jumbo()

            # System Monitoring Elephant
            self.elephants['kaavan'] = get_kaavan()

            # Audio Elephant
            self.elephants['koshik'] = get_koshik()

            # Performance Elephant
            self.elephants['peanuts'] = get_peanuts()

            # Security Elephant
            init_satao(self.app)

            # Package Management Elephant
            self.elephants['stampy'] = get_stampy()

            # Database Elephant
            self.elephants['tantor'] = get_tantor()

        except Exception as e:
            print(f"Warning: Some elephants failed to initialize: {e}")

    def _setup_routes(self):
        """Setup basic routes for the example"""

        @self.app.route('/')
        def index():
            return render_template('index.html',
                                example_name=self.name,
                                example_description=self.description,
                                elephants=self.elephants)

        @self.app.route('/elephants')
        def elephant_showcase():
            """Showcase all elephant capabilities"""
            elephant_status = {}
            for name, elephant in self.elephants.items():
                try:
                    if hasattr(elephant, 'get_status'):
                        elephant_status[name] = elephant.get_status()
                    else:
                        elephant_status[name] = {'status': 'active', 'name': name}
                except:
                    elephant_status[name] = {'status': 'error', 'name': name}

            return render_template('elephants.html',
                                elephants=elephant_status,
                                example_name=self.name)

        @self.app.route('/auth/login', methods=['GET', 'POST'])
        def login():
            if not HERD_AVAILABLE:
                return render_template('auth/login.html', error='Authentication system not available')
            
            if request.method == 'POST':
                email = request.form.get('email')
                password = request.form.get('password')
                remember = request.form.get('remember', False)

                if Herd.login(email, password, remember):
                    return redirect(url_for('dashboard'))
                else:
                    return render_template('auth/login.html', error='Invalid credentials')

            return render_template('auth/login.html')

        @self.app.route('/auth/register', methods=['GET', 'POST'])
        def register():
            if not HERD_AVAILABLE:
                return render_template('auth/register.html', error='Authentication system not available')
            
            if request.method == 'POST':
                data = {
                    'email': request.form.get('email'),
                    'password': request.form.get('password'),
                    'first_name': request.form.get('first_name'),
                    'last_name': request.form.get('last_name')
                }

                try:
                    user = Herd.create_user(data)
                    return redirect(url_for('login'))
                except Exception as e:
                    return render_template('auth/register.html', error=str(e))

            return render_template('auth/register.html')

        @self.app.route('/auth/logout')
        def logout():
            if HERD_AVAILABLE:
                Herd.logout()
            return redirect(url_for('index'))

        @self.app.route('/dashboard')
        def dashboard():
            if not HERD_AVAILABLE:
                return render_template('dashboard.html', user=None, error='Authentication system not available')
            
            if not Herd.check():
                return redirect(url_for('login'))

            user = Herd.user()
            return render_template('dashboard.html', user=user)

        @self.app.route('/api/elephants/<elephant_name>/demo')
        def elephant_demo(elephant_name):
            """Demo specific elephant functionality"""
            if elephant_name not in self.elephants:
                return jsonify({'error': 'Elephant not found'}), 404

            elephant = self.elephants[elephant_name]

            # Demo different elephants
            if elephant_name == 'babar':
                # Content management demo
                story = elephant.create_story({
                    'title': 'Demo Story',
                    'content': 'This is a demo story created by Babar',
                    'type': 'post'
                })
                return jsonify({'success': True, 'story': story})

            elif elephant_name == 'dumbo':
                # HTTP client demo
                response = elephant.get('https://httpbin.org/json')
                return jsonify({'success': True, 'response': {
                    'status_code': response.status_code,
                    'content_type': response.content_type
                }})

            elif elephant_name == 'elmer':
                # Theme generator demo
                theme = elephant.create_evolving_theme('demo_theme', '#3B82F6')
                return jsonify({'success': True, 'theme': {
                    'name': theme.name,
                    'mood': theme.mood.value,
                    'harmony_type': theme.harmony_type.value
                }})

            elif elephant_name == 'heffalump':
                # Search demo
                results = elephant.hunt('demo', ['content'])
                return jsonify({'success': True, 'results': len(results)})

            elif elephant_name == 'horton':
                # Background jobs demo
                job_id = elephant.dispatch('demo_job', {'message': 'Hello from Horton'})
                return jsonify({'success': True, 'job_id': job_id})

            elif elephant_name == 'koshik':
                # Audio demo
                notification_id = elephant.notify('success', {'message': 'Demo notification'})
                return jsonify({'success': True, 'notification_id': notification_id})

            elif elephant_name == 'peanuts':
                # Performance demo
                status = elephant.get_performance_status()
                return jsonify({'success': True, 'status': status})

            else:
                return jsonify({'success': True, 'message': f'{elephant_name} is active'})

    def get_template_context(self) -> Dict[str, Any]:
        """Get context data for templates"""
        return {
            'example_name': self.name,
            'example_description': self.description,
            'elephants': self.elephants,
            'herd': self.herd,
            'user': Herd.user() if HERD_AVAILABLE and Herd.check() else None
        }

    def run(self, debug: bool = True, host: str = '127.0.0.1', port: int = 5000):
        """Run the example application"""
        if not self.app:
            self.create_app()

        print(f"🚀 Starting {self.name} example...")
        print(f"📖 Description: {self.description}")
        print(f"🌐 URL: http://{host}:{port}")
        print(f"🐘 Elephants loaded: {len(self.elephants)}")

        self.app.run(debug=debug, host=host, port=port) 