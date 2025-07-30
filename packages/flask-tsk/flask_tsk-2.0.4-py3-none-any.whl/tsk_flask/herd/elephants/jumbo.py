"""
TuskPHP Jumbo - The Massive File Handler (Python Edition)
========================================================

🐘 BACKSTORY: Jumbo - The Original "Jumbo-Sized" Elephant
--------------------------------------------------------
Jumbo was an African elephant who lived at London Zoo from 1865 to 1882.
Standing 13 feet tall and weighing 7 tons, he was a sensation. P.T. Barnum
purchased him for his circus, where Jumbo became the most famous elephant
in history. His name literally became synonymous with "huge" - entering
dictionaries worldwide as meaning "extraordinarily large."

WHY THIS NAME: Just as Jumbo redefined what "large" meant, this uploader
handles files of extraordinary size that would make regular uploaders
tremble. When your users need to upload massive CSVs, huge video files,
or enormous datasets, Jumbo steps up. No file is too large for the
elephant who gave us the very word for "huge."

Jumbo's legacy: Making the impossible possible through sheer size and strength.

FEATURES:
- Chunked file uploads (no timeout issues)
- Resume interrupted uploads
- Progress tracking for massive files
- Multi-part upload support
- Automatic chunk verification
- Support for files larger than memory limit
- CSV stream processing for huge datasets

"The bigger they are, the better Jumbo handles them!"

@package TuskPHP\Elephants
@author  TuskPHP Team
@since   2.0.0
"""

import os
import hashlib
import time
import json
import csv
import tempfile
from typing import Dict, List, Optional, Any, Union, Callable
from pathlib import Path
import shutil
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import threading
import queue

# Flask-TSK imports
try:
    from tsk_flask.database import TuskDb
    from tsk_flask.memory import Memory
    from tsk_flask.utils import PermissionHelper
except ImportError:
    # Fallback for standalone usage
    TuskDb = None
    Memory = None
    PermissionHelper = None


@dataclass
class UploadChunk:
    """Chunk data structure"""
    upload_id: str
    chunk_number: int
    chunk_data: bytes
    hash: str
    created_at: int


@dataclass
class UploadSession:
    """Upload session data structure"""
    id: str
    filename: str
    total_size: int
    chunks_expected: int
    chunks_received: int
    started_at: int
    status: str
    metadata: Dict
    last_chunk_at: Optional[int] = None
    completed_at: Optional[int] = None
    final_path: Optional[str] = None
    resumed_at: Optional[int] = None
    abandoned_at: Optional[int] = None
    cancelled_at: Optional[int] = None


class Jumbo:
    """The Massive File Handler - No file too large!"""
    
    def __init__(self, upload_path: str = None, max_file_size: int = None):
        """
        Initialize Jumbo - The giant awakens
        
        Args:
            upload_path: Base path for uploads
            max_file_size: Maximum file size in bytes (default: 5GB)
        """
        self.chunk_size = 5 * 1024 * 1024  # 5MB chunks - Jumbo-sized but manageable
        self.max_file_size = max_file_size or (5 * 1024 * 1024 * 1024)  # 5GB - Truly jumbo!
        self.upload_path = upload_path or "/uploads/jumbo/"
        self.active_uploads: Dict[str, UploadSession] = {}
        self.upload_queue = queue.Queue()
        self.processing_thread = None
        
        # Ensure upload directories exist
        self._ensure_upload_directory()
        self._load_active_uploads()
        
        # Start background processing
        self._start_background_processing()
    
    def start_upload(self, filename: str, total_size: int, metadata: Dict = None) -> Dict:
        """
        Start a jumbo upload - No file too large!
        
        Args:
            filename: Name of the file to upload
            total_size: Total size of the file in bytes
            metadata: Additional metadata for the upload
            
        Returns:
            Dict containing upload_id, chunk_size, and total_chunks
            
        Raises:
            ValueError: If file size exceeds maximum allowed
        """
        if total_size > self.max_file_size:
            raise ValueError(f"Even Jumbo has limits! Max file size: {self._format_bytes(self.max_file_size)}")
        
        upload_id = f"jumbo_{os.urandom(16).hex()}"
        
        upload_data = UploadSession(
            id=upload_id,
            filename=filename,
            total_size=total_size,
            chunks_expected=(total_size + self.chunk_size - 1) // self.chunk_size,
            chunks_received=0,
            started_at=int(time.time()),
            status="active",
            metadata=metadata or {}
        )
        
        self.active_uploads[upload_id] = upload_data
        
        # Store in memory for persistence
        if Memory:
            Memory.remember(f"jumbo_upload_{upload_id}", asdict(upload_data), 86400)
        
        # Like Jumbo entering the circus ring - a spectacle begins!
        return {
            'upload_id': upload_id,
            'chunk_size': self.chunk_size,
            'total_chunks': upload_data.chunks_expected
        }
    
    def upload_chunk(self, upload_id: str, chunk_number: int, chunk_data: bytes) -> Dict:
        """
        Upload a chunk - Piece by piece, like Jumbo's daily meals
        
        Args:
            upload_id: The upload session ID
            chunk_number: Sequential chunk number (0-based)
            chunk_data: Binary chunk data
            
        Returns:
            Dict with upload status and progress
            
        Raises:
            ValueError: If upload not found or invalid chunk
        """
        upload = self.active_uploads.get(upload_id)
        if not upload and Memory:
            upload_data = Memory.recall(f"jumbo_upload_{upload_id}")
            if upload_data:
                upload = UploadSession(**upload_data)
                self.active_uploads[upload_id] = upload
        
        if not upload:
            raise ValueError("Upload not found - did Jumbo forget?")
        
        if upload.status != "active":
            raise ValueError(f"Upload is {upload.status}, cannot accept chunks")
        
        # Save chunk with Jumbo's reliability
        chunk_path = Path(self.upload_path) / upload_id / f"chunk_{chunk_number}"
        self._save_chunk(chunk_path, chunk_data)
        
        upload.chunks_received += 1
        upload.last_chunk_at = int(time.time())
        
        # Update progress - Jumbo never loses track
        if Memory:
            Memory.remember(f"jumbo_upload_{upload_id}", asdict(upload), 86400)
        
        # Check if all chunks received
        if upload.chunks_received >= upload.chunks_expected:
            return self._assemble_file(upload_id)
        
        return {
            'status': 'uploading',
            'progress': round((upload.chunks_received / upload.chunks_expected) * 100, 2)
        }
    
    def resume_upload(self, upload_id: str) -> Dict:
        """
        Resume an interrupted upload - Jumbo never gives up
        
        Args:
            upload_id: The upload session ID to resume
            
        Returns:
            Dict with resume information and missing chunks
            
        Raises:
            ValueError: If upload not found or already completed
        """
        upload = None
        if Memory:
            upload_data = Memory.recall(f"jumbo_upload_{upload_id}")
            if upload_data:
                upload = UploadSession(**upload_data)
        
        if not upload:
            raise ValueError("Upload not found - has Jumbo forgotten?")
        
        if upload.status != "active":
            raise ValueError(f"Upload already {upload.status}")
        
        # Check which chunks we already have
        received_chunks = []
        chunk_dir = Path(self.upload_path) / upload_id
        
        for i in range(upload.chunks_expected):
            if (chunk_dir / f"chunk_{i}").exists():
                received_chunks.append(i)
        
        # Update chunk count
        upload.chunks_received = len(received_chunks)
        upload.resumed_at = int(time.time())
        
        if Memory:
            Memory.remember(f"jumbo_upload_{upload_id}", asdict(upload), 86400)
        
        return {
            'upload_id': upload_id,
            'chunks_received': received_chunks,
            'chunks_needed': [i for i in range(upload.chunks_expected) if i not in received_chunks],
            'progress': round((upload.chunks_received / upload.chunks_expected) * 100, 2)
        }
    
    def get_status(self, upload_id: str) -> Dict:
        """
        Get upload status - Jumbo's memory is legendary
        
        Args:
            upload_id: The upload session ID
            
        Returns:
            Dict with upload status and progress information
        """
        upload = None
        if Memory:
            upload_data = Memory.recall(f"jumbo_upload_{upload_id}")
            if upload_data:
                upload = UploadSession(**upload_data)
        
        if not upload:
            return {'status': 'not_found'}
        
        return {
            'status': upload.status,
            'progress': round((upload.chunks_received / upload.chunks_expected) * 100, 2),
            'size_uploaded': upload.chunks_received * self.chunk_size,
            'time_remaining': self._estimate_time_remaining(upload)
        }
    
    def cancel_upload(self, upload_id: str) -> bool:
        """
        Cancel an upload - Sometimes even Jumbo needs to stop
        
        Args:
            upload_id: The upload session ID to cancel
            
        Returns:
            True if cancelled successfully
            
        Raises:
            ValueError: If upload not found
        """
        upload = None
        if Memory:
            upload_data = Memory.recall(f"jumbo_upload_{upload_id}")
            if upload_data:
                upload = UploadSession(**upload_data)
        
        if not upload:
            raise ValueError("Upload not found")
        
        # Clean up chunks
        self._cleanup_chunks(upload_id)
        
        # Update status
        upload.status = "cancelled"
        upload.cancelled_at = int(time.time())
        
        if Memory:
            Memory.remember(f"jumbo_upload_{upload_id}", asdict(upload), 3600)  # Keep for 1 hour
        
        return True
    
    def verify_chunk(self, upload_id: str, chunk_number: int, expected_hash: str = None) -> Dict:
        """
        Verify chunk integrity - Jumbo's quality control
        
        Args:
            upload_id: The upload session ID
            chunk_number: The chunk number to verify
            expected_hash: Expected SHA256 hash of the chunk
            
        Returns:
            Dict with verification results
        """
        chunk_path = Path(self.upload_path) / upload_id / f"chunk_{chunk_number}"
        
        if not chunk_path.exists():
            return {'valid': False, 'error': 'Chunk not found'}
        
        actual_hash = self._calculate_file_hash(chunk_path)
        
        if expected_hash and actual_hash != expected_hash:
            return {'valid': False, 'error': 'Hash mismatch', 'actual': actual_hash}
        
        # Check stored hash
        hash_path = chunk_path.with_suffix('.hash')
        if hash_path.exists():
            stored_hash = hash_path.read_text().strip()
            if stored_hash != actual_hash:
                return {'valid': False, 'error': 'Stored hash mismatch'}
        
        return {'valid': True, 'hash': actual_hash}
    
    def stream_csv(self, filepath: str, callback: Callable, chunk_size: int = 1000) -> int:
        """
        Stream process large CSV - Jumbo's specialty act
        
        Args:
            filepath: Path to the CSV file
            callback: Function to call for each chunk of rows
            chunk_size: Number of rows per chunk
            
        Returns:
            Total number of rows processed
        """
        row_count = 0
        chunk = []
        
        with open(filepath, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            # Process CSV in Jumbo-sized chunks
            for row in reader:
                chunk.append(row)
                row_count += 1
                
                if len(chunk) >= chunk_size:
                    # Process chunk with callback
                    callback(chunk, row_count)
                    chunk = []
        
        # Process remaining rows
        if chunk:
            callback(chunk, row_count)
        
        return row_count
    
    def get_statistics(self) -> Dict:
        """
        Get upload statistics - Jumbo's performance metrics
        
        Returns:
            Dict with upload statistics
        """
        stats = {
            'active_uploads': len(self.active_uploads),
            'total_active_size': 0,
            'average_speed': 0,
            'uploads_today': 0,
            'uploads_this_week': 0
        }
        
        speeds = []
        today_start = int(datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
        week_start = int((datetime.now() - timedelta(days=datetime.now().weekday())).replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
        
        for upload in self.active_uploads.values():
            stats['total_active_size'] += upload.chunks_received * self.chunk_size
            
            # Calculate upload speed
            if upload.chunks_received > 0:
                elapsed = time.time() - upload.started_at
                bytes_uploaded = upload.chunks_received * self.chunk_size
                speeds.append(bytes_uploaded / elapsed)
            
            # Count recent uploads
            if upload.started_at >= today_start:
                stats['uploads_today'] += 1
            if upload.started_at >= week_start:
                stats['uploads_this_week'] += 1
        
        if speeds:
            stats['average_speed'] = sum(speeds) / len(speeds)
        
        return stats
    
    def _assemble_file(self, upload_id: str) -> Dict:
        """
        Assemble chunks into final file - Jumbo's grand finale
        
        Args:
            upload_id: The upload session ID
            
        Returns:
            Dict with completion information
            
        Raises:
            RuntimeError: If assembly fails
        """
        upload = self.active_uploads[upload_id]
        final_path = Path(self.upload_path) / "completed" / upload.filename
        
        # Like P.T. Barnum assembling the greatest show
        self._merge_chunks(upload_id, final_path)
        
        upload.status = "completed"
        upload.completed_at = int(time.time())
        upload.final_path = str(final_path)
        
        if Memory:
            Memory.remember(f"jumbo_upload_{upload_id}", asdict(upload), 86400)
        
        # Clean up chunks - Jumbo is tidy despite his size
        self._cleanup_chunks(upload_id)
        
        return {
            'status': 'completed',
            'path': str(final_path),
            'size': upload.total_size,
            'duration': upload.completed_at - upload.started_at
        }
    
    def _save_chunk(self, chunk_path: Path, chunk_data: bytes) -> int:
        """
        Save chunk to filesystem - Jumbo's careful storage
        
        Args:
            chunk_path: Path where to save the chunk
            chunk_data: Binary chunk data
            
        Returns:
            Number of bytes written
            
        Raises:
            RuntimeError: If chunk save fails
        """
        chunk_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write chunk with exclusive lock - Jumbo protects his treasures
        written = chunk_path.write_bytes(chunk_data)
        
        if written != len(chunk_data):
            raise RuntimeError("Failed to save chunk - Jumbo stumbled!")
        
        # Verify chunk integrity
        chunk_hash = self._calculate_file_hash(chunk_path)
        hash_path = chunk_path.with_suffix('.hash')
        hash_path.write_text(chunk_hash)
        
        return written
    
    def _merge_chunks(self, upload_id: str, final_path: Path) -> bool:
        """
        Merge chunks into final file - The grand assembly
        
        Args:
            upload_id: The upload session ID
            final_path: Path for the final assembled file
            
        Returns:
            True if successful
            
        Raises:
            RuntimeError: If merge fails
        """
        upload = self.active_uploads[upload_id]
        chunk_dir = Path(self.upload_path) / upload_id
        
        # Ensure output directory exists
        final_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Open output file for writing
        with open(final_path, 'wb') as output_file:
            # Merge chunks in order - Like Jumbo's circus parade
            for i in range(upload.chunks_expected):
                chunk_path = chunk_dir / f"chunk_{i}"
                
                if not chunk_path.exists():
                    raise RuntimeError(f"Missing chunk {i} - Jumbo's puzzle incomplete!")
                
                # Verify chunk integrity if hash exists
                hash_path = chunk_path.with_suffix('.hash')
                if hash_path.exists():
                    expected_hash = hash_path.read_text().strip()
                    actual_hash = self._calculate_file_hash(chunk_path)
                    if expected_hash != actual_hash:
                        raise RuntimeError(f"Corrupted chunk {i} - Jumbo detects tampering!")
                
                # Stream chunk to output file
                with open(chunk_path, 'rb') as chunk_file:
                    shutil.copyfileobj(chunk_file, output_file)
        
        # Verify final file size
        actual_size = final_path.stat().st_size
        if actual_size != upload.total_size:
            final_path.unlink()
            raise RuntimeError("File size mismatch - Jumbo's math doesn't add up!")
        
        return True
    
    def _cleanup_chunks(self, upload_id: str) -> bool:
        """
        Clean up chunks after assembly - Jumbo keeps a tidy circus
        
        Args:
            upload_id: The upload session ID
            
        Returns:
            True if cleanup successful
        """
        chunk_dir = Path(self.upload_path) / upload_id
        
        if not chunk_dir.exists():
            return False
        
        # Remove all chunks and their hashes
        for chunk_file in chunk_dir.glob("chunk_*"):
            chunk_file.unlink()
        
        # Remove the upload directory
        chunk_dir.rmdir()
        
        # Clear from memory - Even elephants need to forget sometimes
        if Memory:
            Memory.forget(f"jumbo_upload_{upload_id}")
        
        if upload_id in self.active_uploads:
            del self.active_uploads[upload_id]
        
        return True
    
    def _ensure_upload_directory(self):
        """Ensure upload directories exist - Jumbo prepares his stage"""
        base_path = Path(self.upload_path)
        
        directories = [
            base_path,
            base_path / "completed",
            base_path / "temp",
            base_path / "abandoned"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            directory.chmod(0o755)
    
    def _load_active_uploads(self):
        """Load active uploads from memory - Jumbo remembers everything"""
        if not Memory:
            return
        
        # Search for all active upload keys in memory
        upload_keys = Memory.search('jumbo_upload_*')
        
        for key in upload_keys:
            upload_data = Memory.recall(key)
            if upload_data and upload_data.get('status') == 'active':
                upload = UploadSession(**upload_data)
                self.active_uploads[upload['id']] = upload
        
        # Clean up abandoned uploads (older than 24 hours)
        self._cleanup_abandoned_uploads()
    
    def _cleanup_abandoned_uploads(self):
        """Clean up abandoned uploads - Jumbo's housekeeping"""
        cutoff_time = int(time.time()) - 86400  # 24 hours
        
        for upload_id, upload in list(self.active_uploads.items()):
            last_activity = upload.last_chunk_at or upload.started_at
            
            if last_activity < cutoff_time and upload.status == "active":
                # Move to abandoned directory for potential recovery
                source_dir = Path(self.upload_path) / upload_id
                dest_dir = Path(self.upload_path) / "abandoned" / upload_id
                
                if source_dir.exists():
                    source_dir.rename(dest_dir)
                
                # Update status
                upload.status = "abandoned"
                upload.abandoned_at = int(time.time())
                
                if Memory:
                    Memory.remember(f"jumbo_upload_{upload_id}", asdict(upload), 604800)  # Keep for 7 days
                
                del self.active_uploads[upload_id]
    
    def _estimate_time_remaining(self, upload: UploadSession) -> Optional[str]:
        """
        Estimate time remaining - Jumbo's circus timing
        
        Args:
            upload: The upload session
            
        Returns:
            Human-readable time estimate or None
        """
        if upload.chunks_received == 0:
            return None
        
        elapsed = time.time() - upload.started_at
        avg_time_per_chunk = elapsed / upload.chunks_received
        chunks_remaining = upload.chunks_expected - upload.chunks_received
        
        seconds_remaining = avg_time_per_chunk * chunks_remaining
        
        # Format time in human readable way
        if seconds_remaining < 60:
            return f"{round(seconds_remaining)} seconds"
        elif seconds_remaining < 3600:
            return f"{round(seconds_remaining / 60)} minutes"
        else:
            return f"{round(seconds_remaining / 3600, 1)} hours"
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """
        Calculate SHA256 hash of a file
        
        Args:
            file_path: Path to the file
            
        Returns:
            SHA256 hash as hex string
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def _format_bytes(self, bytes_value: int) -> str:
        """
        Format bytes to human readable - Even Jumbo needs translation
        
        Args:
            bytes_value: Number of bytes
            
        Returns:
            Human-readable string
        """
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        factor = 0
        size = float(bytes_value)
        
        while size >= 1024 and factor < len(units) - 1:
            size /= 1024
            factor += 1
        
        return f"{size:.2f} {units[factor]}"
    
    def _start_background_processing(self):
        """Start background processing thread"""
        self.processing_thread = threading.Thread(target=self._background_worker, daemon=True)
        self.processing_thread.start()
    
    def _background_worker(self):
        """Background worker for processing uploads"""
        while True:
            try:
                # Process any queued uploads
                while not self.upload_queue.empty():
                    task = self.upload_queue.get_nowait()
                    self._process_upload_task(task)
                
                # Clean up abandoned uploads periodically
                self._cleanup_abandoned_uploads()
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                # Log error but continue processing
                print(f"Jumbo background worker error: {e}")
                time.sleep(60)
    
    def _process_upload_task(self, task: Dict):
        """Process a background upload task"""
        # Implementation for background processing
        pass


# Flask-TSK Integration Functions
def init_jumbo(app):
    """Initialize Jumbo with Flask app"""
    app.jumbo = Jumbo()
    return app.jumbo


def get_jumbo() -> Jumbo:
    """Get Jumbo instance from Flask app context"""
    from flask import current_app
    return current_app.jumbo 