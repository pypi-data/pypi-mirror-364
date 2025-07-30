"""
Flask-TSK Examples Package

This package contains comprehensive examples showcasing Flask-TSK capabilities,
particularly the Herd authentication system and various application templates.

Examples included:
- basic_auth: Simple authentication example
- blog_system: Blog with user authentication
- ecommerce: E-commerce with user accounts
- dashboard: Admin dashboard with role-based access
- api_service: REST API with authentication
- social_network: Social features with user profiles
- portfolio: Portfolio website with admin panel
- saas_app: SaaS application template
"""

__version__ = "1.0.0"
__author__ = "Flask-TSK Team"

from .basic_auth import BasicAuthExample
from .blog_system import BlogSystemExample
from .ecommerce import EcommerceExample
from .dashboard import DashboardExample
from .api_service import APIServiceExample
from .social_network import SocialNetworkExample
from .portfolio import PortfolioExample
from .saas_app import SaaSAppExample

__all__ = [
    'BasicAuthExample',
    'BlogSystemExample', 
    'EcommerceExample',
    'DashboardExample',
    'APIServiceExample',
    'SocialNetworkExample',
    'PortfolioExample',
    'SaaSAppExample'
] 