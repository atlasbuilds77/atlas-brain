"""
Atlas Eyes - Natural Language Query Interface
Helper functions for Atlas to query health data in natural language
"""

from typing import Optional, Dict, List
from datetime import datetime, timedelta
from event_store import EventStore
import time


class AtlasQuery:
    """
    Natural language interface for health data queries
    Provides simple, human-readable responses for Atlas
    """
    
    def __init__(self, db_path: str = "motion_events.db"):
        """
        Initialize query interface
        
        Args:
            db_path: Path to event database
        """
        self.store = EventStore(db_path)
    
    def get_current_heart_rate(self, max_age_seconds: int = 60) -> str:
        """
        Get current heart rate
        
        Args:
            max_age_seconds: Maximum age of reading to consider "current"
        
        Returns:
            Human-readable heart rate status
        """
        latest = self.store.get_latest('heartbeat', min_confidence=0.5)
        
        if not latest:
            return "No heart rate data available yet."
        
        # Check if reading is recent
        age = time.time() - latest['timestamp']
        
        if age > max_age_seconds:
            age_desc = self._format_time_ago(age)
            return f"Last reading was {latest['value']:.0f} BPM ({age_desc} ago). No current data."
        
        # Format confidence level
        confidence = latest['confidence']
        if confidence >= 0.8:
            conf_desc = "confident"
        elif confidence >= 0.6:
            conf_desc = "likely"
        else:
            conf_desc = "possible"
        
        return f"{latest['value']:.0f} BPM ({conf_desc})"
    
    def check_for_tremors(self, last_hours: int = 24, min_confidence: float = 0.7) -> str:
        """
        Check for tremor episodes
        
        Args:
            last_hours: Look back this many hours
            min_confidence: Minimum confidence threshold
        
        Returns:
            Human-readable tremor status
        """
        events = self.store.get_history('tremor', hours=last_hours)
        
        # Filter by confidence
        confident_events = [e for e in events if e['confidence'] >= min_confidence]
        
        if not confident_events:
            if not events:
                return f"No tremors detected in the last {last_hours} hours."
            else:
                return f"No high-confidence tremors in the last {last_hours} hours ({len(events)} low-confidence detections)."
        
        # Group into episodes (events within 5 minutes are same episode)
        episodes = self._group_into_episodes(confident_events, gap_seconds=300)
        
        if len(episodes) == 1:
            ep = episodes[0]
            avg_freq = sum(e['value'] for e in ep) / len(ep)
            time_ago = self._format_time_ago(time.time() - ep[0]['timestamp'])
            return f"1 tremor episode detected ({avg_freq:.1f} Hz, {time_ago} ago)"
        else:
            most_recent = episodes[0]
            avg_freq = sum(e['value'] for e in most_recent) / len(most_recent)
            time_ago = self._format_time_ago(time.time() - most_recent[0]['timestamp'])
            return f"{len(episodes)} tremor episodes detected in the last {last_hours} hours. Most recent: {avg_freq:.1f} Hz, {time_ago} ago"
    
    def health_summary(self, hours: int = 24) -> str:
        """
        Get overall health summary
        
        Args:
            hours: Time window in hours
        
        Returns:
            Formatted health report
        """
        # Get stats for each event type
        heartbeat_stats = self.store.get_stats('heartbeat', hours=hours)
        tremor_stats = self.store.get_stats('tremor', hours=hours)
        motion_stats = self.store.get_stats('motion_spike', hours=hours)
        
        lines = [f"Health Summary (last {hours} hours):"]
        lines.append("")
        
        # Heartbeat
        if heartbeat_stats['count'] > 0:
            avg_bpm = heartbeat_stats['avg_value']
            min_bpm = heartbeat_stats['min_value']
            max_bpm = heartbeat_stats['max_value']
            avg_conf = heartbeat_stats['avg_confidence']
            
            lines.append(f"❤️  Heart Rate:")
            lines.append(f"   Average: {avg_bpm:.0f} BPM")
            lines.append(f"   Range: {min_bpm:.0f}-{max_bpm:.0f} BPM")
            lines.append(f"   Readings: {heartbeat_stats['count']} (avg confidence: {avg_conf:.1%})")
        else:
            lines.append("❤️  Heart Rate: No data")
        
        lines.append("")
        
        # Tremor
        if tremor_stats['count'] > 0:
            episodes = self._count_episodes('tremor', hours, min_confidence=0.7)
            avg_freq = tremor_stats['avg_value']
            
            lines.append(f"🤝 Tremor:")
            lines.append(f"   Episodes: {episodes}")
            lines.append(f"   Average frequency: {avg_freq:.1f} Hz")
            lines.append(f"   Total detections: {tremor_stats['count']}")
        else:
            lines.append("🤝 Tremor: None detected")
        
        lines.append("")
        
        # Motion anomalies
        if motion_stats['count'] > 0:
            lines.append(f"⚡ Motion Spikes: {motion_stats['count']}")
        else:
            lines.append("⚡ Motion Spikes: None")
        
        return "\n".join(lines)
    
    def get_heart_rate_history(
        self,
        hours: int = 24,
        min_confidence: float = 0.5,
        format: str = 'summary'
    ) -> str:
        """
        Get heart rate history
        
        Args:
            hours: Time window in hours
            min_confidence: Minimum confidence threshold
            format: 'summary' or 'detailed'
        
        Returns:
            Formatted history
        """
        events = self.store.get_history('heartbeat', hours=hours)
        events = [e for e in events if e['confidence'] >= min_confidence]
        
        if not events:
            return f"No heart rate data in the last {hours} hours."
        
        if format == 'summary':
            values = [e['value'] for e in events]
            avg = sum(values) / len(values)
            min_val = min(values)
            max_val = max(values)
            
            return f"Heart rate over last {hours} hours: {avg:.0f} BPM avg (range: {min_val:.0f}-{max_val:.0f}, {len(events)} readings)"
        
        elif format == 'detailed':
            lines = [f"Heart Rate History (last {hours} hours):"]
            lines.append("")
            
            # Show most recent 10
            recent = sorted(events, key=lambda x: x['timestamp'], reverse=True)[:10]
            
            for event in recent:
                time_ago = self._format_time_ago(time.time() - event['timestamp'])
                conf = event['confidence']
                lines.append(f"  {event['value']:.0f} BPM - {time_ago} ago (confidence: {conf:.0%})")
            
            if len(events) > 10:
                lines.append(f"  ... and {len(events) - 10} more readings")
            
            return "\n".join(lines)
        
        else:
            return "Unknown format. Use 'summary' or 'detailed'."
    
    def get_time_series_data(
        self,
        event_type: str,
        hours: int = 24,
        bucket_minutes: int = 5
    ) -> List[Dict]:
        """
        Get time-series data for plotting/analysis
        
        Args:
            event_type: Type of event ('heartbeat', 'tremor', etc.)
            hours: Time window in hours
            bucket_minutes: Time bucket size in minutes
        
        Returns:
            List of time-series data points
        """
        return self.store.get_time_series(event_type, hours, bucket_minutes)
    
    def is_everything_normal(self, hours: int = 1) -> str:
        """
        Quick health check
        
        Args:
            hours: Time window to check
        
        Returns:
            Simple yes/no status with details
        """
        issues = []
        
        # Check heart rate
        latest_hr = self.store.get_latest('heartbeat', min_confidence=0.5)
        if latest_hr:
            bpm = latest_hr['value']
            age = time.time() - latest_hr['timestamp']
            
            if age > 3600:  # More than 1 hour old
                issues.append("No recent heart rate data")
            elif bpm < 50 or bpm > 120:
                issues.append(f"Heart rate unusual: {bpm:.0f} BPM")
        else:
            issues.append("No heart rate data")
        
        # Check for tremors
        tremor_events = self.store.get_history('tremor', hours=hours)
        tremor_events = [e for e in tremor_events if e['confidence'] >= 0.7]
        
        if tremor_events:
            episodes = self._count_episodes('tremor', hours, min_confidence=0.7)
            issues.append(f"{episodes} tremor episode(s) in last {hours} hour(s)")
        
        # Check for motion spikes
        spike_count = self.store.count_events('motion_spike', hours=hours)
        if spike_count > 10:
            issues.append(f"{spike_count} motion spikes (unusual activity)")
        
        if not issues:
            return f"✅ Everything looks normal (last {hours} hour(s))"
        else:
            return f"⚠️  Some issues detected:\n  • " + "\n  • ".join(issues)
    
    def _format_time_ago(self, seconds: float) -> str:
        """Format seconds into human-readable time ago"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds/60)}m"
        elif seconds < 86400:
            hours = int(seconds/3600)
            return f"{hours}h"
        else:
            days = int(seconds/86400)
            return f"{days}d"
    
    def _group_into_episodes(
        self,
        events: List[Dict],
        gap_seconds: int = 300
    ) -> List[List[Dict]]:
        """
        Group events into episodes based on time gaps
        
        Args:
            events: List of events (must be sorted by timestamp)
            gap_seconds: Maximum gap between events in same episode
        
        Returns:
            List of episodes (each episode is a list of events)
        """
        if not events:
            return []
        
        # Sort by timestamp
        sorted_events = sorted(events, key=lambda x: x['timestamp'], reverse=True)
        
        episodes = []
        current_episode = [sorted_events[0]]
        
        for event in sorted_events[1:]:
            # Check time gap from last event in current episode
            gap = current_episode[-1]['timestamp'] - event['timestamp']
            
            if gap <= gap_seconds:
                current_episode.append(event)
            else:
                episodes.append(current_episode)
                current_episode = [event]
        
        # Add last episode
        if current_episode:
            episodes.append(current_episode)
        
        return episodes
    
    def _count_episodes(
        self,
        event_type: str,
        hours: int,
        min_confidence: float = 0.7,
        gap_seconds: int = 300
    ) -> int:
        """Count distinct episodes of an event type"""
        events = self.store.get_history(event_type, hours=hours)
        events = [e for e in events if e['confidence'] >= min_confidence]
        episodes = self._group_into_episodes(events, gap_seconds)
        return len(episodes)
    
    def close(self):
        """Close database connection"""
        self.store.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Convenience functions for direct use
def get_current_heart_rate(db_path: str = "motion_events.db") -> str:
    """Quick function: Get current heart rate"""
    with AtlasQuery(db_path) as query:
        return query.get_current_heart_rate()


def check_for_tremors(last_hours: int = 24, db_path: str = "motion_events.db") -> str:
    """Quick function: Check for tremors"""
    with AtlasQuery(db_path) as query:
        return query.check_for_tremors(last_hours)


def health_summary(hours: int = 24, db_path: str = "motion_events.db") -> str:
    """Quick function: Get health summary"""
    with AtlasQuery(db_path) as query:
        return query.health_summary(hours)


def is_everything_normal(hours: int = 1, db_path: str = "motion_events.db") -> str:
    """Quick function: Quick health check"""
    with AtlasQuery(db_path) as query:
        return query.is_everything_normal(hours)
