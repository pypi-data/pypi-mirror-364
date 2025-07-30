#!/usr/bin/env python3
"""
TuskLang Performance Benchmark
Demonstrates the speed improvements over Flask's default Jinja2 rendering
"""

import time
import asyncio
import threading
from typing import Dict, Any, List
import statistics
import json

# Import our performance engine
from performance_engine import (
    TurboTemplateEngine, 
    render_turbo_template, 
    render_turbo_template_async,
    get_performance_stats,
    optimize_flask_app
)

# Try to import Flask for comparison
try:
    from flask import Flask, render_template_string
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("Flask not available for comparison")

# Try to import Jinja2 for direct comparison
try:
    from jinja2 import Template
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False
    print("Jinja2 not available for comparison")


class PerformanceBenchmark:
    """Comprehensive performance benchmarking"""
    
    def __init__(self):
        self.results = {}
        self.turbo_engine = TurboTemplateEngine()
        
        # Sample templates for testing
        self.simple_template = """
        <h1>Hello {{ name }}!</h1>
        <p>Welcome to {{ app_name }}</p>
        <p>Current time: {{ current_time }}</p>
        <p>User ID: {{ user_id }}</p>
        """
        
        self.complex_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>{{ page_title }}</title>
            <meta name="description" content="{{ page_description }}">
        </head>
        <body>
            <header>
                <h1>{{ site_name }}</h1>
                <nav>
                    {% for item in navigation %}
                    <a href="{{ item.url }}">{{ item.text }}</a>
                    {% endfor %}
                </nav>
            </header>
            
            <main>
                <section class="hero">
                    <h2>{{ hero_title }}</h2>
                    <p>{{ hero_description }}</p>
                    <button onclick="alert('{{ button_text }}')">{{ button_text }}</button>
                </section>
                
                <section class="content">
                    {% for post in posts %}
                    <article>
                        <h3>{{ post.title }}</h3>
                        <p>{{ post.excerpt }}</p>
                        <small>By {{ post.author }} on {{ post.date }}</small>
                    </article>
                    {% endfor %}
                </section>
                
                <aside>
                    <h3>Recent Comments</h3>
                    {% for comment in comments %}
                    <div class="comment">
                        <strong>{{ comment.author }}</strong>: {{ comment.text }}
                    </div>
                    {% endfor %}
                </aside>
            </main>
            
            <footer>
                <p>&copy; {{ current_year }} {{ site_name }}. All rights reserved.</p>
            </footer>
        </body>
        </html>
        """
        
        self.tsk_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>{{ tsk_config('site', 'title', 'Default Title') }}</title>
        </head>
        <body>
            <h1>{{ tsk_function('utils', 'format_greeting', name) }}</h1>
            <p>Database: {{ tsk_config('database', 'type', 'sqlite') }}</p>
            <p>Environment: {{ tsk_config('app', 'environment', 'development') }}</p>
            <p>Current time: {{ tsk_function('utils', 'format_datetime', current_time) }}</p>
            
            {% for item in items %}
            <div class="item">
                <h3>{{ item.title }}</h3>
                <p>{{ tsk_function('content', 'truncate', item.description, 100) }}</p>
            </div>
            {% endfor %}
        </body>
        </html>
        """
    
    def generate_test_context(self, complexity: str = 'simple') -> Dict[str, Any]:
        """Generate test context data"""
        if complexity == 'simple':
            return {
                'name': 'World',
                'app_name': 'TuskLang Flask',
                'current_time': '2024-01-15 12:00:00',
                'user_id': 12345
            }
        elif complexity == 'complex':
            return {
                'page_title': 'Performance Test Page',
                'page_description': 'Testing template rendering performance',
                'site_name': 'TuskLang Demo',
                'navigation': [
                    {'url': '/', 'text': 'Home'},
                    {'url': '/about', 'text': 'About'},
                    {'url': '/contact', 'text': 'Contact'}
                ],
                'hero_title': 'Welcome to TuskLang',
                'hero_description': 'The fastest template engine for Flask',
                'button_text': 'Get Started',
                'posts': [
                    {
                        'title': 'First Post',
                        'excerpt': 'This is the first post excerpt...',
                        'author': 'John Doe',
                        'date': '2024-01-15'
                    },
                    {
                        'title': 'Second Post',
                        'excerpt': 'This is the second post excerpt...',
                        'author': 'Jane Smith',
                        'date': '2024-01-14'
                    }
                ],
                'comments': [
                    {'author': 'User1', 'text': 'Great post!'},
                    {'author': 'User2', 'text': 'Very informative.'}
                ],
                'current_year': 2024
            }
        else:  # tsk
            return {
                'name': 'Developer',
                'current_time': '2024-01-15 12:00:00',
                'items': [
                    {'title': 'Item 1', 'description': 'This is a very long description that will be truncated by the TuskLang function'},
                    {'title': 'Item 2', 'description': 'Another long description for testing the truncation functionality'},
                    {'title': 'Item 3', 'description': 'Yet another description to test performance with multiple items'}
                ]
            }
    
    def benchmark_turbo_engine(self, template: str, context: Dict[str, Any], iterations: int = 1000) -> Dict[str, Any]:
        """Benchmark TuskLang turbo engine"""
        print(f"🧪 Benchmarking TuskLang Turbo Engine ({iterations} iterations)...")
        
        times = []
        for i in range(iterations):
            start_time = time.time()
            result = self.turbo_engine.render_template(template, context)
            end_time = time.time()
            times.append(end_time - start_time)
        
        stats = {
            'engine': 'TuskLang Turbo',
            'iterations': iterations,
            'total_time': sum(times),
            'avg_time': statistics.mean(times),
            'min_time': min(times),
            'max_time': max(times),
            'median_time': statistics.median(times),
            'renders_per_second': iterations / sum(times),
            'result_length': len(result)
        }
        
        print(f"✅ TuskLang Turbo: {stats['avg_time']*1000:.2f}ms avg, {stats['renders_per_second']:.0f} renders/sec")
        return stats
    
    def benchmark_flask_jinja2(self, template: str, context: Dict[str, Any], iterations: int = 1000) -> Dict[str, Any]:
        """Benchmark Flask's Jinja2 engine"""
        if not FLASK_AVAILABLE:
            return {'error': 'Flask not available'}
        
        print(f"🧪 Benchmarking Flask Jinja2 ({iterations} iterations)...")
        
        app = Flask(__name__)
        times = []
        
        for i in range(iterations):
            start_time = time.time()
            with app.app_context():
                result = render_template_string(template, **context)
            end_time = time.time()
            times.append(end_time - start_time)
        
        stats = {
            'engine': 'Flask Jinja2',
            'iterations': iterations,
            'total_time': sum(times),
            'avg_time': statistics.mean(times),
            'min_time': min(times),
            'max_time': max(times),
            'median_time': statistics.median(times),
            'renders_per_second': iterations / sum(times),
            'result_length': len(result)
        }
        
        print(f"✅ Flask Jinja2: {stats['avg_time']*1000:.2f}ms avg, {stats['renders_per_second']:.0f} renders/sec")
        return stats
    
    def benchmark_pure_jinja2(self, template: str, context: Dict[str, Any], iterations: int = 1000) -> Dict[str, Any]:
        """Benchmark pure Jinja2 engine"""
        if not JINJA2_AVAILABLE:
            return {'error': 'Jinja2 not available'}
        
        print(f"🧪 Benchmarking Pure Jinja2 ({iterations} iterations)...")
        
        jinja_template = Template(template)
        times = []
        
        for i in range(iterations):
            start_time = time.time()
            result = jinja_template.render(**context)
            end_time = time.time()
            times.append(end_time - start_time)
        
        stats = {
            'engine': 'Pure Jinja2',
            'iterations': iterations,
            'total_time': sum(times),
            'avg_time': statistics.mean(times),
            'min_time': min(times),
            'max_time': max(times),
            'median_time': statistics.median(times),
            'renders_per_second': iterations / sum(times),
            'result_length': len(result)
        }
        
        print(f"✅ Pure Jinja2: {stats['avg_time']*1000:.2f}ms avg, {stats['renders_per_second']:.0f} renders/sec")
        return stats
    
    def benchmark_async_rendering(self, template: str, context: Dict[str, Any], iterations: int = 100) -> Dict[str, Any]:
        """Benchmark async rendering"""
        print(f"🧪 Benchmarking Async Rendering ({iterations} iterations)...")
        
        async def async_benchmark():
            times = []
            for i in range(iterations):
                start_time = time.time()
                result = await render_turbo_template_async(template, context)
                end_time = time.time()
                times.append(end_time - start_time)
            return times
        
        times = asyncio.run(async_benchmark())
        
        stats = {
            'engine': 'TuskLang Async',
            'iterations': iterations,
            'total_time': sum(times),
            'avg_time': statistics.mean(times),
            'min_time': min(times),
            'max_time': max(times),
            'median_time': statistics.median(times),
            'renders_per_second': iterations / sum(times),
            'result_length': len(result)
        }
        
        print(f"✅ TuskLang Async: {stats['avg_time']*1000:.2f}ms avg, {stats['renders_per_second']:.0f} renders/sec")
        return stats
    
    def benchmark_batch_rendering(self, template: str, contexts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Benchmark batch rendering"""
        print(f"🧪 Benchmarking Batch Rendering ({len(contexts)} templates)...")
        
        templates = [{'content': template, 'context': ctx} for ctx in contexts]
        
        start_time = time.time()
        results = self.turbo_engine.batch_render(templates)
        end_time = time.time()
        
        total_time = end_time - start_time
        
        stats = {
            'engine': 'TuskLang Batch',
            'iterations': len(contexts),
            'total_time': total_time,
            'avg_time': total_time / len(contexts),
            'renders_per_second': len(contexts) / total_time,
            'result_length': sum(len(r) for r in results)
        }
        
        print(f"✅ TuskLang Batch: {stats['avg_time']*1000:.2f}ms avg, {stats['renders_per_second']:.0f} renders/sec")
        return stats
    
    def run_comprehensive_benchmark(self):
        """Run comprehensive performance benchmark"""
        print("🚀 TuskLang Performance Benchmark")
        print("=" * 50)
        
        # Test simple template
        print("\n📊 Simple Template Benchmark")
        print("-" * 30)
        simple_context = self.generate_test_context('simple')
        
        self.results['simple'] = {
            'turbo': self.benchmark_turbo_engine(self.simple_template, simple_context, 1000),
            'flask': self.benchmark_flask_jinja2(self.simple_template, simple_context, 1000),
            'jinja2': self.benchmark_pure_jinja2(self.simple_template, simple_context, 1000)
        }
        
        # Test complex template
        print("\n📊 Complex Template Benchmark")
        print("-" * 30)
        complex_context = self.generate_test_context('complex')
        
        self.results['complex'] = {
            'turbo': self.benchmark_turbo_engine(self.complex_template, complex_context, 500),
            'flask': self.benchmark_flask_jinja2(self.complex_template, complex_context, 500),
            'jinja2': self.benchmark_pure_jinja2(self.complex_template, complex_context, 500)
        }
        
        # Test TuskLang template
        print("\n📊 TuskLang Template Benchmark")
        print("-" * 30)
        tsk_context = self.generate_test_context('tsk')
        
        self.results['tsk'] = {
            'turbo': self.benchmark_turbo_engine(self.tsk_template, tsk_context, 200),
            'flask': self.benchmark_flask_jinja2(self.tsk_template, tsk_context, 200),
            'jinja2': self.benchmark_pure_jinja2(self.tsk_template, tsk_context, 200)
        }
        
        # Test async rendering
        print("\n📊 Async Rendering Benchmark")
        print("-" * 30)
        self.results['async'] = {
            'async': self.benchmark_async_rendering(self.complex_template, complex_context, 100)
        }
        
        # Test batch rendering
        print("\n📊 Batch Rendering Benchmark")
        print("-" * 30)
        batch_contexts = [self.generate_test_context('simple') for _ in range(50)]
        self.results['batch'] = {
            'batch': self.benchmark_batch_rendering(self.simple_template, batch_contexts)
        }
        
        # Performance statistics
        print("\n📊 Performance Statistics")
        print("-" * 30)
        turbo_stats = get_performance_stats()
        print(f"Cache hit rate: {turbo_stats.get('cache_hit_rate', 0):.1f}%")
        print(f"Total renders: {turbo_stats.get('total_renders', 0)}")
        print(f"Compiled templates: {turbo_stats.get('compiled_templates', 0)}")
        
        return self.results
    
    def generate_report(self) -> str:
        """Generate comprehensive performance report"""
        report = []
        report.append("# TuskLang Performance Benchmark Report")
        report.append("")
        report.append("## Summary")
        report.append("")
        
        # Calculate speed improvements
        for test_type, engines in self.results.items():
            if 'turbo' in engines and 'flask' in engines:
                turbo_avg = engines['turbo']['avg_time']
                flask_avg = engines['flask']['avg_time']
                speedup = flask_avg / turbo_avg if turbo_avg > 0 else 0
                
                report.append(f"### {test_type.title()} Templates")
                report.append(f"- **TuskLang Turbo**: {turbo_avg*1000:.2f}ms average")
                report.append(f"- **Flask Jinja2**: {flask_avg*1000:.2f}ms average")
                report.append(f"- **Speed Improvement**: {speedup:.1f}x faster")
                report.append("")
        
        report.append("## Detailed Results")
        report.append("")
        report.append("```json")
        report.append(json.dumps(self.results, indent=2))
        report.append("```")
        
        return "\n".join(report)


def main():
    """Run the performance benchmark"""
    benchmark = PerformanceBenchmark()
    results = benchmark.run_comprehensive_benchmark()
    
    # Generate and save report
    report = benchmark.generate_report()
    with open('performance_report.md', 'w') as f:
        f.write(report)
    
    print(f"\n📄 Performance report saved to: performance_report.md")
    print(f"📊 Results: {json.dumps(results, indent=2)}")


if __name__ == "__main__":
    main() 