"""
Blog System Example

A complete blog system showcasing content management with Babar elephant,
user authentication with Herd, and various elephant services integration.
"""

from flask import render_template, request, jsonify, redirect, url_for, flash
from .base_example import BaseExample
from tsk_flask.herd import Herd


class BlogSystemExample(BaseExample):
    """Blog system example with content management and elephant services"""
    
    def __init__(self):
        super().__init__(
            name="Blog System",
            description="Complete blog system with content management, user authentication, and elephant services"
        )
    
    def create_app(self, config=None):
        """Create the blog system example app"""
        app = super().create_app(config)
        
        # Add blog-specific routes
        self._add_blog_routes()
        
        return app
    
    def _add_blog_routes(self):
        """Add blog system specific routes"""
        
        @self.app.route('/blog')
        def blog_index():
            """Blog homepage showing all posts"""
            try:
                if 'babar' in self.elephants:
                    # Get all published posts
                    library = self.elephants['babar'].get_library({
                        'status': 'published',
                        'type': 'post',
                        'limit': 10
                    })
                    posts = library.get('stories', [])
                else:
                    posts = []
                
                return render_template('blog/index.html', posts=posts)
            except Exception as e:
                return render_template('blog/index.html', posts=[], error=str(e))
        
        @self.app.route('/blog/post/<post_id>')
        def blog_post(post_id):
            """Individual blog post page"""
            try:
                if 'babar' in self.elephants:
                    post = self.elephants['babar'].get_story(post_id)
                    if not post:
                        return render_template('error.html', error='Post not found'), 404
                else:
                    post = None
                
                return render_template('blog/post.html', post=post)
            except Exception as e:
                return render_template('error.html', error=str(e)), 500
        
        @self.app.route('/blog/create', methods=['GET', 'POST'])
        def create_post():
            """Create new blog post - requires authentication"""
            if not Herd.check():
                return redirect(url_for('login'))
            
            if request.method == 'POST':
                title = request.form.get('title')
                content = request.form.get('content')
                excerpt = request.form.get('excerpt', '')
                
                if not title or not content:
                    flash('Title and content are required', 'error')
                    return render_template('blog/create.html')
                
                try:
                    if 'babar' in self.elephants:
                        story = self.elephants['babar'].create_story({
                            'title': title,
                            'content': content,
                            'excerpt': excerpt,
                            'type': 'post',
                            'status': 'draft'
                        })
                        
                        flash('Post created successfully!', 'success')
                        return redirect(url_for('blog_post', post_id=story.get('id')))
                    else:
                        flash('Content management system not available', 'error')
                        
                except Exception as e:
                    flash(f'Error creating post: {str(e)}', 'error')
            
            return render_template('blog/create.html')
        
        @self.app.route('/blog/edit/<post_id>', methods=['GET', 'POST'])
        def edit_post(post_id):
            """Edit blog post - requires authentication and ownership"""
            if not Herd.check():
                return redirect(url_for('login'))
            
            try:
                if 'babar' in self.elephants:
                    post = self.elephants['babar'].get_story(post_id)
                    if not post:
                        return render_template('error.html', error='Post not found'), 404
                    
                    # Check ownership
                    user = Herd.user()
                    if post.get('author_id') != user.get('id') and user.get('role') != 'admin':
                        return render_template('error.html', error='Access denied'), 403
                    
                    if request.method == 'POST':
                        title = request.form.get('title')
                        content = request.form.get('content')
                        excerpt = request.form.get('excerpt', '')
                        status = request.form.get('status', 'draft')
                        
                        updated_story = self.elephants['babar'].update_story(post_id, {
                            'title': title,
                            'content': content,
                            'excerpt': excerpt,
                            'status': status
                        })
                        
                        flash('Post updated successfully!', 'success')
                        return redirect(url_for('blog_post', post_id=post_id))
                    
                    return render_template('blog/edit.html', post=post)
                else:
                    return render_template('error.html', error='Content management system not available'), 500
                    
            except Exception as e:
                return render_template('error.html', error=str(e)), 500
        
        @self.app.route('/blog/publish/<post_id>')
        def publish_post(post_id):
            """Publish a draft post"""
            if not Herd.check():
                return redirect(url_for('login'))
            
            try:
                if 'babar' in self.elephants:
                    post = self.elephants['babar'].get_story(post_id)
                    if not post:
                        return jsonify({'error': 'Post not found'}), 404
                    
                    # Check ownership
                    user = Herd.user()
                    if post.get('author_id') != user.get('id') and user.get('role') != 'admin':
                        return jsonify({'error': 'Access denied'}), 403
                    
                    result = self.elephants['babar'].publish(post_id)
                    return jsonify({'success': True, 'message': 'Post published successfully'})
                else:
                    return jsonify({'error': 'Content management system not available'}), 500
                    
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/blog/search')
        def search_posts():
            """Search blog posts using Heffalump"""
            query = request.args.get('q', '')
            
            if not query:
                return redirect(url_for('blog_index'))
            
            try:
                if 'heffalump' in self.elephants:
                    # Search in content
                    results = self.elephants['heffalump'].hunt(query, ['content', 'title'])
                    
                    # Get full post details for search results
                    posts = []
                    if 'babar' in self.elephants:
                        for result in results[:10]:  # Limit to 10 results
                            try:
                                post = self.elephants['babar'].get_story(result.id)
                                if post:
                                    posts.append(post)
                            except:
                                continue
                    
                    return render_template('blog/search.html', posts=posts, query=query)
                else:
                    return render_template('blog/search.html', posts=[], query=query, error='Search not available')
                    
            except Exception as e:
                return render_template('blog/search.html', posts=[], query=query, error=str(e))
        
        @self.app.route('/blog/my-posts')
        def my_posts():
            """User's own posts"""
            if not Herd.check():
                return redirect(url_for('login'))
            
            try:
                if 'babar' in self.elephants:
                    user = Herd.user()
                    library = self.elephants['babar'].get_library({
                        'author_id': user.get('id'),
                        'limit': 20
                    })
                    posts = library.get('stories', [])
                else:
                    posts = []
                
                return render_template('blog/my_posts.html', posts=posts)
            except Exception as e:
                return render_template('blog/my_posts.html', posts=[], error=str(e))
        
        @self.app.route('/api/blog/stats')
        def blog_stats():
            """Blog statistics API"""
            if not Herd.check():
                return jsonify({'error': 'Authentication required'}), 401
            
            try:
                stats = {}
                
                if 'babar' in self.elephants:
                    # Get content statistics
                    library = self.elephants['babar'].get_library({'limit': 1000})
                    all_posts = library.get('stories', [])
                    
                    stats['total_posts'] = len(all_posts)
                    stats['published_posts'] = len([p for p in all_posts if p.get('status') == 'published'])
                    stats['draft_posts'] = len([p for p in all_posts if p.get('status') == 'draft'])
                    
                    # Get user's posts
                    user = Herd.user()
                    user_posts = [p for p in all_posts if p.get('author_id') == user.get('id')]
                    stats['my_posts'] = len(user_posts)
                
                if 'peanuts' in self.elephants:
                    # Get performance stats
                    perf_stats = self.elephants['peanuts'].get_performance_status()
                    stats['performance'] = perf_stats
                
                return jsonify(stats)
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500


def create_blog_system_example():
    """Factory function to create blog system example"""
    return BlogSystemExample()


if __name__ == '__main__':
    example = create_blog_system_example()
    example.run() 