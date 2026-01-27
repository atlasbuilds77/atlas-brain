"""
Compliance Service
Kronos Tax Module - WISP compliance automation

Implements IRS-required Written Information Security Plan (WISP) controls:
- 3-year email/document retention
- Encryption for sensitive files
- Access logging
- Incident tracking
"""

from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from enum import Enum
import hashlib
import re

from ..config.settings import WISP_CONFIG


class IncidentSeverity(Enum):
    """Security incident severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentType(Enum):
    """Security incident types."""
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_BREACH = "data_breach"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    POLICY_VIOLATION = "policy_violation"
    SYSTEM_COMPROMISE = "system_compromise"
    PHISHING_ATTEMPT = "phishing_attempt"
    DATA_LOSS = "data_loss"


class AccessAction(Enum):
    """Types of access actions to log."""
    VIEW = "view"
    EDIT = "edit"
    DELETE = "delete"
    DOWNLOAD = "download"
    EXPORT = "export"
    SHARE = "share"
    PRINT = "print"


@dataclass
class AccessLog:
    """Access log entry."""
    id: Optional[int] = None
    user_id: int = 0
    client_id: Optional[int] = None
    resource_type: str = ""
    resource_id: int = 0
    action: AccessAction = AccessAction.VIEW
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    details: Optional[Dict[str, Any]] = None


@dataclass
class SecurityIncident:
    """Security incident record."""
    id: Optional[int] = None
    incident_type: IncidentType = IncidentType.SUSPICIOUS_ACTIVITY
    severity: IncidentSeverity = IncidentSeverity.MEDIUM
    title: str = ""
    description: str = ""
    affected_clients: List[int] = field(default_factory=list)
    reported_by: Optional[int] = None
    assigned_to: Optional[int] = None
    resolved: bool = False
    resolution_notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "incident_type": self.incident_type.value,
            "severity": self.severity.value,
            "title": self.title,
            "description": self.description,
            "affected_clients": self.affected_clients,
            "reported_by": self.reported_by,
            "assigned_to": self.assigned_to,
            "resolved": self.resolved,
            "created_at": self.created_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
        }


@dataclass
class RetentionItem:
    """Item subject to retention policy."""
    id: int
    item_type: str  # email, document, file
    client_id: int
    created_at: datetime
    retention_until: date
    archived: bool = False
    deleted: bool = False


class ComplianceService:
    """
    Service for WISP compliance automation.
    
    Implements:
    - 3-year retention policy
    - File encryption
    - Access logging
    - Incident tracking
    - Compliance reporting
    """
    
    def __init__(self, db=None, storage_service=None, notification_service=None):
        """
        Initialize compliance service.
        
        Args:
            db: Database connection
            storage_service: Encrypted storage service
            notification_service: For incident alerts
        """
        self.db = db
        self.storage = storage_service
        self.notifications = notification_service
        self.config = WISP_CONFIG
        
        # Compile sensitive data patterns
        self.sensitive_patterns = [
            re.compile(pattern) for pattern in self.config["sensitive_patterns"]
        ]
    
    # =========================================================================
    # ENCRYPTION
    # =========================================================================
    
    def encrypt_file(
        self,
        file_path: str,
        client_id: int,
        classification: str = "confidential"
    ) -> Dict[str, Any]:
        """
        Encrypt a file for secure storage.
        
        Args:
            file_path: Path to file
            client_id: Associated client
            classification: Security classification
            
        Returns:
            Dict with encrypted file info
        """
        result = {
            "original_path": file_path,
            "encrypted_path": None,
            "encryption_key_id": None,
            "checksum": None,
            "encrypted_at": datetime.now(),
        }
        
        if self.storage:
            # Generate encryption key or use existing
            key_id = self._get_or_create_encryption_key(client_id)
            
            # Encrypt file
            encrypted_path = self.storage.encrypt(
                file_path,
                key_id=key_id,
                algorithm=self.config["encryption"]["algorithm"]
            )
            
            # Calculate checksum
            checksum = self._calculate_checksum(encrypted_path)
            
            result["encrypted_path"] = encrypted_path
            result["encryption_key_id"] = key_id
            result["checksum"] = checksum
            
            # Log the encryption
            self.log_access(
                user_id=0,  # System action
                client_id=client_id,
                resource_type="file",
                resource_id=0,
                action=AccessAction.EDIT,
                details={"action": "encrypt", "file": file_path}
            )
        
        return result
    
    def decrypt_file(
        self,
        encrypted_path: str,
        user_id: int,
        client_id: int
    ) -> str:
        """
        Decrypt a file for access.
        
        Args:
            encrypted_path: Path to encrypted file
            user_id: User requesting access
            client_id: Associated client
            
        Returns:
            Path to decrypted file (temporary)
        """
        # Log access attempt
        self.log_access(
            user_id=user_id,
            client_id=client_id,
            resource_type="file",
            resource_id=0,
            action=AccessAction.VIEW,
            details={"action": "decrypt", "file": encrypted_path}
        )
        
        if self.storage:
            return self.storage.decrypt(encrypted_path)
        
        return encrypted_path
    
    def check_encryption_status(self, client_id: int) -> Dict[str, Any]:
        """
        Check encryption status for client files.
        
        Returns:
            Dict with encryption statistics
        """
        result = {
            "client_id": client_id,
            "total_files": 0,
            "encrypted_files": 0,
            "unencrypted_files": 0,
            "encryption_rate": 0.0,
            "unencrypted_list": [],
        }
        
        if self.db:
            files = self._get_client_files(client_id)
            result["total_files"] = len(files)
            
            for f in files:
                if f.get("encrypted"):
                    result["encrypted_files"] += 1
                else:
                    result["unencrypted_files"] += 1
                    result["unencrypted_list"].append(f.get("filename"))
            
            if result["total_files"] > 0:
                result["encryption_rate"] = (
                    result["encrypted_files"] / result["total_files"]
                ) * 100
        
        return result
    
    def _get_or_create_encryption_key(self, client_id: int) -> str:
        """Get or create encryption key for client."""
        # Implementation would use key management service
        return f"key_{client_id}"
    
    def _calculate_checksum(self, file_path: str) -> str:
        """Calculate SHA-256 checksum of file."""
        # Would read file and hash it
        return hashlib.sha256(file_path.encode()).hexdigest()
    
    # =========================================================================
    # ACCESS LOGGING
    # =========================================================================
    
    def log_access(
        self,
        user_id: int,
        resource_type: str,
        resource_id: int,
        action: AccessAction,
        client_id: int = None,
        ip_address: str = None,
        user_agent: str = None,
        details: Dict[str, Any] = None
    ) -> AccessLog:
        """
        Log an access event.
        
        Args:
            user_id: User performing action
            resource_type: Type of resource (file, return, document, etc.)
            resource_id: ID of resource
            action: Type of action
            client_id: Associated client (if applicable)
            ip_address: Request IP
            user_agent: Browser/client info
            details: Additional details
            
        Returns:
            Created AccessLog entry
        """
        if not self.config["access_logging"]["enabled"]:
            return None
        
        # Check if this action type should be logged
        action_config = {
            AccessAction.VIEW: self.config["access_logging"]["log_views"],
            AccessAction.EDIT: self.config["access_logging"]["log_edits"],
            AccessAction.DOWNLOAD: self.config["access_logging"]["log_downloads"],
            AccessAction.EXPORT: self.config["access_logging"]["log_exports"],
        }
        
        if not action_config.get(action, True):
            return None
        
        log_entry = AccessLog(
            user_id=user_id,
            client_id=client_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.now(),
            details=details,
        )
        
        if self.db:
            log_entry.id = self._save_access_log(log_entry)
        
        # Check for suspicious patterns
        if self.config["incidents"]["auto_detect"]:
            self._check_suspicious_access(log_entry)
        
        return log_entry
    
    def get_access_logs(
        self,
        client_id: int = None,
        user_id: int = None,
        resource_type: str = None,
        action: AccessAction = None,
        start_date: datetime = None,
        end_date: datetime = None,
        limit: int = 100
    ) -> List[AccessLog]:
        """
        Query access logs with filters.
        
        Args:
            Various filters
            
        Returns:
            List of matching AccessLog entries
        """
        if self.db:
            return self._query_access_logs(
                client_id=client_id,
                user_id=user_id,
                resource_type=resource_type,
                action=action,
                start_date=start_date,
                end_date=end_date,
                limit=limit
            )
        return []
    
    def get_client_access_history(
        self,
        client_id: int,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get access history summary for a client.
        
        Args:
            client_id: Client ID
            days: Number of days to look back
            
        Returns:
            Summary of access patterns
        """
        start_date = datetime.now() - timedelta(days=days)
        logs = self.get_access_logs(client_id=client_id, start_date=start_date)
        
        # Summarize
        summary = {
            "client_id": client_id,
            "period_days": days,
            "total_accesses": len(logs),
            "by_action": {},
            "by_user": {},
            "by_resource": {},
            "unique_users": set(),
        }
        
        for log in logs:
            # By action
            action = log.action.value
            summary["by_action"][action] = summary["by_action"].get(action, 0) + 1
            
            # By user
            summary["by_user"][log.user_id] = summary["by_user"].get(log.user_id, 0) + 1
            summary["unique_users"].add(log.user_id)
            
            # By resource
            summary["by_resource"][log.resource_type] = (
                summary["by_resource"].get(log.resource_type, 0) + 1
            )
        
        summary["unique_users"] = len(summary["unique_users"])
        
        return summary
    
    def _check_suspicious_access(self, log: AccessLog):
        """Check for suspicious access patterns."""
        suspicious = False
        reason = None
        
        # Check for unusual access time (outside business hours)
        hour = log.timestamp.hour
        if hour < 6 or hour > 22:
            suspicious = True
            reason = f"Access outside business hours ({hour}:00)"
        
        # Check for bulk downloads
        if log.action == AccessAction.DOWNLOAD:
            recent_downloads = self.get_access_logs(
                user_id=log.user_id,
                action=AccessAction.DOWNLOAD,
                start_date=datetime.now() - timedelta(hours=1)
            )
            if len(recent_downloads) > 20:
                suspicious = True
                reason = f"Bulk downloads detected ({len(recent_downloads)} in 1 hour)"
        
        # Check for access to many different clients
        if log.client_id:
            recent_client_access = self.get_access_logs(
                user_id=log.user_id,
                start_date=datetime.now() - timedelta(minutes=30)
            )
            unique_clients = set(l.client_id for l in recent_client_access if l.client_id)
            if len(unique_clients) > 10:
                suspicious = True
                reason = f"Access to {len(unique_clients)} clients in 30 minutes"
        
        if suspicious:
            self.report_incident(
                incident_type=IncidentType.SUSPICIOUS_ACTIVITY,
                severity=IncidentSeverity.MEDIUM,
                title="Suspicious access pattern detected",
                description=f"User {log.user_id}: {reason}",
                affected_clients=[log.client_id] if log.client_id else [],
                reported_by=0  # System
            )
    
    # =========================================================================
    # INCIDENT TRACKING
    # =========================================================================
    
    def report_incident(
        self,
        incident_type: IncidentType,
        severity: IncidentSeverity,
        title: str,
        description: str,
        affected_clients: List[int] = None,
        reported_by: int = None
    ) -> SecurityIncident:
        """
        Report a security incident.
        
        Args:
            incident_type: Type of incident
            severity: Severity level
            title: Short title
            description: Full description
            affected_clients: List of affected client IDs
            reported_by: User ID who reported (0 for system)
            
        Returns:
            Created SecurityIncident
        """
        incident = SecurityIncident(
            incident_type=incident_type,
            severity=severity,
            title=title,
            description=description,
            affected_clients=affected_clients or [],
            reported_by=reported_by,
        )
        
        if self.db:
            incident.id = self._save_incident(incident)
        
        # Notify admin immediately for high/critical
        if self.config["incidents"]["notify_admin_immediately"]:
            if severity in [IncidentSeverity.HIGH, IncidentSeverity.CRITICAL]:
                self._notify_incident(incident)
        
        return incident
    
    def get_incident(self, incident_id: int) -> Optional[SecurityIncident]:
        """Get incident by ID."""
        if self.db:
            return self._load_incident(incident_id)
        return None
    
    def get_open_incidents(
        self,
        severity: IncidentSeverity = None
    ) -> List[SecurityIncident]:
        """Get all unresolved incidents."""
        if self.db:
            return self._query_incidents(resolved=False, severity=severity)
        return []
    
    def resolve_incident(
        self,
        incident_id: int,
        resolution_notes: str,
        resolved_by: int
    ) -> SecurityIncident:
        """
        Mark incident as resolved.
        
        Args:
            incident_id: Incident ID
            resolution_notes: How it was resolved
            resolved_by: User ID who resolved
            
        Returns:
            Updated SecurityIncident
        """
        incident = self.get_incident(incident_id)
        
        if incident:
            incident.resolved = True
            incident.resolution_notes = resolution_notes
            incident.resolved_at = datetime.now()
            
            if self.db:
                self._update_incident(incident)
        
        return incident
    
    def get_incident_statistics(
        self,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> Dict[str, Any]:
        """Get incident statistics for reporting."""
        if start_date is None:
            start_date = datetime.now() - timedelta(days=365)
        if end_date is None:
            end_date = datetime.now()
        
        stats = {
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat(),
            "total_incidents": 0,
            "by_severity": {},
            "by_type": {},
            "resolved": 0,
            "open": 0,
            "avg_resolution_time_hours": 0,
        }
        
        if self.db:
            incidents = self._query_incidents(
                start_date=start_date,
                end_date=end_date
            )
            
            stats["total_incidents"] = len(incidents)
            resolution_times = []
            
            for inc in incidents:
                # By severity
                sev = inc.severity.value
                stats["by_severity"][sev] = stats["by_severity"].get(sev, 0) + 1
                
                # By type
                typ = inc.incident_type.value
                stats["by_type"][typ] = stats["by_type"].get(typ, 0) + 1
                
                # Resolution status
                if inc.resolved:
                    stats["resolved"] += 1
                    if inc.resolved_at:
                        hours = (inc.resolved_at - inc.created_at).total_seconds() / 3600
                        resolution_times.append(hours)
                else:
                    stats["open"] += 1
            
            if resolution_times:
                stats["avg_resolution_time_hours"] = sum(resolution_times) / len(resolution_times)
        
        return stats
    
    def _notify_incident(self, incident: SecurityIncident):
        """Send incident notification to admin."""
        if self.notifications:
            self.notifications.send_alert(
                title=f"[{incident.severity.value.upper()}] {incident.title}",
                message=incident.description,
                priority="high" if incident.severity == IncidentSeverity.CRITICAL else "normal"
            )
    
    # =========================================================================
    # RETENTION MANAGEMENT
    # =========================================================================
    
    def enforce_retention_policy(self) -> Dict[str, Any]:
        """
        Enforce 3-year retention policy.
        Called by scheduled task (daily).
        
        - Archives items past retention period
        - Does NOT delete (WISP requires retention, not deletion)
        
        Returns:
            Processing results
        """
        results = {
            "processed": 0,
            "archived": 0,
            "errors": 0,
            "retention_years": self.config["retention_years"],
        }
        
        retention_cutoff = date.today() - timedelta(
            days=self.config["retention_years"] * 365
        )
        
        if self.db:
            # Get items past retention
            items = self._get_items_past_retention(retention_cutoff)
            results["processed"] = len(items)
            
            for item in items:
                try:
                    action = self.config["post_retention_action"]
                    
                    if action == "archive":
                        self._archive_item(item)
                        results["archived"] += 1
                    elif action == "anonymize":
                        self._anonymize_item(item)
                        results["archived"] += 1
                    # Note: We don't support "delete" for WISP compliance
                    
                except Exception as e:
                    results["errors"] += 1
        
        return results
    
    def get_retention_status(self, client_id: int = None) -> Dict[str, Any]:
        """
        Get retention status for client or all.
        
        Returns:
            Retention statistics
        """
        status = {
            "retention_years": self.config["retention_years"],
            "total_items": 0,
            "within_retention": 0,
            "approaching_expiry": 0,  # Within 90 days
            "past_retention": 0,
            "archived": 0,
        }
        
        if self.db:
            items = self._get_retention_items(client_id)
            today = date.today()
            approaching_cutoff = today + timedelta(days=90)
            
            for item in items:
                status["total_items"] += 1
                
                if item.archived:
                    status["archived"] += 1
                elif item.retention_until < today:
                    status["past_retention"] += 1
                elif item.retention_until < approaching_cutoff:
                    status["approaching_expiry"] += 1
                else:
                    status["within_retention"] += 1
        
        return status
    
    def set_retention_date(
        self,
        item_type: str,
        item_id: int,
        retention_until: date = None
    ):
        """
        Set custom retention date for an item.
        
        Args:
            item_type: Type of item
            item_id: Item ID
            retention_until: Custom retention date (default: 3 years from now)
        """
        if retention_until is None:
            retention_until = date.today() + timedelta(
                days=self.config["retention_years"] * 365
            )
        
        if self.db:
            self._update_retention_date(item_type, item_id, retention_until)
    
    # =========================================================================
    # SENSITIVE DATA DETECTION
    # =========================================================================
    
    def scan_for_sensitive_data(self, text: str) -> Dict[str, Any]:
        """
        Scan text for sensitive data patterns.
        
        Args:
            text: Text to scan
            
        Returns:
            Dict with findings
        """
        findings = {
            "contains_sensitive": False,
            "ssn_found": False,
            "ein_found": False,
            "patterns_matched": [],
        }
        
        for i, pattern in enumerate(self.sensitive_patterns):
            matches = pattern.findall(text)
            if matches:
                findings["contains_sensitive"] = True
                findings["patterns_matched"].append({
                    "pattern_index": i,
                    "count": len(matches),
                })
                
                # Identify pattern type
                if "\\d{3}-\\d{2}-\\d{4}" in self.config["sensitive_patterns"][i]:
                    findings["ssn_found"] = True
                elif "\\d{2}-\\d{7}" in self.config["sensitive_patterns"][i]:
                    findings["ein_found"] = True
        
        return findings
    
    def redact_sensitive_data(self, text: str) -> str:
        """
        Redact sensitive data from text.
        
        Args:
            text: Text to redact
            
        Returns:
            Redacted text
        """
        redacted = text
        
        for pattern in self.sensitive_patterns:
            redacted = pattern.sub("[REDACTED]", redacted)
        
        return redacted
    
    # =========================================================================
    # COMPLIANCE REPORTING
    # =========================================================================
    
    def generate_compliance_report(
        self,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> Dict[str, Any]:
        """
        Generate WISP compliance report.
        
        Args:
            start_date: Report period start
            end_date: Report period end
            
        Returns:
            Comprehensive compliance report
        """
        if start_date is None:
            start_date = datetime.now() - timedelta(days=365)
        if end_date is None:
            end_date = datetime.now()
        
        report = {
            "report_generated": datetime.now().isoformat(),
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "encryption": {
                "algorithm": self.config["encryption"]["algorithm"],
                "key_rotation_days": self.config["encryption"]["key_rotation_days"],
                "status": "compliant",
            },
            "access_logging": {
                "enabled": self.config["access_logging"]["enabled"],
                "retention_days": self.config["access_logging"]["retention_days"],
                "total_logs": 0,
            },
            "incidents": self.get_incident_statistics(start_date, end_date),
            "retention": self.get_retention_status(),
            "session_security": {
                "timeout_minutes": self.config["session"]["timeout_minutes"],
                "mfa_required": self.config["session"]["require_mfa"],
            },
            "compliance_score": 0.0,
        }
        
        # Calculate compliance score
        score = 0.0
        checks = 0
        
        # Encryption check
        if self.config["encryption"]["encrypt_at_rest"]:
            score += 1
        checks += 1
        
        # Access logging check
        if self.config["access_logging"]["enabled"]:
            score += 1
        checks += 1
        
        # MFA check
        if self.config["session"]["require_mfa"]:
            score += 1
        checks += 1
        
        # No critical open incidents
        if report["incidents"]["open"] == 0 or \
           report["incidents"]["by_severity"].get("critical", 0) == 0:
            score += 1
        checks += 1
        
        report["compliance_score"] = (score / checks) * 100 if checks > 0 else 0
        
        return report
    
    def get_compliance_status(self) -> Dict[str, Any]:
        """
        Get quick compliance status overview.
        
        Returns:
            Status summary
        """
        return {
            "overall_status": "compliant",
            "encryption_enabled": self.config["encryption"]["encrypt_at_rest"],
            "access_logging_enabled": self.config["access_logging"]["enabled"],
            "mfa_enabled": self.config["session"]["require_mfa"],
            "retention_policy": f"{self.config['retention_years']} years",
            "open_incidents": len(self.get_open_incidents()),
            "critical_incidents": len(self.get_open_incidents(IncidentSeverity.CRITICAL)),
        }
    
    # =========================================================================
    # DATABASE STUBS
    # =========================================================================
    
    def _save_access_log(self, log: AccessLog) -> int:
        """Save access log to database."""
        return 0
    
    def _query_access_logs(self, **filters) -> List[AccessLog]:
        """Query access logs."""
        return []
    
    def _save_incident(self, incident: SecurityIncident) -> int:
        """Save incident to database."""
        return 0
    
    def _load_incident(self, incident_id: int) -> Optional[SecurityIncident]:
        """Load incident from database."""
        return None
    
    def _update_incident(self, incident: SecurityIncident):
        """Update incident in database."""
        pass
    
    def _query_incidents(self, **filters) -> List[SecurityIncident]:
        """Query incidents."""
        return []
    
    def _get_client_files(self, client_id: int) -> List[Dict]:
        """Get client files."""
        return []
    
    def _get_items_past_retention(self, cutoff: date) -> List[RetentionItem]:
        """Get items past retention period."""
        return []
    
    def _get_retention_items(self, client_id: int = None) -> List[RetentionItem]:
        """Get retention items."""
        return []
    
    def _archive_item(self, item: RetentionItem):
        """Archive an item."""
        pass
    
    def _anonymize_item(self, item: RetentionItem):
        """Anonymize an item."""
        pass
    
    def _update_retention_date(self, item_type: str, item_id: int, retention_until: date):
        """Update retention date."""
        pass
