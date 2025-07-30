"""
TuskPHP Babar - The Royal CMS (Python Edition)
==============================================

🐘 BACKSTORY: Babar - The Elephant King
--------------------------------------
Babar, created by Jean de Brunhoff in 1931, is perhaps the most famous
fictional elephant. After his mother was killed by hunters, young Babar
fled to the city where he was educated by the Old Lady. He returned to
the elephant kingdom wearing a green suit, bringing civilization and
modern ideas. He became king, built the city of Celesteville, and ruled
with wisdom and compassion, always balancing tradition with progress.

WHY THIS NAME: Like King Babar who brought order and civilization to
the elephant kingdom, this CMS brings structure and elegance to content
management. Babar transformed a jungle into a functioning society with
rules, roles, and culture - exactly what this CMS does for your content.
Role-based access, organized hierarchies, and civilized content management.

"In the great forest, a little elephant is born. His name is Babar."

FEATURES:
- Hierarchical content organization (like Celesteville)
- Integration with Herd role-based access control
- Multi-language support (Babar spoke French!)
- Version control and content history
- Workflow management with approvals
- Rich media management
- SEO-friendly URLs and metadata
- Component-based page builder
- Theme integration with all 13 TuskPHP themes

@package TuskPHP\Elephants
@author  TuskPHP Team
@since   2.0.0
"""

import json
import time
import hashlib
import re
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
from pathlib import Path

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


class ContentStatus(Enum):
    """Content status enumeration"""
    DRAFT = "draft"
    PUBLISHED = "published"
    DELETED = "deleted"
    ARCHIVED = "archived"


class ContentType(Enum):
    """Content type enumeration"""
    PAGE = "page"
    POST = "post"
    ARTICLE = "article"
    STORY = "story"
    COMPONENT = "component"


@dataclass
class Content:
    """Content data structure"""
    id: str
    title: str
    slug: str
    content: str
    excerpt: str
    type: str
    status: str
    author_id: int
    created_at: int
    updated_at: int
    published_at: Optional[int] = None
    deleted_at: Optional[int] = None
    version: int = 1
    language: str = "en"
    parent_id: Optional[str] = None
    template: str = "default"
    theme: str = "tusk_modern"
    meta_title: str = ""
    meta_description: str = ""
    meta_keywords: str = ""
    featured_image: Optional[str] = None
    components: List[Dict] = None
    settings: Dict = None

    def __post_init__(self):
        if self.components is None:
            self.components = []
        if self.settings is None:
            self.settings = {}


class Babar:
    """Babar - The Royal CMS (Python Edition)"""
    
    def __init__(self, db_path: str = None):
        self.current_user = None
        self.default_language = 'en'
        self.languages = ['en', 'fr', 'es', 'de']  # Babar was international!
        self.db_path = db_path or "babar_cms.db"
        
        # CMS-specific capabilities
        self.cms_capabilities = {
            'cms.view': 'View CMS interface',
            'cms.create': 'Create content',
            'cms.edit': 'Edit content',
            'cms.edit_others': 'Edit others\' content',
            'cms.publish': 'Publish content',
            'cms.delete': 'Delete content',
            'cms.manage_media': 'Manage media library',
            'cms.manage_settings': 'Manage CMS settings',
            'cms.view_analytics': 'View content analytics',
            'cms.manage_themes': 'Manage themes',
            'cms.export': 'Export content'
        }
        
        self.initialize_cms_tables()
        self.initialize_cms_capabilities()
    
    def set_current_user(self, user: Dict):
        """Set the current user for permission checks"""
        self.current_user = user
    
    def has_permission(self, capability: str) -> bool:
        """Check if user has permission for CMS action"""
        if not self.current_user:
            return False
        
        # Super admin can do everything
        if self.current_user.get('role') == 'admin':
            return True
        
        # Check specific capability
        user_capabilities = self.current_user.get('capabilities', [])
        return capability in user_capabilities
    
    def create_story(self, data: Dict) -> Dict:
        """Create content - Building Celesteville, one page at a time"""
        if not self.has_permission('cms.create'):
            raise Exception("You need royal permission to create content in Celesteville!")
        
        story = Content(
            id=self.generate_id(),
            title=data.get('title', 'Untitled Story'),
            slug=self.generate_slug(data.get('title', 'untitled-story')),
            content=data.get('content', ''),
            excerpt=data.get('excerpt', self.generate_excerpt(data.get('content', ''))),
            type=data.get('type', 'page'),
            status='draft',
            author_id=self.current_user['id'],
            created_at=int(time.time()),
            updated_at=int(time.time()),
            language=data.get('language', self.default_language),
            parent_id=data.get('parent_id'),
            template=data.get('template', 'default'),
            theme=data.get('theme', 'tusk_modern'),
            meta_title=data.get('meta_title', data.get('title', '')),
            meta_description=data.get('meta_description', ''),
            meta_keywords=data.get('meta_keywords', ''),
            featured_image=data.get('featured_image'),
            components=data.get('components', []),
            settings=data.get('settings', {})
        )
        
        # Store in the royal archives
        result = self.insert_content(story)
        
        if result:
            # Cache the story for quick access
            if Memory:
                Memory.remember(f"babar_story_{story.id}", asdict(story), 3600)
            
            # Create initial version
            self.create_version(story, 'Initial creation')
            
            # Track activity
            if Herd:
                Herd.track('cms_content_created', {
                    'content_id': story.id,
                    'title': story.title,
                    'type': story.type
                })
            
            return {'success': True, 'data': asdict(story)}
        
        return {'success': False, 'error': 'Failed to create content'}
    
    def update_story(self, story_id: str, data: Dict) -> Dict:
        """Update existing content"""
        story = self.get_story(story_id)
        
        if not story:
            return {'success': False, 'error': 'Content not found'}
        
        # Check permissions
        can_edit = (self.has_permission('cms.edit') or 
                   (self.has_permission('cms.edit_others') and story['author_id'] != self.current_user['id']) or
                   (story['author_id'] == self.current_user['id']))
        
        if not can_edit:
            raise Exception("You don't have permission to edit this royal decree!")
        
        # Update data
        update_data = {
            'title': data.get('title', story['title']),
            'content': data.get('content', story['content']),
            'excerpt': data.get('excerpt', story['excerpt']),
            'type': data.get('type', story['type']),
            'updated_at': int(time.time()),
            'version': story['version'] + 1,
            'language': data.get('language', story['language']),
            'parent_id': data.get('parent_id', story['parent_id']),
            'template': data.get('template', story['template']),
            'theme': data.get('theme', story['theme']),
            'meta_title': data.get('meta_title', story['meta_title']),
            'meta_description': data.get('meta_description', story['meta_description']),
            'meta_keywords': data.get('meta_keywords', story['meta_keywords']),
            'featured_image': data.get('featured_image', story['featured_image']),
            'components': data.get('components', story['components']),
            'settings': data.get('settings', story['settings'])
        }
        
        # Update slug if title changed
        if data.get('title') and data['title'] != story['title']:
            update_data['slug'] = self.generate_slug(data['title'])
        
        result = self.update_content(story_id, update_data)
        
        if result:
            # Create version history
            self.create_version({**story, **update_data}, 'Content updated')
            
            # Clear cache
            if Memory:
                Memory.forget(f"babar_story_{story_id}")
            
            # Track activity
            if Herd:
                Herd.track('cms_content_updated', {
                    'content_id': story_id,
                    'title': update_data['title'],
                    'version': update_data['version']
                })
            
            return {'success': True, 'data': update_data}
        
        return {'success': False, 'error': 'Failed to update content'}
    
    def publish(self, story_id: str) -> Dict:
        """Publish content - Royal decree makes it official"""
        if not self.has_permission('cms.publish'):
            raise Exception("Only the King and his ministers can publish royal decrees!")
        
        story = self.get_story(story_id)
        if not story:
            return {'success': False, 'error': 'Content not found'}
        
        update_data = {
            'status': 'published',
            'published_at': int(time.time()),
            'updated_at': int(time.time())
        }
        
        result = self.update_content(story_id, update_data)
        
        if result:
            # Create version history
            self.create_version({**story, **update_data}, 'Content published')
            
            # Clear cache
            if Memory:
                Memory.forget(f"babar_story_{story_id}")
            
            # Track activity
            if Herd:
                Herd.track('cms_content_published', {
                    'content_id': story_id,
                    'title': story['title']
                })
            
            # Announce to the kingdom
            self.announce_publication(story)
            
            return {'success': True, 'message': 'Royal decree has been published!'}
        
        return {'success': False, 'error': 'Failed to publish content'}
    
    def get_story(self, identifier: Union[str, int]) -> Optional[Dict]:
        """Get single story by ID or slug"""
        # Try cache first
        if isinstance(identifier, str) and not identifier.isdigit():
            # It's a slug
            if Memory:
                story = Memory.recall(f"babar_story_slug_{identifier}")
                if story:
                    return story
            
            story = self.get_content_by_slug(identifier)
        else:
            # It's an ID
            if Memory:
                story = Memory.recall(f"babar_story_{identifier}")
                if story:
                    return story
            
            story = self.get_content_by_id(identifier)
        
        if story:
            # Cache it
            if Memory:
                Memory.remember(f"babar_story_{story['id']}", story, 3600)
                if story.get('slug'):
                    Memory.remember(f"babar_story_slug_{story['slug']}", story, 3600)
        
        return story
    
    def get_library(self, filters: Dict = None) -> Dict:
        """List content with filters - The royal library"""
        if filters is None:
            filters = {}
        
        query = "SELECT * FROM babar_content WHERE 1=1"
        params = []
        
        # Apply filters
        if filters.get('type'):
            query += " AND type = ?"
            params.append(filters['type'])
        
        if filters.get('status'):
            query += " AND status = ?"
            params.append(filters['status'])
        
        if filters.get('language'):
            query += " AND language = ?"
            params.append(filters['language'])
        
        if filters.get('author_id'):
            query += " AND author_id = ?"
            params.append(filters['author_id'])
        
        if filters.get('parent_id'):
            query += " AND parent_id = ?"
            params.append(filters['parent_id'])
        
        # Search functionality
        if filters.get('search'):
            search = filters['search']
            query += " AND (title LIKE ? OR content LIKE ? OR excerpt LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
        
        # Pagination
        page = filters.get('page', 1)
        per_page = filters.get('per_page', 20)
        offset = (page - 1) * per_page
        
        # Order
        order_by = filters.get('order_by', 'updated_at')
        order_dir = filters.get('order_dir', 'desc')
        query += f" ORDER BY {order_by} {order_dir.upper()}"
        query += f" LIMIT {per_page} OFFSET {offset}"
        
        stories = self.execute_query(query, params)
        
        # Get total count for pagination
        count_query = "SELECT COUNT(*) as total FROM babar_content WHERE 1=1"
        count_params = []
        
        if filters.get('type'):
            count_query += " AND type = ?"
            count_params.append(filters['type'])
        if filters.get('status'):
            count_query += " AND status = ?"
            count_params.append(filters['status'])
        if filters.get('language'):
            count_query += " AND language = ?"
            count_params.append(filters['language'])
        if filters.get('author_id'):
            count_query += " AND author_id = ?"
            count_params.append(filters['author_id'])
        
        total_result = self.execute_query(count_query, count_params)
        total = total_result[0]['total'] if total_result else 0
        
        # Decode JSON fields for each story
        for story in stories:
            if story.get('components'):
                story['components'] = json.loads(story['components'])
            if story.get('settings'):
                story['settings'] = json.loads(story['settings'])
        
        return {
            'data': stories,
            'pagination': {
                'current_page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': (total + per_page - 1) // per_page
            }
        }
    
    def delete_story(self, story_id: str) -> Dict:
        """Delete content (soft delete)"""
        if not self.has_permission('cms.delete'):
            raise Exception("You don't have permission to banish stories from Celesteville!")
        
        story = self.get_story(story_id)
        if not story:
            return {'success': False, 'error': 'Content not found'}
        
        update_data = {
            'status': 'deleted',
            'deleted_at': int(time.time()),
            'updated_at': int(time.time())
        }
        
        result = self.update_content(story_id, update_data)
        
        if result:
            # Clear cache
            if Memory:
                Memory.forget(f"babar_story_{story_id}")
                if story.get('slug'):
                    Memory.forget(f"babar_story_slug_{story['slug']}")
            
            # Track activity
            if Herd:
                Herd.track('cms_content_deleted', {
                    'content_id': story_id,
                    'title': story['title']
                })
            
            return {'success': True, 'message': 'Content has been banished from the kingdom'}
        
        return {'success': False, 'error': 'Failed to delete content'}
    
    def get_analytics(self) -> Dict:
        """Get content analytics and statistics"""
        if not self.has_permission('cms.view_analytics'):
            raise Exception("You need royal permission to view the kingdom's analytics!")
        
        total_content = self.execute_query("SELECT COUNT(*) as count FROM babar_content")[0]['count']
        published_content = self.execute_query("SELECT COUNT(*) as count FROM babar_content WHERE status = 'published'")[0]['count']
        draft_content = self.execute_query("SELECT COUNT(*) as count FROM babar_content WHERE status = 'draft'")[0]['count']
        
        content_by_type = self.execute_query("""
            SELECT type, COUNT(*) as count 
            FROM babar_content 
            WHERE status != 'deleted' 
            GROUP BY type
        """)
        
        recent_activity = self.execute_query("""
            SELECT * FROM babar_content 
            WHERE status != 'deleted' 
            ORDER BY updated_at DESC 
            LIMIT 10
        """)
        
        return {
            'summary': {
                'total_content': total_content,
                'published': published_content,
                'drafts': draft_content,
                'deleted': total_content - published_content - draft_content
            },
            'content_by_type': content_by_type,
            'recent_activity': recent_activity,
            'system_info': {
                'cms_version': '2.0.0',
                'themes_available': 13,
                'components_available': self.get_available_components_count(),
                'languages_supported': len(self.languages)
            }
        }
    
    def get_version_history(self, story_id: str) -> List[Dict]:
        """Get version history for content"""
        if not self.has_permission('cms.view'):
            return []
        
        return self.execute_query("""
            SELECT * FROM babar_versions 
            WHERE content_id = ? 
            ORDER BY version_number DESC
        """, [story_id])
    
    # Database operations
    def initialize_cms_tables(self):
        """Ensure CMS database tables exist"""
        tables = {
            'babar_content': """
                CREATE TABLE IF NOT EXISTS babar_content (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    slug TEXT UNIQUE,
                    content TEXT,
                    excerpt TEXT,
                    type TEXT DEFAULT 'page',
                    status TEXT DEFAULT 'draft',
                    author_id INTEGER NOT NULL,
                    created_at INTEGER NOT NULL,
                    updated_at INTEGER NOT NULL,
                    published_at INTEGER,
                    deleted_at INTEGER,
                    version INTEGER DEFAULT 1,
                    language TEXT DEFAULT 'en',
                    parent_id TEXT,
                    template TEXT DEFAULT 'default',
                    theme TEXT DEFAULT 'tusk_modern',
                    meta_title TEXT,
                    meta_description TEXT,
                    meta_keywords TEXT,
                    featured_image TEXT,
                    components TEXT,
                    settings TEXT
                )
            """,
            'babar_versions': """
                CREATE TABLE IF NOT EXISTS babar_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_id TEXT NOT NULL,
                    version_number INTEGER NOT NULL,
                    title TEXT,
                    content TEXT,
                    components TEXT,
                    settings TEXT,
                    changed_by INTEGER NOT NULL,
                    changed_at INTEGER NOT NULL,
                    change_note TEXT
                )
            """
        }
        
        for table_name, sql in tables.items():
            self.execute_query(sql)
    
    def initialize_cms_capabilities(self):
        """Initialize CMS capabilities in the database"""
        # This would normally be handled by a capabilities table
        # For now, we'll just ensure the capabilities are defined
        pass
    
    def insert_content(self, content: Content) -> bool:
        """Insert content into database"""
        query = """
            INSERT INTO babar_content (
                id, title, slug, content, excerpt, type, status, author_id,
                created_at, updated_at, published_at, deleted_at, version,
                language, parent_id, template, theme, meta_title,
                meta_description, meta_keywords, featured_image, components, settings
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = [
            content.id, content.title, content.slug, content.content,
            content.excerpt, content.type, content.status, content.author_id,
            content.created_at, content.updated_at, content.published_at,
            content.deleted_at, content.version, content.language,
            content.parent_id, content.template, content.theme,
            content.meta_title, content.meta_description, content.meta_keywords,
            content.featured_image, json.dumps(content.components),
            json.dumps(content.settings)
        ]
        
        try:
            self.execute_query(query, params)
            return True
        except Exception as e:
            print(f"Error inserting content: {e}")
            return False
    
    def update_content(self, content_id: str, update_data: Dict) -> bool:
        """Update content in database"""
        set_clauses = []
        params = []
        
        for key, value in update_data.items():
            if key in ['components', 'settings']:
                set_clauses.append(f"{key} = ?")
                params.append(json.dumps(value))
            else:
                set_clauses.append(f"{key} = ?")
                params.append(value)
        
        params.append(content_id)
        
        query = f"UPDATE babar_content SET {', '.join(set_clauses)} WHERE id = ?"
        
        try:
            self.execute_query(query, params)
            return True
        except Exception as e:
            print(f"Error updating content: {e}")
            return False
    
    def get_content_by_id(self, content_id: str) -> Optional[Dict]:
        """Get content by ID"""
        result = self.execute_query("SELECT * FROM babar_content WHERE id = ?", [content_id])
        return result[0] if result else None
    
    def get_content_by_slug(self, slug: str) -> Optional[Dict]:
        """Get content by slug"""
        result = self.execute_query("SELECT * FROM babar_content WHERE slug = ?", [slug])
        return result[0] if result else None
    
    def execute_query(self, query: str, params: List = None) -> List[Dict]:
        """Execute database query"""
        if params is None:
            params = []
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, params)
            if query.strip().upper().startswith('SELECT'):
                result = [dict(row) for row in cursor.fetchall()]
            else:
                conn.commit()
                result = True
        except Exception as e:
            print(f"Database error: {e}")
            result = []
        finally:
            conn.close()
        
        return result
    
    def create_version(self, story: Dict, change_note: str = ''):
        """Create version history entry"""
        version = {
            'content_id': story['id'],
            'version_number': story['version'],
            'title': story['title'],
            'content': story['content'],
            'components': json.dumps(story.get('components', [])),
            'settings': json.dumps(story.get('settings', {})),
            'changed_by': self.current_user['id'],
            'changed_at': int(time.time()),
            'change_note': change_note or f"Version {story['version']} of the royal chronicles"
        }
        
        query = """
            INSERT INTO babar_versions (
                content_id, version_number, title, content, components,
                settings, changed_by, changed_at, change_note
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = [
            version['content_id'], version['version_number'], version['title'],
            version['content'], version['components'], version['settings'],
            version['changed_by'], version['changed_at'], version['change_note']
        ]
        
        self.execute_query(query, params)
    
    def generate_id(self) -> str:
        """Generate unique ID for content"""
        import secrets
        return 'story_' + secrets.token_hex(8)
    
    def generate_slug(self, title: str) -> str:
        """Generate URL-friendly slug"""
        slug = re.sub(r'[^a-zA-Z0-9\s-]', '', title.lower())
        slug = re.sub(r'[\s-]+', '-', slug)
        slug = slug.strip('-')
        
        # Ensure uniqueness
        original_slug = slug
        counter = 1
        
        while self.get_content_by_slug(slug):
            slug = f"{original_slug}-{counter}"
            counter += 1
        
        return slug
    
    def generate_excerpt(self, content: str, length: int = 160) -> str:
        """Generate excerpt from content"""
        import re
        text = re.sub(r'<[^>]+>', '', content)
        if len(text) <= length:
            return text
        
        return text[:length] + '...'
    
    def get_available_components_count(self) -> int:
        """Count available components"""
        component_dir = Path(__file__).parent.parent / 'components'
        if not component_dir.exists():
            return 0
        
        components = list(component_dir.glob('*.py'))
        return len(components)
    
    def announce_publication(self, story: Dict):
        """Announce publication (could trigger notifications, cache clearing, etc.)"""
        # This could trigger various actions:
        # - Send notifications to subscribers
        # - Clear relevant caches
        # - Update search indices
        # - Trigger webhooks
        
        if Memory:
            Memory.forget('cms_published_content_cache')
        
        # Log the royal announcement
        print(f"🎺 Royal Herald: '{story['title']}' has been published in Celesteville!")


# Flask-TSK integration
def init_babar(app):
    """Initialize Babar CMS with Flask app"""
    babar = Babar()
    app.babar = babar
    return babar


def get_babar() -> Babar:
    """Get Babar CMS instance from Flask app context"""
    from flask import current_app
    return current_app.babar 