"""
Flask-TSK Forms Components
Bootstrap-style form components for Flask applications
"""

from flask import render_template_string
from typing import Dict, List, Optional

class FormComponent:
    """Form component system for Flask-TSK"""
    
    @staticmethod
    def input_field(name: str, label: str = "", type: str = "text", value: str = "", 
                   placeholder: str = "", required: bool = False, error: str = "") -> str:
        """Generate an input field"""
        
        template = '''
        <div class="form-group {{ 'has-error' if error else '' }}">
            {% if label %}
                <label for="{{ name }}" class="form-label">{{ label }}</label>
            {% endif %}
            <input type="{{ type }}" 
                   id="{{ name }}" 
                   name="{{ name }}" 
                   value="{{ value }}" 
                   placeholder="{{ placeholder }}"
                   class="form-input {{ 'is-invalid' if error else '' }}"
                   {{ 'required' if required else '' }}>
            {% if error %}
                <div class="form-error">{{ error }}</div>
            {% endif %}
        </div>
        '''
        
        return render_template_string(template, name=name, label=label, type=type, 
                                    value=value, placeholder=placeholder, required=required, error=error)
    
    @staticmethod
    def textarea(name: str, label: str = "", value: str = "", placeholder: str = "", 
                rows: int = 4, required: bool = False, error: str = "") -> str:
        """Generate a textarea field"""
        
        template = '''
        <div class="form-group {{ 'has-error' if error else '' }}">
            {% if label %}
                <label for="{{ name }}" class="form-label">{{ label }}</label>
            {% endif %}
            <textarea id="{{ name }}" 
                      name="{{ name }}" 
                      rows="{{ rows }}"
                      placeholder="{{ placeholder }}"
                      class="form-textarea {{ 'is-invalid' if error else '' }}"
                      {{ 'required' if required else '' }}>{{ value }}</textarea>
            {% if error %}
                <div class="form-error">{{ error }}</div>
            {% endif %}
        </div>
        '''
        
        return render_template_string(template, name=name, label=label, value=value, 
                                    placeholder=placeholder, rows=rows, required=required, error=error)
    
    @staticmethod
    def select(name: str, label: str = "", options: List[Dict] = None, 
              selected: str = "", required: bool = False, error: str = "") -> str:
        """Generate a select dropdown"""
        
        template = '''
        <div class="form-group {{ 'has-error' if error else '' }}">
            {% if label %}
                <label for="{{ name }}" class="form-label">{{ label }}</label>
            {% endif %}
            <select id="{{ name }}" 
                    name="{{ name }}" 
                    class="form-select {{ 'is-invalid' if error else '' }}"
                    {{ 'required' if required else '' }}>
                {% for option in options %}
                    <option value="{{ option.value }}" {{ 'selected' if option.value == selected else '' }}>
                        {{ option.text }}
                    </option>
                {% endfor %}
            </select>
            {% if error %}
                <div class="form-error">{{ error }}</div>
            {% endif %}
        </div>
        '''
        
        return render_template_string(template, name=name, label=label, options=options or [], 
                                    selected=selected, required=required, error=error)
    
    @staticmethod
    def checkbox(name: str, label: str = "", checked: bool = False, value: str = "1") -> str:
        """Generate a checkbox field"""
        
        template = '''
        <div class="form-group">
            <label class="checkbox-label">
                <input type="checkbox" 
                       name="{{ name }}" 
                       value="{{ value }}"
                       class="form-checkbox"
                       {{ 'checked' if checked else '' }}>
                <span class="checkmark"></span>
                {{ label }}
            </label>
        </div>
        '''
        
        return render_template_string(template, name=name, label=label, checked=checked, value=value)
    
    @staticmethod
    def radio_group(name: str, label: str = "", options: List[Dict] = None, 
                   selected: str = "") -> str:
        """Generate a radio button group"""
        
        template = '''
        <div class="form-group">
            {% if label %}
                <label class="form-label">{{ label }}</label>
            {% endif %}
            <div class="radio-group">
                {% for option in options %}
                    <label class="radio-label">
                        <input type="radio" 
                               name="{{ name }}" 
                               value="{{ option.value }}"
                               class="form-radio"
                               {{ 'checked' if option.value == selected else '' }}>
                        <span class="radio-mark"></span>
                        {{ option.text }}
                    </label>
                {% endfor %}
            </div>
        </div>
        '''
        
        return render_template_string(template, name=name, label=label, options=options or [], selected=selected)
    
    @staticmethod
    def button(text: str, type: str = "button", style: str = "primary", 
              size: str = "medium", disabled: bool = False) -> str:
        """Generate a button"""
        
        template = '''
        <button type="{{ type }}" 
                class="btn btn-{{ style }} btn-{{ size }}"
                {{ 'disabled' if disabled else '' }}>
            {{ text }}
        </button>
        '''
        
        return render_template_string(template, text=text, type=type, style=style, 
                                    size=size, disabled=disabled)
    
    @staticmethod
    def form(method: str = "POST", action: str = "", enctype: str = "", 
            fields: List[str] = None, submit_text: str = "Submit") -> str:
        """Generate a complete form"""
        
        template = '''
        <form method="{{ method }}" 
              action="{{ action }}"
              {% if enctype %}enctype="{{ enctype }}"{% endif %}
              class="form">
            {% for field in fields %}
                {{ field | safe }}
            {% endfor %}
            
            <div class="form-actions">
                {{ submit_button | safe }}
            </div>
        </form>
        '''
        
        submit_button = FormComponent.button(submit_text, type="submit")
        
        return render_template_string(template, method=method, action=action, 
                                    enctype=enctype, fields=fields or [], submit_button=submit_button) 