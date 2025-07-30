#!/usr/bin/env python3
"""
Flask-TSK Component System Example
Demonstrates how to use Flask-TSK as the Bootstrap for Flask applications
"""

from flask import Flask, render_template, request, jsonify
from tsk_flask import FlaskTSK
from tsk_flask.components.navigation import NavigationComponent
from tsk_flask.components.forms import FormComponent
from tsk_flask.components.ui import UIComponent

app = Flask(__name__)
tsk = FlaskTSK(app)

# Setup project structure (creates tsk/ folder with all components)
tsk.setup_project_structure()

@app.route('/')
def index():
    """Home page with navigation and hero section"""
    
    # Navigation items
    nav_items = [
        {'url': '/', 'text': 'Home', 'active': True, 'icon': '🏠'},
        {'url': '/components', 'text': 'Components', 'active': False, 'icon': '🧩'},
        {'url': '/forms', 'text': 'Forms', 'active': False, 'icon': '📝'},
        {'url': '/ui', 'text': 'UI Elements', 'active': False, 'icon': '🎨'},
        {'url': '/about', 'text': 'About', 'active': False, 'icon': 'ℹ️'}
    ]
    
    # Generate navigation
    navigation = NavigationComponent.navbar(nav_items, brand="Flask-TSK Demo")
    
    # Hero section
    hero_content = UIComponent.card(
        title="🚀 Welcome to Flask-TSK",
        content="""
        <p>Flask-TSK is the Bootstrap for the Flask world! Create beautiful, 
        responsive web applications with our comprehensive component system.</p>
        
        <div class="hero-features">
            <div class="feature">
                <h4>⚡ Performance</h4>
                <p>Up to 59x faster template rendering</p>
            </div>
            <div class="feature">
                <h4>🧩 Components</h4>
                <p>50+ ready-to-use components</p>
            </div>
            <div class="feature">
                <h4>🎨 Themes</h4>
                <p>Multiple themes and customization</p>
            </div>
        </div>
        """,
        theme="hero"
    )
    
    return render_template('index.html', 
                         navigation=navigation,
                         hero=hero_content,
                         title="Flask-TSK Demo")

@app.route('/components')
def components():
    """Components showcase page"""
    
    # Navigation
    nav_items = [
        {'url': '/', 'text': 'Home', 'active': False, 'icon': '🏠'},
        {'url': '/components', 'text': 'Components', 'active': True, 'icon': '🧩'},
        {'url': '/forms', 'text': 'Forms', 'active': False, 'icon': '📝'},
        {'url': '/ui', 'text': 'UI Elements', 'active': False, 'icon': '🎨'},
        {'url': '/about', 'text': 'About', 'active': False, 'icon': 'ℹ️'}
    ]
    
    navigation = NavigationComponent.navbar(nav_items, brand="Flask-TSK Demo")
    
    # Component examples
    components = {
        'navigation': {
            'title': 'Navigation Components',
            'examples': [
                {
                    'name': 'Navbar',
                    'code': NavigationComponent.navbar(nav_items, theme="modern")
                },
                {
                    'name': 'Breadcrumb',
                    'code': NavigationComponent.breadcrumb([
                        {'url': '/', 'text': 'Home'},
                        {'url': '/components', 'text': 'Components', 'active': True}
                    ])
                },
                {
                    'name': 'Sidebar',
                    'code': NavigationComponent.sidebar(nav_items)
                }
            ]
        },
        'ui': {
            'title': 'UI Components',
            'examples': [
                {
                    'name': 'Cards',
                    'code': UIComponent.card(
                        title="Sample Card",
                        content="This is a sample card component with some content.",
                        footer="Card footer"
                    )
                },
                {
                    'name': 'Alerts',
                    'code': UIComponent.alert("This is a success alert!", type="success")
                },
                {
                    'name': 'Progress Bar',
                    'code': UIComponent.progress_bar(75, "Loading...", theme="success")
                }
            ]
        }
    }
    
    return render_template('components.html',
                         navigation=navigation,
                         components=components,
                         title="Components - Flask-TSK Demo")

@app.route('/forms')
def forms():
    """Forms showcase page"""
    
    # Navigation
    nav_items = [
        {'url': '/', 'text': 'Home', 'active': False, 'icon': '🏠'},
        {'url': '/components', 'text': 'Components', 'active': False, 'icon': '🧩'},
        {'url': '/forms', 'text': 'Forms', 'active': True, 'icon': '📝'},
        {'url': '/ui', 'text': 'UI Elements', 'active': False, 'icon': '🎨'},
        {'url': '/about', 'text': 'About', 'active': False, 'icon': 'ℹ️'}
    ]
    
    navigation = NavigationComponent.navbar(nav_items, brand="Flask-TSK Demo")
    
    # Form examples
    form_examples = {
        'basic': {
            'title': 'Basic Form',
            'form': FormComponent.form(
                method="POST",
                action="/submit",
                fields=[
                    FormComponent.input_field("name", "Name", required=True),
                    FormComponent.input_field("email", "Email", type="email", required=True),
                    FormComponent.textarea("message", "Message", rows=4),
                    FormComponent.button("Submit", type="submit")
                ]
            )
        },
        'advanced': {
            'title': 'Advanced Form',
            'form': FormComponent.form(
                method="POST",
                action="/submit-advanced",
                fields=[
                    FormComponent.input_field("username", "Username", required=True),
                    FormComponent.input_field("password", "Password", type="password", required=True),
                    FormComponent.select("country", "Country", [
                        {'value': 'us', 'text': 'United States'},
                        {'value': 'ca', 'text': 'Canada'},
                        {'value': 'uk', 'text': 'United Kingdom'}
                    ]),
                    FormComponent.checkbox("newsletter", "Subscribe to newsletter"),
                    FormComponent.radio_group("gender", "Gender", [
                        {'value': 'male', 'text': 'Male'},
                        {'value': 'female', 'text': 'Female'},
                        {'value': 'other', 'text': 'Other'}
                    ]),
                    FormComponent.button("Submit", type="submit", style="success")
                ]
            )
        }
    }
    
    return render_template('forms.html',
                         navigation=navigation,
                         form_examples=form_examples,
                         title="Forms - Flask-TSK Demo")

@app.route('/ui')
def ui_elements():
    """UI elements showcase page"""
    
    # Navigation
    nav_items = [
        {'url': '/', 'text': 'Home', 'active': False, 'icon': '🏠'},
        {'url': '/components', 'text': 'Components', 'active': False, 'icon': '🧩'},
        {'url': '/forms', 'text': 'Forms', 'active': False, 'icon': '📝'},
        {'url': '/ui', 'text': 'UI Elements', 'active': True, 'icon': '🎨'},
        {'url': '/about', 'text': 'About', 'active': False, 'icon': 'ℹ️'}
    ]
    
    navigation = NavigationComponent.navbar(nav_items, brand="Flask-TSK Demo")
    
    # UI examples
    ui_examples = {
        'cards': {
            'title': 'Card Variations',
            'examples': [
                UIComponent.card("Default Card", "This is a default card."),
                UIComponent.card("Success Card", "This is a success card.", theme="success"),
                UIComponent.card("Warning Card", "This is a warning card.", theme="warning"),
                UIComponent.card("Error Card", "This is an error card.", theme="error")
            ]
        },
        'alerts': {
            'title': 'Alert Types',
            'examples': [
                UIComponent.alert("Info alert", type="info"),
                UIComponent.alert("Success alert", type="success"),
                UIComponent.alert("Warning alert", type="warning"),
                UIComponent.alert("Error alert", type="error")
            ]
        },
        'progress': {
            'title': 'Progress Bars',
            'examples': [
                UIComponent.progress_bar(25, "Basic", theme="default"),
                UIComponent.progress_bar(50, "Success", theme="success"),
                UIComponent.progress_bar(75, "Warning", theme="warning"),
                UIComponent.progress_bar(90, "Error", theme="error")
            ]
        },
        'badges': {
            'title': 'Badges',
            'examples': [
                UIComponent.badge("Default", theme="default"),
                UIComponent.badge("Success", theme="success"),
                UIComponent.badge("Warning", theme="warning"),
                UIComponent.badge("Error", theme="error")
            ]
        }
    }
    
    return render_template('ui.html',
                         navigation=navigation,
                         ui_examples=ui_examples,
                         title="UI Elements - Flask-TSK Demo")

@app.route('/about')
def about():
    """About page"""
    
    # Navigation
    nav_items = [
        {'url': '/', 'text': 'Home', 'active': False, 'icon': '🏠'},
        {'url': '/components', 'text': 'Components', 'active': False, 'icon': '🧩'},
        {'url': '/forms', 'text': 'Forms', 'active': False, 'icon': '📝'},
        {'url': '/ui', 'text': 'UI Elements', 'active': False, 'icon': '🎨'},
        {'url': '/about', 'text': 'About', 'active': True, 'icon': 'ℹ️'}
    ]
    
    navigation = NavigationComponent.navbar(nav_items, brand="Flask-TSK Demo")
    
    # Breadcrumb
    breadcrumb = NavigationComponent.breadcrumb([
        {'url': '/', 'text': 'Home'},
        {'url': '/about', 'text': 'About', 'active': True}
    ])
    
    # About content
    about_content = UIComponent.card(
        title="About Flask-TSK",
        content="""
        <p>Flask-TSK is a revolutionary Flask extension that provides:</p>
        <ul>
            <li>⚡ Up to 59x faster template rendering</li>
            <li>🧩 50+ ready-to-use components</li>
            <li>🎨 Multiple themes and customization</li>
            <li>📱 Responsive design out of the box</li>
            <li>🔧 Built-in optimization tools</li>
        </ul>
        <p>It's the Bootstrap for the Flask world!</p>
        """,
        theme="about"
    )
    
    return render_template('about.html',
                         navigation=navigation,
                         breadcrumb=breadcrumb,
                         about_content=about_content,
                         title="About - Flask-TSK Demo")

@app.route('/submit', methods=['POST'])
def submit_form():
    """Handle form submission"""
    data = request.form
    return jsonify({
        'success': True,
        'message': 'Form submitted successfully!',
        'data': dict(data)
    })

if __name__ == '__main__':
    app.run(debug=True) 