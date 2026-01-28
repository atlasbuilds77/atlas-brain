"""
Atlas Eyes - Event Database
Persistent storage for health monitoring events (heartbeat, tremor, motion)
"""

import sqlite3
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import threading
from queue import Queue
from contextlib import contextmanager


class EventStore:
    """
    SQLite-based event store for health monitoring data
    Thread-safe with async writes to prevent blocking
    """
    
    def __init__(self, db_path: str = "motion_events.db", retention_days: int = 30):
        """
        Initialize event store
        
        Args:
            db_path: Path to SQLite database file
            retention_days: Number of days to keep events (default 30)
        """
        self.db_path = Path(db_path).expanduser()
        self.retention_days = retention_days
        
        # Async write queue
        self.write_queue = Queue(maxsize=1000)
        self.writer_thread = None
        self.running = False
        
        # Thread-local connections for thread safety
        self._local = threading.local()
        
        # Initialize database
        self._init_database()
        
    def _get_connection(self) -> sqlite3.Connection:
        """Get thread-local database connection"""
        if not hasattr(self._local, 'conn'):
            self._local.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn
    
    @contextmanager
    def _get_cursor(self):
        """Context manager for database cursor"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
    
    def _init_database(self):
        """Create database schema if not exists"""
        with self._get_cursor() as cursor:
            # Main events table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    event_type TEXT NOT NULL,
                    value REAL,
                    confidence REAL,
                    metadata TEXT,
                    created_at REAL DEFAULT (strftime('%s', 'now'))
                )
            """)
            
            # Indexes for fast queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON events(timestamp DESC)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_event_type 
                ON events(event_type, timestamp DESC)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_created_at 
                ON events(created_at DESC)
            """)
            
            # Summary statistics table (for fast aggregate queries)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS event_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL UNIQUE,
                    event_type TEXT NOT NULL,
                    count INTEGER DEFAULT 0,
                    avg_value REAL,
                    min_value REAL,
                    max_value REAL,
                    avg_confidence REAL,
                    updated_at REAL DEFAULT (strftime('%s', 'now'))
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_stats_date 
                ON event_stats(date DESC, event_type)
            """)
    
    def start_writer(self):
        """Start async writer thread"""
        if self.running:
            return
        
        self.running = True
        self.writer_thread = threading.Thread(target=self._write_worker, daemon=True)
        self.writer_thread.start()
    
    def stop_writer(self):
        """Stop async writer thread"""
        self.running = False
        if self.writer_thread:
            self.writer_thread.join(timeout=5)
    
    def _write_worker(self):
        """Background worker for async writes"""
        while self.running:
            try:
                # Get batch of events (wait up to 1 second)
                events = []
                timeout = 1.0
                
                try:
                    event = self.write_queue.get(timeout=timeout)
                    events.append(event)
                    
                    # Drain queue for batch insert (up to 100 events)
                    while not self.write_queue.empty() and len(events) < 100:
                        events.append(self.write_queue.get_nowait())
                
                except:
                    continue
                
                # Batch insert
                if events:
                    self._batch_insert(events)
                
            except Exception as e:
                print(f"Error in write worker: {e}")
                time.sleep(1)
    
    def _batch_insert(self, events: List[Dict]):
        """Insert multiple events in a single transaction"""
        with self._get_cursor() as cursor:
            for event in events:
                cursor.execute("""
                    INSERT INTO events (timestamp, event_type, value, confidence, metadata)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    event['timestamp'],
                    event['event_type'],
                    event.get('value'),
                    event.get('confidence'),
                    json.dumps(event.get('metadata', {}))
                ))
    
    def log_event(
        self,
        event_type: str,
        value: Optional[float] = None,
        confidence: Optional[float] = None,
        metadata: Optional[Dict] = None,
        timestamp: Optional[float] = None,
        async_write: bool = True
    ) -> int:
        """
        Log a health monitoring event
        
        Args:
            event_type: Type of event ('heartbeat', 'tremor', 'motion_spike', 'anomaly')
            value: Numeric value (BPM for heartbeat, Hz for tremor, etc.)
            confidence: Confidence score (0-1)
            metadata: Additional JSON metadata
            timestamp: Event timestamp (uses current time if None)
            async_write: Use async queue (True) or write immediately (False)
        
        Returns:
            Event ID (or 0 for async writes)
        """
        if timestamp is None:
            timestamp = time.time()
        
        event = {
            'timestamp': timestamp,
            'event_type': event_type,
            'value': value,
            'confidence': confidence,
            'metadata': metadata or {}
        }
        
        if async_write and self.running:
            # Add to queue for background write
            try:
                self.write_queue.put_nowait(event)
                return 0  # ID not available for async writes
            except:
                # Queue full, fall back to sync write
                pass
        
        # Synchronous write
        with self._get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO events (timestamp, event_type, value, confidence, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (
                event['timestamp'],
                event['event_type'],
                event.get('value'),
                event.get('confidence'),
                json.dumps(event.get('metadata', {}))
            ))
            return cursor.lastrowid
    
    def query_recent(
        self,
        event_type: Optional[str] = None,
        limit: int = 100,
        min_confidence: Optional[float] = None
    ) -> List[Dict]:
        """
        Query recent events
        
        Args:
            event_type: Filter by event type (None for all)
            limit: Maximum number of events to return
            min_confidence: Minimum confidence threshold
        
        Returns:
            List of event dictionaries
        """
        with self._get_cursor() as cursor:
            query = "SELECT * FROM events WHERE 1=1"
            params = []
            
            if event_type:
                query += " AND event_type = ?"
                params.append(event_type)
            
            if min_confidence is not None:
                query += " AND confidence >= ?"
                params.append(min_confidence)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [self._row_to_dict(row) for row in rows]
    
    def get_history(
        self,
        event_type: str,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        hours: Optional[int] = None
    ) -> List[Dict]:
        """
        Get event history for a time range
        
        Args:
            event_type: Event type to query
            start_time: Start timestamp (Unix time)
            end_time: End timestamp (Unix time)
            hours: Alternative to start_time: last N hours
        
        Returns:
            List of event dictionaries
        """
        if hours is not None:
            end_time = time.time()
            start_time = end_time - (hours * 3600)
        
        with self._get_cursor() as cursor:
            query = "SELECT * FROM events WHERE event_type = ?"
            params = [event_type]
            
            if start_time is not None:
                query += " AND timestamp >= ?"
                params.append(start_time)
            
            if end_time is not None:
                query += " AND timestamp <= ?"
                params.append(end_time)
            
            query += " ORDER BY timestamp ASC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [self._row_to_dict(row) for row in rows]
    
    def get_stats(
        self,
        event_type: str,
        hours: int = 24
    ) -> Dict:
        """
        Get statistics for an event type
        
        Args:
            event_type: Event type to query
            hours: Time window in hours (default 24)
        
        Returns:
            Dictionary with count, avg, min, max, etc.
        """
        start_time = time.time() - (hours * 3600)
        
        with self._get_cursor() as cursor:
            cursor.execute("""
                SELECT 
                    COUNT(*) as count,
                    AVG(value) as avg_value,
                    MIN(value) as min_value,
                    MAX(value) as max_value,
                    AVG(confidence) as avg_confidence,
                    MIN(timestamp) as first_timestamp,
                    MAX(timestamp) as last_timestamp
                FROM events
                WHERE event_type = ? AND timestamp >= ?
            """, (event_type, start_time))
            
            row = cursor.fetchone()
            
            return {
                'event_type': event_type,
                'hours': hours,
                'count': row['count'] or 0,
                'avg_value': row['avg_value'],
                'min_value': row['min_value'],
                'max_value': row['max_value'],
                'avg_confidence': row['avg_confidence'],
                'first_timestamp': row['first_timestamp'],
                'last_timestamp': row['last_timestamp'],
                'time_span_seconds': (row['last_timestamp'] - row['first_timestamp']) if row['last_timestamp'] else 0
            }
    
    def get_latest(
        self,
        event_type: str,
        min_confidence: Optional[float] = None
    ) -> Optional[Dict]:
        """
        Get the most recent event of a type
        
        Args:
            event_type: Event type to query
            min_confidence: Minimum confidence threshold
        
        Returns:
            Event dictionary or None
        """
        events = self.query_recent(
            event_type=event_type,
            limit=1,
            min_confidence=min_confidence
        )
        return events[0] if events else None
    
    def count_events(
        self,
        event_type: Optional[str] = None,
        hours: Optional[int] = None
    ) -> int:
        """
        Count events
        
        Args:
            event_type: Filter by event type (None for all)
            hours: Time window in hours (None for all time)
        
        Returns:
            Number of events
        """
        with self._get_cursor() as cursor:
            query = "SELECT COUNT(*) as count FROM events WHERE 1=1"
            params = []
            
            if event_type:
                query += " AND event_type = ?"
                params.append(event_type)
            
            if hours is not None:
                start_time = time.time() - (hours * 3600)
                query += " AND timestamp >= ?"
                params.append(start_time)
            
            cursor.execute(query, params)
            return cursor.fetchone()['count']
    
    def cleanup_old_events(self) -> int:
        """
        Delete events older than retention period
        
        Returns:
            Number of events deleted
        """
        cutoff_time = time.time() - (self.retention_days * 86400)
        
        with self._get_cursor() as cursor:
            cursor.execute("DELETE FROM events WHERE timestamp < ?", (cutoff_time,))
            return cursor.rowcount
    
    def get_time_series(
        self,
        event_type: str,
        hours: int = 24,
        bucket_minutes: int = 5
    ) -> List[Dict]:
        """
        Get time-series data bucketed by time intervals
        
        Args:
            event_type: Event type to query
            hours: Time window in hours
            bucket_minutes: Bucket size in minutes
        
        Returns:
            List of {timestamp, count, avg_value, avg_confidence}
        """
        start_time = time.time() - (hours * 3600)
        bucket_seconds = bucket_minutes * 60
        
        with self._get_cursor() as cursor:
            cursor.execute("""
                SELECT 
                    CAST(timestamp / ? AS INTEGER) * ? as bucket_start,
                    COUNT(*) as count,
                    AVG(value) as avg_value,
                    AVG(confidence) as avg_confidence
                FROM events
                WHERE event_type = ? AND timestamp >= ?
                GROUP BY bucket_start
                ORDER BY bucket_start ASC
            """, (bucket_seconds, bucket_seconds, event_type, start_time))
            
            rows = cursor.fetchall()
            
            return [{
                'timestamp': row['bucket_start'],
                'count': row['count'],
                'avg_value': row['avg_value'],
                'avg_confidence': row['avg_confidence']
            } for row in rows]
    
    def _row_to_dict(self, row: sqlite3.Row) -> Dict:
        """Convert SQLite row to dictionary"""
        event = {
            'id': row['id'],
            'timestamp': row['timestamp'],
            'event_type': row['event_type'],
            'value': row['value'],
            'confidence': row['confidence'],
            'created_at': row['created_at']
        }
        
        # Parse metadata JSON
        if row['metadata']:
            try:
                event['metadata'] = json.loads(row['metadata'])
            except:
                event['metadata'] = {}
        else:
            event['metadata'] = {}
        
        return event
    
    def close(self):
        """Close database connections and stop writer"""
        self.stop_writer()
        
        if hasattr(self._local, 'conn'):
            self._local.conn.close()
    
    def __enter__(self):
        self.start_writer()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Convenience functions for common operations
def log_heartbeat(store: EventStore, bpm: float, confidence: float, metadata: Optional[Dict] = None):
    """Log a heartbeat event"""
    return store.log_event('heartbeat', value=bpm, confidence=confidence, metadata=metadata)


def log_tremor(store: EventStore, frequency_hz: float, confidence: float, metadata: Optional[Dict] = None):
    """Log a tremor detection event"""
    return store.log_event('tremor', value=frequency_hz, confidence=confidence, metadata=metadata)


def log_motion_spike(store: EventStore, intensity: float, metadata: Optional[Dict] = None):
    """Log a motion spike/anomaly"""
    return store.log_event('motion_spike', value=intensity, metadata=metadata)


def log_anomaly(store: EventStore, description: str, metadata: Optional[Dict] = None):
    """Log a general anomaly"""
    meta = metadata or {}
    meta['description'] = description
    return store.log_event('anomaly', metadata=meta)
