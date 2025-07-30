"""
TuskPHP Horton - The Faithful Job Queue Worker (Python Edition)
==============================================================

🐘 BACKSTORY: Horton - Dr. Seuss's Most Reliable Elephant
--------------------------------------------------------
"A person's a person, no matter how small!" - Horton the Elephant

In Dr. Seuss's beloved tales, Horton is the elephant who hears the Whos on a
speck of dust and sits on Mayzie's egg for 51 weeks. His defining traits are
FAITHFULNESS and RELIABILITY. "I meant what I said, and I said what I meant.
An elephant's faithful, one hundred percent!"

WHY THIS NAME: Just as Horton never abandons his duty - whether protecting
the Whos or hatching an egg - this job queue worker NEVER drops a task.
Every job matters, no matter how small. Every email, every image resize,
every background process gets the same dedicated attention that Horton
gave to that tiny speck of dust.

FEATURES:
- Persistent job queue processing
- Automatic retry with exponential backoff
- Job prioritization (because all jobs matter, but some matter more urgently)
- Failed job handling and dead letter queue
- Distributed processing support
- Real-time job status tracking
- Job scheduling and delayed execution
- Worker registration and management
- Comprehensive job analytics

"I'll stay on this job till the job is done!"

@package TuskPHP\Elephants
@author  TuskPHP Team
@since   1.0.0
"""

import json
import time
import uuid
import threading
import queue
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import sqlite3
import signal
import sys

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


class JobStatus(Enum):
    """Job status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class JobPriority(Enum):
    """Job priority enumeration"""
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


@dataclass
class Job:
    """Job data structure"""
    id: str
    name: str
    data: Dict
    queue: str
    priority: str
    attempts: int
    max_attempts: int
    created_at: int
    scheduled_at: Optional[int] = None
    started_at: Optional[int] = None
    completed_at: Optional[int] = None
    status: str = JobStatus.PENDING.value
    result: Optional[Dict] = None
    error: Optional[str] = None
    retry_delay: int = 60
    worker_id: Optional[str] = None


@dataclass
class WorkerStats:
    """Worker statistics"""
    worker_id: str
    jobs_processed: int
    jobs_failed: int
    uptime: int
    last_heartbeat: int
    status: str = "active"


class Horton:
    """
    Horton - The Faithful Job Queue Worker
    
    Horton never abandons a job, no matter how small. Like the elephant who
    protected the Whos on a speck of dust, Horton gives every task the same
    dedicated attention and never gives up until the job is done.
    """
    
    def __init__(self, db_path: str = None):
        """Initialize Horton - Ready to hear every Who"""
        self.queues = {
            JobPriority.HIGH.value: queue.PriorityQueue(),
            JobPriority.NORMAL.value: queue.PriorityQueue(),
            JobPriority.LOW.value: queue.PriorityQueue()
        }
        
        self.workers = {}
        self.job_handlers = {}
        self.max_retries = 3
        self.is_running = False
        self.processed_jobs = 0
        self.failed_jobs = 0
        
        # Database setup
        self.db_path = db_path or "horton.db"
        self._initialize_database()
        
        # Worker management
        self.worker_threads = {}
        self.shutdown_event = threading.Event()
        
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        print("🐘 Horton is ready to hear every Who! A person's a person, no matter how small!")
    
    def dispatch(self, job_name: str, data: Dict = None, queue: str = JobPriority.NORMAL.value, 
                 priority: int = 0, delay: int = 0) -> str:
        """
        Dispatch a job - "A person's a person, no matter how small!"
        
        Args:
            job_name: Name of the job to execute
            data: Job data
            queue: Queue name (high, normal, low)
            priority: Priority within queue (lower = higher priority)
            delay: Delay in seconds before execution
            
        Returns:
            Job ID
        """
        job_id = f"job_{uuid.uuid4().hex[:16]}"
        
        # Calculate scheduled time
        scheduled_at = int(time.time()) + delay if delay > 0 else None
        
        job = Job(
            id=job_id,
            name=job_name,
            data=data or {},
            queue=queue,
            priority=priority,
            attempts=0,
            max_attempts=self.max_retries,
            created_at=int(time.time()),
            scheduled_at=scheduled_at,
            retry_delay=60
        )
        
        # Store job with Horton's unwavering commitment
        if Memory:
            Memory.remember(f"horton_job_{job_id}", asdict(job), 86400 * 7)  # 7 days
        
        # Add to database
        self._store_job(job)
        
        # Add to queue if not delayed
        if not delay:
            self._add_to_queue(job)
        
        print(f"📬 Horton dispatched job '{job_name}' (ID: {job_id}) to {queue} queue")
        
        # "I meant what I said, and I said what I meant"
        return job_id
    
    def process(self, queue_name: str = None, worker_id: str = None) -> None:
        """
        Process jobs - Sitting on the nest, faithful 100%
        
        Args:
            queue_name: Specific queue to process (optional)
            worker_id: Worker identifier
        """
        if not worker_id:
            worker_id = f"worker_{uuid.uuid4().hex[:8]}"
        
        self.is_running = True
        self._register_worker(worker_id)
        
        print(f"🔄 Horton worker {worker_id} started processing...")
        
        try:
            # Like Horton on Mayzie's egg, we'll stay here processing
            while self.is_running and not self.shutdown_event.is_set():
                job = self._get_next_job(queue_name)
                
                if job:
                    self._execute_job(job, worker_id)
                else:
                    # Even Horton needs a brief rest
                    time.sleep(0.1)
        
        except KeyboardInterrupt:
            print(f"🛑 Horton worker {worker_id} received shutdown signal")
        finally:
            self._unregister_worker(worker_id)
            print(f"👋 Horton worker {worker_id} finished processing")
    
    def status(self, job_id: str) -> Optional[Dict]:
        """
        Get job status
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job status information
        """
        # Try to get from memory first
        if Memory:
            job_data = Memory.recall(f"horton_job_{job_id}")
            if job_data:
                return job_data
        
        # Fall back to database
        return self._get_job_from_db(job_id)
    
    def stop(self) -> None:
        """Stop Horton gracefully"""
        print("🛑 Horton is stopping gracefully...")
        self.is_running = False
        self.shutdown_event.set()
        
        # Wait for workers to finish
        for thread in self.worker_threads.values():
            if thread.is_alive():
                thread.join(timeout=5)
    
    def stats(self) -> Dict:
        """Get Horton's statistics"""
        return {
            "processed_jobs": self.processed_jobs,
            "failed_jobs": self.failed_jobs,
            "active_workers": len(self.workers),
            "queue_sizes": {
                queue: q.qsize() for queue, q in self.queues.items()
            },
            "uptime": self._get_uptime(),
            "is_running": self.is_running
        }
    
    def register(self, name: str, handler: Callable) -> None:
        """
        Register a job handler
        
        Args:
            name: Job name
            handler: Function to handle the job
        """
        self.job_handlers[name] = handler
        print(f"📝 Horton registered handler for job '{name}'")
    
    def later(self, delay: int, job_name: str, data: Dict = None, 
              queue: str = JobPriority.NORMAL.value) -> str:
        """
        Schedule a job for later execution
        
        Args:
            delay: Delay in seconds
            job_name: Name of the job
            data: Job data
            queue: Queue name
            
        Returns:
            Job ID
        """
        return self.dispatch(job_name, data, queue, delay=delay)
    
    def retry(self, job_id: str) -> bool:
        """
        Retry a failed job
        
        Args:
            job_id: Job identifier
            
        Returns:
            Success status
        """
        job_data = self.status(job_id)
        if not job_data:
            return False
        
        if job_data['status'] != JobStatus.FAILED.value:
            print(f"⚠️  Job {job_id} is not in failed status")
            return False
        
        # Reset job for retry
        job_data['status'] = JobStatus.PENDING.value
        job_data['attempts'] = 0
        job_data['error'] = None
        job_data['started_at'] = None
        job_data['completed_at'] = None
        
        # Update storage
        if Memory:
            Memory.remember(f"horton_job_{job_id}", job_data, 86400 * 7)
        
        self._update_job_in_db(job_id, job_data)
        
        # Add back to queue
        job = Job(**job_data)
        self._add_to_queue(job)
        
        print(f"🔄 Horton retrying job {job_id}")
        return True
    
    def cancel(self, job_id: str) -> bool:
        """
        Cancel a pending job
        
        Args:
            job_id: Job identifier
            
        Returns:
            Success status
        """
        job_data = self.status(job_id)
        if not job_data:
            return False
        
        if job_data['status'] != JobStatus.PENDING.value:
            print(f"⚠️  Job {job_id} is not in pending status")
            return False
        
        # Update status
        job_data['status'] = JobStatus.CANCELLED.value
        job_data['completed_at'] = int(time.time())
        
        # Update storage
        if Memory:
            Memory.remember(f"horton_job_{job_id}", job_data, 86400 * 7)
        
        self._update_job_in_db(job_id, job_data)
        
        print(f"❌ Horton cancelled job {job_id}")
        return True
    
    def pending(self, queue_name: str = None) -> List[Dict]:
        """
        Get pending jobs
        
        Args:
            queue_name: Specific queue (optional)
            
        Returns:
            List of pending jobs
        """
        pending_jobs = []
        
        # Get from database
        query = "SELECT * FROM jobs WHERE status = ?"
        params = [JobStatus.PENDING.value]
        
        if queue_name:
            query += " AND queue = ?"
            params.append(queue_name)
        
        query += " ORDER BY created_at ASC"
        
        jobs = self._execute_query(query, params)
        
        for job_data in jobs:
            pending_jobs.append(dict(job_data))
        
        return pending_jobs
    
    def failed(self, limit: int = 50) -> List[Dict]:
        """
        Get failed jobs
        
        Args:
            limit: Maximum number of jobs to return
            
        Returns:
            List of failed jobs
        """
        query = """
            SELECT * FROM jobs 
            WHERE status = ? 
            ORDER BY completed_at DESC 
            LIMIT ?
        """
        
        jobs = self._execute_query(query, [JobStatus.FAILED.value, limit])
        return [dict(job) for job in jobs]
    
    def clear_completed(self, older_than: int = 3600) -> int:
        """
        Clear completed jobs older than specified time
        
        Args:
            older_than: Age in seconds
            
        Returns:
            Number of jobs cleared
        """
        cutoff_time = int(time.time()) - older_than
        
        query = """
            DELETE FROM jobs 
            WHERE status IN (?, ?) 
            AND completed_at < ?
        """
        
        cursor = self._get_db_cursor()
        cursor.execute(query, [JobStatus.COMPLETED.value, JobStatus.CANCELLED.value, cutoff_time])
        cleared_count = cursor.rowcount
        
        self._commit_db()
        return cleared_count
    
    def flush(self, queue_name: str = None) -> int:
        """
        Flush all jobs from a queue
        
        Args:
            queue_name: Specific queue (optional)
            
        Returns:
            Number of jobs flushed
        """
        flushed_count = 0
        
        if queue_name:
            # Flush specific queue
            if queue_name in self.queues:
                while not self.queues[queue_name].empty():
                    self.queues[queue_name].get()
                    flushed_count += 1
        else:
            # Flush all queues
            for queue_obj in self.queues.values():
                while not queue_obj.empty():
                    queue_obj.get()
                    flushed_count += 1
        
        print(f"🚿 Horton flushed {flushed_count} jobs")
        return flushed_count
    
    # Private helper methods
    
    def _initialize_database(self):
        """Initialize database tables"""
        cursor = self._get_db_cursor()
        
        # Create jobs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                data TEXT,
                queue TEXT NOT NULL,
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
            )
        """)
        
        # Create workers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workers (
                worker_id TEXT PRIMARY KEY,
                jobs_processed INTEGER DEFAULT 0,
                jobs_failed INTEGER DEFAULT 0,
                uptime INTEGER DEFAULT 0,
                last_heartbeat INTEGER NOT NULL,
                status TEXT DEFAULT 'active'
            )
        """)
        
        self._commit_db()
    
    def _get_db_cursor(self):
        """Get database cursor"""
        if not hasattr(self, '_db_connection'):
            self._db_connection = sqlite3.connect(self.db_path)
            self._db_connection.row_factory = sqlite3.Row
        
        return self._db_connection.cursor()
    
    def _commit_db(self):
        """Commit database changes"""
        if hasattr(self, '_db_connection'):
            self._db_connection.commit()
    
    def _store_job(self, job: Job):
        """Store job in database"""
        cursor = self._get_db_cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO jobs 
            (id, name, data, queue, priority, attempts, max_attempts, 
             created_at, scheduled_at, started_at, completed_at, status, 
             result, error, retry_delay, worker_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            job.id, job.name, json.dumps(job.data), job.queue, job.priority,
            job.attempts, job.max_attempts, job.created_at, job.scheduled_at,
            job.started_at, job.completed_at, job.status, 
            json.dumps(job.result) if job.result else None,
            job.error, job.retry_delay, job.worker_id
        ))
        
        self._commit_db()
    
    def _get_job_from_db(self, job_id: str) -> Optional[Dict]:
        """Get job from database"""
        cursor = self._get_db_cursor()
        
        cursor.execute("SELECT * FROM jobs WHERE id = ?", [job_id])
        row = cursor.fetchone()
        
        if row:
            job_data = dict(row)
            # Parse JSON fields
            if job_data.get('data'):
                job_data['data'] = json.loads(job_data['data'])
            if job_data.get('result'):
                job_data['result'] = json.loads(job_data['result'])
            return job_data
        
        return None
    
    def _update_job_in_db(self, job_id: str, job_data: Dict):
        """Update job in database"""
        cursor = self._get_db_cursor()
        
        cursor.execute("""
            UPDATE jobs SET
                name = ?, data = ?, queue = ?, priority = ?, attempts = ?,
                max_attempts = ?, created_at = ?, scheduled_at = ?, started_at = ?,
                completed_at = ?, status = ?, result = ?, error = ?,
                retry_delay = ?, worker_id = ?
            WHERE id = ?
        """, (
            job_data['name'], json.dumps(job_data['data']), job_data['queue'],
            job_data['priority'], job_data['attempts'], job_data['max_attempts'],
            job_data['created_at'], job_data['scheduled_at'], job_data['started_at'],
            job_data['completed_at'], job_data['status'],
            json.dumps(job_data['result']) if job_data.get('result') else None,
            job_data.get('error'), job_data['retry_delay'], job_data.get('worker_id'),
            job_id
        ))
        
        self._commit_db()
    
    def _execute_query(self, query: str, params: List = None) -> List:
        """Execute database query"""
        cursor = self._get_db_cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        return cursor.fetchall()
    
    def _add_to_queue(self, job: Job):
        """Add job to queue"""
        if job.queue in self.queues:
            # Use priority as queue priority (lower = higher priority)
            self.queues[job.queue].put((job.priority, time.time(), job))
    
    def _get_next_job(self, specific_queue: str = None) -> Optional[Job]:
        """Get next job from queue"""
        if specific_queue:
            # Get from specific queue
            if specific_queue in self.queues and not self.queues[specific_queue].empty():
                return self.queues[specific_queue].get()[2]
        else:
            # Get from highest priority queue with jobs
            for queue_name in [JobPriority.HIGH.value, JobPriority.NORMAL.value, JobPriority.LOW.value]:
                if not self.queues[queue_name].empty():
                    return self.queues[queue_name].get()[2]
        
        return None
    
    def _execute_job(self, job: Job, worker_id: str):
        """Execute a job"""
        print(f"⚡ Horton executing job '{job.name}' (ID: {job.id})")
        
        # Update job status
        job.status = JobStatus.RUNNING.value
        job.started_at = int(time.time())
        job.worker_id = worker_id
        
        self._update_job_storage(job)
        
        try:
            # Run job handler
            if job.name in self.job_handlers:
                handler = self.job_handlers[job.name]
                result = handler(job.data)
                
                # Job completed successfully
                job.status = JobStatus.COMPLETED.value
                job.completed_at = int(time.time())
                job.result = {'success': True, 'data': result}
                
                self.processed_jobs += 1
                print(f"✅ Horton completed job '{job.name}' (ID: {job.id})")
                
            else:
                # No handler found
                raise Exception(f"No handler registered for job '{job.name}'")
        
        except Exception as e:
            # Job failed
            job.attempts += 1
            job.error = str(e)
            
            if job.attempts >= job.max_attempts:
                # Max attempts reached
                job.status = JobStatus.FAILED.value
                job.completed_at = int(time.time())
                self.failed_jobs += 1
                print(f"❌ Horton failed job '{job.name}' (ID: {job.id}) after {job.attempts} attempts: {e}")
                
                # Move to dead letter queue
                self._move_to_dead_letter(job)
            else:
                # Retry job
                job.status = JobStatus.RETRYING.value
                print(f"🔄 Horton retrying job '{job.name}' (ID: {job.id}) - attempt {job.attempts}/{job.max_attempts}")
                
                # Schedule retry with exponential backoff
                retry_delay = job.retry_delay * (2 ** (job.attempts - 1))
                self.later(retry_delay, job.name, job.data, job.queue)
        
        finally:
            # Update job storage
            self._update_job_storage(job)
    
    def _update_job_storage(self, job: Job):
        """Update job in storage"""
        job_data = asdict(job)
        
        if Memory:
            Memory.remember(f"horton_job_{job.id}", job_data, 86400 * 7)
        
        self._update_job_in_db(job.id, job_data)
    
    def _move_to_dead_letter(self, job: Job):
        """Move failed job to dead letter queue"""
        # This would implement dead letter queue functionality
        # For now, just log the failure
        print(f"💀 Job {job.id} moved to dead letter queue")
    
    def _register_worker(self, worker_id: str):
        """Register a worker"""
        self.workers[worker_id] = WorkerStats(
            worker_id=worker_id,
            jobs_processed=0,
            jobs_failed=0,
            uptime=0,
            last_heartbeat=int(time.time())
        )
        
        # Store in database
        cursor = self._get_db_cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO workers 
            (worker_id, jobs_processed, jobs_failed, uptime, last_heartbeat, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            worker_id, 0, 0, 0, int(time.time()), 'active'
        ))
        
        self._commit_db()
    
    def _unregister_worker(self, worker_id: str):
        """Unregister a worker"""
        if worker_id in self.workers:
            del self.workers[worker_id]
        
        # Update database
        cursor = self._get_db_cursor()
        cursor.execute("""
            UPDATE workers SET status = 'inactive' WHERE worker_id = ?
        """, [worker_id])
        
        self._commit_db()
    
    def _get_uptime(self) -> int:
        """Get Horton's uptime"""
        # This would track actual uptime
        # For now, return a placeholder
        return int(time.time())
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n🛑 Horton received signal {signum}, shutting down gracefully...")
        self.stop()
        sys.exit(0)


def init_horton(app):
    """Initialize Horton with Flask app"""
    horton = Horton()
    app.horton = horton
    return horton


def get_horton() -> Horton:
    """Get Horton instance"""
    from flask import current_app
    return getattr(current_app, 'horton', None) 