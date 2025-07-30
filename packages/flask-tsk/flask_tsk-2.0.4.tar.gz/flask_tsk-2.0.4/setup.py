#!/usr/bin/env python3
"""
Setup script for Flask-TSK
Revolutionary Flask Extension for TuskLang Integration
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Flask-TSK - Revolutionary Flask Extension for TuskLang Integration"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name='flask-tsk',
    version='2.0.4',
    description='Revolutionary Flask Extension for TuskLang Integration - Up to 59x Faster Template Rendering (Verified)',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    author='Grim Development Team',
    author_email='grim@example.com',
    url='https://github.com/grim-project/flask-tsk',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask>=2.0.0',
        'tusktsk>=2.0.4',
        # Performance optimizations (59x faster rendering)
        'orjson>=3.0.0',           # Ultra-fast JSON serialization
        'ujson>=5.0.0',            # Fast JSON parsing  
        'msgpack>=1.0.0',          # Binary data serialization
        # Multi-database support
        'psycopg2-binary>=2.9.0',  # PostgreSQL adapter
        'pymongo>=4.0.0',          # MongoDB driver
        'redis>=5.0.0',            # Redis client
        # Modern async framework support
        'fastapi>=0.104.1',        # High-performance web framework
        'uvicorn[standard]>=0.24.0', # ASGI server
        'pydantic>=2.5.0',         # Data validation
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'pytest-flask>=1.2.0',
            'black>=22.0.0',
            'flake8>=4.0.0',
            'mypy>=0.950',
        ],
        'minimal': [
            'Flask>=2.0.0',
            'tusktsk>=2.0.4',
        ],
    },
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Systems Administration',
        'Topic :: Text Processing :: Markup :: HTML',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
    keywords='flask tusk tusktsk configuration management performance template-engine turbo verified-benchmarks',
    project_urls={
        'Bug Reports': 'https://github.com/grim-project/flask-tsk/issues',
        'Source': 'https://github.com/grim-project/flask-tsk',
        'Documentation': 'https://flask-tsk.readthedocs.io/',
        'Performance Guide': 'https://github.com/grim-project/flask-tsk/blob/main/PERFORMANCE_REVOLUTION.md',
    },
    entry_points={
        'console_scripts': [
            'flask-tsk=tsk_flask.cli:main',
        ],
    },
) 