"""
Flask-TSK UI Components
Bootstrap-style UI components for Flask applications
"""

from flask import render_template_string
from typing import Dict, List, Optional

class UIComponent:
    """UI component system for Flask-TSK"""
    
    @staticmethod
    def card(title: str = "", content: str = "", footer: str = "", 
            image: str = "", theme: str = "default") -> str:
        """Generate a card component"""
        
        template = '''
        <div class="card card-{{ theme }}">
            {% if image %}
                <div class="card-image">
                    <img src="{{ image }}" alt="{{ title }}">
                </div>
            {% endif %}
            
            <div class="card-body">
                {% if title %}
                    <h3 class="card-title">{{ title }}</h3>
                {% endif %}
                <div class="card-content">
                    {{ content | safe }}
                </div>
            </div>
            
            {% if footer %}
                <div class="card-footer">
                    {{ footer | safe }}
                </div>
            {% endif %}
        </div>
        '''
        
        return render_template_string(template, title=title, content=content, 
                                    footer=footer, image=image, theme=theme)
    
    @staticmethod
    def alert(message: str, type: str = "info", dismissible: bool = True) -> str:
        """Generate an alert component"""
        
        template = '''
        <div class="alert alert-{{ type }} {{ 'alert-dismissible' if dismissible else '' }}">
            <div class="alert-content">
                {{ message | safe }}
            </div>
            {% if dismissible %}
                <button type="button" class="alert-close" onclick="this.parentElement.remove()">
                    <span>&times;</span>
                </button>
            {% endif %}
        </div>
        '''
        
        return render_template_string(template, message=message, type=type, dismissible=dismissible)
    
    @staticmethod
    def modal(id: str, title: str, content: str, footer: str = "") -> str:
        """Generate a modal component"""
        
        template = '''
        <div class="modal" id="{{ id }}">
            <div class="modal-overlay" onclick="closeModal('{{ id }}')"></div>
            <div class="modal-content">
                <div class="modal-header">
                    <h3 class="modal-title">{{ title }}</h3>
                    <button type="button" class="modal-close" onclick="closeModal('{{ id }}')">
                        <span>&times;</span>
                    </button>
                </div>
                
                <div class="modal-body">
                    {{ content | safe }}
                </div>
                
                {% if footer %}
                    <div class="modal-footer">
                        {{ footer | safe }}
                    </div>
                {% endif %}
            </div>
        </div>
        '''
        
        return render_template_string(template, id=id, title=title, content=content, footer=footer)
    
    @staticmethod
    def tabs(tabs: List[Dict], active_tab: str = "") -> str:
        """Generate a tabs component"""
        
        template = '''
        <div class="tabs">
            <div class="tab-nav">
                {% for tab in tabs %}
                    <button class="tab-button {{ 'active' if tab.id == active_tab else '' }}"
                            onclick="switchTab('{{ tab.id }}')">
                        {% if tab.icon %}<span class="tab-icon">{{ tab.icon }}</span>{% endif %}
                        <span class="tab-title">{{ tab.title }}</span>
                    </button>
                {% endfor %}
            </div>
            
            <div class="tab-content">
                {% for tab in tabs %}
                    <div class="tab-panel {{ 'active' if tab.id == active_tab else '' }}" 
                         id="tab-{{ tab.id }}">
                        {{ tab.content | safe }}
                    </div>
                {% endfor %}
            </div>
        </div>
        '''
        
        return render_template_string(template, tabs=tabs, active_tab=active_tab)
    
    @staticmethod
    def accordion(items: List[Dict]) -> str:
        """Generate an accordion component"""
        
        template = '''
        <div class="accordion">
            {% for item in items %}
                <div class="accordion-item">
                    <button class="accordion-header" onclick="toggleAccordion(this)">
                        <span class="accordion-title">{{ item.title }}</span>
                        <span class="accordion-icon">▼</span>
                    </button>
                    <div class="accordion-content">
                        <div class="accordion-body">
                            {{ item.content | safe }}
                        </div>
                    </div>
                </div>
            {% endfor %}
        </div>
        '''
        
        return render_template_string(template, items=items)
    
    @staticmethod
    def progress_bar(progress: int, label: str = "", theme: str = "default") -> str:
        """Generate a progress bar component"""
        
        template = '''
        <div class="progress">
            {% if label %}
                <div class="progress-label">{{ label }}</div>
            {% endif %}
            <div class="progress-bar progress-{{ theme }}">
                <div class="progress-fill" style="width: {{ progress }}%"></div>
            </div>
            <div class="progress-text">{{ progress }}%</div>
        </div>
        '''
        
        return render_template_string(template, progress=progress, label=label, theme=theme)
    
    @staticmethod
    def badge(text: str, theme: str = "default") -> str:
        """Generate a badge component"""
        
        template = '''
        <span class="badge badge-{{ theme }}">{{ text }}</span>
        '''
        
        return render_template_string(template, text=text, theme=theme)
    
    @staticmethod
    def tooltip(text: str, content: str, position: str = "top") -> str:
        """Generate a tooltip component"""
        
        template = '''
        <span class="tooltip" data-tooltip="{{ content }}" data-position="{{ position }}">
            {{ text }}
        </span>
        '''
        
        return render_template_string(template, text=text, content=content, position=position)
    
    @staticmethod
    def spinner(size: str = "medium", theme: str = "default") -> str:
        """Generate a loading spinner"""
        
        template = '''
        <div class="spinner spinner-{{ size }} spinner-{{ theme }}">
            <div class="spinner-circle"></div>
        </div>
        '''
        
        return render_template_string(template, size=size, theme=theme) 