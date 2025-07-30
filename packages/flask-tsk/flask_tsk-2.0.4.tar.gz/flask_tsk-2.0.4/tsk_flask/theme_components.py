"""
Flask-TSK Theme Components Library
Pre-built headers, footers, navigation, and other UI components
"""

from flask import render_template_string
from typing import Dict, List, Optional, Any
from themes import BaseTheme

class ThemeComponents:
    """Comprehensive theme component library"""
    
    @staticmethod
    def render_header_modern(nav_data: Dict = None, user_data: Dict = None) -> str:
        """Modern header component"""
        template = '''
        <header class="header-modern">
            <div class="container">
                <div class="header-content">
                    <div class="header-brand">
                        <a href="/" class="brand-logo">
                            <span class="brand-icon">🐘</span>
                            <span class="brand-text">Flask-TSK</span>
                        </a>
                    </div>
                    
                    <nav class="header-nav">
                        {% for item in nav_data.main_nav %}
                            <a href="{{ item.url }}" class="nav-link {{ 'active' if item.active else '' }}">
                                <span class="nav-icon">{{ item.icon }}</span>
                                <span class="nav-text">{{ item.text }}</span>
                            </a>
                        {% endfor %}
                    </nav>
                    
                    <div class="header-actions">
                        {% if user_data %}
                            <div class="user-menu">
                                <div class="user-avatar">
                                    <img src="{{ user_data.user.avatar }}" alt="{{ user_data.user.name }}">
                                    <span class="notification-badge">{{ user_data.user.notifications }}</span>
                                </div>
                                <div class="user-dropdown">
                                    <div class="user-info">
                                        <strong>{{ user_data.user.name }}</strong>
                                        <span>{{ user_data.user.role }}</span>
                                    </div>
                                    {% for item in user_data.menu_items %}
                                        <a href="{{ item.url }}" class="dropdown-item">
                                            <span class="item-icon">{{ item.icon }}</span>
                                            <span class="item-text">{{ item.text }}</span>
                                        </a>
                                    {% endfor %}
                                </div>
                            </div>
                        {% endif %}
                    </div>
                </div>
            </div>
        </header>
        '''
        return render_template_string(template, nav_data=nav_data or {}, user_data=user_data)
    
    @staticmethod
    def render_footer_modern(stats_data: Dict = None, activity_data: Dict = None) -> str:
        """Modern footer component"""
        template = '''
        <footer class="footer-modern">
            <div class="container">
                <div class="footer-content">
                    <div class="footer-section">
                        <h3>Flask-TSK</h3>
                        <p>Revolutionary Flask extension with TuskLang integration</p>
                        <div class="social-links">
                            <a href="#" class="social-link">🐦</a>
                            <a href="#" class="social-link">📘</a>
                            <a href="#" class="social-link">💻</a>
                        </div>
                    </div>
                    
                    {% if stats_data %}
                    <div class="footer-section">
                        <h4>Quick Stats</h4>
                        <div class="stats-grid">
                            <div class="stat-item">
                                <span class="stat-number">{{ stats_data.total_users }}</span>
                                <span class="stat-label">Users</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-number">{{ stats_data.active_projects }}</span>
                                <span class="stat-label">Projects</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-number">${{ stats_data.total_revenue }}</span>
                                <span class="stat-label">Revenue</span>
                            </div>
                        </div>
                    </div>
                    {% endif %}
                    
                    {% if activity_data %}
                    <div class="footer-section">
                        <h4>Recent Activity</h4>
                        <div class="activity-list">
                            {% for activity in activity_data.activities %}
                                <div class="activity-item">
                                    <span class="activity-icon">📝</span>
                                    <span class="activity-text">{{ activity.user }} {{ activity.type }}</span>
                                    <span class="activity-time">{{ activity.time }}</span>
                                </div>
                            {% endfor %}
                        </div>
                    </div>
                    {% endif %}
                </div>
                
                <div class="footer-bottom">
                    <p>&copy; 2024 Flask-TSK. Powered by <a href="https://github.com/cyber-boost/tusktsk">TuskLang</a></p>
                </div>
            </div>
        </footer>
        '''
        return render_template_string(template, stats_data=stats_data, activity_data=activity_data)
    
    @staticmethod
    def render_navigation_sidebar(nav_items: List[Dict] = None, title: str = "Navigation") -> str:
        """Sidebar navigation component"""
        template = '''
        <aside class="sidebar-nav">
            <div class="sidebar-header">
                <h3>{{ title }}</h3>
            </div>
            <nav class="sidebar-menu">
                {% for item in nav_items %}
                    <a href="{{ item.url }}" class="sidebar-item {{ 'active' if item.active else '' }}">
                        <span class="item-icon">{{ item.icon }}</span>
                        <span class="item-text">{{ item.text }}</span>
                        {% if item.badge %}
                            <span class="item-badge">{{ item.badge }}</span>
                        {% endif %}
                    </a>
                {% endfor %}
            </nav>
        </aside>
        '''
        return render_template_string(template, nav_items=nav_items or [], title=title)
    
    @staticmethod
    def render_dashboard_widget(widget_data: Dict) -> str:
        """Dashboard widget component"""
        template = '''
        <div class="dashboard-widget widget-{{ widget_data.type }}">
            <div class="widget-header">
                <h3>{{ widget_data.title }}</h3>
                {% if widget_data.icon %}
                    <span class="widget-icon">{{ widget_data.icon }}</span>
                {% endif %}
            </div>
            <div class="widget-content">
                {% if widget_data.type == 'stats' %}
                    <div class="stats-grid">
                        {% for stat in widget_data.stats %}
                            <div class="stat-item">
                                <span class="stat-number">{{ stat.value }}</span>
                                <span class="stat-label">{{ stat.label }}</span>
                            </div>
                        {% endfor %}
                    </div>
                {% elif widget_data.type == 'chart' %}
                    <div class="chart-container">
                        <canvas id="{{ widget_data.chart_id }}"></canvas>
                    </div>
                {% elif widget_data.type == 'list' %}
                    <div class="list-container">
                        {% for item in widget_data.items %}
                            <div class="list-item">
                                <span class="item-icon">{{ item.icon }}</span>
                                <span class="item-text">{{ item.text }}</span>
                                <span class="item-time">{{ item.time }}</span>
                            </div>
                        {% endfor %}
                    </div>
                {% endif %}
            </div>
        </div>
        '''
        return render_template_string(template, widget_data=widget_data)
    
    @staticmethod
    def render_data_table(table_data: Dict) -> str:
        """Data table component with TuskLang integration"""
        template = '''
        <div class="data-table-container">
            <div class="table-header">
                <h3>{{ table_data.title }}</h3>
                {% if table_data.actions %}
                    <div class="table-actions">
                        {% for action in table_data.actions %}
                            <button class="btn btn-{{ action.type }}" onclick="{{ action.onclick }}">
                                {{ action.icon }} {{ action.text }}
                            </button>
                        {% endfor %}
                    </div>
                {% endif %}
            </div>
            
            <div class="table-wrapper">
                <table class="data-table">
                    <thead>
                        <tr>
                            {% for column in table_data.columns %}
                                <th>{{ column.title }}</th>
                            {% endfor %}
                            {% if table_data.actions %}
                                <th>Actions</th>
                            {% endif %}
                        </tr>
                    </thead>
                    <tbody>
                        {% for row in table_data.rows %}
                            <tr>
                                {% for column in table_data.columns %}
                                    <td>
                                        {% if column.type == 'image' %}
                                            <img src="{{ row[column.key] }}" alt="{{ row[column.key] }}" class="table-image">
                                        {% elif column.type == 'badge' %}
                                            <span class="badge badge-{{ row[column.key].type }}">{{ row[column.key].text }}</span>
                                        {% elif column.type == 'link' %}
                                            <a href="{{ row[column.key].url }}">{{ row[column.key].text }}</a>
                                        {% else %}
                                            {{ row[column.key] }}
                                        {% endif %}
                                    </td>
                                {% endfor %}
                                {% if table_data.row_actions %}
                                    <td class="row-actions">
                                        {% for action in table_data.row_actions %}
                                            <button class="btn btn-sm btn-{{ action.type }}" 
                                                    onclick="{{ action.onclick }}({{ row.id }})">
                                                {{ action.icon }}
                                            </button>
                                        {% endfor %}
                                    </td>
                                {% endif %}
                            </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            
            {% if table_data.pagination %}
                <div class="table-pagination">
                    <div class="pagination-info">
                        Showing {{ table_data.pagination.start }} to {{ table_data.pagination.end }} 
                        of {{ table_data.pagination.total }} entries
                    </div>
                    <div class="pagination-controls">
                        {% if table_data.pagination.has_prev %}
                            <a href="?page={{ table_data.pagination.prev_page }}" class="btn btn-sm">Previous</a>
                        {% endif %}
                        {% for page in table_data.pagination.pages %}
                            <a href="?page={{ page }}" class="btn btn-sm {{ 'active' if page == table_data.pagination.current_page else '' }}">
                                {{ page }}
                            </a>
                        {% endfor %}
                        {% if table_data.pagination.has_next %}
                            <a href="?page={{ table_data.pagination.next_page }}" class="btn btn-sm">Next</a>
                        {% endif %}
                    </div>
                </div>
            {% endif %}
        </div>
        '''
        return render_template_string(template, table_data=table_data)
    
    @staticmethod
    def render_form_component(form_data: Dict) -> str:
        """Form component with validation"""
        template = '''
        <form class="form-component" method="{{ form_data.method }}" action="{{ form_data.action }}">
            {% if form_data.title %}
                <h3>{{ form_data.title }}</h3>
            {% endif %}
            
            {% for field in form_data.fields %}
                <div class="form-group">
                    <label for="{{ field.name }}" class="form-label">
                        {{ field.label }}
                        {% if field.required %}
                            <span class="required">*</span>
                        {% endif %}
                    </label>
                    
                    {% if field.type == 'text' or field.type == 'email' or field.type == 'password' %}
                        <input type="{{ field.type }}" 
                               id="{{ field.name }}" 
                               name="{{ field.name }}" 
                               class="form-control {{ 'error' if field.error else '' }}"
                               value="{{ field.value or '' }}"
                               placeholder="{{ field.placeholder or '' }}"
                               {% if field.required %}required{% endif %}>
                    
                    {% elif field.type == 'textarea' %}
                        <textarea id="{{ field.name }}" 
                                  name="{{ field.name }}" 
                                  class="form-control {{ 'error' if field.error else '' }}"
                                  rows="{{ field.rows or 4 }}"
                                  placeholder="{{ field.placeholder or '' }}"
                                  {% if field.required %}required{% endif %}>{{ field.value or '' }}</textarea>
                    
                    {% elif field.type == 'select' %}
                        <select id="{{ field.name }}" 
                                name="{{ field.name }}" 
                                class="form-control {{ 'error' if field.error else '' }}"
                                {% if field.required %}required{% endif %}>
                            {% for option in field.options %}
                                <option value="{{ option.value }}" 
                                        {{ 'selected' if option.value == field.value else '' }}>
                                    {{ option.label }}
                                </option>
                            {% endfor %}
                        </select>
                    
                    {% elif field.type == 'checkbox' %}
                        <div class="checkbox-group">
                            {% for option in field.options %}
                                <label class="checkbox-item">
                                    <input type="checkbox" 
                                           name="{{ field.name }}" 
                                           value="{{ option.value }}"
                                           {{ 'checked' if option.value in field.value else '' }}>
                                    <span class="checkmark"></span>
                                    {{ option.label }}
                                </label>
                            {% endfor %}
                        </div>
                    
                    {% elif field.type == 'radio' %}
                        <div class="radio-group">
                            {% for option in field.options %}
                                <label class="radio-item">
                                    <input type="radio" 
                                           name="{{ field.name }}" 
                                           value="{{ option.value }}"
                                           {{ 'checked' if option.value == field.value else '' }}>
                                    <span class="radio-mark"></span>
                                    {{ option.label }}
                                </label>
                            {% endfor %}
                        </div>
                    {% endif %}
                    
                    {% if field.error %}
                        <div class="form-error">{{ field.error }}</div>
                    {% endif %}
                    
                    {% if field.help_text %}
                        <div class="form-help">{{ field.help_text }}</div>
                    {% endif %}
                </div>
            {% endfor %}
            
            <div class="form-actions">
                {% for button in form_data.buttons %}
                    <button type="{{ button.type or 'button' }}" 
                            class="btn btn-{{ button.style or 'primary' }}"
                            {% if button.onclick %}onclick="{{ button.onclick }}"{% endif %}>
                        {{ button.icon or '' }} {{ button.text }}
                    </button>
                {% endfor %}
            </div>
        </form>
        '''
        return render_template_string(template, form_data=form_data)
    
    @staticmethod
    def render_alert_component(alert_data: Dict) -> str:
        """Alert component"""
        template = '''
        <div class="alert alert-{{ alert_data.type }} {{ 'dismissible' if alert_data.dismissible else '' }}">
            {% if alert_data.icon %}
                <span class="alert-icon">{{ alert_data.icon }}</span>
            {% endif %}
            <div class="alert-content">
                {% if alert_data.title %}
                    <h4 class="alert-title">{{ alert_data.title }}</h4>
                {% endif %}
                <div class="alert-message">{{ alert_data.message }}</div>
                {% if alert_data.actions %}
                    <div class="alert-actions">
                        {% for action in alert_data.actions %}
                            <button class="btn btn-sm btn-{{ action.type }}" onclick="{{ action.onclick }}">
                                {{ action.text }}
                            </button>
                        {% endfor %}
                    </div>
                {% endif %}
            </div>
            {% if alert_data.dismissible %}
                <button class="alert-close" onclick="this.parentElement.remove()">×</button>
            {% endif %}
        </div>
        '''
        return render_template_string(template, alert_data=alert_data)
    
    @staticmethod
    def render_modal_component(modal_data: Dict) -> str:
        """Modal component"""
        template = '''
        <div class="modal" id="{{ modal_data.id }}">
            <div class="modal-backdrop" onclick="closeModal('{{ modal_data.id }}')"></div>
            <div class="modal-content">
                <div class="modal-header">
                    <h3>{{ modal_data.title }}</h3>
                    <button class="modal-close" onclick="closeModal('{{ modal_data.id }}')">×</button>
                </div>
                <div class="modal-body">
                    {{ modal_data.content | safe }}
                </div>
                {% if modal_data.footer %}
                    <div class="modal-footer">
                        {% for button in modal_data.footer %}
                            <button class="btn btn-{{ button.style or 'secondary' }}" 
                                    onclick="{{ button.onclick }}">
                                {{ button.text }}
                            </button>
                        {% endfor %}
                    </div>
                {% endif %}
            </div>
        </div>
        '''
        return render_template_string(template, modal_data=modal_data)

# Global component instance
theme_components = ThemeComponents()

def get_theme_components() -> ThemeComponents:
    """Get global theme components instance"""
    return theme_components 