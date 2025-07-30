"""
Flask-TSK Layout Components
Layout management for Flask applications including headers, footers, and page structures
"""

from flask import render_template_string
from typing import Dict, List, Optional

class LayoutComponent:
    """Layout component system for Flask-TSK"""
    
    @staticmethod
    def header(title: str = "Flask-TSK", navigation: List[Dict] = None, 
              theme: str = "default", show_search: bool = True) -> str:
        """Generate a page header with navigation"""
        
        nav_items = navigation or []
        
        template = '''
        <header class="header header-{{ theme }}">
            <div class="container">
                <div class="header-top">
                    <div class="header-brand">
                        <h1 class="header-title">{{ title }}</h1>
                    </div>
                    
                    {% if show_search %}
                    <div class="header-search">
                        <form class="search-form" action="/search" method="GET">
                            <input type="text" name="q" placeholder="Search..." class="search-input">
                            <button type="submit" class="search-button">
                                <i class="fas fa-search"></i>
                            </button>
                        </form>
                    </div>
                    {% endif %}
                </div>
                
                {% if nav_items %}
                <nav class="header-nav">
                    <ul class="nav-list">
                        {% for item in nav_items %}
                        <li class="nav-item {{ 'active' if item.active else '' }}">
                            <a href="{{ item.url }}" class="nav-link">
                                {% if item.icon %}<i class="{{ item.icon }}"></i>{% endif %}
                                {{ item.text }}
                            </a>
                        </li>
                        {% endfor %}
                    </ul>
                </nav>
                {% endif %}
            </div>
        </header>
        '''
        
        return render_template_string(template, title=title, nav_items=nav_items, 
                                    theme=theme, show_search=show_search)
    
    @staticmethod
    def footer(copyright_text: str = "© 2024 Flask-TSK", 
              links: List[Dict] = None, social_links: List[Dict] = None,
              theme: str = "default") -> str:
        """Generate a page footer"""
        
        links = links or []
        social_links = social_links or []
        
        template = '''
        <footer class="footer footer-{{ theme }}">
            <div class="container">
                <div class="footer-content">
                    <div class="footer-section">
                        <h3 class="footer-title">Quick Links</h3>
                        <ul class="footer-links">
                            {% for link in links %}
                            <li class="footer-link-item">
                                <a href="{{ link.url }}" class="footer-link">{{ link.text }}</a>
                            </li>
                            {% endfor %}
                        </ul>
                    </div>
                    
                    {% if social_links %}
                    <div class="footer-section">
                        <h3 class="footer-title">Follow Us</h3>
                        <div class="social-links">
                            {% for social in social_links %}
                            <a href="{{ social.url }}" class="social-link" target="_blank">
                                <i class="{{ social.icon }}"></i>
                            </a>
                            {% endfor %}
                        </div>
                    </div>
                    {% endif %}
                </div>
                
                <div class="footer-bottom">
                    <p class="footer-copyright">{{ copyright_text }}</p>
                </div>
            </div>
        </footer>
        '''
        
        return render_template_string(template, copyright_text=copyright_text, 
                                    links=links, social_links=social_links, theme=theme)
    
    @staticmethod
    def page_layout(title: str = "Flask-TSK", content: str = "", 
                   header_nav: List[Dict] = None, footer_links: List[Dict] = None,
                   theme: str = "default") -> str:
        """Generate a complete page layout with header, content, and footer"""
        
        header_nav = header_nav or []
        footer_links = footer_links or []
        
        template = '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{{ title }}</title>
            <link rel="stylesheet" href="/static/css/flask-tsk.css">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        </head>
        <body class="theme-{{ theme }}">
            {{ header | safe }}
            
            <main class="main-content">
                {{ content | safe }}
            </main>
            
            {{ footer | safe }}
            
            <script src="/static/js/flask-tsk.js"></script>
        </body>
        </html>
        '''
        
        header = LayoutComponent.header(title, header_nav, theme)
        footer = LayoutComponent.footer(f"© 2024 {title}", footer_links, theme=theme)
        
        return render_template_string(template, title=title, content=content, 
                                    header=header, footer=footer, theme=theme)
    
    @staticmethod
    def sidebar_layout(content: str = "", sidebar_content: str = "", 
                     sidebar_position: str = "left", theme: str = "default") -> str:
        """Generate a layout with sidebar"""
        
        template = '''
        <div class="layout-sidebar layout-sidebar-{{ sidebar_position }} theme-{{ theme }}">
            <aside class="sidebar">
                {{ sidebar_content | safe }}
            </aside>
            
            <main class="main-content">
                {{ content | safe }}
            </main>
        </div>
        '''
        
        return render_template_string(template, content=content, 
                                    sidebar_content=sidebar_content,
                                    sidebar_position=sidebar_position, theme=theme)
    
    @staticmethod
    def grid_layout(items: List[Dict], columns: int = 3, theme: str = "default") -> str:
        """Generate a responsive grid layout"""
        
        template = '''
        <div class="grid-layout grid-{{ columns }}-columns theme-{{ theme }}">
            {% for item in items %}
            <div class="grid-item">
                {% if item.title %}
                <h3 class="grid-item-title">{{ item.title }}</h3>
                {% endif %}
                
                {% if item.image %}
                <div class="grid-item-image">
                    <img src="{{ item.image }}" alt="{{ item.title or 'Grid item' }}">
                </div>
                {% endif %}
                
                <div class="grid-item-content">
                    {{ item.content | safe }}
                </div>
                
                {% if item.link %}
                <div class="grid-item-action">
                    <a href="{{ item.link.url }}" class="btn btn-primary">{{ item.link.text }}</a>
                </div>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        '''
        
        return render_template_string(template, items=items, columns=columns, theme=theme) 