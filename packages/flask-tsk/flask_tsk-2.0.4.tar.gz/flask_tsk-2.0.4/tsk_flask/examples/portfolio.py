"""
Portfolio Example

A personal portfolio website showcasing projects, skills, and admin panel
with elephant services integration for content management.
"""

from flask import render_template, request, jsonify, redirect, url_for, flash
from .base_example import BaseExample
from tsk_flask.herd import Herd
import time


class PortfolioExample(BaseExample):
    """Portfolio example with project showcase and admin panel"""
    
    def __init__(self):
        super().__init__(
            name="Portfolio Website",
            description="Personal portfolio website with project showcase and admin panel"
        )
        self.projects = self._initialize_projects()
        self.skills = self._initialize_skills()
    
    def create_app(self, config=None):
        """Create the portfolio example app"""
        app = super().create_app(config)
        
        # Add portfolio specific routes
        self._add_portfolio_routes()
        
        return app
    
    def _initialize_projects(self):
        """Initialize sample projects"""
        projects = [
            {
                'id': '1',
                'title': 'Flask-TSK Framework',
                'description': 'A comprehensive Flask framework with elephant services',
                'image': '/static/images/flask-tsk.jpg',
                'technologies': ['Python', 'Flask', 'SQLite', 'JavaScript'],
                'github_url': 'https://github.com/example/flask-tsk',
                'live_url': 'https://flask-tsk.example.com',
                'featured': True
            },
            {
                'id': '2',
                'title': 'E-commerce Platform',
                'description': 'Full-stack e-commerce solution with payment integration',
                'image': '/static/images/ecommerce.jpg',
                'technologies': ['React', 'Node.js', 'MongoDB', 'Stripe'],
                'github_url': 'https://github.com/example/ecommerce',
                'live_url': 'https://ecommerce.example.com',
                'featured': True
            },
            {
                'id': '3',
                'title': 'Social Network App',
                'description': 'Real-time social networking application',
                'image': '/static/images/social.jpg',
                'technologies': ['Vue.js', 'Firebase', 'Socket.io'],
                'github_url': 'https://github.com/example/social',
                'live_url': 'https://social.example.com',
                'featured': False
            }
        ]
        
        # Store projects using Babar if available
        if 'babar' in self.elephants:
            for project in projects:
                try:
                    self.elephants['babar'].create_story({
                        'title': project['title'],
                        'content': project['description'],
                        'type': 'project',
                        'status': 'published',
                        'metadata': {
                            'project_id': project['id'],
                            'image': project['image'],
                            'technologies': project['technologies'],
                            'github_url': project['github_url'],
                            'live_url': project['live_url'],
                            'featured': project['featured']
                        }
                    })
                except:
                    pass
        
        return projects
    
    def _initialize_skills(self):
        """Initialize skills data"""
        return [
            {'name': 'Python', 'level': 90, 'category': 'Programming'},
            {'name': 'JavaScript', 'level': 85, 'category': 'Programming'},
            {'name': 'React', 'level': 80, 'category': 'Frontend'},
            {'name': 'Vue.js', 'level': 75, 'category': 'Frontend'},
            {'name': 'Node.js', 'level': 80, 'category': 'Backend'},
            {'name': 'Flask', 'level': 85, 'category': 'Backend'},
            {'name': 'MongoDB', 'level': 70, 'category': 'Database'},
            {'name': 'PostgreSQL', 'level': 75, 'category': 'Database'},
            {'name': 'Docker', 'level': 70, 'category': 'DevOps'},
            {'name': 'AWS', 'level': 65, 'category': 'Cloud'}
        ]
    
    def _add_portfolio_routes(self):
        """Add portfolio specific routes"""
        
        @self.app.route('/')
        def home():
            """Portfolio homepage"""
            featured_projects = [p for p in self.projects if p.get('featured', False)]
            
            return render_template('portfolio/home.html', 
                                featured_projects=featured_projects,
                                skills=self.skills)
        
        @self.app.route('/about')
        def about():
            """About page"""
            return render_template('portfolio/about.html')
        
        @self.app.route('/projects')
        def projects():
            """Projects showcase page"""
            return render_template('portfolio/projects.html', projects=self.projects)
        
        @self.app.route('/project/<project_id>')
        def project_detail(project_id):
            """Individual project page"""
            project = next((p for p in self.projects if p['id'] == project_id), None)
            
            if not project:
                return render_template('error.html', error='Project not found'), 404
            
            return render_template('portfolio/project.html', project=project)
        
        @self.app.route('/contact')
        def contact():
            """Contact page"""
            return render_template('portfolio/contact.html')
        
        @self.app.route('/contact', methods=['POST'])
        def submit_contact():
            """Handle contact form submission"""
            name = request.form.get('name')
            email = request.form.get('email')
            message = request.form.get('message')
            
            if not all([name, email, message]):
                flash('All fields are required', 'error')
                return render_template('portfolio/contact.html')
            
            # Process contact form using Horton background job
            if 'horton' in self.elephants:
                try:
                    job_id = self.elephants['horton'].dispatch('process_contact', {
                        'name': name,
                        'email': email,
                        'message': message,
                        'timestamp': int(time.time())
                    })
                except:
                    pass
            
            # Notify with Koshik
            if 'koshik' in self.elephants:
                try:
                    self.elephants['koshik'].notify('success', {
                        'message': 'Contact message sent successfully!'
                    })
                except:
                    pass
            
            flash('Thank you for your message! I\'ll get back to you soon.', 'success')
            return redirect(url_for('contact'))
        
        @self.app.route('/admin')
        def admin_dashboard():
            """Admin dashboard"""
            if not Herd.check():
                return redirect(url_for('login'))
            
            user = Herd.user()
            if user.get('role') != 'admin':
                return render_template('error.html', 
                                     error='Access denied. Admin role required.'), 403
            
            # Get portfolio statistics
            stats = {
                'total_projects': len(self.projects),
                'featured_projects': len([p for p in self.projects if p.get('featured', False)]),
                'total_skills': len(self.skills),
                'skills_by_category': {}
            }
            
            for skill in self.skills:
                category = skill['category']
                if category not in stats['skills_by_category']:
                    stats['skills_by_category'][category] = 0
                stats['skills_by_category'][category] += 1
            
            return render_template('portfolio/admin/dashboard.html', 
                                user=user, 
                                stats=stats,
                                projects=self.projects)
        
        @self.app.route('/admin/projects')
        def admin_projects():
            """Project management"""
            if not Herd.check():
                return redirect(url_for('login'))
            
            user = Herd.user()
            if user.get('role') != 'admin':
                return render_template('error.html', 
                                     error='Access denied. Admin role required.'), 403
            
            return render_template('portfolio/admin/projects.html', 
                                user=user, 
                                projects=self.projects)
        
        @self.app.route('/admin/projects/create', methods=['GET', 'POST'])
        def create_project():
            """Create new project"""
            if not Herd.check():
                return redirect(url_for('login'))
            
            user = Herd.user()
            if user.get('role') != 'admin':
                return render_template('error.html', 
                                     error='Access denied. Admin role required.'), 403
            
            if request.method == 'POST':
                # Handle image upload with Jumbo
                image = request.files.get('image')
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
                            image_path = '/static/images/default-project.jpg'
                
                # Create project
                technologies = request.form.get('technologies', '').split(',')
                technologies = [tech.strip() for tech in technologies if tech.strip()]
                
                new_project = {
                    'id': str(len(self.projects) + 1),
                    'title': request.form.get('title'),
                    'description': request.form.get('description'),
                    'image': image_path or '/static/images/default-project.jpg',
                    'technologies': technologies,
                    'github_url': request.form.get('github_url'),
                    'live_url': request.form.get('live_url'),
                    'featured': request.form.get('featured') == 'on'
                }
                
                self.projects.append(new_project)
                
                # Store in Babar
                if 'babar' in self.elephants:
                    try:
                        self.elephants['babar'].create_story({
                            'title': new_project['title'],
                            'content': new_project['description'],
                            'type': 'project',
                            'status': 'published',
                            'metadata': {
                                'project_id': new_project['id'],
                                'image': new_project['image'],
                                'technologies': new_project['technologies'],
                                'github_url': new_project['github_url'],
                                'live_url': new_project['live_url'],
                                'featured': new_project['featured']
                            }
                        })
                    except:
                        pass
                
                flash('Project created successfully!', 'success')
                return redirect(url_for('admin_projects'))
            
            return render_template('portfolio/admin/create_project.html')
        
        @self.app.route('/admin/skills')
        def admin_skills():
            """Skill management"""
            if not Herd.check():
                return redirect(url_for('login'))
            
            user = Herd.user()
            if user.get('role') != 'admin':
                return render_template('error.html', 
                                     error='Access denied. Admin role required.'), 403
            
            return render_template('portfolio/admin/skills.html', 
                                user=user, 
                                skills=self.skills)
        
        @self.app.route('/admin/skills/create', methods=['GET', 'POST'])
        def create_skill():
            """Create new skill"""
            if not Herd.check():
                return redirect(url_for('login'))
            
            user = Herd.user()
            if user.get('role') != 'admin':
                return render_template('error.html', 
                                     error='Access denied. Admin role required.'), 403
            
            if request.method == 'POST':
                new_skill = {
                    'name': request.form.get('name'),
                    'level': int(request.form.get('level', 50)),
                    'category': request.form.get('category', 'Programming')
                }
                
                self.skills.append(new_skill)
                
                flash('Skill added successfully!', 'success')
                return redirect(url_for('admin_skills'))
            
            return render_template('portfolio/admin/create_skill.html')
        
        @self.app.route('/api/portfolio/stats')
        def api_portfolio_stats():
            """Portfolio statistics API"""
            stats = {
                'projects': {
                    'total': len(self.projects),
                    'featured': len([p for p in self.projects if p.get('featured', False)])
                },
                'skills': {
                    'total': len(self.skills),
                    'categories': {}
                }
            }
            
            for skill in self.skills:
                category = skill['category']
                if category not in stats['skills']['categories']:
                    stats['skills']['categories'][category] = 0
                stats['skills']['categories'][category] += 1
            
            return jsonify(stats)


def create_portfolio_example():
    """Factory function to create portfolio example"""
    return PortfolioExample()


if __name__ == '__main__':
    example = create_portfolio_example()
    example.run() 