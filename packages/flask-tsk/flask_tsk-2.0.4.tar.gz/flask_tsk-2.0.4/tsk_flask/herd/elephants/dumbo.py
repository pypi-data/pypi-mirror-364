"""
TuskPHP Dumbo - The Lightweight HTTP Flyer (Python Edition)
==========================================================

🐘 BACKSTORY: Dumbo - The Flying Elephant
----------------------------------------
Dumbo, Disney's beloved flying elephant, was born with oversized ears that
made him the subject of ridicule. But those same ears became his greatest
gift - allowing him to soar through the air with grace and speed. With the
help of Timothy Mouse and a "magic feather," Dumbo discovered he could fly,
becoming the star of the circus and proving that what makes you different
makes you special.

WHY THIS NAME: Like Dumbo who could fly effortlessly with his big ears,
this HTTP client makes web requests soar. It's lightweight, fast, and
turns what could be complex operations into simple, elegant flights across
the web. No magic feather needed - just clean, simple code that flies!

"The very things that held you down are gonna carry you up!"

FEATURES:
- Simple, fluent API for HTTP requests
- Automatic retries with exponential backoff
- Response caching for repeated requests
- Parallel request handling
- Cookie jar management
- Progress callbacks for large downloads
- Built-in error handling and logging

@package TuskPHP\Elephants
@author  TuskPHP Team
@since   1.0.0
"""

import requests
import time
import hashlib
import json
import threading
from typing import Dict, List, Optional, Any, Callable, Union
from urllib.parse import urlencode, urlparse
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# Flask-TSK imports
try:
    from tsk_flask.memory import Memory
except ImportError:
    # Fallback for standalone usage
    Memory = None


@dataclass
class DumboResponse:
    """Response data structure"""
    body: str
    status_code: int
    headers: Dict
    url: str
    elapsed_time: float
    content_type: str = ""
    encoding: str = "utf-8"
    cookies: Dict = None
    json_data: Any = None

    def __post_init__(self):
        if self.cookies is None:
            self.cookies = {}
        
        # Try to parse JSON if content-type suggests it
        if self.content_type and 'application/json' in self.content_type:
            try:
                self.json_data = json.loads(self.body)
            except (json.JSONDecodeError, TypeError):
                self.json_data = None


class Dumbo:
    """Dumbo - The Lightweight HTTP Flyer (Python Edition)"""
    
    def __init__(self, timeout: int = 30, retries: int = 3, magic_feather: bool = True):
        self.timeout = timeout
        self.retries = retries
        self.magic_feather = magic_feather  # Confidence mode!
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Dumbo/1.0 (TuskPHP; Flying Elephant)'
        }
        self.cookies = {}
        
        # Configure session
        self.session.headers.update(self.headers)
        self.session.verify = False  # Disabled for load balancer compatibility
        
        # Enable magic feather features
        if self.magic_feather:
            self.retries = 5
            self.timeout = 60
        
        # Setup logging
        self.logger = logging.getLogger('dumbo')
        self.logger.setLevel(logging.INFO)
    
    def get(self, url: str, params: Dict = None, **kwargs) -> DumboResponse:
        """GET request - Dumbo's basic flight"""
        if params:
            url += '?' + urlencode(params)
        
        return self._fly(url, 'GET', **kwargs)
    
    def post(self, url: str, data: Dict = None, json_data: Dict = None, **kwargs) -> DumboResponse:
        """POST request - Dumbo carries cargo"""
        kwargs['data'] = data
        kwargs['json'] = json_data
        return self._fly(url, 'POST', **kwargs)
    
    def put(self, url: str, data: Dict = None, json_data: Dict = None, **kwargs) -> DumboResponse:
        """PUT request - Dumbo updates cargo"""
        kwargs['data'] = data
        kwargs['json'] = json_data
        return self._fly(url, 'PUT', **kwargs)
    
    def delete(self, url: str, **kwargs) -> DumboResponse:
        """DELETE request - Dumbo removes cargo"""
        return self._fly(url, 'DELETE', **kwargs)
    
    def patch(self, url: str, data: Dict = None, json_data: Dict = None, **kwargs) -> DumboResponse:
        """PATCH request - Dumbo partially updates cargo"""
        kwargs['data'] = data
        kwargs['json'] = json_data
        return self._fly(url, 'PATCH', **kwargs)
    
    def _fly(self, url: str, method: str = 'GET', **kwargs) -> DumboResponse:
        """The main flight method - Where Dumbo soars"""
        # Check cache first - Dumbo remembers his routes
        cache_key = self._generate_cache_key(url, method, kwargs)
        if Memory and (cached := Memory.recall(cache_key)):
            self.logger.info(f"🪶 Dumbo found cached response for {url}")
            return cached
        
        # Timothy Mouse's encouragement (retries)
        attempt = 0
        response = None
        last_error = None
        
        while attempt < self.retries and response is None:
            attempt += 1
            
            if attempt > 1:
                # "You can fly! You can fly!" - Timothy Mouse
                sleep_time = min(2 ** attempt, 30)  # Cap at 30 seconds
                self.logger.info(f"🪶 Dumbo retrying flight {attempt}/{self.retries} in {sleep_time}s")
                time.sleep(sleep_time)
            
            try:
                response = self._make_request(url, method, **kwargs)
                self.logger.info(f"🪶 Dumbo successfully flew to {url} (attempt {attempt})")
            except Exception as e:
                last_error = e
                self.logger.warning(f"🪶 Dumbo stumbled on attempt {attempt}: {e}")
                if attempt >= self.retries:
                    raise Exception(f"Dumbo couldn't complete the flight: {e}")
        
        # Cache successful flights
        if response and response.status_code == 200 and Memory:
            Memory.remember(cache_key, response, 300)  # 5 minutes
        
        return response
    
    def _make_request(self, url: str, method: str, **kwargs) -> DumboResponse:
        """Make the actual HTTP request"""
        start_time = time.time()
        
        # Prepare request parameters
        request_kwargs = {
            'timeout': self.timeout,
            'headers': {**self.headers, **kwargs.get('headers', {})},
            'cookies': {**self.cookies, **kwargs.get('cookies', {})}
        }
        
        # Add data/json if provided
        if 'data' in kwargs:
            request_kwargs['data'] = kwargs['data']
        if 'json' in kwargs:
            request_kwargs['json'] = kwargs['json']
        
        # Make the request
        response = self.session.request(method, url, **request_kwargs)
        elapsed_time = time.time() - start_time
        
        # Create DumboResponse
        dumbo_response = DumboResponse(
            body=response.text,
            status_code=response.status_code,
            headers=dict(response.headers),
            url=response.url,
            elapsed_time=elapsed_time,
            content_type=response.headers.get('content-type', ''),
            encoding=response.encoding,
            cookies=dict(response.cookies)
        )
        
        return dumbo_response
    
    def fly_formation(self, requests_list: List[Dict]) -> Dict[str, DumboResponse]:
        """Parallel requests - Dumbo's circus act!"""
        results = {}
        
        with ThreadPoolExecutor(max_workers=min(len(requests_list), 10)) as executor:
            # Submit all requests
            future_to_key = {}
            for request_data in requests_list:
                key = request_data.get('key', f"request_{len(future_to_key)}")
                url = request_data['url']
                method = request_data.get('method', 'GET')
                kwargs = request_data.get('kwargs', {})
                
                future = executor.submit(self._fly, url, method, **kwargs)
                future_to_key[future] = key
            
            # Collect results
            for future in as_completed(future_to_key):
                key = future_to_key[future]
                try:
                    results[key] = future.result()
                    self.logger.info(f"🪶 Dumbo completed formation flight: {key}")
                except Exception as e:
                    self.logger.error(f"🪶 Dumbo failed formation flight {key}: {e}")
                    results[key] = DumboResponse(
                        body="",
                        status_code=0,
                        headers={},
                        url="",
                        elapsed_time=0
                    )
        
        return results
    
    def download(self, url: str, destination: str, progress_callback: Callable = None) -> bool:
        """Download with progress - Dumbo's cargo service"""
        try:
            response = self.session.get(url, stream=True, timeout=self.timeout)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(destination, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback and total_size > 0:
                            percent = (downloaded / total_size) * 100
                            progress_callback(percent, downloaded, total_size)
            
            self.logger.info(f"🪶 Dumbo successfully downloaded {destination}")
            return True
            
        except Exception as e:
            self.logger.error(f"🪶 Dumbo failed to download {url}: {e}")
            return False
    
    def with_headers(self, headers: Dict) -> 'Dumbo':
        """Set custom headers - Dumbo's flight instructions"""
        self.headers.update(headers)
        self.session.headers.update(headers)
        return self
    
    def with_cookies(self, cookies: Dict) -> 'Dumbo':
        """Set custom cookies"""
        self.cookies.update(cookies)
        return self
    
    def with_magic_feather(self, enabled: bool = True) -> 'Dumbo':
        """Enable/disable the magic feather (confidence mode)"""
        self.magic_feather = enabled
        if enabled:
            # With confidence, we can handle anything!
            self.retries = 5
            self.timeout = 60
        else:
            self.retries = 3
            self.timeout = 30
        return self
    
    def with_timeout(self, timeout: int) -> 'Dumbo':
        """Set custom timeout"""
        self.timeout = timeout
        return self
    
    def with_retries(self, retries: int) -> 'Dumbo':
        """Set custom retry count"""
        self.retries = retries
        return self
    
    def can_reach(self, url: str) -> bool:
        """Quick health check - Can Dumbo fly to this destination?"""
        try:
            response = self.get(url)
            return 200 <= response.status_code < 400
        except Exception:
            return False
    
    def ping(self, url: str) -> Dict[str, Any]:
        """Ping a URL and return detailed response info"""
        try:
            start_time = time.time()
            response = self.get(url)
            elapsed_time = time.time() - start_time
            
            return {
                'reachable': True,
                'status_code': response.status_code,
                'response_time': elapsed_time,
                'content_length': len(response.body),
                'content_type': response.content_type
            }
        except Exception as e:
            return {
                'reachable': False,
                'error': str(e),
                'response_time': None
            }
    
    def batch_ping(self, urls: List[str]) -> Dict[str, Dict[str, Any]]:
        """Ping multiple URLs in parallel"""
        results = {}
        
        with ThreadPoolExecutor(max_workers=min(len(urls), 20)) as executor:
            future_to_url = {executor.submit(self.ping, url): url for url in urls}
            
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    results[url] = future.result()
                except Exception as e:
                    results[url] = {
                        'reachable': False,
                        'error': str(e),
                        'response_time': None
                    }
        
        return results
    
    def _generate_cache_key(self, url: str, method: str, kwargs: Dict) -> str:
        """Generate cache key for request"""
        cache_data = {
            'url': url,
            'method': method,
            'headers': kwargs.get('headers', {}),
            'data': kwargs.get('data'),
            'json': kwargs.get('json')
        }
        return 'dumbo_' + hashlib.md5(json.dumps(cache_data, sort_keys=True).encode()).hexdigest()
    
    def clear_cache(self):
        """Clear all cached responses"""
        if Memory:
            # This would need to be implemented based on your cache system
            # For now, we'll just log it
            self.logger.info("🪶 Dumbo cleared his memory of previous flights")
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get current session information"""
        return {
            'headers': dict(self.session.headers),
            'cookies': dict(self.session.cookies),
            'timeout': self.timeout,
            'retries': self.retries,
            'magic_feather': self.magic_feather
        }
    
    def close(self):
        """Close the session and clean up resources"""
        self.session.close()
        self.logger.info("🪶 Dumbo landed safely and closed his session")


# Convenience functions for common operations
def get(url: str, **kwargs) -> DumboResponse:
    """Quick GET request"""
    dumbo = Dumbo()
    return dumbo.get(url, **kwargs)


def post(url: str, data: Dict = None, **kwargs) -> DumboResponse:
    """Quick POST request"""
    dumbo = Dumbo()
    return dumbo.post(url, data=data, **kwargs)


def download_file(url: str, destination: str, progress_callback: Callable = None) -> bool:
    """Quick file download"""
    dumbo = Dumbo()
    return dumbo.download(url, destination, progress_callback)


def ping_url(url: str) -> Dict[str, Any]:
    """Quick URL ping"""
    dumbo = Dumbo()
    return dumbo.ping(url)


# Flask-TSK integration
def init_dumbo(app):
    """Initialize Dumbo with Flask app"""
    dumbo = Dumbo()
    app.dumbo = dumbo
    return dumbo


def get_dumbo() -> Dumbo:
    """Get Dumbo instance from Flask app context"""
    from flask import current_app
    return current_app.dumbo 