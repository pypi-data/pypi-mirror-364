"""
Flask-TSK Navigation Components
Bootstrap-style navigation components for Flask applications
"""

from flask import render_template_string
from typing import Dict, List, Optional

class NavigationComponent:
    """Navigation component system for Flask-TSK"""
    
    @staticmethod
    def navbar(items: List[Dict], brand: str = "Flask-TSK", theme: str = "default") -> str:
        """Generate a responsive navigation bar"""
        
        template = '''
        <nav class="navbar navbar-{{ theme }}">
            <div class="container">
                <div class="navbar-brand">
                    <a href="{{ brand_url }}" class="navbar-item">
                        {{ brand }}
                    </a>
                </div>
                
                <div class="navbar-menu">
                    {% for item in items %}
                        <a href="{{ item.url }}" class="navbar-item {{ 'active' if item.active else '' }}">
                            {% if item.icon %}{{ item.icon }} {% endif %}{{ item.text }}
                        </a>
                    {% endfor %}
                </div>
                
                <div class="navbar-toggle" onclick="toggleMobileMenu()">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        </nav>
        '''
        
        return render_template_string(template, items=items, brand=brand, theme=theme)
    
    @staticmethod
    def breadcrumb(items: List[Dict]) -> str:
        """Generate breadcrumb navigation"""
        
        template = '''
        <nav class="breadcrumb" aria-label="breadcrumb">
            <ol class="breadcrumb-list">
                {% for item in items %}
                    <li class="breadcrumb-item {{ 'active' if item.active else '' }}">
                        {% if item.active %}
                            {{ item.text }}
                        {% else %}
                            <a href="{{ item.url }}" class="breadcrumb-link">{{ item.text }}</a>
                        {% endif %}
                    </li>
                {% endfor %}
            </ol>
        </nav>
        '''
        
        return render_template_string(template, items=items)
    
    @staticmethod
    def sidebar(items: List[Dict], title: str = "Navigation") -> str:
        """Generate a sidebar navigation"""
        
        template = '''
        <aside class="sidebar">
            <div class="sidebar-header">
                <h3>{{ title }}</h3>
            </div>
            <nav class="sidebar-nav">
                <ul class="sidebar-menu">
                    {% for item in items %}
                        <li class="sidebar-item {{ 'active' if item.active else '' }}">
                            <a href="{{ item.url }}" class="sidebar-link">
                                {% if item.icon %}<span class="sidebar-icon">{{ item.icon }}</span>{% endif %}
                                <span class="sidebar-text">{{ item.text }}</span>
                            </a>
                        </li>
                    {% endfor %}
                </ul>
            </nav>
        </aside>
        '''
        
        return render_template_string(template, items=items, title=title)
    
    @staticmethod
    def pagination(current_page: int, total_pages: int, base_url: str = "?page=") -> str:
        """Generate pagination controls"""
        
        template = '''
        <nav class="pagination" aria-label="Page navigation">
            <ul class="pagination-list">
                {% if current_page > 1 %}
                    <li class="pagination-item">
                        <a href="{{ base_url }}{{ current_page - 1 }}" class="pagination-link">Previous</a>
                    </li>
                {% endif %}
                
                {% for page in range(1, total_pages + 1) %}
                    <li class="pagination-item {{ 'active' if page == current_page else '' }}">
                        <a href="{{ base_url }}{{ page }}" class="pagination-link">{{ page }}</a>
                    </li>
                {% endfor %}
                
                {% if current_page < total_pages %}
                    <li class="pagination-item">
                        <a href="{{ base_url }}{{ current_page + 1 }}" class="pagination-link">Next</a>
                    </li>
                {% endif %}
            </ul>
        </nav>
        '''
        
        return render_template_string(template, current_page=current_page, total_pages=total_pages, base_url=base_url) 