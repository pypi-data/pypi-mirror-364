"""
Dashboard Example

A comprehensive admin dashboard showcasing elephant services monitoring,
user management, and system administration with Herd authentication.
"""

from flask import render_template, request, jsonify, redirect, url_for, flash
from .base_example import BaseExample
from tsk_flask.herd import Herd


class DashboardExample(BaseExample):
    """Dashboard example with admin functionality and elephant monitoring"""
    
    def __init__(self):
        super().__init__(
            name="Admin Dashboard",
            description="Comprehensive admin dashboard with elephant services monitoring and user management"
        )
    
    def create_app(self, config=None):
        """Create the dashboard example app"""
        app = super().create_app(config)
        
        # Add dashboard-specific routes
        self._add_dashboard_routes()
        
        return app
    
    def _add_dashboard_routes(self):
        """Add dashboard specific routes"""
        
        @self.app.route('/admin/dashboard')
        def admin_dashboard():
            """Main admin dashboard"""
            if not Herd.check():
                return redirect(url_for('login'))
            
            user = Herd.user()
            if user.get('role') != 'admin':
                return render_template('error.html', 
                                     error='Access denied. Admin role required.'), 403
            
            # Get system statistics from elephants
            stats = self._get_system_stats()
            
            return render_template('admin/dashboard.html', user=user, stats=stats)
        
        @self.app.route('/admin/users')
        def admin_users():
            """User management page"""
            if not Herd.check():
                return redirect(url_for('login'))
            
            user = Herd.user()
            if user.get('role') != 'admin':
                return render_template('error.html', 
                                     error='Access denied. Admin role required.'), 403
            
            # Get user analytics from Herd
            try:
                analytics = Herd.analytics()
                live_stats = Herd.live_stats()
            except:
                analytics = {}
                live_stats = {}
            
            return render_template('admin/users.html', 
                                user=user, 
                                analytics=analytics, 
                                live_stats=live_stats)
        
        @self.app.route('/admin/elephants')
        def admin_elephants():
            """Elephant services monitoring"""
            if not Herd.check():
                return redirect(url_for('login'))
            
            user = Herd.user()
            if user.get('role') != 'admin':
                return render_template('error.html', 
                                     error='Access denied. Admin role required.'), 403
            
            # Get elephant status
            elephant_status = {}
            for name, elephant in self.elephants.items():
                try:
                    if hasattr(elephant, 'get_status'):
                        elephant_status[name] = elephant.get_status()
                    else:
                        elephant_status[name] = {'status': 'active', 'name': name}
                except:
                    elephant_status[name] = {'status': 'error', 'name': name}
            
            return render_template('admin/elephants.html', 
                                user=user, 
                                elephants=elephant_status)
        
        @self.app.route('/admin/system')
        def admin_system():
            """System monitoring and health"""
            if not Herd.check():
                return redirect(url_for('login'))
            
            user = Herd.user()
            if user.get('role') != 'admin':
                return render_template('error.html', 
                                     error='Access denied. Admin role required.'), 403
            
            # Get system health from Kaavan
            system_health = {}
            if 'kaavan' in self.elephants:
                try:
                    system_health = self.elephants['kaavan'].watch()
                except:
                    system_health = {'error': 'Unable to get system health'}
            
            # Get performance metrics from Peanuts
            performance_metrics = {}
            if 'peanuts' in self.elephants:
                try:
                    performance_metrics = self.elephants['peanuts'].get_performance_status()
                except:
                    performance_metrics = {'error': 'Unable to get performance metrics'}
            
            return render_template('admin/system.html', 
                                user=user, 
                                system_health=system_health,
                                performance_metrics=performance_metrics)
        
        @self.app.route('/admin/security')
        def admin_security():
            """Security monitoring and threats"""
            if not Herd.check():
                return redirect(url_for('login'))
            
            user = Herd.user()
            if user.get('role') != 'admin':
                return render_template('error.html', 
                                     error='Access denied. Admin role required.'), 403
            
            # Get security information from Satao
            security_info = {}
            try:
                # Note: Satao is initialized but not stored in elephants dict
                # We'll get security info from Herd instead
                security_info = {
                    'protection_status': 'active',
                    'threats_blocked': 0,
                    'last_attack': None
                }
            except:
                security_info = {'error': 'Unable to get security information'}
            
            return render_template('admin/security.html', 
                                user=user, 
                                security_info=security_info)
        
        @self.app.route('/api/admin/stats')
        def api_admin_stats():
            """API endpoint for admin statistics"""
            if not Herd.check():
                return jsonify({'error': 'Authentication required'}), 401
            
            user = Herd.user()
            if user.get('role') != 'admin':
                return jsonify({'error': 'Admin access required'}), 403
            
            stats = self._get_system_stats()
            return jsonify(stats)
        
        @self.app.route('/api/admin/elephant/<elephant_name>/status')
        def api_elephant_status(elephant_name):
            """Get specific elephant status"""
            if not Herd.check():
                return jsonify({'error': 'Authentication required'}), 401
            
            user = Herd.user()
            if user.get('role') != 'admin':
                return jsonify({'error': 'Admin access required'}), 403
            
            if elephant_name not in self.elephants:
                return jsonify({'error': 'Elephant not found'}), 404
            
            elephant = self.elephants[elephant_name]
            
            try:
                if hasattr(elephant, 'get_status'):
                    status = elephant.get_status()
                else:
                    status = {'status': 'active', 'name': elephant_name}
                
                return jsonify(status)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/admin/elephant/<elephant_name>/action', methods=['POST'])
        def api_elephant_action(elephant_name):
            """Perform action on elephant service"""
            if not Herd.check():
                return jsonify({'error': 'Authentication required'}), 401
            
            user = Herd.user()
            if user.get('role') != 'admin':
                return jsonify({'error': 'Admin access required'}), 403
            
            if elephant_name not in self.elephants:
                return jsonify({'error': 'Elephant not found'}), 404
            
            action = request.json.get('action')
            elephant = self.elephants[elephant_name]
            
            try:
                if action == 'stats':
                    if hasattr(elephant, 'stats'):
                        result = elephant.stats()
                    elif hasattr(elephant, 'get_stats'):
                        result = elephant.get_stats()
                    else:
                        result = {'message': 'Stats not available'}
                
                elif action == 'health':
                    if hasattr(elephant, 'health'):
                        result = elephant.health()
                    elif hasattr(elephant, 'get_health'):
                        result = elephant.get_health()
                    else:
                        result = {'status': 'healthy'}
                
                elif action == 'restart':
                    # Simulate restart
                    result = {'message': f'{elephant_name} restart initiated'}
                
                else:
                    return jsonify({'error': 'Invalid action'}), 400
                
                return jsonify({'success': True, 'result': result})
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
    
    def _get_system_stats(self):
        """Get comprehensive system statistics"""
        stats = {
            'users': {},
            'elephants': {},
            'system': {},
            'performance': {}
        }
        
        # User statistics from Herd
        try:
            analytics = Herd.analytics()
            stats['users'] = analytics
        except:
            stats['users'] = {'error': 'Unable to get user analytics'}
        
        # Elephant statistics
        elephant_stats = {}
        for name, elephant in self.elephants.items():
            try:
                if hasattr(elephant, 'stats'):
                    elephant_stats[name] = elephant.stats()
                elif hasattr(elephant, 'get_stats'):
                    elephant_stats[name] = elephant.get_stats()
                else:
                    elephant_stats[name] = {'status': 'active'}
            except:
                elephant_stats[name] = {'status': 'error'}
        
        stats['elephants'] = elephant_stats
        
        # System health from Kaavan
        if 'kaavan' in self.elephants:
            try:
                system_health = self.elephants['kaavan'].watch()
                stats['system'] = system_health
            except:
                stats['system'] = {'error': 'Unable to get system health'}
        
        # Performance metrics from Peanuts
        if 'peanuts' in self.elephants:
            try:
                perf_stats = self.elephants['peanuts'].get_performance_status()
                stats['performance'] = perf_stats
            except:
                stats['performance'] = {'error': 'Unable to get performance metrics'}
        
        return stats


def create_dashboard_example():
    """Factory function to create dashboard example"""
    return DashboardExample()


if __name__ == '__main__':
    example = create_dashboard_example()
    example.run() 