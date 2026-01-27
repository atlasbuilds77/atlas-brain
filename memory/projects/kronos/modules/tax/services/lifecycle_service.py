"""
Lifecycle Service
Kronos Tax Module - Client lifecycle management

Handles onboarding, filing status, retention monitoring, and win-back campaigns.
"""

from dataclasses import dataclass
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any, Tuple
from enum import Enum

from ..models import (
    ClientTaxProfile, TaxSituation, FilingFrequency,
    TaxReturn, FilingStatus
)
from ..config.settings import LIFECYCLE_CONFIG, WINBACK_CONFIG


class ClientStatus(Enum):
    """Client lifecycle status."""
    PROSPECT = "prospect"
    NEW_CLIENT = "new_client"
    ACTIVE = "active"
    SEASONAL = "seasonal"
    INACTIVE = "inactive"
    CHURNED = "churned"
    WINBACK = "winback"


class OnboardingStage(Enum):
    """Onboarding workflow stages."""
    INTAKE = "intake"
    QUALIFICATION = "qualification"
    ENGAGEMENT_SIGNED = "engagement_signed"
    PROFILE_COMPLETE = "profile_complete"
    DOCUMENTS_UPLOADED = "documents_uploaded"
    ACTIVE = "active"


@dataclass
class RetentionRisk:
    """Client retention risk assessment."""
    client_id: int
    risk_score: float  # 0.0 to 1.0
    risk_level: str    # low, medium, high, critical
    factors: List[str]
    recommended_actions: List[str]
    last_assessed: datetime


class LifecycleService:
    """
    Service for managing client lifecycle.
    
    Handles:
    - New client onboarding
    - Filing status tracking
    - Retention monitoring
    - Win-back campaigns
    """
    
    def __init__(self, db=None, email_service=None, task_service=None):
        """
        Initialize lifecycle service.
        
        Args:
            db: Database connection
            email_service: Email service for communications
            task_service: Task service for creating follow-ups
        """
        self.db = db
        self.email_service = email_service
        self.task_service = task_service
        self.lifecycle_config = LIFECYCLE_CONFIG
        self.winback_config = WINBACK_CONFIG
    
    # =========================================================================
    # ONBOARDING
    # =========================================================================
    
    def onboard_client(
        self,
        name: str,
        email: str,
        phone: str = None,
        tax_situation: str = "w2_employee",
        lead_source: str = "unknown",
        **kwargs
    ) -> Tuple[int, ClientTaxProfile]:
        """
        Onboard a new client.
        
        Creates:
        - Core client record
        - Tax profile
        - Initial onboarding task
        
        Args:
            name: Client name
            email: Client email
            phone: Phone number
            tax_situation: Tax situation type
            lead_source: How client found us
            
        Returns:
            Tuple of (client_id, ClientTaxProfile)
        """
        # Create core client record (via Core Engine)
        client_id = self._create_client(name, email, phone, lead_source)
        
        # Create tax profile
        profile = ClientTaxProfile(
            client_id=client_id,
            tax_situation=TaxSituation(tax_situation),
            client_since_year=date.today().year,
        )
        
        if self.db:
            profile.id = self._save_tax_profile(profile)
        
        # Create onboarding tasks
        self._create_onboarding_tasks(client_id, profile)
        
        # Send welcome email
        if self.email_service:
            self._send_welcome_email(email, name)
        
        return client_id, profile
    
    def get_onboarding_status(self, client_id: int) -> Dict[str, Any]:
        """
        Get client onboarding status.
        
        Returns:
            Dict with stage, completed steps, next actions
        """
        profile = self.get_tax_profile(client_id)
        
        # Determine current stage
        stage = self._determine_onboarding_stage(client_id, profile)
        
        # Get completed steps
        completed = self._get_completed_onboarding_steps(client_id)
        
        # Get next actions
        next_actions = self._get_next_onboarding_actions(stage)
        
        return {
            "client_id": client_id,
            "current_stage": stage.value,
            "completed_steps": completed,
            "next_actions": next_actions,
            "progress_percentage": (len(completed) / 6) * 100,
            "is_complete": stage == OnboardingStage.ACTIVE,
        }
    
    def advance_onboarding(
        self,
        client_id: int,
        completed_stage: str
    ) -> Dict[str, Any]:
        """
        Mark onboarding stage as complete and advance.
        
        Args:
            client_id: Client ID
            completed_stage: Stage that was completed
            
        Returns:
            Updated onboarding status
        """
        # Record completion
        self._record_onboarding_completion(client_id, completed_stage)
        
        # Get new status
        return self.get_onboarding_status(client_id)
    
    def _create_onboarding_tasks(self, client_id: int, profile: ClientTaxProfile):
        """Create tasks for onboarding workflow."""
        tasks = [
            {
                "type": "onboarding",
                "title": "Send engagement letter",
                "client_id": client_id,
                "due_days": 1,
            },
            {
                "type": "onboarding",
                "title": "Collect tax profile information",
                "client_id": client_id,
                "due_days": 3,
            },
            {
                "type": "onboarding",
                "title": "Request initial documents",
                "client_id": client_id,
                "due_days": 5,
            },
        ]
        
        if self.task_service:
            for task in tasks:
                self.task_service.create_task(**task)
    
    # =========================================================================
    # FILING STATUS TRACKING
    # =========================================================================
    
    def create_tax_return(
        self,
        client_id: int,
        year: int,
        filing_type: str = "personal"
    ) -> TaxReturn:
        """
        Create a tax return record for tracking.
        
        Args:
            client_id: Client ID
            year: Tax year
            filing_type: Type of return
            
        Returns:
            Created TaxReturn
        """
        from ..models import FilingType
        
        tax_return = TaxReturn(
            client_id=client_id,
            year=year,
            filing_type=FilingType(filing_type),
            status=FilingStatus.NOT_STARTED,
        )
        
        if self.db:
            tax_return.id = self._save_tax_return(tax_return)
        
        return tax_return
    
    def update_filing_status(
        self,
        client_id: int,
        year: int,
        status: str,
        notes: str = None
    ) -> TaxReturn:
        """
        Update filing status for a client's return.
        
        Args:
            client_id: Client ID
            year: Tax year
            status: New status
            notes: Optional notes
            
        Returns:
            Updated TaxReturn
        """
        tax_return = self._get_tax_return(client_id, year)
        
        if tax_return is None:
            # Create if doesn't exist
            tax_return = self.create_tax_return(client_id, year)
        
        # Update status
        old_status = tax_return.status
        tax_return.status = FilingStatus(status)
        tax_return.updated_at = datetime.now()
        
        if notes:
            tax_return.preparer_notes = notes
        
        # Handle filed status
        if status == "filed" and tax_return.filed_date is None:
            tax_return.filed_date = date.today()
        
        # Handle extended status
        if status == "extended" and tax_return.extension_date is None:
            tax_return.extension_date = date.today()
        
        if self.db:
            self._update_tax_return(tax_return)
        
        # Notify client if status changed significantly
        if self._should_notify_client(old_status, tax_return.status):
            self._send_status_update(client_id, tax_return)
        
        return tax_return
    
    def get_filing_pipeline(self, year: int = None) -> Dict[str, Any]:
        """
        Get filing pipeline statistics.
        
        Returns:
            Dict with counts by filing status
        """
        if year is None:
            year = date.today().year - 1
        
        pipeline = {
            "year": year,
            "stages": {},
            "total": 0,
            "filed": 0,
            "completion_rate": 0.0,
        }
        
        if self.db:
            stats = self._get_filing_stats(year)
            pipeline["stages"] = stats
            pipeline["total"] = sum(stats.values())
            pipeline["filed"] = stats.get("filed", 0) + stats.get("extended", 0)
            if pipeline["total"] > 0:
                pipeline["completion_rate"] = (pipeline["filed"] / pipeline["total"]) * 100
        
        return pipeline
    
    def get_client_filing_history(self, client_id: int) -> List[TaxReturn]:
        """Get all tax returns for a client."""
        if self.db:
            return self._load_client_returns(client_id)
        return []
    
    def _should_notify_client(
        self,
        old_status: FilingStatus,
        new_status: FilingStatus
    ) -> bool:
        """Determine if client should be notified of status change."""
        notify_statuses = [
            FilingStatus.READY_TO_FILE,
            FilingStatus.FILED,
            FilingStatus.EXTENDED,
        ]
        return new_status in notify_statuses and old_status != new_status
    
    # =========================================================================
    # RETENTION MONITORING
    # =========================================================================
    
    def check_retention_risk(self, client_id: int) -> RetentionRisk:
        """
        Assess retention risk for a client.
        
        Analyzes:
        - Years since last return
        - Response time to communications
        - Price complaints
        - Service issues
        
        Returns:
            RetentionRisk assessment
        """
        factors = []
        risk_score = 0.0
        
        # Get client data
        profile = self.get_tax_profile(client_id)
        returns = self.get_client_filing_history(client_id)
        
        # Factor 1: Years since last return
        if returns:
            last_return = max(returns, key=lambda r: r.year)
            years_since = date.today().year - last_return.year - 1
            if years_since >= 2:
                risk_score += 0.4
                factors.append(f"No return filed in {years_since} years")
            elif years_since >= 1:
                risk_score += 0.2
                factors.append("Did not return last year")
        else:
            risk_score += 0.3
            factors.append("No filing history")
        
        # Factor 2: Declining engagement
        if profile and profile.consecutive_years > 0:
            # Check for gaps
            if len(profile.years_filed) < profile.consecutive_years:
                risk_score += 0.1
                factors.append("Irregular filing pattern")
        
        # Factor 3: Check for complaints (would come from Core Engine)
        # complaints = self._get_client_complaints(client_id)
        # if complaints > 0:
        #     risk_score += 0.2 * complaints
        #     factors.append(f"{complaints} recorded complaints")
        
        # Factor 4: Response time (slow responders more likely to churn)
        # avg_response = self._get_avg_response_time(client_id)
        # if avg_response > 7:  # days
        #     risk_score += 0.1
        #     factors.append("Slow to respond to communications")
        
        # Determine risk level
        risk_score = min(risk_score, 1.0)
        thresholds = self.lifecycle_config["retention_risk"]
        
        if risk_score >= thresholds["critical"]:
            risk_level = "critical"
        elif risk_score >= thresholds["high"]:
            risk_level = "high"
        elif risk_score >= thresholds["medium"]:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        # Recommended actions
        actions = self._get_retention_actions(risk_level, factors)
        
        return RetentionRisk(
            client_id=client_id,
            risk_score=risk_score,
            risk_level=risk_level,
            factors=factors,
            recommended_actions=actions,
            last_assessed=datetime.now()
        )
    
    def get_at_risk_clients(
        self,
        min_risk_level: str = "medium"
    ) -> List[RetentionRisk]:
        """
        Get all clients above risk threshold.
        
        Args:
            min_risk_level: Minimum risk level to include
            
        Returns:
            List of RetentionRisk assessments
        """
        at_risk = []
        
        if self.db:
            client_ids = self._get_all_client_ids()
            for client_id in client_ids:
                risk = self.check_retention_risk(client_id)
                if self._risk_level_meets_threshold(risk.risk_level, min_risk_level):
                    at_risk.append(risk)
        
        # Sort by risk score (highest first)
        at_risk.sort(key=lambda r: r.risk_score, reverse=True)
        
        return at_risk
    
    def run_retention_scan(self) -> Dict[str, Any]:
        """
        Run daily retention risk scan.
        Called by scheduled task.
        
        Returns:
            Scan results summary
        """
        results = {
            "scanned": 0,
            "low_risk": 0,
            "medium_risk": 0,
            "high_risk": 0,
            "critical_risk": 0,
            "winback_triggered": 0,
        }
        
        if self.db:
            client_ids = self._get_active_client_ids()
            results["scanned"] = len(client_ids)
            
            for client_id in client_ids:
                risk = self.check_retention_risk(client_id)
                results[f"{risk.risk_level}_risk"] += 1
                
                # Auto-trigger win-back for high/critical
                if risk.risk_level in ["high", "critical"]:
                    if self._should_start_winback(client_id):
                        self.start_winback_campaign(client_id)
                        results["winback_triggered"] += 1
        
        return results
    
    def _get_retention_actions(
        self,
        risk_level: str,
        factors: List[str]
    ) -> List[str]:
        """Get recommended actions based on risk."""
        actions = []
        
        if risk_level == "critical":
            actions.append("Personal phone call from preparer")
            actions.append("Offer loyalty discount")
            actions.append("Schedule in-person meeting")
        elif risk_level == "high":
            actions.append("Personal email from preparer")
            actions.append("Win-back campaign")
            actions.append("Check-in call")
        elif risk_level == "medium":
            actions.append("Automated re-engagement email")
            actions.append("Add to seasonal reminder list")
        else:
            actions.append("Standard seasonal communications")
        
        return actions
    
    def _risk_level_meets_threshold(
        self,
        level: str,
        threshold: str
    ) -> bool:
        """Check if risk level meets minimum threshold."""
        levels = ["low", "medium", "high", "critical"]
        return levels.index(level) >= levels.index(threshold)
    
    # =========================================================================
    # WIN-BACK CAMPAIGNS
    # =========================================================================
    
    def start_winback_campaign(self, client_id: int) -> Dict[str, Any]:
        """
        Start win-back campaign for a churning client.
        
        Args:
            client_id: Client ID
            
        Returns:
            Campaign details
        """
        # Check if already in campaign
        if self._has_active_winback(client_id):
            return {"status": "already_active", "client_id": client_id}
        
        # Create campaign
        campaign = {
            "client_id": client_id,
            "started_at": datetime.now(),
            "current_step": 0,
            "status": "active",
            "sequence": self.winback_config["campaign_sequence"],
        }
        
        if self.db:
            campaign["id"] = self._save_winback_campaign(campaign)
        
        # Update client status
        self._update_client_status(client_id, ClientStatus.WINBACK)
        
        # Schedule first touch
        self._schedule_winback_touch(campaign, 0)
        
        return campaign
    
    def process_winback_touches(self) -> Dict[str, Any]:
        """
        Process due win-back campaign touches.
        Called by scheduled task (weekly).
        
        Returns:
            Processing results
        """
        results = {
            "processed": 0,
            "emails_sent": 0,
            "campaigns_completed": 0,
            "responses_received": 0,
        }
        
        if self.db:
            active_campaigns = self._get_active_winback_campaigns()
            
            for campaign in active_campaigns:
                # Check for response
                if self._client_responded(campaign["client_id"]):
                    self._complete_winback_success(campaign)
                    results["responses_received"] += 1
                    continue
                
                # Check if touch is due
                if self._winback_touch_due(campaign):
                    step = campaign["current_step"]
                    sequence = campaign["sequence"]
                    
                    if step < len(sequence):
                        touch = sequence[step]
                        self._execute_winback_touch(campaign, touch)
                        results["emails_sent"] += 1
                        campaign["current_step"] += 1
                        self._update_winback_campaign(campaign)
                    else:
                        # Campaign complete with no response
                        self._complete_winback_failure(campaign)
                        results["campaigns_completed"] += 1
                
                results["processed"] += 1
        
        return results
    
    def stop_winback_campaign(
        self,
        client_id: int,
        reason: str = "manual"
    ):
        """Stop win-back campaign for client."""
        if self.db:
            self._deactivate_winback_campaign(client_id, reason)
    
    def _execute_winback_touch(self, campaign: Dict, touch: Dict):
        """Execute a win-back campaign touch."""
        client_id = campaign["client_id"]
        
        if touch["type"] == "email":
            template = touch["template"]
            email = self._get_client_email(client_id)
            
            if self.email_service:
                self.email_service.send_template(
                    to=email,
                    template=template,
                    variables={
                        "client_name": self._get_client_name(client_id),
                        "last_year": self._get_last_filing_year(client_id),
                    }
                )
    
    def _complete_winback_success(self, campaign: Dict):
        """Handle successful win-back (client responded)."""
        client_id = campaign["client_id"]
        
        # Update campaign
        campaign["status"] = "success"
        campaign["completed_at"] = datetime.now()
        if self.db:
            self._update_winback_campaign(campaign)
        
        # Update client status back to active
        self._update_client_status(client_id, ClientStatus.ACTIVE)
    
    def _complete_winback_failure(self, campaign: Dict):
        """Handle failed win-back (no response)."""
        client_id = campaign["client_id"]
        
        # Update campaign
        campaign["status"] = "failed"
        campaign["completed_at"] = datetime.now()
        if self.db:
            self._update_winback_campaign(campaign)
        
        # Mark client as churned if configured
        if self.winback_config["mark_churned_after"]:
            self._update_client_status(client_id, ClientStatus.CHURNED)
    
    # =========================================================================
    # TAX PROFILE MANAGEMENT
    # =========================================================================
    
    def get_tax_profile(self, client_id: int) -> Optional[ClientTaxProfile]:
        """Get tax profile for client."""
        if self.db:
            return self._load_tax_profile(client_id)
        return None
    
    def update_tax_profile(
        self,
        client_id: int,
        **updates
    ) -> ClientTaxProfile:
        """Update tax profile fields."""
        profile = self.get_tax_profile(client_id)
        
        if profile is None:
            profile = ClientTaxProfile(client_id=client_id)
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        
        profile.updated_at = datetime.now()
        
        if self.db:
            if profile.id:
                self._update_tax_profile(profile)
            else:
                profile.id = self._save_tax_profile(profile)
        
        return profile
    
    # =========================================================================
    # INTERNAL HELPERS
    # =========================================================================
    
    def _send_welcome_email(self, email: str, name: str):
        """Send welcome email to new client."""
        if self.email_service:
            self.email_service.send_template(
                to=email,
                template="welcome",
                variables={"name": name}
            )
    
    def _send_status_update(self, client_id: int, tax_return: TaxReturn):
        """Send filing status update to client."""
        email = self._get_client_email(client_id)
        
        if self.email_service and email:
            self.email_service.send_template(
                to=email,
                template="filing_status_update",
                variables={
                    "year": tax_return.year,
                    "status": tax_return.status.value,
                    "filed_date": tax_return.filed_date,
                }
            )
    
    def _determine_onboarding_stage(
        self,
        client_id: int,
        profile: ClientTaxProfile
    ) -> OnboardingStage:
        """Determine current onboarding stage."""
        # Check completed steps
        completed = self._get_completed_onboarding_steps(client_id)
        
        stages = list(OnboardingStage)
        for stage in reversed(stages):
            if stage.value in completed:
                idx = stages.index(stage)
                if idx < len(stages) - 1:
                    return stages[idx + 1]
                return stage
        
        return OnboardingStage.INTAKE
    
    def _get_completed_onboarding_steps(self, client_id: int) -> List[str]:
        """Get list of completed onboarding steps."""
        # Would query database for completed tasks/milestones
        return []
    
    def _get_next_onboarding_actions(
        self,
        stage: OnboardingStage
    ) -> List[str]:
        """Get next actions for onboarding stage."""
        actions = {
            OnboardingStage.INTAKE: [
                "Schedule initial consultation",
                "Send new client questionnaire",
            ],
            OnboardingStage.QUALIFICATION: [
                "Review client needs",
                "Prepare engagement letter",
            ],
            OnboardingStage.ENGAGEMENT_SIGNED: [
                "Send tax profile form",
                "Request prior year returns",
            ],
            OnboardingStage.PROFILE_COMPLETE: [
                "Create document checklist",
                "Send organizer",
            ],
            OnboardingStage.DOCUMENTS_UPLOADED: [
                "Review documents",
                "Begin tax preparation",
            ],
            OnboardingStage.ACTIVE: [
                "Onboarding complete",
            ],
        }
        return actions.get(stage, [])
    
    # =========================================================================
    # DATABASE STUBS
    # =========================================================================
    
    def _create_client(self, name, email, phone, source) -> int:
        """Create client in Core Engine."""
        return 0
    
    def _save_tax_profile(self, profile: ClientTaxProfile) -> int:
        """Save tax profile."""
        return 0
    
    def _load_tax_profile(self, client_id: int) -> Optional[ClientTaxProfile]:
        """Load tax profile."""
        return None
    
    def _update_tax_profile(self, profile: ClientTaxProfile):
        """Update tax profile."""
        pass
    
    def _save_tax_return(self, tax_return: TaxReturn) -> int:
        """Save tax return."""
        return 0
    
    def _get_tax_return(self, client_id: int, year: int) -> Optional[TaxReturn]:
        """Get tax return."""
        return None
    
    def _update_tax_return(self, tax_return: TaxReturn):
        """Update tax return."""
        pass
    
    def _load_client_returns(self, client_id: int) -> List[TaxReturn]:
        """Load all returns for client."""
        return []
    
    def _get_filing_stats(self, year: int) -> Dict[str, int]:
        """Get filing statistics."""
        return {}
    
    def _get_all_client_ids(self) -> List[int]:
        """Get all client IDs."""
        return []
    
    def _get_active_client_ids(self) -> List[int]:
        """Get active client IDs."""
        return []
    
    def _get_client_email(self, client_id: int) -> str:
        """Get client email."""
        return ""
    
    def _get_client_name(self, client_id: int) -> str:
        """Get client name."""
        return ""
    
    def _get_last_filing_year(self, client_id: int) -> int:
        """Get last year client filed."""
        return 0
    
    def _update_client_status(self, client_id: int, status: ClientStatus):
        """Update client status."""
        pass
    
    def _record_onboarding_completion(self, client_id: int, stage: str):
        """Record onboarding stage completion."""
        pass
    
    def _has_active_winback(self, client_id: int) -> bool:
        """Check if client has active win-back campaign."""
        return False
    
    def _should_start_winback(self, client_id: int) -> bool:
        """Check if win-back should be started."""
        return True
    
    def _save_winback_campaign(self, campaign: Dict) -> int:
        """Save win-back campaign."""
        return 0
    
    def _update_winback_campaign(self, campaign: Dict):
        """Update win-back campaign."""
        pass
    
    def _get_active_winback_campaigns(self) -> List[Dict]:
        """Get active win-back campaigns."""
        return []
    
    def _deactivate_winback_campaign(self, client_id: int, reason: str):
        """Deactivate win-back campaign."""
        pass
    
    def _schedule_winback_touch(self, campaign: Dict, step: int):
        """Schedule win-back touch."""
        pass
    
    def _winback_touch_due(self, campaign: Dict) -> bool:
        """Check if win-back touch is due."""
        return False
    
    def _client_responded(self, client_id: int) -> bool:
        """Check if client responded during campaign."""
        return False
