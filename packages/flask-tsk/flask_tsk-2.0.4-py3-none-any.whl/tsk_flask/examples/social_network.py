"""
Social Network Example

A social network application showcasing user profiles, content sharing,
real-time features, and comprehensive elephant services integration.
"""

from flask import render_template, request, jsonify, redirect, url_for, flash
from .base_example import BaseExample
from tsk_flask.herd import Herd
import time


class SocialNetworkExample(BaseExample):
    """Social network example with user profiles and content sharing"""
    
    def __init__(self):
        super().__init__(
            name="Social Network",
            description="Social network with user profiles, content sharing, and elephant services"
        )
        self.posts = []
        self.profiles = {}
    
    def create_app(self, config=None):
        """Create the social network example app"""
        app = super().create_app(config)
        
        # Add social network specific routes
        self._add_social_routes()
        
        return app
    
    def _add_social_routes(self):
        """Add social network specific routes"""
        
        @self.app.route('/feed')
        def feed():
            """Main social feed"""
            if not Herd.check():
                return redirect(url_for('login'))
            
            # Get posts using Babar
            try:
                if 'babar' in self.elephants:
                    library = self.elephants['babar'].get_library({
                        'type': 'post',
                        'status': 'published',
                        'limit': 20
                    })
                    posts = library.get('stories', [])
                else:
                    posts = self.posts
            except:
                posts = self.posts
            
            return render_template('social/feed.html', posts=posts)
        
        @self.app.route('/profile/<user_id>')
        def user_profile(user_id):
            """User profile page"""
            if not Herd.check():
                return redirect(url_for('login'))
            
            # Get user profile
            profile = self.profiles.get(user_id, {
                'id': user_id,
                'name': f'User {user_id}',
                'bio': 'No bio available',
                'avatar': '/static/images/default-avatar.jpg'
            })
            
            # Get user's posts
            try:
                if 'babar' in self.elephants:
                    library = self.elephants['babar'].get_library({
                        'author_id': user_id,
                        'type': 'post',
                        'status': 'published',
                        'limit': 10
                    })
                    posts = library.get('stories', [])
                else:
                    posts = [p for p in self.posts if p.get('author_id') == user_id]
            except:
                posts = [p for p in self.posts if p.get('author_id') == user_id]
            
            return render_template('social/profile.html', profile=profile, posts=posts)
        
        @self.app.route('/post/create', methods=['GET', 'POST'])
        def create_post():
            """Create new post"""
            if not Herd.check():
                return redirect(url_for('login'))
            
            if request.method == 'POST':
                content = request.form.get('content')
                image = request.files.get('image')
                
                if not content:
                    flash('Content is required', 'error')
                    return render_template('social/create_post.html')
                
                user = Herd.user()
                
                # Handle image upload with Jumbo
                image_path = None
                if image and image.filename:
                    if 'jumbo' in self.elephants:
                        try:
                            upload_result = self.elephants['jumbo'].start_upload(
                                image.filename,
                                len(image.read())
                            )
                            image_path = f'/static/images/{image.filename}'
                        except:
                            image_path = None
                
                # Create post using Babar
                try:
                    if 'babar' in self.elephants:
                        story = self.elephants['babar'].create_story({
                            'title': f'Post by {user.get("first_name", "User")}',
                            'content': content,
                            'type': 'post',
                            'status': 'published',
                            'metadata': {
                                'image': image_path,
                                'author_name': f"{user.get('first_name', '')} {user.get('last_name', '')}",
                                'likes': 0,
                                'comments': []
                            }
                        })
                        
                        # Notify with Koshik
                        if 'koshik' in self.elephants:
                            try:
                                self.elephants['koshik'].notify('success', {
                                    'message': 'Post created successfully!'
                                })
                            except:
                                pass
                        
                        flash('Post created successfully!', 'success')
                        return redirect(url_for('feed'))
                    else:
                        # Fallback to simple storage
                        post = {
                            'id': str(len(self.posts) + 1),
                            'content': content,
                            'author_id': user.get('id'),
                            'author_name': f"{user.get('first_name', '')} {user.get('last_name', '')}",
                            'image': image_path,
                            'likes': 0,
                            'comments': [],
                            'created_at': int(time.time())
                        }
                        self.posts.append(post)
                        flash('Post created successfully!', 'success')
                        return redirect(url_for('feed'))
                        
                except Exception as e:
                    flash(f'Error creating post: {str(e)}', 'error')
            
            return render_template('social/create_post.html')
        
        @self.app.route('/post/<post_id>')
        def view_post(post_id):
            """View individual post"""
            try:
                if 'babar' in self.elephants:
                    post = self.elephants['babar'].get_story(post_id)
                    if not post:
                        return render_template('error.html', error='Post not found'), 404
                else:
                    post = next((p for p in self.posts if p['id'] == post_id), None)
                    if not post:
                        return render_template('error.html', error='Post not found'), 404
                
                return render_template('social/post.html', post=post)
            except Exception as e:
                return render_template('error.html', error=str(e)), 500
        
        @self.app.route('/post/<post_id>/like', methods=['POST'])
        def like_post(post_id):
            """Like a post"""
            if not Herd.check():
                return jsonify({'error': 'Authentication required'}), 401
            
            try:
                if 'babar' in self.elephants:
                    post = self.elephants['babar'].get_story(post_id)
                    if not post:
                        return jsonify({'error': 'Post not found'}), 404
                    
                    # Update likes in metadata
                    metadata = post.get('metadata', {})
                    metadata['likes'] = metadata.get('likes', 0) + 1
                    
                    self.elephants['babar'].update_story(post_id, {
                        'metadata': metadata
                    })
                    
                    return jsonify({'success': True, 'likes': metadata['likes']})
                else:
                    # Fallback to simple storage
                    post = next((p for p in self.posts if p['id'] == post_id), None)
                    if not post:
                        return jsonify({'error': 'Post not found'}), 404
                    
                    post['likes'] += 1
                    return jsonify({'success': True, 'likes': post['likes']})
                    
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/post/<post_id>/comment', methods=['POST'])
        def comment_post(post_id):
            """Add comment to post"""
            if not Herd.check():
                return jsonify({'error': 'Authentication required'}), 401
            
            content = request.form.get('content')
            if not content:
                return jsonify({'error': 'Comment content required'}), 400
            
            user = Herd.user()
            comment = {
                'id': str(int(time.time())),
                'content': content,
                'author_id': user.get('id'),
                'author_name': f"{user.get('first_name', '')} {user.get('last_name', '')}",
                'created_at': int(time.time())
            }
            
            try:
                if 'babar' in self.elephants:
                    post = self.elephants['babar'].get_story(post_id)
                    if not post:
                        return jsonify({'error': 'Post not found'}), 404
                    
                    # Add comment to metadata
                    metadata = post.get('metadata', {})
                    comments = metadata.get('comments', [])
                    comments.append(comment)
                    metadata['comments'] = comments
                    
                    self.elephants['babar'].update_story(post_id, {
                        'metadata': metadata
                    })
                    
                    return jsonify({'success': True, 'comment': comment})
                else:
                    # Fallback to simple storage
                    post = next((p for p in self.posts if p['id'] == post_id), None)
                    if not post:
                        return jsonify({'error': 'Post not found'}), 404
                    
                    post['comments'].append(comment)
                    return jsonify({'success': True, 'comment': comment})
                    
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/search')
        def search():
            """Search posts and users using Heffalump"""
            query = request.args.get('q', '')
            
            if not query:
                return redirect(url_for('feed'))
            
            results = {'posts': [], 'users': []}
            
            try:
                if 'heffalump' in self.elephants:
                    # Search in posts
                    post_results = self.elephants['heffalump'].hunt(query, ['content', 'title'])
                    
                    # Get full post details
                    if 'babar' in self.elephants:
                        for result in post_results:
                            try:
                                post = self.elephants['babar'].get_story(result.id)
                                if post:
                                    results['posts'].append(post)
                            except:
                                continue
                    
                    # Search in user profiles
                    user_results = self.elephants['heffalump'].hunt(query, ['name', 'bio'])
                    for result in user_results:
                        user_id = result.id
                        if user_id in self.profiles:
                            results['users'].append(self.profiles[user_id])
                
                else:
                    # Fallback to simple search
                    for post in self.posts:
                        if query.lower() in post.get('content', '').lower():
                            results['posts'].append(post)
                    
                    for profile in self.profiles.values():
                        if query.lower() in profile.get('name', '').lower() or query.lower() in profile.get('bio', '').lower():
                            results['users'].append(profile)
                            
            except Exception as e:
                flash(f'Search error: {str(e)}', 'error')
            
            return render_template('social/search.html', results=results, query=query)
        
        @self.app.route('/settings/profile', methods=['GET', 'POST'])
        def edit_profile():
            """Edit user profile"""
            if not Herd.check():
                return redirect(url_for('login'))
            
            user = Herd.user()
            
            if request.method == 'POST':
                # Handle avatar upload with Jumbo
                avatar = request.files.get('avatar')
                avatar_path = None
                
                if avatar and avatar.filename:
                    if 'jumbo' in self.elephants:
                        try:
                            upload_result = self.elephants['jumbo'].start_upload(
                                avatar.filename,
                                len(avatar.read())
                            )
                            avatar_path = f'/static/images/{avatar.filename}'
                        except:
                            avatar_path = None
                
                # Update profile
                profile_data = {
                    'id': user.get('id'),
                    'name': request.form.get('name', f"{user.get('first_name', '')} {user.get('last_name', '')}"),
                    'bio': request.form.get('bio', ''),
                    'avatar': avatar_path or '/static/images/default-avatar.jpg'
                }
                
                self.profiles[user.get('id')] = profile_data
                
                flash('Profile updated successfully!', 'success')
                return redirect(url_for('user_profile', user_id=user.get('id')))
            
            # Get current profile
            current_profile = self.profiles.get(user.get('id'), {
                'name': f"{user.get('first_name', '')} {user.get('last_name', '')}",
                'bio': '',
                'avatar': '/static/images/default-avatar.jpg'
            })
            
            return render_template('social/edit_profile.html', profile=current_profile)


def create_social_network_example():
    """Factory function to create social network example"""
    return SocialNetworkExample()


if __name__ == '__main__':
    example = create_social_network_example()
    example.run() 