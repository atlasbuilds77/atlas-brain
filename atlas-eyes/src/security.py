"""
Atlas Eyes Security Module
Authentication, authorization, and audit logging
"""

import os
import json
import hashlib
import secrets
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict


class SecurityManager:
    """Manages authentication, authorization, and audit logging for Atlas Eyes"""
    
    def __init__(self, log_dir: str = None):
        self.log_dir = Path(log_dir or "/Users/atlasbuilds/clawd/atlas-eyes/logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.audit_log_path = self.log_dir / "audit.log"
        self.access_log_path = self.log_dir / "access.log"
        
        # Load or generate API token
        self.token_file = self.log_dir / ".api_token"
        self.api_token = self._load_or_generate_token()
        
        # System state
        self.system_enabled = True
        self.kill_switch_triggered = False
    
    def _load_or_generate_token(self) -> str:
        """Load existing token or generate new one"""
        if self.token_file.exists():
            with open(self.token_file, 'r') as f:
                return f.read().strip()
        else:
            # Generate secure random token
            token = secrets.token_urlsafe(32)
            with open(self.token_file, 'w') as f:
                f.write(token)
            # Secure the file (owner read-only)
            os.chmod(self.token_file, 0o400)
            return token
    
    def verify_token(self, token: Optional[str]) -> bool:
        """Verify API token"""
        if not token:
            return False
        return secrets.compare_digest(token, self.api_token)
    
    def log_access(self, user: str, action: str, result: str, details: Dict = None):
        """Log access attempt"""
        timestamp = datetime.now().isoformat()
        log_entry = {
            'timestamp': timestamp,
            'user': user,
            'action': action,
            'result': result,
            'details': details or {}
        }
        
        with open(self.access_log_path, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def log_audit(self, event: str, user: str, data: Dict = None):
        """Log security-relevant event"""
        timestamp = datetime.now().isoformat()
        audit_entry = {
            'timestamp': timestamp,
            'event': event,
            'user': user,
            'data': data or {}
        }
        
        with open(self.audit_log_path, 'a') as f:
            f.write(json.dumps(audit_entry) + '\n')
    
    def trigger_kill_switch(self, user: str, reason: str):
        """Emergency disable of camera system"""
        self.kill_switch_triggered = True
        self.system_enabled = False
        
        self.log_audit('KILL_SWITCH_TRIGGERED', user, {
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        })
    
    def is_system_enabled(self) -> bool:
        """Check if system is enabled"""
        return self.system_enabled and not self.kill_switch_triggered
    
    def reset_kill_switch(self, user: str):
        """Reset kill switch (admin only)"""
        self.kill_switch_triggered = False
        self.system_enabled = True
        
        self.log_audit('KILL_SWITCH_RESET', user, {
            'timestamp': datetime.now().isoformat()
        })
    
    def get_token(self) -> str:
        """Get current API token (for authorized users only)"""
        return self.api_token


# Global kill switch flag
_KILL_SWITCH_FILE = Path("/Users/atlasbuilds/clawd/atlas-eyes/logs/.kill_switch")

def check_kill_switch() -> bool:
    """Check if kill switch is active (global, persistent)"""
    return _KILL_SWITCH_FILE.exists()

def activate_kill_switch(reason: str = "Manual trigger"):
    """Activate global kill switch"""
    _KILL_SWITCH_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(_KILL_SWITCH_FILE, 'w') as f:
        f.write(json.dumps({
            'activated': datetime.now().isoformat(),
            'reason': reason
        }))
    print(f"🔴 KILL SWITCH ACTIVATED: {reason}")

def deactivate_kill_switch():
    """Deactivate global kill switch (admin only)"""
    if _KILL_SWITCH_FILE.exists():
        _KILL_SWITCH_FILE.unlink()
    print("✅ Kill switch deactivated")
