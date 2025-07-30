"""
Flask-TSK Blog Components
Blog components for Flask applications
"""

from flask import render_template_string
from typing import Dict, List, Optional
from datetime import datetime

class BlogComponent:
    """Blog component system for Flask-TSK"""
    
    @staticmethod
    def blog_post(post: Dict, show_author: bool = True, show_date: bool = True) -> str:
        """Generate a blog post component"""
        
        template = '''
        <article class="blog-post">
            {% if post.image %}
            <div class="blog-post-image">
                <img src="{{ post.image }}" alt="{{ post.title }}">
            </div>
            {% endif %}
            
            <div class="blog-post-content">
                <h2 class="blog-post-title">
                    <a href="/blog/{{ post.slug }}">{{ post.title }}</a>
                </h2>
                
                {% if show_author or show_date %}
                <div class="blog-post-meta">
                    {% if show_author and post.author %}
                    <span class="blog-post-author">
                        <i class="fas fa-user"></i>
                        {{ post.author }}
                    </span>
                    {% endif %}
                    
                    {% if show_date and post.published_date %}
                    <span class="blog-post-date">
                        <i class="fas fa-calendar"></i>
                        {{ post.published_date.strftime('%B %d, %Y') }}
                    </span>
                    {% endif %}
                    
                    {% if post.category %}
                    <span class="blog-post-category">
                        <i class="fas fa-folder"></i>
                        <a href="/blog/category/{{ post.category.slug }}">{{ post.category.name }}</a>
                    </span>
                    {% endif %}
                </div>
                {% endif %}
                
                <div class="blog-post-excerpt">
                    {{ post.excerpt or post.content[:200] + '...' }}
                </div>
                
                <div class="blog-post-footer">
                    <a href="/blog/{{ post.slug }}" class="btn btn-outline">Read More</a>
                    
                    {% if post.tags %}
                    <div class="blog-post-tags">
                        {% for tag in post.tags %}
                        <a href="/blog/tag/{{ tag.slug }}" class="tag">{{ tag.name }}</a>
                        {% endfor %}
                    </div>
                    {% endif %}
                </div>
            </div>
        </article>
        '''
        
        return render_template_string(template, post=post, show_author=show_author, show_date=show_date)
    
    @staticmethod
    def blog_list(posts: List[Dict], show_pagination: bool = True, posts_per_page: int = 10) -> str:
        """Generate a blog listing component"""
        
        template = '''
        <div class="blog-list">
            {% if posts %}
            <div class="blog-posts">
                {% for post in posts %}
                <div class="blog-post-item">
                    {{ blog_post | safe }}
                </div>
                {% endfor %}
            </div>
            
            {% if show_pagination and total_pages > 1 %}
            <div class="blog-pagination">
                {% if current_page > 1 %}
                <a href="?page={{ current_page - 1 }}" class="pagination-link pagination-prev">
                    <i class="fas fa-chevron-left"></i> Previous
                </a>
                {% endif %}
                
                <div class="pagination-numbers">
                    {% for page in range(1, total_pages + 1) %}
                    <a href="?page={{ page }}" class="pagination-link {{ 'active' if page == current_page else '' }}">
                        {{ page }}
                    </a>
                    {% endfor %}
                </div>
                
                {% if current_page < total_pages %}
                <a href="?page={{ current_page + 1 }}" class="pagination-link pagination-next">
                    Next <i class="fas fa-chevron-right"></i>
                </a>
                {% endif %}
            </div>
            {% endif %}
            
            {% else %}
            <div class="blog-empty">
                <p>No blog posts found.</p>
            </div>
            {% endif %}
        </div>
        '''
        
        total_pages = (len(posts) + posts_per_page - 1) // posts_per_page
        current_page = 1  # This would come from request.args.get('page', 1, type=int)
        
        blog_posts = [BlogComponent.blog_post(post) for post in posts]
        
        return render_template_string(template, posts=posts, blog_post=''.join(blog_posts),
                                    show_pagination=show_pagination, total_pages=total_pages,
                                    current_page=current_page)
    
    @staticmethod
    def blog_sidebar(categories: List[Dict] = None, recent_posts: List[Dict] = None,
                    tags: List[Dict] = None) -> str:
        """Generate a blog sidebar component"""
        
        categories = categories or []
        recent_posts = recent_posts or []
        tags = tags or []
        
        template = '''
        <aside class="blog-sidebar">
            {% if categories %}
            <div class="sidebar-widget">
                <h3 class="widget-title">Categories</h3>
                <ul class="category-list">
                    {% for category in categories %}
                    <li class="category-item">
                        <a href="/blog/category/{{ category.slug }}" class="category-link">
                            {{ category.name }}
                            <span class="category-count">({{ category.post_count }})</span>
                        </a>
                    </li>
                    {% endfor %}
                </ul>
            </div>
            {% endif %}
            
            {% if recent_posts %}
            <div class="sidebar-widget">
                <h3 class="widget-title">Recent Posts</h3>
                <ul class="recent-posts-list">
                    {% for post in recent_posts %}
                    <li class="recent-post-item">
                        <a href="/blog/{{ post.slug }}" class="recent-post-link">
                            <div class="recent-post-image">
                                {% if post.image %}
                                <img src="{{ post.image }}" alt="{{ post.title }}">
                                {% endif %}
                            </div>
                            <div class="recent-post-content">
                                <h4 class="recent-post-title">{{ post.title }}</h4>
                                <span class="recent-post-date">{{ post.published_date.strftime('%M %d') }}</span>
                            </div>
                        </a>
                    </li>
                    {% endfor %}
                </ul>
            </div>
            {% endif %}
            
            {% if tags %}
            <div class="sidebar-widget">
                <h3 class="widget-title">Tags</h3>
                <div class="tag-cloud">
                    {% for tag in tags %}
                    <a href="/blog/tag/{{ tag.slug }}" class="tag tag-{{ tag.size }}">
                        {{ tag.name }}
                    </a>
                    {% endfor %}
                </div>
            </div>
            {% endif %}
        </aside>
        '''
        
        return render_template_string(template, categories=categories, recent_posts=recent_posts, tags=tags)
    
    @staticmethod
    def blog_search(search_query: str = "", results: List[Dict] = None) -> str:
        """Generate a blog search component"""
        
        results = results or []
        
        template = '''
        <div class="blog-search">
            <form class="search-form" method="GET" action="/blog/search">
                <div class="search-input-group">
                    <input type="text" name="q" value="{{ search_query }}" 
                           placeholder="Search blog posts..." class="search-input">
                    <button type="submit" class="search-button">
                        <i class="fas fa-search"></i>
                    </button>
                </div>
            </form>
            
            {% if search_query %}
            <div class="search-results">
                <h3>Search Results for "{{ search_query }}"</h3>
                
                {% if results %}
                <p class="results-count">{{ results|length }} result(s) found</p>
                
                <div class="search-results-list">
                    {% for post in results %}
                    <div class="search-result-item">
                        <h4 class="result-title">
                            <a href="/blog/{{ post.slug }}">{{ post.title }}</a>
                        </h4>
                        <p class="result-excerpt">{{ post.excerpt }}</p>
                        <div class="result-meta">
                            <span class="result-date">{{ post.published_date.strftime('%B %d, %Y') }}</span>
                            {% if post.category %}
                            <span class="result-category">{{ post.category.name }}</span>
                            {% endif %}
                        </div>
                    </div>
                    {% endfor %}
                </div>
                
                {% else %}
                <p class="no-results">No results found for "{{ search_query }}"</p>
                <p>Try different keywords or browse our <a href="/blog">blog posts</a>.</p>
                {% endif %}
            </div>
            {% endif %}
        </div>
        '''
        
        return render_template_string(template, search_query=search_query, results=results) 