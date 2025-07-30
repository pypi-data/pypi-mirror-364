-- Flask-TSK Elephant Services Database Template
-- This file contains database schemas for all elephant services

-- ==========================================
-- BABAR CMS TABLES
-- ==========================================

-- CMS Content table
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
);

-- CMS Version history
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
);

-- ==========================================
-- HORTON JOB QUEUE TABLES
-- ==========================================

-- Jobs table
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    data TEXT,
    queue TEXT DEFAULT 'default',
    priority INTEGER DEFAULT 0,
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    created_at INTEGER NOT NULL,
    scheduled_at INTEGER,
    started_at INTEGER,
    completed_at INTEGER,
    status TEXT DEFAULT 'pending',
    result TEXT,
    error TEXT,
    retry_delay INTEGER DEFAULT 60,
    worker_id TEXT
);

-- Workers table
CREATE TABLE IF NOT EXISTS workers (
    worker_id TEXT PRIMARY KEY,
    jobs_processed INTEGER DEFAULT 0,
    jobs_failed INTEGER DEFAULT 0,
    uptime INTEGER DEFAULT 0,
    last_heartbeat INTEGER,
    status TEXT DEFAULT 'active'
);

-- ==========================================
-- SATAO SECURITY TABLES
-- ==========================================

-- Blocked IPs
CREATE TABLE IF NOT EXISTS blocked_ips (
    ip TEXT PRIMARY KEY,
    time REAL NOT NULL,
    reason TEXT NOT NULL,
    attempts INTEGER DEFAULT 1,
    expires REAL
);

-- Security events
CREATE TABLE IF NOT EXISTS security_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip TEXT NOT NULL,
    event_type TEXT NOT NULL,
    details TEXT,
    timestamp REAL NOT NULL,
    threat_level TEXT DEFAULT 'low'
);

-- Security alerts
CREATE TABLE IF NOT EXISTS security_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_type TEXT NOT NULL,
    message TEXT NOT NULL,
    severity TEXT DEFAULT 'warning',
    timestamp REAL NOT NULL,
    resolved BOOLEAN DEFAULT 0,
    resolved_at REAL
);

-- ==========================================
-- THEME ANALYZER TABLES
-- ==========================================

-- Theme analytics
CREATE TABLE IF NOT EXISTS theme_analytics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    theme TEXT NOT NULL,
    user_id INTEGER,
    session_id TEXT NOT NULL,
    ip_address TEXT,
    user_agent TEXT,
    page_url TEXT,
    timestamp INTEGER NOT NULL,
    context TEXT,
    load_time INTEGER,
    viewport_width INTEGER,
    viewport_height INTEGER,
    device_type TEXT DEFAULT 'desktop'
);

-- Theme A/B tests
CREATE TABLE IF NOT EXISTS theme_ab_tests (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    themes TEXT NOT NULL,
    traffic_split TEXT NOT NULL,
    success_metrics TEXT,
    target_audience TEXT,
    start_date INTEGER NOT NULL,
    end_date INTEGER NOT NULL,
    status TEXT DEFAULT 'active',
    created_by INTEGER
);

-- ==========================================
-- KOSHIK AUDIO TABLES
-- ==========================================

-- Audio notifications
CREATE TABLE IF NOT EXISTS koshik_notifications (
    id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    sound_type TEXT DEFAULT 'default',
    message TEXT,
    created_at INTEGER NOT NULL,
    played BOOLEAN DEFAULT 0,
    options TEXT
);

-- User audio preferences
CREATE TABLE IF NOT EXISTS koshik_preferences (
    user_id INTEGER PRIMARY KEY,
    volume REAL DEFAULT 0.7,
    language TEXT DEFAULT 'en',
    rate REAL DEFAULT 1.0,
    pitch REAL DEFAULT 1.0,
    voice TEXT DEFAULT 'koshik',
    updated_at INTEGER NOT NULL
);

-- ==========================================
-- JUMBO UPLOAD TABLES
-- ==========================================

-- Upload sessions
CREATE TABLE IF NOT EXISTS jumbo_uploads (
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    total_size INTEGER NOT NULL,
    chunks_expected INTEGER NOT NULL,
    chunks_received INTEGER DEFAULT 0,
    started_at INTEGER NOT NULL,
    status TEXT DEFAULT 'uploading',
    metadata TEXT,
    last_chunk_at INTEGER,
    completed_at INTEGER,
    final_path TEXT,
    resumed_at INTEGER,
    abandoned_at INTEGER,
    cancelled_at INTEGER
);

-- Upload chunks
CREATE TABLE IF NOT EXISTS jumbo_chunks (
    upload_id TEXT NOT NULL,
    chunk_number INTEGER NOT NULL,
    chunk_data BLOB NOT NULL,
    hash TEXT NOT NULL,
    created_at INTEGER NOT NULL,
    PRIMARY KEY (upload_id, chunk_number)
);

-- ==========================================
-- KAAVAN MONITORING TABLES
-- ==========================================

-- System health records
CREATE TABLE IF NOT EXISTS kaavan_health (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER NOT NULL,
    files_status TEXT,
    database_status TEXT,
    cron_status TEXT,
    errors_status TEXT,
    backups_status TEXT,
    overall_score REAL NOT NULL
);

-- Monitoring alerts
CREATE TABLE IF NOT EXISTS kaavan_alerts (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    severity TEXT NOT NULL,
    message TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    resolved BOOLEAN DEFAULT 0,
    resolved_at INTEGER,
    metadata TEXT
);

-- ==========================================
-- TANTOR WEBSOCKET TABLES
-- ==========================================

-- WebSocket connections
CREATE TABLE IF NOT EXISTS tantor_connections (
    client_id TEXT PRIMARY KEY,
    handshake_complete BOOLEAN DEFAULT 0,
    last_ping INTEGER,
    joined_at INTEGER NOT NULL,
    channels TEXT,
    user_data TEXT
);

-- WebSocket messages
CREATE TABLE IF NOT EXISTS tantor_messages (
    id TEXT PRIMARY KEY,
    channel TEXT NOT NULL,
    message TEXT NOT NULL,
    sender TEXT NOT NULL,
    timestamp REAL NOT NULL,
    message_type TEXT DEFAULT 'chat',
    data TEXT
);

-- ==========================================
-- PEANUTS PERFORMANCE TABLES
-- ==========================================

-- Performance metrics
CREATE TABLE IF NOT EXISTS peanuts_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    response_times TEXT,
    memory_usage TEXT,
    db_query_times TEXT,
    error_rate REAL DEFAULT 0.0,
    concurrent_users INTEGER DEFAULT 0,
    cache_hit_rate REAL DEFAULT 0.0,
    last_updated INTEGER NOT NULL,
    performance_score REAL DEFAULT 0.0
);

-- Performance mode history
CREATE TABLE IF NOT EXISTS peanuts_mode_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mode TEXT NOT NULL,
    reason TEXT,
    score REAL NOT NULL,
    timestamp INTEGER NOT NULL
);

-- ==========================================
-- INDEXES FOR PERFORMANCE
-- ==========================================

-- Babar indexes
CREATE INDEX IF NOT EXISTS idx_babar_content_slug ON babar_content(slug);
CREATE INDEX IF NOT EXISTS idx_babar_content_author ON babar_content(author_id);
CREATE INDEX IF NOT EXISTS idx_babar_content_status ON babar_content(status);
CREATE INDEX IF NOT EXISTS idx_babar_versions_content ON babar_versions(content_id);

-- Horton indexes
CREATE INDEX IF NOT EXISTS idx_jobs_queue ON jobs(queue);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs(created_at);
CREATE INDEX IF NOT EXISTS idx_workers_status ON workers(status);

-- Satao indexes
CREATE INDEX IF NOT EXISTS idx_blocked_ips_expires ON blocked_ips(expires);
CREATE INDEX IF NOT EXISTS idx_security_events_ip ON security_events(ip);
CREATE INDEX IF NOT EXISTS idx_security_events_timestamp ON security_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_security_alerts_resolved ON security_alerts(resolved);

-- Theme analyzer indexes
CREATE INDEX IF NOT EXISTS idx_theme_analytics_theme ON theme_analytics(theme);
CREATE INDEX IF NOT EXISTS idx_theme_analytics_user ON theme_analytics(user_id);
CREATE INDEX IF NOT EXISTS idx_theme_analytics_timestamp ON theme_analytics(timestamp);
CREATE INDEX IF NOT EXISTS idx_theme_ab_tests_status ON theme_ab_tests(status);

-- Koshik indexes
CREATE INDEX IF NOT EXISTS idx_koshik_notifications_user ON koshik_notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_koshik_notifications_played ON koshik_notifications(played);

-- Jumbo indexes
CREATE INDEX IF NOT EXISTS idx_jumbo_uploads_status ON jumbo_uploads(status);
CREATE INDEX IF NOT EXISTS idx_jumbo_uploads_started_at ON jumbo_uploads(started_at);

-- Kaavan indexes
CREATE INDEX IF NOT EXISTS idx_kaavan_health_timestamp ON kaavan_health(timestamp);
CREATE INDEX IF NOT EXISTS idx_kaavan_alerts_resolved ON kaavan_alerts(resolved);

-- Tantor indexes
CREATE INDEX IF NOT EXISTS idx_tantor_connections_joined_at ON tantor_connections(joined_at);
CREATE INDEX IF NOT EXISTS idx_tantor_messages_channel ON tantor_messages(channel);
CREATE INDEX IF NOT EXISTS idx_tantor_messages_timestamp ON tantor_messages(timestamp);

-- Peanuts indexes
CREATE INDEX IF NOT EXISTS idx_peanuts_metrics_last_updated ON peanuts_metrics(last_updated);
CREATE INDEX IF NOT EXISTS idx_peanuts_mode_history_timestamp ON peanuts_mode_history(timestamp); 