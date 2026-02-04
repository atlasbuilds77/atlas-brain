#!/usr/bin/env python3
"""
Registry Utilities - Thread-safe registry operations with file locking.
All scripts that touch spawn-registry.json MUST use these functions.

Uses fcntl.flock() for advisory file locking (POSIX-compliant, works on macOS).
"""

import json
import fcntl
import os
import sys
import tempfile
from datetime import datetime
from contextlib import contextmanager

# Default registry path (relative to clawd workspace)
DEFAULT_REGISTRY = os.path.join(os.path.expanduser("~"), "clawd", "memory", "consciousness", "spawn-registry.json")

# Lock file path (separate from registry to avoid issues with JSON truncation)
LOCK_FILE = os.path.join(os.path.expanduser("~"), "clawd", "memory", "consciousness", ".spawn-registry.lock")

# Instance file (persistent storage, NOT /tmp)
INSTANCE_FILE = os.path.join(os.path.expanduser("~"), "clawd", "memory", "consciousness", "current-instance.txt")


@contextmanager
def registry_lock(timeout_seconds=10):
    """
    Acquire an exclusive file lock on the registry lock file.
    Uses a separate .lock file to avoid truncation issues.
    
    Usage:
        with registry_lock():
            data = read_registry()
            # modify data
            write_registry(data)
    """
    os.makedirs(os.path.dirname(LOCK_FILE), exist_ok=True)
    lock_fd = open(LOCK_FILE, 'w')
    try:
        fcntl.flock(lock_fd.fileno(), fcntl.LOCK_EX)
        yield lock_fd
    finally:
        fcntl.flock(lock_fd.fileno(), fcntl.LOCK_UN)
        lock_fd.close()


def read_registry(path=None):
    """Read the registry file safely. Returns default structure if missing/corrupt."""
    path = path or DEFAULT_REGISTRY
    try:
        with open(path, 'r') as f:
            data = json.load(f)
        # Ensure required keys exist
        data.setdefault('parent_instance', 'unknown')
        data.setdefault('spawns', {})
        data.setdefault('discovery_bus', [])
        data.setdefault('last_sync', None)
        return data
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {
            "parent_instance": "unknown",
            "spawns": {},
            "discovery_bus": [],
            "last_sync": None
        }


def write_registry(data, path=None):
    """
    Write registry atomically using temp file + rename.
    This prevents corruption from interrupted writes.
    """
    path = path or DEFAULT_REGISTRY
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    # Update sync timestamp
    data['last_sync'] = datetime.utcnow().isoformat() + 'Z'
    
    # Write to temp file first, then atomically rename
    dir_name = os.path.dirname(path)
    fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix='.tmp', prefix='.registry-')
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)  # Atomic on POSIX
    except:
        # Clean up temp file on failure
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def safe_string(value):
    """Sanitize a string for safe use in JSON. Prevents injection."""
    if not isinstance(value, str):
        value = str(value)
    # json.dumps handles all escaping properly
    return json.loads(json.dumps(value))


def get_instance_id():
    """Read current instance ID from persistent storage."""
    try:
        with open(INSTANCE_FILE, 'r') as f:
            return f.read().strip()
    except (FileNotFoundError, OSError):
        return "unknown"


def set_instance_id(instance_id):
    """Write instance ID to persistent storage."""
    os.makedirs(os.path.dirname(INSTANCE_FILE), exist_ok=True)
    with open(INSTANCE_FILE, 'w') as f:
        f.write(instance_id)


def utcnow_iso():
    """Return current UTC time in ISO format with Z suffix."""
    return datetime.utcnow().isoformat() + 'Z'


if __name__ == '__main__':
    # Self-test
    print("Registry utils self-test:")
    print(f"  DEFAULT_REGISTRY: {DEFAULT_REGISTRY}")
    print(f"  LOCK_FILE: {LOCK_FILE}")
    print(f"  INSTANCE_FILE: {INSTANCE_FILE}")
    print(f"  Current instance: {get_instance_id()}")
    
    # Test locking
    with registry_lock():
        data = read_registry()
        print(f"  Registry has {len(data.get('spawns', {}))} spawns")
        print(f"  Discovery bus has {len(data.get('discovery_bus', []))} entries")
    
    print("  Lock acquired and released successfully")
    print("  ✅ All tests passed")
