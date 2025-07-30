"""
Flask-TSK Example Runner

A comprehensive example runner that allows developers to easily run and showcase
different Flask-TSK examples with elephant services integration.
"""

import sys
import os
import argparse
from typing import Dict, Any, Optional
from flask import Flask

from .examples import (
    BasicAuthExample,
    BlogSystemExample,
    EcommerceExample,
    DashboardExample,
    APIServiceExample,
    SocialNetworkExample,
    PortfolioExample,
    SaaSAppExample
)


class ExampleRunner:
    """Runner for Flask-TSK examples"""
    
    def __init__(self):
        self.examples = {
            'basic-auth': {
                'class': BasicAuthExample,
                'name': 'Basic Authentication',
                'description': 'Simple authentication example showcasing Herd with elephant services',
                'port': 5000
            },
            'blog': {
                'class': BlogSystemExample,
                'name': 'Blog System',
                'description': 'Complete blog system with content management and elephant services',
                'port': 5001
            },
            'ecommerce': {
                'class': EcommerceExample,
                'name': 'E-commerce System',
                'description': 'Complete e-commerce system with product management and elephant services',
                'port': 5002
            },
            'dashboard': {
                'class': DashboardExample,
                'name': 'Admin Dashboard',
                'description': 'Comprehensive admin dashboard with elephant services monitoring',
                'port': 5003
            },
            'api': {
                'class': APIServiceExample,
                'name': 'API Service',
                'description': 'REST API service with authentication and elephant services',
                'port': 5004
            },
            'social': {
                'class': SocialNetworkExample,
                'name': 'Social Network',
                'description': 'Social network with user profiles and content sharing',
                'port': 5005
            },
            'portfolio': {
                'class': PortfolioExample,
                'name': 'Portfolio Website',
                'description': 'Personal portfolio website with project showcase and admin panel',
                'port': 5006
            },
            'saas': {
                'class': SaaSAppExample,
                'name': 'SaaS Application',
                'description': 'Software-as-a-Service application with subscription management',
                'port': 5007
            }
        }
    
    def list_examples(self):
        """List all available examples"""
        print("🐘 Flask-TSK Examples Available:")
        print("=" * 50)
        
        for key, example in self.examples.items():
            print(f"📁 {key}")
            print(f"   Name: {example['name']}")
            print(f"   Description: {example['description']}")
            print(f"   Port: {example['port']}")
            print()
    
    def run_example(self, example_key: str, host: str = '127.0.0.1', port: Optional[int] = None, debug: bool = True):
        """Run a specific example"""
        if example_key not in self.examples:
            print(f"❌ Example '{example_key}' not found!")
            print("Available examples:")
            self.list_examples()
            return False
        
        example_info = self.examples[example_key]
        example_class = example_info['class']
        
        # Use provided port or default
        if port is None:
            port = example_info['port']
        
        try:
            # Create and run the example
            example = example_class()
            example.run(debug=debug, host=host, port=port)
            return True
            
        except Exception as e:
            print(f"❌ Error running example '{example_key}': {str(e)}")
            return False
    
    def run_all_examples(self, host: str = '127.0.0.1', debug: bool = False):
        """Run all examples on different ports"""
        print("🚀 Starting all Flask-TSK examples...")
        print("=" * 50)
        
        import threading
        import time
        
        threads = []
        
        for key, example_info in self.examples.items():
            def run_example_thread(example_key, example_info):
                try:
                    example = example_info['class']()
                    print(f"🐘 Starting {example_info['name']} on port {example_info['port']}")
                    example.run(debug=debug, host=host, port=example_info['port'])
                except Exception as e:
                    print(f"❌ Error in {example_key}: {str(e)}")
            
            thread = threading.Thread(
                target=run_example_thread,
                args=(key, example_info),
                daemon=True
            )
            threads.append(thread)
            thread.start()
            time.sleep(1)  # Small delay between starts
        
        print("\n✅ All examples started!")
        print("🌐 URLs:")
        for key, example_info in self.examples.items():
            print(f"   {example_info['name']}: http://{host}:{example_info['port']}")
        
        print("\n⏹️  Press Ctrl+C to stop all examples")
        
        try:
            # Keep main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping all examples...")
            return True
    
    def show_example_info(self, example_key: str):
        """Show detailed information about an example"""
        if example_key not in self.examples:
            print(f"❌ Example '{example_key}' not found!")
            return False
        
        example_info = self.examples[example_key]
        
        print(f"🐘 {example_info['name']}")
        print("=" * 50)
        print(f"Description: {example_info['description']}")
        print(f"Default Port: {example_info['port']}")
        print(f"Class: {example_info['class'].__name__}")
        
        # Show elephant services used
        example = example_info['class']()
        print(f"\n🐘 Elephant Services:")
        for name, elephant in example.elephants.items():
            print(f"   - {name}: {type(elephant).__name__}")
        
        return True


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description='Flask-TSK Example Runner')
    parser.add_argument('command', nargs='?', choices=['list', 'run', 'run-all', 'info'],
                       help='Command to execute')
    parser.add_argument('example', nargs='?', help='Example to run or show info for')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, help='Port to run on (overrides default)')
    parser.add_argument('--debug', action='store_true', default=True, help='Run in debug mode')
    parser.add_argument('--no-debug', dest='debug', action='store_false', help='Disable debug mode')
    
    args = parser.parse_args()
    
    runner = ExampleRunner()
    
    if args.command == 'list' or not args.command:
        runner.list_examples()
        
    elif args.command == 'run':
        if not args.example:
            print("❌ Please specify an example to run!")
            print("Available examples:")
            runner.list_examples()
            sys.exit(1)
        
        success = runner.run_example(args.example, args.host, args.port, args.debug)
        if not success:
            sys.exit(1)
    
    elif args.command == 'run-all':
        runner.run_all_examples(args.host, args.debug)
    
    elif args.command == 'info':
        if not args.example:
            print("❌ Please specify an example to show info for!")
            print("Available examples:")
            runner.list_examples()
            sys.exit(1)
        
        success = runner.show_example_info(args.example)
        if not success:
            sys.exit(1)


if __name__ == '__main__':
    main() 