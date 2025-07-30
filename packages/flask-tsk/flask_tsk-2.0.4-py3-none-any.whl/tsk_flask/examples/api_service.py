"""
API Service Example

A REST API service showcasing authentication, elephant services integration,
and modern API development patterns with Flask-TSK.
"""

from flask import render_template, request, jsonify, redirect, url_for
from .base_example import BaseExample
from tsk_flask.herd import Herd
import time


class APIServiceExample(BaseExample):
    """API service example with REST endpoints and elephant integration"""
    
    def __init__(self):
        super().__init__(
            name="API Service",
            description="REST API service with authentication and elephant services integration"
        )
    
    def create_app(self, config=None):
        """Create the API service example app"""
        app = super().create_app(config)
        
        # Add API-specific routes
        self._add_api_routes()
        
        return app
    
    def _add_api_routes(self):
        """Add API service specific routes"""
        
        @self.app.route('/api/v1/status')
        def api_status():
            """API status endpoint"""
            return jsonify({
                'status': 'healthy',
                'version': '1.0.0',
                'elephants': len(self.elephants),
                'timestamp': int(time.time())
            })
        
        @self.app.route('/api/v1/elephants')
        def api_elephants():
            """Get elephant services status"""
            elephant_status = {}
            for name, elephant in self.elephants.items():
                try:
                    if hasattr(elephant, 'get_status'):
                        elephant_status[name] = elephant.get_status()
                    else:
                        elephant_status[name] = {'status': 'active', 'name': name}
                except:
                    elephant_status[name] = {'status': 'error', 'name': name}
            
            return jsonify({'elephants': elephant_status})
        
        @self.app.route('/api/v1/elephants/<elephant_name>/demo', methods=['POST'])
        def api_elephant_demo(elephant_name):
            """Demo elephant functionality via API"""
            if elephant_name not in self.elephants:
                return jsonify({'error': 'Elephant not found'}), 404
            
            elephant = self.elephants[elephant_name]
            data = request.get_json() or {}
            
            try:
                if elephant_name == 'babar':
                    # Content management demo
                    story = elephant.create_story({
                        'title': data.get('title', 'API Demo Story'),
                        'content': data.get('content', 'Created via API'),
                        'type': 'post'
                    })
                    return jsonify({'success': True, 'story': story})
                
                elif elephant_name == 'dumbo':
                    # HTTP client demo
                    url = data.get('url', 'https://httpbin.org/json')
                    response = elephant.get(url)
                    return jsonify({
                        'success': True,
                        'response': {
                            'status_code': response.status_code,
                            'content_type': response.content_type,
                            'url': response.url
                        }
                    })
                
                elif elephant_name == 'elmer':
                    # Theme generator demo
                    theme = elephant.create_evolving_theme(
                        data.get('name', 'api_theme'),
                        data.get('color', '#3B82F6')
                    )
                    return jsonify({
                        'success': True,
                        'theme': {
                            'name': theme.name,
                            'mood': theme.mood.value,
                            'harmony_type': theme.harmony_type.value
                        }
                    })
                
                elif elephant_name == 'heffalump':
                    # Search demo
                    query = data.get('query', 'demo')
                    results = elephant.hunt(query, ['content'])
                    return jsonify({
                        'success': True,
                        'results': len(results),
                        'query': query
                    })
                
                elif elephant_name == 'horton':
                    # Background jobs demo
                    job_data = data.get('data', {'message': 'API demo job'})
                    job_id = elephant.dispatch('api_demo_job', job_data)
                    return jsonify({
                        'success': True,
                        'job_id': job_id,
                        'message': 'Job dispatched successfully'
                    })
                
                elif elephant_name == 'koshik':
                    # Audio demo
                    notification_id = elephant.notify('success', {
                        'message': data.get('message', 'API demo notification')
                    })
                    return jsonify({
                        'success': True,
                        'notification_id': notification_id
                    })
                
                elif elephant_name == 'peanuts':
                    # Performance demo
                    status = elephant.get_performance_status()
                    return jsonify({
                        'success': True,
                        'performance': status
                    })
                
                else:
                    return jsonify({
                        'success': True,
                        'message': f'{elephant_name} is active',
                        'available_methods': [method for method in dir(elephant) if not method.startswith('_')]
                    })
                    
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/v1/users/profile')
        def api_user_profile():
            """Get authenticated user profile"""
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
        
        @self.app.route('/api/v1/users/profile', methods=['PUT'])
        def api_update_profile():
            """Update user profile"""
            if not Herd.check():
                return jsonify({'error': 'Authentication required'}), 401
            
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            # In a real app, would update user profile
            return jsonify({'success': True, 'message': 'Profile updated'})
        
        @self.app.route('/api/v1/content', methods=['GET'])
        def api_get_content():
            """Get content using Babar"""
            if 'babar' not in self.elephants:
                return jsonify({'error': 'Content management not available'}), 503
            
            try:
                filters = request.args.to_dict()
                library = self.elephants['babar'].get_library(filters)
                return jsonify(library)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/v1/content', methods=['POST'])
        def api_create_content():
            """Create content using Babar"""
            if not Herd.check():
                return jsonify({'error': 'Authentication required'}), 401
            
            if 'babar' not in self.elephants:
                return jsonify({'error': 'Content management not available'}), 503
            
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            try:
                story = self.elephants['babar'].create_story(data)
                return jsonify({'success': True, 'story': story}), 201
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/v1/search', methods=['POST'])
        def api_search():
            """Search using Heffalump"""
            if 'heffalump' not in self.elephants:
                return jsonify({'error': 'Search not available'}), 503
            
            data = request.get_json()
            if not data or 'query' not in data:
                return jsonify({'error': 'Query required'}), 400
            
            try:
                results = self.elephants['heffalump'].hunt(
                    data['query'],
                    data.get('search_in', ['content'])
                )
                return jsonify({
                    'success': True,
                    'results': [{'id': r.id, 'content': r.content, 'score': r.score} for r in results]
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/v1/jobs', methods=['POST'])
        def api_dispatch_job():
            """Dispatch background job using Horton"""
            if not Herd.check():
                return jsonify({'error': 'Authentication required'}), 401
            
            if 'horton' not in self.elephants:
                return jsonify({'error': 'Background jobs not available'}), 503
            
            data = request.get_json()
            if not data or 'job_name' not in data:
                return jsonify({'error': 'Job name required'}), 400
            
            try:
                job_id = self.elephants['horton'].dispatch(
                    data['job_name'],
                    data.get('data', {}),
                    data.get('queue', 'normal')
                )
                return jsonify({
                    'success': True,
                    'job_id': job_id,
                    'message': 'Job dispatched successfully'
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/v1/jobs/<job_id>/status')
        def api_job_status(job_id):
            """Get job status using Horton"""
            if 'horton' not in self.elephants:
                return jsonify({'error': 'Background jobs not available'}), 503
            
            try:
                status = self.elephants['horton'].status(job_id)
                if status:
                    return jsonify({'success': True, 'status': status})
                else:
                    return jsonify({'error': 'Job not found'}), 404
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/v1/upload', methods=['POST'])
        def api_start_upload():
            """Start file upload using Jumbo"""
            if not Herd.check():
                return jsonify({'error': 'Authentication required'}), 401
            
            if 'jumbo' not in self.elephants:
                return jsonify({'error': 'File upload not available'}), 503
            
            data = request.get_json()
            if not data or 'filename' not in data or 'size' not in data:
                return jsonify({'error': 'Filename and size required'}), 400
            
            try:
                upload_info = self.elephants['jumbo'].start_upload(
                    data['filename'],
                    data['size'],
                    data.get('metadata', {})
                )
                return jsonify({
                    'success': True,
                    'upload_id': upload_info['upload_id'],
                    'chunks_expected': upload_info['chunks_expected']
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/v1/upload/<upload_id>/chunk', methods=['POST'])
        def api_upload_chunk(upload_id):
            """Upload file chunk using Jumbo"""
            if not Herd.check():
                return jsonify({'error': 'Authentication required'}), 401
            
            if 'jumbo' not in self.elephants:
                return jsonify({'error': 'File upload not available'}), 503
            
            data = request.get_json()
            if not data or 'chunk_number' not in data or 'chunk_data' not in data:
                return jsonify({'error': 'Chunk number and data required'}), 400
            
            try:
                import base64
                chunk_data = base64.b64decode(data['chunk_data'])
                result = self.elephants['jumbo'].upload_chunk(
                    upload_id,
                    data['chunk_number'],
                    chunk_data
                )
                return jsonify({'success': True, 'result': result})
            except Exception as e:
                return jsonify({'error': str(e)}), 500


def create_api_service_example():
    """Factory function to create API service example"""
    return APIServiceExample()


if __name__ == '__main__':
    example = create_api_service_example()
    example.run() 