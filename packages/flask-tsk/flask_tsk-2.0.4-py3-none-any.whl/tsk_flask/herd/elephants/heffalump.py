"""
TuskPHP Heffalump - The Fuzzy Search Expert (Python Edition)
============================================================

🐘 BACKSTORY: Heffalump - The Mysterious Elephant
------------------------------------------------
In A.A. Milne's Winnie-the-Pooh stories, Heffalumps are mysterious
elephant-like creatures that exist mostly in imagination. Pooh and Piglet
are both fascinated and frightened by them, setting elaborate traps that
never quite work. Heffalumps are elusive, hard to define precisely, and
everyone seems to have a slightly different idea of what they look like.
The beauty is in their ambiguity - they might be scary, or friendly, big
or small, real or imagined.

WHY THIS NAME: Like the elusive Heffalump that's hard to pin down exactly,
this fuzzy search system finds matches even when you're not quite sure what
you're looking for. It handles misspellings, partial matches, and "sounds
like" searches - perfect for when users are hunting for something as
mysterious as a Heffalump.

"A Heffalump or Horrible Heffalump is a creature mentioned in the Winnie-the-Pooh stories"

FEATURES:
- Levenshtein distance matching
- Phonetic matching (Soundex/Metaphone)
- N-gram similarity
- Fuzzy autocomplete
- Typo correction
- "Did you mean?" suggestions
- Weighted multi-field search
- Elasticsearch integration
- Multi-instance support
- Search analytics

@package TuskPHP\Elephants
@author  TuskPHP Team
@since   1.0.0
"""

import json
import time
import re
import hashlib
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import sqlite3
from difflib import SequenceMatcher
import unicodedata

# Optional imports for advanced features
try:
    import jellyfish
    JELLYFISH_AVAILABLE = True
except ImportError:
    JELLYFISH_AVAILABLE = False

try:
    from elasticsearch import Elasticsearch
    ELASTICSEARCH_AVAILABLE = True
except ImportError:
    ELASTICSEARCH_AVAILABLE = False

# Flask-TSK imports
try:
    from tsk_flask.database import TuskDb
    from tsk_flask.memory import Memory
    from tsk_flask.herd import Herd
    from tsk_flask.utils import PermissionHelper
except ImportError:
    # Fallback for standalone usage
    TuskDb = None
    Memory = None
    Herd = None
    PermissionHelper = None


class SearchType(Enum):
    """Search type enumeration"""
    EXACT = "exact"
    FUZZY = "fuzzy"
    PHONETIC = "phonetic"
    NGRAM = "ngram"
    AUTOSUGGEST = "autosuggest"


@dataclass
class SearchResult:
    """Search result data structure"""
    id: str
    content: str
    score: float
    confidence: float
    match_type: str
    metadata: Dict = None
    highlights: List[str] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.highlights is None:
            self.highlights = []


@dataclass
class SearchAnalytics:
    """Search analytics data structure"""
    query: str
    results_count: int
    response_time: float
    timestamp: int
    user_id: Optional[int] = None
    search_type: str = "fuzzy"


class Heffalump:
    """
    Heffalump - The Fuzzy Search Expert
    
    Heffalump finds what you're looking for even when you're not quite sure
    what it is. Like the mysterious creature from Winnie-the-Pooh, Heffalump
    is elusive but always there when you need to find something.
    """
    
    def __init__(self, instance_id: str = 'default', config: Dict = None):
        """Initialize Heffalump - The search begins"""
        self.instance_id = instance_id
        self.config = self._load_configuration(instance_id, config or {})
        
        # Search configuration
        self.tolerance = self.config.get('tolerance', 2)
        self.min_similarity = self.config.get('min_similarity', 0.7)
        self.soundex_enabled = self.config.get('soundex_enabled', True)
        
        # Search index and data
        self.search_index = []
        self.analytics = []
        
        # Initialize components
        self.db = None
        self.elastic_client = None
        
        if TuskDb:
            self.db = TuskDb()
        
        self._initialize_elasticsearch()
        self._load_search_index()
        self._prepare_hunting()
        
        print(f"🔍 Heffalump instance '{instance_id}' is ready to hunt!")
    
    def hunt(self, query: str, search_in: List[str] = None) -> List[SearchResult]:
        """
        Fuzzy search - Looking for Heffalumps in the woods
        
        Args:
            query: Search query
            search_in: List of strings to search in (optional)
            
        Returns:
            List of SearchResult objects
        """
        query = query.lower().strip()
        results = []
        
        # Use provided search_in or default index
        haystack = search_in if search_in is not None else self.search_index
        
        # First, check for exact match
        exact_match = self._exact_match(query, haystack)
        if exact_match:
            return [exact_match]
        
        print(f"🔍 Heffalump hunting for something like '{query}'...")
        
        # Try different hunting techniques
        levenshtein_results = self._levenshtein_hunt(query, haystack)
        soundex_results = self._soundex_hunt(query, haystack) if self.soundex_enabled else []
        ngram_results = self._ngram_hunt(query, haystack)
        
        # Combine results
        results = levenshtein_results + soundex_results + ngram_results
        
        # Remove duplicates and sort by confidence
        results = self._deduplicate_results(results)
        results.sort(key=lambda x: x.confidence, reverse=True)
        
        # Track search analytics
        self._track_search(query, results, time.time())
        
        return results
    
    def hunt_enhanced(self, query: str, options: Dict = None) -> List[SearchResult]:
        """
        Enhanced search with advanced features
        
        Args:
            query: Search query
            options: Search options (elasticsearch, weights, etc.)
            
        Returns:
            List of SearchResult objects
        """
        if options is None:
            options = {}
        
        # Try Elasticsearch first if available
        if self.elastic_client and options.get('use_elasticsearch', True):
            elastic_results = self._elasticsearch_hunt(query, options)
            if elastic_results:
                return elastic_results
        
        # Fall back to regular fuzzy search
        return self.hunt(query, options.get('search_in'))
    
    def did_you_mean(self, query: str, context: Dict = None) -> List[str]:
        """
        Generate "Did you mean?" suggestions
        
        Args:
            query: Query to suggest alternatives for
            context: Additional context for suggestions
            
        Returns:
            List of suggested queries
        """
        suggestions = []
        query_lower = query.lower()
        
        # Check for common typos
        common_typos = {
            'teh': 'the',
            'recieve': 'receive',
            'seperate': 'separate',
            'occured': 'occurred',
            'neccessary': 'necessary',
            'definately': 'definitely',
            'accomodate': 'accommodate',
            'begining': 'beginning',
            'beleive': 'believe',
            'calender': 'calendar'
        }
        
        # Check for exact typo matches
        if query_lower in common_typos:
            suggestions.append(common_typos[query_lower])
        
        # Generate phonetic suggestions
        if self.soundex_enabled:
            phonetic_suggestions = self._generate_phonetic_suggestions(query)
            suggestions.extend(phonetic_suggestions)
        
        # Generate n-gram suggestions
        ngram_suggestions = self._generate_ngram_suggestions(query)
        suggestions.extend(ngram_suggestions)
        
        # Remove duplicates and limit results
        suggestions = list(set(suggestions))[:5]
        
        return suggestions
    
    def track_suggestions(self, partial: str, limit: int = 5) -> List[str]:
        """
        Track and suggest based on partial input
        
        Args:
            partial: Partial query string
            limit: Maximum number of suggestions
            
        Returns:
            List of suggestions
        """
        if len(partial) < 2:
            return []
        
        suggestions = []
        partial_lower = partial.lower()
        
        # Find items that start with the partial
        for item in self.search_index:
            if isinstance(item, str) and item.lower().startswith(partial_lower):
                suggestions.append(item)
            elif isinstance(item, dict) and 'content' in item:
                if item['content'].lower().startswith(partial_lower):
                    suggestions.append(item['content'])
        
        # Also find items that contain the partial
        for item in self.search_index:
            if isinstance(item, str) and partial_lower in item.lower():
                if item not in suggestions:
                    suggestions.append(item)
            elif isinstance(item, dict) and 'content' in item:
                if partial_lower in item['content'].lower() and item['content'] not in suggestions:
                    suggestions.append(item['content'])
        
        # Sort by relevance (exact prefix matches first)
        suggestions.sort(key=lambda x: (not x.lower().startswith(partial_lower), x.lower()))
        
        return suggestions[:limit]
    
    def index(self, id: str, content: str, metadata: Dict = None) -> bool:
        """
        Index content for searching
        
        Args:
            id: Unique identifier
            content: Content to index
            metadata: Additional metadata
            
        Returns:
            Success status
        """
        try:
            indexed_item = {
                'id': id,
                'content': content,
                'metadata': metadata or {},
                'indexed_at': int(time.time())
            }
            
            # Add to search index
            self.search_index.append(indexed_item)
            
            # Index in Elasticsearch if available
            if self.elastic_client:
                self._elasticsearch_index(id, content, metadata)
            
            return True
            
        except Exception as e:
            print(f"Error indexing content: {e}")
            return False
    
    def bulk_index(self, items: List[Dict]) -> Dict:
        """
        Bulk index multiple items
        
        Args:
            items: List of items to index
            
        Returns:
            Indexing results
        """
        results = {
            'successful': 0,
            'failed': 0,
            'errors': []
        }
        
        for item in items:
            try:
                success = self.index(
                    item.get('id'),
                    item.get('content'),
                    item.get('metadata')
                )
                if success:
                    results['successful'] += 1
                else:
                    results['failed'] += 1
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(str(e))
        
        return results
    
    def get_analytics(self, days: int = 30) -> Dict:
        """
        Get search analytics
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Analytics data
        """
        cutoff_time = int(time.time()) - (days * 24 * 60 * 60)
        
        recent_analytics = [
            a for a in self.analytics 
            if a.timestamp >= cutoff_time
        ]
        
        if not recent_analytics:
            return {
                'total_searches': 0,
                'average_response_time': 0,
                'most_common_queries': [],
                'search_types': {}
            }
        
        # Calculate statistics
        total_searches = len(recent_analytics)
        avg_response_time = sum(a.response_time for a in recent_analytics) / total_searches
        
        # Most common queries
        query_counts = {}
        for a in recent_analytics:
            query_counts[a.query] = query_counts.get(a.query, 0) + 1
        
        most_common = sorted(query_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Search types
        type_counts = {}
        for a in recent_analytics:
            type_counts[a.search_type] = type_counts.get(a.search_type, 0) + 1
        
        return {
            'total_searches': total_searches,
            'average_response_time': avg_response_time,
            'most_common_queries': most_common,
            'search_types': type_counts
        }
    
    @staticmethod
    def create_instance(instance_id: str, config: Dict) -> 'Heffalump':
        """
        Create a new Heffalump instance
        
        Args:
            instance_id: Instance identifier
            config: Configuration dictionary
            
        Returns:
            New Heffalump instance
        """
        return Heffalump(instance_id, config)
    
    @staticmethod
    def get_all_instances() -> Dict[str, 'Heffalump']:
        """
        Get all Heffalump instances
        
        Returns:
            Dictionary of instances
        """
        # This would track instances in a class variable
        # For now, return empty dict
        return {}
    
    # Private helper methods
    
    def _load_configuration(self, instance_id: str, custom_config: Dict) -> Dict:
        """Load configuration for instance"""
        default_config = {
            'tolerance': 2,
            'min_similarity': 0.7,
            'soundex_enabled': True,
            'ngram_size': 2,
            'max_results': 50,
            'elasticsearch_url': 'http://localhost:9200',
            'elasticsearch_index': f'heffalump_{instance_id}'
        }
        
        # Merge custom config
        config = default_config.copy()
        config.update(custom_config)
        
        return config
    
    def _initialize_elasticsearch(self):
        """Initialize Elasticsearch client"""
        if not ELASTICSEARCH_AVAILABLE:
            return
        
        try:
            self.elastic_client = Elasticsearch([self.config['elasticsearch_url']])
            self._create_search_index()
        except Exception as e:
            print(f"Elasticsearch initialization failed: {e}")
            self.elastic_client = None
    
    def _create_search_index(self):
        """Create Elasticsearch index"""
        if not self.elastic_client:
            return
        
        try:
            index_name = self.config['elasticsearch_index']
            
            # Check if index exists
            if not self.elastic_client.indices.exists(index=index_name):
                # Create index with mapping
                mapping = {
                    "mappings": {
                        "properties": {
                            "content": {
                                "type": "text",
                                "analyzer": "standard"
                            },
                            "metadata": {
                                "type": "object"
                            },
                            "indexed_at": {
                                "type": "date"
                            }
                        }
                    }
                }
                
                self.elastic_client.indices.create(
                    index=index_name,
                    body=mapping
                )
                
                print(f"Created Elasticsearch index: {index_name}")
        
        except Exception as e:
            print(f"Error creating Elasticsearch index: {e}")
    
    def _load_search_index(self):
        """Load search index from database or files"""
        try:
            if self.db:
                # Load from database
                self._load_from_database()
            else:
                # Load from files
                self._load_from_files()
        
        except Exception as e:
            print(f"Error loading search index: {e}")
            self.search_index = []
    
    def _load_from_database(self):
        """Load search index from database"""
        if not self.db:
            return
        
        try:
            # This would load from the database
            # For now, use empty list
            self.search_index = []
        except Exception as e:
            print(f"Error loading from database: {e}")
    
    def _load_from_files(self):
        """Load search index from files"""
        try:
            # This would load from files
            # For now, use empty list
            self.search_index = []
        except Exception as e:
            print(f"Error loading from files: {e}")
    
    def _prepare_hunting(self):
        """Prepare for search operations"""
        # Pre-process search index for better performance
        if self.search_index:
            print(f"🔍 Heffalump prepared {len(self.search_index)} items for hunting")
    
    def _exact_match(self, query: str, haystack: List) -> Optional[SearchResult]:
        """Find exact match"""
        query_lower = query.lower()
        
        for item in haystack:
            if isinstance(item, str):
                if item.lower() == query_lower:
                    return SearchResult(
                        id=hashlib.md5(item.encode()).hexdigest(),
                        content=item,
                        score=1.0,
                        confidence=1.0,
                        match_type=SearchType.EXACT.value
                    )
            elif isinstance(item, dict) and 'content' in item:
                if item['content'].lower() == query_lower:
                    return SearchResult(
                        id=item.get('id', hashlib.md5(item['content'].encode()).hexdigest()),
                        content=item['content'],
                        score=1.0,
                        confidence=1.0,
                        match_type=SearchType.EXACT.value,
                        metadata=item.get('metadata', {})
                    )
        
        return None
    
    def _levenshtein_hunt(self, query: str, haystack: List) -> List[SearchResult]:
        """Search using Levenshtein distance"""
        results = []
        
        for item in haystack:
            if isinstance(item, str):
                distance = self._levenshtein_distance(query, item.lower())
                if distance <= self.tolerance:
                    confidence = self._get_confidence(distance)
                    if confidence >= self.min_similarity:
                        results.append(SearchResult(
                            id=hashlib.md5(item.encode()).hexdigest(),
                            content=item,
                            score=1.0 - (distance / len(query)),
                            confidence=confidence,
                            match_type=SearchType.FUZZY.value
                        ))
            elif isinstance(item, dict) and 'content' in item:
                distance = self._levenshtein_distance(query, item['content'].lower())
                if distance <= self.tolerance:
                    confidence = self._get_confidence(distance)
                    if confidence >= self.min_similarity:
                        results.append(SearchResult(
                            id=item.get('id', hashlib.md5(item['content'].encode()).hexdigest()),
                            content=item['content'],
                            score=1.0 - (distance / len(query)),
                            confidence=confidence,
                            match_type=SearchType.FUZZY.value,
                            metadata=item.get('metadata', {})
                        ))
        
        return results
    
    def _soundex_hunt(self, query: str, haystack: List) -> List[SearchResult]:
        """Search using phonetic matching"""
        if not JELLYFISH_AVAILABLE:
            return []
        
        results = []
        query_soundex = jellyfish.soundex(query)
        
        for item in haystack:
            if isinstance(item, str):
                item_soundex = jellyfish.soundex(item.lower())
                if query_soundex == item_soundex:
                    results.append(SearchResult(
                        id=hashlib.md5(item.encode()).hexdigest(),
                        content=item,
                        score=0.8,
                        confidence=0.8,
                        match_type=SearchType.PHONETIC.value
                    ))
            elif isinstance(item, dict) and 'content' in item:
                item_soundex = jellyfish.soundex(item['content'].lower())
                if query_soundex == item_soundex:
                    results.append(SearchResult(
                        id=item.get('id', hashlib.md5(item['content'].encode()).hexdigest()),
                        content=item['content'],
                        score=0.8,
                        confidence=0.8,
                        match_type=SearchType.PHONETIC.value,
                        metadata=item.get('metadata', {})
                    ))
        
        return results
    
    def _ngram_hunt(self, query: str, haystack: List, n: int = 2) -> List[SearchResult]:
        """Search using n-gram similarity"""
        results = []
        query_ngrams = self._get_ngrams(query, n)
        
        for item in haystack:
            if isinstance(item, str):
                item_ngrams = self._get_ngrams(item.lower(), n)
                similarity = self._calculate_ngram_similarity(query_ngrams, item_ngrams)
                if similarity >= self.min_similarity:
                    results.append(SearchResult(
                        id=hashlib.md5(item.encode()).hexdigest(),
                        content=item,
                        score=similarity,
                        confidence=similarity,
                        match_type=SearchType.NGRAM.value
                    ))
            elif isinstance(item, dict) and 'content' in item:
                item_ngrams = self._get_ngrams(item['content'].lower(), n)
                similarity = self._calculate_ngram_similarity(query_ngrams, item_ngrams)
                if similarity >= self.min_similarity:
                    results.append(SearchResult(
                        id=item.get('id', hashlib.md5(item['content'].encode()).hexdigest()),
                        content=item['content'],
                        score=similarity,
                        confidence=similarity,
                        match_type=SearchType.NGRAM.value,
                        metadata=item.get('metadata', {})
                    ))
        
        return results
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings"""
        if JELLYFISH_AVAILABLE:
            return jellyfish.levenshtein_distance(s1, s2)
        else:
            # Fallback implementation
            return self._simple_levenshtein(s1, s2)
    
    def _simple_levenshtein(self, s1: str, s2: str) -> int:
        """Simple Levenshtein distance implementation"""
        if len(s1) < len(s2):
            return self._simple_levenshtein(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def _get_ngrams(self, string: str, n: int) -> List[str]:
        """Get n-grams from string"""
        return [string[i:i+n] for i in range(len(string) - n + 1)]
    
    def _calculate_ngram_similarity(self, ngrams1: List[str], ngrams2: List[str]) -> float:
        """Calculate similarity between n-gram sets"""
        if not ngrams1 or not ngrams2:
            return 0.0
        
        intersection = set(ngrams1) & set(ngrams2)
        union = set(ngrams1) | set(ngrams2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _get_confidence(self, distance: int) -> float:
        """Get confidence score from distance"""
        return max(0.0, 1.0 - (distance / 10.0))
    
    def _deduplicate_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """Remove duplicate results"""
        seen = set()
        unique_results = []
        
        for result in results:
            result_key = f"{result.id}:{result.content}"
            if result_key not in seen:
                seen.add(result_key)
                unique_results.append(result)
        
        return unique_results
    
    def _elasticsearch_hunt(self, query: str, options: Dict) -> List[SearchResult]:
        """Search using Elasticsearch"""
        if not self.elastic_client:
            return []
        
        try:
            index_name = self.config['elasticsearch_index']
            
            # Prepare search query
            search_body = {
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["content^2", "metadata.*"],
                        "fuzziness": "AUTO"
                    }
                },
                "size": options.get('max_results', 20)
            }
            
            response = self.elastic_client.search(
                index=index_name,
                body=search_body
            )
            
            return self._format_elasticsearch_results(response)
        
        except Exception as e:
            print(f"Elasticsearch search failed: {e}")
            return []
    
    def _format_elasticsearch_results(self, response: Dict) -> List[SearchResult]:
        """Format Elasticsearch response"""
        results = []
        
        for hit in response.get('hits', {}).get('hits', []):
            source = hit['_source']
            score = hit['_score']
            
            results.append(SearchResult(
                id=hit['_id'],
                content=source.get('content', ''),
                score=score,
                confidence=min(1.0, score / 10.0),  # Normalize score
                match_type=SearchType.FUZZY.value,
                metadata=source.get('metadata', {})
            ))
        
        return results
    
    def _elasticsearch_index(self, id: str, content: str, metadata: Dict):
        """Index content in Elasticsearch"""
        if not self.elastic_client:
            return
        
        try:
            index_name = self.config['elasticsearch_index']
            
            doc = {
                'content': content,
                'metadata': metadata or {},
                'indexed_at': datetime.now().isoformat()
            }
            
            self.elastic_client.index(
                index=index_name,
                id=id,
                body=doc
            )
        
        except Exception as e:
            print(f"Elasticsearch indexing failed: {e}")
    
    def _generate_phonetic_suggestions(self, query: str) -> List[str]:
        """Generate phonetic suggestions"""
        if not JELLYFISH_AVAILABLE:
            return []
        
        suggestions = []
        query_soundex = jellyfish.soundex(query)
        
        for item in self.search_index:
            if isinstance(item, str):
                item_soundex = jellyfish.soundex(item.lower())
                if query_soundex == item_soundex and item.lower() != query.lower():
                    suggestions.append(item)
            elif isinstance(item, dict) and 'content' in item:
                item_soundex = jellyfish.soundex(item['content'].lower())
                if query_soundex == item_soundex and item['content'].lower() != query.lower():
                    suggestions.append(item['content'])
        
        return suggestions[:5]
    
    def _generate_ngram_suggestions(self, query: str) -> List[str]:
        """Generate n-gram suggestions"""
        suggestions = []
        query_ngrams = self._get_ngrams(query, 2)
        
        for item in self.search_index:
            if isinstance(item, str):
                item_ngrams = self._get_ngrams(item.lower(), 2)
                similarity = self._calculate_ngram_similarity(query_ngrams, item_ngrams)
                if similarity > 0.5 and item.lower() != query.lower():
                    suggestions.append(item)
            elif isinstance(item, dict) and 'content' in item:
                item_ngrams = self._get_ngrams(item['content'].lower(), 2)
                similarity = self._calculate_ngram_similarity(query_ngrams, item_ngrams)
                if similarity > 0.5 and item['content'].lower() != query.lower():
                    suggestions.append(item['content'])
        
        return suggestions[:5]
    
    def _track_search(self, query: str, results: List[SearchResult], start_time: float):
        """Track search analytics"""
        response_time = time.time() - start_time
        
        analytics = SearchAnalytics(
            query=query,
            results_count=len(results),
            response_time=response_time,
            timestamp=int(time.time())
        )
        
        self.analytics.append(analytics)
        
        # Keep analytics manageable
        if len(self.analytics) > 1000:
            self.analytics = self.analytics[-1000:]


def init_heffalump(app, instance_id: str = 'default', config: Dict = None):
    """Initialize Heffalump with Flask app"""
    heffalump = Heffalump(instance_id, config)
    setattr(app, f'heffalump_{instance_id}', heffalump)
    return heffalump


def get_heffalump(instance_id: str = 'default') -> Heffalump:
    """Get Heffalump instance"""
    from flask import current_app
    return getattr(current_app, f'heffalump_{instance_id}', None) 