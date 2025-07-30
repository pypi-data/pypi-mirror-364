"""
Flask-TSK Elephant Showcase
==========================
"Showcasing the power of the elephant herd"
Interactive demonstration of all elephant capabilities
Strong. Secure. Scalable. 🐘
"""

from flask import Flask, render_template_string, request, jsonify, current_app
from typing import Dict, List, Optional, Any, Union
import time
from datetime import datetime
import json

from .elephants import (
    get_elephant_herd, showcase_elephant_capabilities, run_elephant_demo,
    get_babar_cms, get_dumbo_http, get_elmer_theme, get_happy_image,
    get_heffalump_search, get_horton_jobs, get_jumbo_upload,
    get_kaavan_monitor, get_koshik_audio, get_satao_security,
    get_stampy_packages, get_tantor_database
)

class ElephantShowcase:
    """Interactive showcase for all elephant capabilities"""
    
    def __init__(self, app: Flask = None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize showcase with Flask app"""
        self.app = app
        
        # Register showcase routes
        app.add_url_rule('/showcase', 'showcase', self.showcase_page, methods=['GET'])
        app.add_url_rule('/showcase/demo', 'showcase_demo', self.run_demo, methods=['POST'])
        app.add_url_rule('/showcase/api/status', 'showcase_status', self.get_status, methods=['GET'])
        app.add_url_rule('/showcase/api/capabilities', 'showcase_capabilities', self.get_capabilities, methods=['GET'])
        
        app.logger.info("🐘 Elephant showcase initialized!")
    
    def showcase_page(self):
        """Main showcase page"""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>🐘 Flask-TSK Elephant Showcase</title>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    color: #333;
                }
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }
                .header {
                    text-align: center;
                    color: white;
                    margin-bottom: 40px;
                }
                .header h1 {
                    font-size: 3rem;
                    margin-bottom: 10px;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                }
                .header p {
                    font-size: 1.2rem;
                    opacity: 0.9;
                }
                .elephant-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                    gap: 20px;
                    margin-bottom: 40px;
                }
                .elephant-card {
                    background: white;
                    border-radius: 15px;
                    padding: 25px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                    transition: transform 0.3s ease, box-shadow 0.3s ease;
                }
                .elephant-card:hover {
                    transform: translateY(-5px);
                    box-shadow: 0 15px 40px rgba(0,0,0,0.15);
                }
                .elephant-header {
                    display: flex;
                    align-items: center;
                    margin-bottom: 15px;
                }
                .elephant-icon {
                    font-size: 2.5rem;
                    margin-right: 15px;
                }
                .elephant-title h3 {
                    font-size: 1.3rem;
                    color: #2c3e50;
                    margin-bottom: 5px;
                }
                .elephant-title p {
                    color: #7f8c8d;
                    font-size: 0.9rem;
                }
                .elephant-description {
                    color: #555;
                    line-height: 1.6;
                    margin-bottom: 20px;
                }
                .elephant-actions {
                    display: flex;
                    gap: 10px;
                    flex-wrap: wrap;
                }
                .btn {
                    padding: 8px 16px;
                    border: none;
                    border-radius: 8px;
                    cursor: pointer;
                    font-size: 0.9rem;
                    transition: all 0.3s ease;
                    text-decoration: none;
                    display: inline-block;
                }
                .btn-primary {
                    background: #3498db;
                    color: white;
                }
                .btn-primary:hover {
                    background: #2980b9;
                }
                .btn-success {
                    background: #27ae60;
                    color: white;
                }
                .btn-success:hover {
                    background: #229954;
                }
                .btn-warning {
                    background: #f39c12;
                    color: white;
                }
                .btn-warning:hover {
                    background: #e67e22;
                }
                .status-bar {
                    background: white;
                    border-radius: 15px;
                    padding: 20px;
                    margin-bottom: 30px;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                }
                .status-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                }
                .status-item {
                    text-align: center;
                    padding: 15px;
                    background: #f8f9fa;
                    border-radius: 10px;
                }
                .status-number {
                    font-size: 2rem;
                    font-weight: bold;
                    color: #2c3e50;
                }
                .status-label {
                    color: #7f8c8d;
                    font-size: 0.9rem;
                }
                .demo-section {
                    background: white;
                    border-radius: 15px;
                    padding: 25px;
                    margin-bottom: 30px;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                }
                .demo-section h2 {
                    color: #2c3e50;
                    margin-bottom: 20px;
                    font-size: 1.5rem;
                }
                .demo-buttons {
                    display: flex;
                    gap: 15px;
                    flex-wrap: wrap;
                }
                .demo-result {
                    margin-top: 20px;
                    padding: 15px;
                    background: #f8f9fa;
                    border-radius: 10px;
                    border-left: 4px solid #3498db;
                    display: none;
                }
                .loading {
                    text-align: center;
                    padding: 20px;
                    color: #7f8c8d;
                }
                .error {
                    background: #e74c3c;
                    color: white;
                    padding: 10px;
                    border-radius: 5px;
                    margin-top: 10px;
                }
                .success {
                    background: #27ae60;
                    color: white;
                    padding: 10px;
                    border-radius: 5px;
                    margin-top: 10px;
                }
                @media (max-width: 768px) {
                    .header h1 { font-size: 2rem; }
                    .elephant-grid { grid-template-columns: 1fr; }
                    .demo-buttons { flex-direction: column; }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🐘 Elephant Herd Showcase</h1>
                    <p>Experience the power of Flask-TSK's complete elephant ecosystem</p>
                </div>
                
                <div class="status-bar">
                    <h2>Herd Status</h2>
                    <div class="status-grid" id="statusGrid">
                        <div class="status-item">
                            <div class="status-number" id="totalElephants">-</div>
                            <div class="status-label">Total Elephants</div>
                        </div>
                        <div class="status-item">
                            <div class="status-number" id="availableElephants">-</div>
                            <div class="status-label">Available</div>
                        </div>
                        <div class="status-item">
                            <div class="status-number" id="healthyElephants">-</div>
                            <div class="status-label">Healthy</div>
                        </div>
                        <div class="status-item">
                            <div class="status-number" id="totalLines">10,026</div>
                            <div class="status-label">Lines of Code</div>
                        </div>
                    </div>
                </div>
                
                <div class="demo-section">
                    <h2>Quick Demos</h2>
                    <div class="demo-buttons">
                        <button class="btn btn-primary" onclick="runDemo('all')">Run All Demos</button>
                        <button class="btn btn-success" onclick="runDemo('content')">Content Demo</button>
                        <button class="btn btn-warning" onclick="runDemo('network')">Network Demo</button>
                        <button class="btn btn-primary" onclick="runDemo('themes')">Theme Demo</button>
                        <button class="btn btn-success" onclick="runDemo('images')">Image Demo</button>
                        <button class="btn btn-warning" onclick="runDemo('search')">Search Demo</button>
                    </div>
                    <div class="demo-result" id="demoResult"></div>
                </div>
                
                <div class="elephant-grid">
                    <div class="elephant-card">
                        <div class="elephant-header">
                            <div class="elephant-icon">👑</div>
                            <div class="elephant-title">
                                <h3>Babar - The Royal CMS</h3>
                                <p>Content Management System</p>
                            </div>
                        </div>
                        <div class="elephant-description">
                            King Babar brings civilization and order to content management. Create, edit, and publish content with royal elegance.
                        </div>
                        <div class="elephant-actions">
                            <a href="/api/elephants/babar/content" class="btn btn-primary">Create Content</a>
                            <a href="/api/elephants/babar/library" class="btn btn-success">View Library</a>
                        </div>
                    </div>
                    
                    <div class="elephant-card">
                        <div class="elephant-header">
                            <div class="elephant-icon">🦅</div>
                            <div class="elephant-title">
                                <h3>Dumbo - The HTTP Flyer</h3>
                                <p>Network Operations</p>
                            </div>
                        </div>
                        <div class="elephant-description">
                            Dumbo makes web requests soar with grace and speed. Handle HTTP operations with magical efficiency.
                        </div>
                        <div class="elephant-actions">
                            <a href="/api/elephants/dumbo/request" class="btn btn-primary">Make Request</a>
                            <a href="/api/elephants/dumbo/ping" class="btn btn-success">Ping URL</a>
                        </div>
                    </div>
                    
                    <div class="elephant-card">
                        <div class="elephant-header">
                            <div class="elephant-icon">🎨</div>
                            <div class="elephant-title">
                                <h3>Elmer - The Theme Artist</h3>
                                <p>Theme Generation</p>
                            </div>
                        </div>
                        <div class="elephant-description">
                            Elmer's patchwork creativity brings beautiful themes to life. Generate harmonious color schemes and cultural themes.
                        </div>
                        <div class="elephant-actions">
                            <a href="/api/elephants/elmer/theme" class="btn btn-primary">Generate Theme</a>
                            <a href="/api/elephants/elmer/cultural/japanese" class="btn btn-success">Cultural Theme</a>
                        </div>
                    </div>
                    
                    <div class="elephant-card">
                        <div class="elephant-header">
                            <div class="elephant-icon">😊</div>
                            <div class="elephant-title">
                                <h3>Happy - The Image Artist</h3>
                                <p>Image Processing</p>
                            </div>
                        </div>
                        <div class="elephant-description">
                            Happy brings joy to image processing with emotional filters and artistic transformations.
                        </div>
                        <div class="elephant-actions">
                            <a href="/api/elephants/happy/filter" class="btn btn-primary">Apply Filter</a>
                            <a href="/api/elephants/happy/emotional" class="btn btn-success">Emotional Filter</a>
                        </div>
                    </div>
                    
                    <div class="elephant-card">
                        <div class="elephant-header">
                            <div class="elephant-icon">🔍</div>
                            <div class="elephant-title">
                                <h3>Heffalump - The Fuzzy Finder</h3>
                                <p>Search & Discovery</p>
                            </div>
                        </div>
                        <div class="elephant-description">
                            Heffalump's fuzzy search finds what you're looking for, even when you're not sure what it's called.
                        </div>
                        <div class="elephant-actions">
                            <a href="/api/elephants/heffalump/search" class="btn btn-primary">Search</a>
                            <a href="/api/elephants/heffalump/suggestions" class="btn btn-success">Suggestions</a>
                        </div>
                    </div>
                    
                    <div class="elephant-card">
                        <div class="elephant-header">
                            <div class="elephant-icon">⚙️</div>
                            <div class="elephant-title">
                                <h3>Horton - The Faithful Worker</h3>
                                <p>Job Processing</p>
                            </div>
                        </div>
                        <div class="elephant-description">
                            Horton faithfully processes jobs in the background, ensuring every task gets completed.
                        </div>
                        <div class="elephant-actions">
                            <a href="/api/elephants/horton/job" class="btn btn-primary">Dispatch Job</a>
                            <a href="/api/elephants/horton/stats" class="btn btn-success">View Stats</a>
                        </div>
                    </div>
                    
                    <div class="elephant-card">
                        <div class="elephant-header">
                            <div class="elephant-icon">📁</div>
                            <div class="elephant-title">
                                <h3>Jumbo - The File Handler</h3>
                                <p>File Upload & Processing</p>
                            </div>
                        </div>
                        <div class="elephant-description">
                            Jumbo handles massive file uploads with chunked processing and resume capabilities.
                        </div>
                        <div class="elephant-actions">
                            <a href="/api/elephants/jumbo/upload/start" class="btn btn-primary">Start Upload</a>
                            <a href="/api/elephants/jumbo/upload/status" class="btn btn-success">Check Status</a>
                        </div>
                    </div>
                    
                    <div class="elephant-card">
                        <div class="elephant-header">
                            <div class="elephant-icon">🛡️</div>
                            <div class="elephant-title">
                                <h3>Kaavan - The Guardian</h3>
                                <p>System Monitoring</p>
                            </div>
                        </div>
                        <div class="elephant-description">
                            Kaavan watches over the system, monitoring health and creating backups automatically.
                        </div>
                        <div class="elephant-actions">
                            <a href="/api/elephants/kaavan/watch" class="btn btn-primary">Watch System</a>
                            <a href="/api/elephants/kaavan/backup" class="btn btn-success">Create Backup</a>
                        </div>
                    </div>
                    
                    <div class="elephant-card">
                        <div class="elephant-header">
                            <div class="elephant-icon">🎵</div>
                            <div class="elephant-title">
                                <h3>Koshik - The Voice</h3>
                                <p>Audio & Notifications</p>
                            </div>
                        </div>
                        <div class="elephant-description">
                            Koshik speaks in multiple languages and creates beautiful notification sounds.
                        </div>
                        <div class="elephant-actions">
                            <a href="/api/elephants/koshik/speak" class="btn btn-primary">Speak</a>
                            <a href="/api/elephants/koshik/notify" class="btn btn-success">Notify</a>
                        </div>
                    </div>
                    
                    <div class="elephant-card">
                        <div class="elephant-header">
                            <div class="elephant-icon">🔒</div>
                            <div class="elephant-title">
                                <h3>Satao - The Protector</h3>
                                <p>Security & Protection</p>
                            </div>
                        </div>
                        <div class="elephant-description">
                            Satao protects the system from threats with real-time monitoring and threat detection.
                        </div>
                        <div class="elephant-actions">
                            <a href="/api/elephants/satao/audit" class="btn btn-primary">Security Audit</a>
                            <a href="/api/elephants/satao/threats" class="btn btn-success">Threat Intel</a>
                        </div>
                    </div>
                    
                    <div class="elephant-card">
                        <div class="elephant-header">
                            <div class="elephant-icon">📦</div>
                            <div class="elephant-title">
                                <h3>Stampy - The Package Manager</h3>
                                <p>App Installation</p>
                            </div>
                        </div>
                        <div class="elephant-description">
                            Stampy manages app installations with dependency resolution and configuration.
                        </div>
                        <div class="elephant-actions">
                            <a href="/api/elephants/stampy/catalog" class="btn btn-primary">View Catalog</a>
                            <a href="/api/elephants/stampy/install" class="btn btn-success">Install App</a>
                        </div>
                    </div>
                    
                    <div class="elephant-card">
                        <div class="elephant-header">
                            <div class="elephant-icon">🗄️</div>
                            <div class="elephant-title">
                                <h3>Tantor - The Database</h3>
                                <p>Database Operations</p>
                            </div>
                        </div>
                        <div class="elephant-description">
                            Tantor manages database operations with reliability and performance optimization.
                        </div>
                        <div class="elephant-actions">
                            <a href="/api/elephants/tantor/status" class="btn btn-primary">Database Status</a>
                            <a href="/api/elephants/tantor/stats" class="btn btn-success">View Stats</a>
                        </div>
                    </div>
                </div>
            </div>
            
            <script>
                // Load status on page load
                document.addEventListener('DOMContentLoaded', function() {
                    loadStatus();
                });
                
                async function loadStatus() {
                    try {
                        const response = await fetch('/showcase/api/status');
                        const data = await response.json();
                        
                        if (data.success) {
                            const status = data.data;
                            document.getElementById('totalElephants').textContent = status.total_count;
                            document.getElementById('availableElephants').textContent = status.available_count;
                            document.getElementById('healthyElephants').textContent = status.available_count;
                        }
                    } catch (error) {
                        console.error('Error loading status:', error);
                    }
                }
                
                async function runDemo(demoType) {
                    const resultDiv = document.getElementById('demoResult');
                    resultDiv.style.display = 'block';
                    resultDiv.innerHTML = '<div class="loading">Running demo...</div>';
                    
                    try {
                        const response = await fetch('/showcase/demo', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({ type: demoType })
                        });
                        
                        const data = await response.json();
                        
                        if (data.success) {
                            resultDiv.innerHTML = '<div class="success">Demo completed successfully!</div>';
                        } else {
                            resultDiv.innerHTML = '<div class="error">Demo failed: ' + data.error + '</div>';
                        }
                    } catch (error) {
                        resultDiv.innerHTML = '<div class="error">Demo error: ' + error.message + '</div>';
                    }
                }
            </script>
        </body>
        </html>
        """
        return html
    
    def run_demo(self):
        """Run elephant demonstration"""
        try:
            data = request.get_json() or {}
            demo_type = data.get('type', 'all')
            
            demo_results = run_elephant_demo(demo_type)
            
            return jsonify({
                'success': True,
                'data': demo_results
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    def get_status(self):
        """Get elephant herd status"""
        try:
            herd = get_elephant_herd()
            status = herd.get_herd_status()
            
            return jsonify({
                'success': True,
                'data': status
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    def get_capabilities(self):
        """Get elephant capabilities"""
        try:
            capabilities = showcase_elephant_capabilities()
            
            return jsonify({
                'success': True,
                'data': capabilities
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

# Global showcase instance
_showcase = None

def init_elephant_showcase(app: Flask) -> ElephantShowcase:
    """Initialize elephant showcase with Flask app"""
    global _showcase
    _showcase = ElephantShowcase(app)
    return _showcase

def get_elephant_showcase() -> ElephantShowcase:
    """Get global elephant showcase instance"""
    global _showcase
    return _showcase 