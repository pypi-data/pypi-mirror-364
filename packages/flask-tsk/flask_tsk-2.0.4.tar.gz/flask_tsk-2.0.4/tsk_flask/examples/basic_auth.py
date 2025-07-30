"""
Basic Authentication Example

A simple example showcasing Herd authentication with elephant services integration.
Perfect for developers learning Flask-TSK authentication.
"""

from flask import render_template, request, jsonify, redirect, url_for
from .base_example import BaseExample

# Import Herd with error handling
try:
    from tsk_flask.herd import Herd
    HERD_AVAILABLE = True
except ImportError:
    HERD_AVAILABLE = False
    Herd = None


class BasicAuthExample(BaseExample):
    """Basic authentication example with elephant showcase"""

    def __init__(self):
        super().__init__(
            name="Basic Authentication",
            description="Simple authentication example showcasing Herd with elephant services"
        )

    def create_app(self, config=None):
        """Create the basic auth example app"""
        app = super().create_app(config)

        # Add example-specific routes
        self._add_basic_auth_routes()

        return app

    def _add_basic_auth_routes(self):
        """Add basic authentication specific routes"""

        @self.app.route('/profile')
        def profile():
            """User profile page - requires authentication"""
            if not HERD_AVAILABLE:
                return render_template('profile.html', user=None, error='Authentication system not available')
            
            if not Herd.check():
                return redirect(url_for('login'))

            user = Herd.user()
            return render_template('profile.html', user=user)

        @self.app.route('/protected')
        def protected():
            """Protected page example"""
            if not HERD_AVAILABLE:
                return render_template('protected.html', user=None, error='Authentication system not available')
            
            if not Herd.check():
                return redirect(url_for('login'))

            user = Herd.user()
            return render_template('protected.html', user=user)

        @self.app.route('/api/user/info')
        def user_info():
            """API endpoint returning user information"""
            if not HERD_AVAILABLE:
                return jsonify({'error': 'Authentication system not available'}), 503
            
            if not Herd.check():
                return jsonify({'error': 'Authentication required'}), 401

            user = Herd.user()
            return jsonify({
                'user_id': user.get('id'),
                'email': user.get('email'),
                'first_name': user.get('first_name'),
                'last_name': user.get('last_name'),
                'role': user.get('role'),
                'created_at': user.get('created_at')
            })

        @self.app.route('/api/elephants/test')
        def test_elephants():
            """Test elephant services"""
            if not HERD_AVAILABLE:
                return jsonify({'error': 'Authentication system not available'}), 503
            
            if not Herd.check():
                return jsonify({'error': 'Authentication required'}), 401

            results = {}

            # Test Babar (Content Management)
            try:
                if 'babar' in self.elephants:
                    story = self.elephants['babar'].create_story({
                        'title': 'Test Story',
                        'content': 'This is a test story from the basic auth example',
                        'type': 'post'
                    })
                    results['babar'] = {'success': True, 'story_id': story.get('id')}
            except Exception as e:
                results['babar'] = {'success': False, 'error': str(e)}

            # Test Dumbo (HTTP Client)
            try:
                if 'dumbo' in self.elephants:
                    response = self.elephants['dumbo'].get('https://httpbin.org/json')
                    results['dumbo'] = {'success': True, 'status_code': response.status_code}
            except Exception as e:
                results['dumbo'] = {'success': False, 'error': str(e)}

            # Test Koshik (Audio)
            try:
                if 'koshik' in self.elephants:
                    notification_id = self.elephants['koshik'].notify('success', {
                        'message': 'Elephant test completed successfully!'
                    })
                    results['koshik'] = {'success': True, 'notification_id': notification_id}
            except Exception as e:
                results['koshik'] = {'success': False, 'error': str(e)}

            return jsonify(results)

        @self.app.route('/admin')
        def admin_panel():
            """Admin panel - requires admin role"""
            if not HERD_AVAILABLE:
                return render_template('admin.html', user=None, error='Authentication system not available')
            
            if not Herd.check():
                return redirect(url_for('login'))

            user = Herd.user()
            if user.get('role') != 'admin':
                return render_template('error.html',
                                     error='Access denied. Admin role required.'), 403

            # Get system stats using elephants
            stats = {}

            if 'peanuts' in self.elephants:
                stats['performance'] = self.elephants['peanuts'].get_performance_status()

            if 'kaavan' in self.elephants:
                stats['system'] = self.elephants['kaavan'].watch()

            return render_template('admin.html', user=user, stats=stats)


def create_basic_auth_example():
    """Factory function to create basic auth example"""
    return BasicAuthExample()


if __name__ == '__main__':
    example = create_basic_auth_example()
    example.run() 