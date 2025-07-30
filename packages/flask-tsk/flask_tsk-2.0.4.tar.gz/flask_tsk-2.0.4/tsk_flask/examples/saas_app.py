"""
SaaS Application Example

A Software-as-a-Service application showcasing subscription management,
user tiers, billing, and comprehensive elephant services integration.
"""

from flask import render_template, request, jsonify, redirect, url_for, flash
from .base_example import BaseExample
from tsk_flask.herd import Herd
import time


class SaaSAppExample(BaseExample):
    """SaaS application example with subscription management"""
    
    def __init__(self):
        super().__init__(
            name="SaaS Application",
            description="Software-as-a-Service application with subscription management and elephant services"
        )
        self.subscriptions = {}
        self.plans = self._initialize_plans()
        self.features = self._initialize_features()
    
    def create_app(self, config=None):
        """Create the SaaS application example app"""
        app = super().create_app(config)
        
        # Add SaaS specific routes
        self._add_saas_routes()
        
        return app
    
    def _initialize_plans(self):
        """Initialize subscription plans"""
        return [
            {
                'id': 'free',
                'name': 'Free',
                'price': 0,
                'features': ['basic_analytics', 'limited_storage'],
                'limits': {
                    'users': 1,
                    'storage': '100MB',
                    'api_calls': 1000
                }
            },
            {
                'id': 'pro',
                'name': 'Professional',
                'price': 29,
                'features': ['advanced_analytics', 'priority_support', 'custom_themes'],
                'limits': {
                    'users': 10,
                    'storage': '10GB',
                    'api_calls': 10000
                }
            },
            {
                'id': 'enterprise',
                'name': 'Enterprise',
                'price': 99,
                'features': ['all_features', 'dedicated_support', 'custom_integrations'],
                'limits': {
                    'users': 'unlimited',
                    'storage': '100GB',
                    'api_calls': 100000
                }
            }
        ]
    
    def _initialize_features(self):
        """Initialize feature definitions"""
        return {
            'basic_analytics': {
                'name': 'Basic Analytics',
                'description': 'Simple usage statistics and reports'
            },
            'advanced_analytics': {
                'name': 'Advanced Analytics',
                'description': 'Detailed analytics with custom dashboards'
            },
            'priority_support': {
                'name': 'Priority Support',
                'description': '24/7 priority customer support'
            },
            'custom_themes': {
                'name': 'Custom Themes',
                'description': 'Customize the look and feel of your dashboard'
            },
            'dedicated_support': {
                'name': 'Dedicated Support',
                'description': 'Dedicated account manager and support team'
            },
            'custom_integrations': {
                'name': 'Custom Integrations',
                'description': 'Custom API integrations and webhooks'
            }
        }
    
    def _add_saas_routes(self):
        """Add SaaS specific routes"""
        
        @self.app.route('/')
        def home():
            """SaaS homepage"""
            return render_template('saas/home.html', plans=self.plans)
        
        @self.app.route('/pricing')
        def pricing():
            """Pricing page"""
            return render_template('saas/pricing.html', plans=self.plans, features=self.features)
        
        @self.app.route('/dashboard')
        def dashboard():
            """User dashboard"""
            if not Herd.check():
                return redirect(url_for('login'))
            
            user = Herd.user()
            subscription = self.subscriptions.get(user.get('id'), {'plan': 'free'})
            plan = next((p for p in self.plans if p['id'] == subscription['plan']), self.plans[0])
            
            # Get user analytics using elephants
            analytics = {}
            if 'peanuts' in self.elephants:
                try:
                    analytics['performance'] = self.elephants['peanuts'].get_performance_status()
                except:
                    pass
            
            return render_template('saas/dashboard.html', 
                                user=user, 
                                plan=plan, 
                                analytics=analytics)
        
        @self.app.route('/features')
        def features():
            """Features showcase"""
            return render_template('saas/features.html', features=self.features)
        
        @self.app.route('/api/features')
        def api_features():
            """API features demo"""
            if not Herd.check():
                return jsonify({'error': 'Authentication required'}), 401
            
            user = Herd.user()
            subscription = self.subscriptions.get(user.get('id'), {'plan': 'free'})
            plan = next((p for p in self.plans if p['id'] == subscription['plan']), self.plans[0])
            
            # Demo different elephant features based on plan
            demo_results = {}
            
            if 'babar' in self.elephants and 'advanced_analytics' in plan['features']:
                try:
                    story = self.elephants['babar'].create_story({
                        'title': 'API Demo Content',
                        'content': 'This content was created via API',
                        'type': 'demo',
                        'status': 'published'
                    })
                    demo_results['content_management'] = {'success': True, 'story_id': story.get('id')}
                except:
                    demo_results['content_management'] = {'success': False, 'error': 'Content management not available'}
            
            if 'dumbo' in self.elephants:
                try:
                    response = self.elephants['dumbo'].get('https://httpbin.org/json')
                    demo_results['http_client'] = {'success': True, 'status_code': response.status_code}
                except:
                    demo_results['http_client'] = {'success': False, 'error': 'HTTP client not available'}
            
            if 'heffalump' in self.elephants and 'advanced_analytics' in plan['features']:
                try:
                    results = self.elephants['heffalump'].hunt('demo', ['content'])
                    demo_results['search'] = {'success': True, 'results': len(results)}
                except:
                    demo_results['search'] = {'success': False, 'error': 'Search not available'}
            
            if 'koshik' in self.elephants and 'priority_support' in plan['features']:
                try:
                    notification_id = self.elephants['koshik'].notify('success', {
                        'message': 'API demo completed successfully!'
                    })
                    demo_results['notifications'] = {'success': True, 'notification_id': notification_id}
                except:
                    demo_results['notifications'] = {'success': False, 'error': 'Notifications not available'}
            
            return jsonify({
                'plan': plan['id'],
                'features': plan['features'],
                'demo_results': demo_results
            })
        
        @self.app.route('/subscribe/<plan_id>')
        def subscribe(plan_id):
            """Subscribe to a plan"""
            if not Herd.check():
                return redirect(url_for('login'))
            
            plan = next((p for p in self.plans if p['id'] == plan_id), None)
            if not plan:
                flash('Invalid plan selected', 'error')
                return redirect(url_for('pricing'))
            
            user = Herd.user()
            
            # Process subscription using Horton background job
            if 'horton' in self.elephants:
                try:
                    job_id = self.elephants['horton'].dispatch('process_subscription', {
                        'user_id': user.get('id'),
                        'plan_id': plan_id,
                        'price': plan['price'],
                        'timestamp': int(time.time())
                    })
                except:
                    pass
            
            # Update subscription
            self.subscriptions[user.get('id')] = {
                'plan': plan_id,
                'started_at': int(time.time()),
                'status': 'active'
            }
            
            # Notify with Koshik
            if 'koshik' in self.elephants:
                try:
                    self.elephants['koshik'].notify('success', {
                        'message': f'Successfully subscribed to {plan["name"]} plan!'
                    })
                except:
                    pass
            
            flash(f'Successfully subscribed to {plan["name"]} plan!', 'success')
            return redirect(url_for('dashboard'))
        
        @self.app.route('/billing')
        def billing():
            """Billing and subscription management"""
            if not Herd.check():
                return redirect(url_for('login'))
            
            user = Herd.user()
            subscription = self.subscriptions.get(user.get('id'), {'plan': 'free'})
            plan = next((p for p in self.plans if p['id'] == subscription['plan']), self.plans[0])
            
            return render_template('saas/billing.html', 
                                user=user, 
                                subscription=subscription,
                                plan=plan,
                                plans=self.plans)
        
        @self.app.route('/admin/subscriptions')
        def admin_subscriptions():
            """Admin subscription management"""
            if not Herd.check():
                return redirect(url_for('login'))
            
            user = Herd.user()
            if user.get('role') != 'admin':
                return render_template('error.html', 
                                     error='Access denied. Admin role required.'), 403
            
            # Get subscription statistics
            stats = {
                'total_subscribers': len(self.subscriptions),
                'plan_distribution': {},
                'revenue': 0
            }
            
            for sub in self.subscriptions.values():
                plan_id = sub['plan']
                if plan_id not in stats['plan_distribution']:
                    stats['plan_distribution'][plan_id] = 0
                stats['plan_distribution'][plan_id] += 1
                
                # Calculate revenue
                plan = next((p for p in self.plans if p['id'] == plan_id), None)
                if plan:
                    stats['revenue'] += plan['price']
            
            return render_template('saas/admin/subscriptions.html', 
                                user=user, 
                                subscriptions=self.subscriptions,
                                plans=self.plans,
                                stats=stats)
        
        @self.app.route('/admin/analytics')
        def admin_analytics():
            """Admin analytics dashboard"""
            if not Herd.check():
                return redirect(url_for('login'))
            
            user = Herd.user()
            if user.get('role') != 'admin':
                return render_template('error.html', 
                                     error='Access denied. Admin role required.'), 403
            
            # Get analytics from elephants
            analytics = {}
            
            if 'peanuts' in self.elephants:
                try:
                    analytics['performance'] = self.elephants['peanuts'].get_performance_status()
                except:
                    pass
            
            if 'kaavan' in self.elephants:
                try:
                    analytics['system'] = self.elephants['kaavan'].watch()
                except:
                    pass
            
            return render_template('saas/admin/analytics.html', 
                                user=user, 
                                analytics=analytics)
        
        @self.app.route('/api/saas/usage')
        def api_usage():
            """Get user usage statistics"""
            if not Herd.check():
                return jsonify({'error': 'Authentication required'}), 401
            
            user = Herd.user()
            subscription = self.subscriptions.get(user.get('id'), {'plan': 'free'})
            plan = next((p for p in self.plans if p['id'] == subscription['plan']), self.plans[0])
            
            # Mock usage data
            usage = {
                'api_calls': {
                    'used': 150,
                    'limit': plan['limits']['api_calls'],
                    'percentage': 15 if plan['limits']['api_calls'] != 'unlimited' else 0
                },
                'storage': {
                    'used': '25MB',
                    'limit': plan['limits']['storage'],
                    'percentage': 25 if plan['limits']['storage'] != 'unlimited' else 0
                },
                'users': {
                    'used': 1,
                    'limit': plan['limits']['users'],
                    'percentage': 100 if plan['limits']['users'] != 'unlimited' else 0
                }
            }
            
            return jsonify({
                'plan': plan['id'],
                'usage': usage,
                'features': plan['features']
            })


def create_saas_app_example():
    """Factory function to create SaaS app example"""
    return SaaSAppExample()


if __name__ == '__main__':
    example = create_saas_app_example()
    example.run() 