"""
Organizer Service
Kronos Tax Module - Tax organizer management and workflow
"""

from dataclasses import dataclass
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from enum import Enum

# Import models (relative imports for module)
from ..models import (
    TaxOrganizer, OrganizerStatus, OrganizerTemplate, OrganizerDashboard
)
from ..config.settings import ORGANIZER_CONFIG, ORGANIZER_TEMPLATES


class OrganizerService:
    """
    Service for managing tax organizers.
    
    Handles:
    - Creating and sending organizers
    - Tracking status (sent/opened/completed)
    - Auto-reminders
    - Progress monitoring
    """
    
    def __init__(self, db=None, email_service=None, portal_service=None):
        """
        Initialize organizer service.
        
        Args:
            db: Database connection (injected from Core Engine)
            email_service: Email service for sending organizers
            portal_service: Secure portal service (e.g., Encyro)
        """
        self.db = db
        self.email_service = email_service
        self.portal_service = portal_service
        self.config = ORGANIZER_CONFIG
    
    # =========================================================================
    # CORE OPERATIONS
    # =========================================================================
    
    def create_organizer(
        self,
        client_id: int,
        year: int,
        template: str = "w2_employee",
        deadline: date = None,
        **kwargs
    ) -> TaxOrganizer:
        """
        Create a new tax organizer for a client.
        
        Args:
            client_id: Client ID
            year: Tax year
            template: Organizer template name
            deadline: Custom deadline (default: 30 days from now)
            
        Returns:
            Created TaxOrganizer instance
        """
        # Validate template
        if template not in ORGANIZER_TEMPLATES:
            raise ValueError(f"Invalid template: {template}. Valid: {ORGANIZER_TEMPLATES}")
        
        # Set default deadline
        if deadline is None:
            deadline = date.today() + timedelta(days=self.config["default_deadline_days"])
        
        # Create organizer
        organizer = TaxOrganizer(
            client_id=client_id,
            year=year,
            template=OrganizerTemplate(template),
            status=OrganizerStatus.NOT_STARTED,
            deadline_date=deadline,
        )
        
        # Load template sections
        organizer.sections = self._load_template_sections(template)
        organizer.total_sections = len(organizer.sections)
        
        # Save to database
        if self.db:
            organizer.id = self._save_organizer(organizer)
        
        return organizer
    
    def send_organizer(
        self,
        organizer_id: int = None,
        organizer: TaxOrganizer = None,
        delivery_method: str = "email",
        email: str = None,
        custom_message: str = None
    ) -> TaxOrganizer:
        """
        Send organizer to client.
        
        Args:
            organizer_id: ID of existing organizer
            organizer: TaxOrganizer instance (alternative to ID)
            delivery_method: 'email', 'portal', or 'both'
            email: Override client email
            custom_message: Custom message to include
            
        Returns:
            Updated TaxOrganizer
        """
        # Get organizer
        if organizer is None:
            organizer = self.get_organizer(organizer_id)
        
        if organizer is None:
            raise ValueError("Organizer not found")
        
        # Get client email if not provided
        if email is None and self.db:
            email = self._get_client_email(organizer.client_id)
        
        portal_link = None
        
        # Send via portal
        if delivery_method in ["portal", "both"] and self.portal_service:
            portal_link = self.portal_service.create_organizer_link(
                client_id=organizer.client_id,
                organizer_id=organizer.id,
                template=organizer.template.value
            )
        
        # Send via email
        if delivery_method in ["email", "both"] and self.email_service:
            self._send_organizer_email(
                organizer=organizer,
                email=email,
                portal_link=portal_link,
                custom_message=custom_message
            )
        
        # Update status
        organizer.mark_sent(
            delivery_method=delivery_method,
            email=email,
            portal_link=portal_link
        )
        
        # Calculate first reminder date
        organizer.next_reminder_date = self._calculate_next_reminder(organizer)
        
        # Save
        if self.db:
            self._update_organizer(organizer)
        
        return organizer
    
    def get_organizer(self, organizer_id: int) -> Optional[TaxOrganizer]:
        """Get organizer by ID."""
        if self.db:
            return self._load_organizer(organizer_id)
        return None
    
    def get_client_organizers(
        self,
        client_id: int,
        year: int = None,
        status: OrganizerStatus = None
    ) -> List[TaxOrganizer]:
        """Get all organizers for a client."""
        if self.db:
            return self._load_client_organizers(client_id, year, status)
        return []
    
    # =========================================================================
    # STATUS UPDATES
    # =========================================================================
    
    def mark_opened(self, organizer_id: int) -> TaxOrganizer:
        """Mark organizer as opened by client."""
        organizer = self.get_organizer(organizer_id)
        if organizer:
            organizer.mark_opened()
            if self.db:
                self._update_organizer(organizer)
        return organizer
    
    def mark_in_progress(self, organizer_id: int) -> TaxOrganizer:
        """Mark organizer as in progress."""
        organizer = self.get_organizer(organizer_id)
        if organizer:
            organizer.mark_in_progress()
            if self.db:
                self._update_organizer(organizer)
        return organizer
    
    def mark_completed(self, organizer_id: int) -> TaxOrganizer:
        """Mark organizer as completed."""
        organizer = self.get_organizer(organizer_id)
        if organizer:
            organizer.mark_completed()
            if self.db:
                self._update_organizer(organizer)
            # Trigger post-completion actions
            self._on_organizer_completed(organizer)
        return organizer
    
    def update_progress(
        self,
        organizer_id: int,
        completed_sections: int
    ) -> TaxOrganizer:
        """Update organizer progress."""
        organizer = self.get_organizer(organizer_id)
        if organizer:
            organizer.update_progress(completed_sections)
            if self.db:
                self._update_organizer(organizer)
        return organizer
    
    # =========================================================================
    # REMINDERS
    # =========================================================================
    
    def send_reminder(
        self,
        organizer_id: int,
        custom_message: str = None
    ) -> TaxOrganizer:
        """Send reminder for incomplete organizer."""
        organizer = self.get_organizer(organizer_id)
        
        if organizer is None:
            raise ValueError("Organizer not found")
        
        if organizer.status == OrganizerStatus.COMPLETED:
            return organizer  # No reminder needed
        
        # Check max reminders
        if organizer.reminder_count >= self.config["max_reminders"]:
            if self.config["escalate_after_max"]:
                self._escalate_organizer(organizer)
            return organizer
        
        # Send reminder email
        if self.email_service:
            self._send_reminder_email(organizer, custom_message)
        
        # Update reminder tracking
        organizer.record_reminder()
        organizer.next_reminder_date = self._calculate_next_reminder(organizer)
        
        if self.db:
            self._update_organizer(organizer)
        
        return organizer
    
    def process_due_reminders(self) -> List[TaxOrganizer]:
        """
        Process all organizers that need reminders.
        Called by scheduled task.
        
        Returns:
            List of organizers that received reminders
        """
        reminded = []
        
        if self.db:
            due_organizers = self._get_due_reminders()
            for organizer in due_organizers:
                try:
                    self.send_reminder(organizer.id)
                    reminded.append(organizer)
                except Exception as e:
                    # Log error but continue processing
                    print(f"Reminder failed for organizer {organizer.id}: {e}")
        
        return reminded
    
    def _calculate_next_reminder(self, organizer: TaxOrganizer) -> Optional[datetime]:
        """Calculate next reminder date based on deadline."""
        if organizer.deadline_date is None:
            return None
        
        reminder_days = self.config["reminder_days"]
        days_until = organizer.days_until_deadline
        
        if days_until is None or days_until <= 0:
            # Overdue - remind daily
            return datetime.now() + timedelta(days=1)
        
        # Find next reminder threshold
        for days in sorted(reminder_days, reverse=True):
            if days_until > days:
                reminder_date = organizer.deadline_date - timedelta(days=days)
                return datetime.combine(reminder_date, 
                                       datetime.min.time().replace(
                                           hour=self.config["reminder_send_hour"]))
        
        return None
    
    # =========================================================================
    # DASHBOARD & REPORTING
    # =========================================================================
    
    def get_dashboard(self, year: int = None) -> OrganizerDashboard:
        """
        Get organizer dashboard statistics.
        
        Args:
            year: Filter by tax year (default: current)
            
        Returns:
            OrganizerDashboard with counts by status
        """
        if year is None:
            year = date.today().year - 1
        
        dashboard = OrganizerDashboard()
        
        if self.db:
            stats = self._get_organizer_stats(year)
            dashboard.total = stats.get("total", 0)
            dashboard.not_started = stats.get("not_started", 0)
            dashboard.sent = stats.get("sent", 0)
            dashboard.opened = stats.get("opened", 0)
            dashboard.in_progress = stats.get("in_progress", 0)
            dashboard.completed = stats.get("completed", 0)
            dashboard.overdue = stats.get("overdue", 0)
        
        return dashboard
    
    def get_status_breakdown(
        self,
        year: int = None,
        assigned_to: int = None
    ) -> Dict[str, int]:
        """Get count of organizers by status."""
        # Implementation depends on database
        return {
            "not_started": 0,
            "sent": 0,
            "opened": 0,
            "in_progress": 0,
            "completed": 0,
            "overdue": 0,
        }
    
    def get_overdue_organizers(self) -> List[TaxOrganizer]:
        """Get all overdue organizers."""
        if self.db:
            return self._load_overdue_organizers()
        return []
    
    def get_average_completion_time(self, year: int = None) -> float:
        """Get average days from sent to completed."""
        if self.db:
            return self._calculate_avg_completion_time(year)
        return 0.0
    
    # =========================================================================
    # TEMPLATE MANAGEMENT
    # =========================================================================
    
    def get_available_templates(self) -> List[str]:
        """Get list of available organizer templates."""
        return ORGANIZER_TEMPLATES
    
    def get_template_info(self, template: str) -> Dict[str, Any]:
        """Get details about a template."""
        return self._load_template_info(template)
    
    def _load_template_sections(self, template: str) -> List[Any]:
        """Load sections for a template."""
        # Template sections defined in templates/organizers/
        templates = {
            "w2_employee": [
                {"id": "personal", "name": "Personal Information", "required": True},
                {"id": "income", "name": "W-2 Income", "required": True},
                {"id": "deductions", "name": "Deductions", "required": False},
                {"id": "credits", "name": "Tax Credits", "required": False},
                {"id": "banking", "name": "Banking Information", "required": True},
            ],
            "self_employed": [
                {"id": "personal", "name": "Personal Information", "required": True},
                {"id": "business_info", "name": "Business Information", "required": True},
                {"id": "income_1099", "name": "1099 Income", "required": True},
                {"id": "expenses", "name": "Business Expenses", "required": True},
                {"id": "home_office", "name": "Home Office", "required": False},
                {"id": "vehicle", "name": "Vehicle Expenses", "required": False},
                {"id": "banking", "name": "Banking Information", "required": True},
            ],
            "rental_property": [
                {"id": "personal", "name": "Personal Information", "required": True},
                {"id": "property", "name": "Property Information", "required": True},
                {"id": "rental_income", "name": "Rental Income", "required": True},
                {"id": "rental_expenses", "name": "Property Expenses", "required": True},
                {"id": "depreciation", "name": "Depreciation", "required": True},
                {"id": "banking", "name": "Banking Information", "required": True},
            ],
        }
        return templates.get(template, templates["w2_employee"])
    
    def _load_template_info(self, template: str) -> Dict[str, Any]:
        """Get template metadata."""
        info = {
            "w2_employee": {
                "name": "W-2 Employee",
                "description": "Standard organizer for W-2 employees",
                "complexity": "basic",
                "estimated_time": "15-20 minutes",
            },
            "self_employed": {
                "name": "Self-Employed / Freelancer",
                "description": "For 1099 contractors and freelancers",
                "complexity": "moderate",
                "estimated_time": "30-45 minutes",
            },
            "small_business": {
                "name": "Small Business Owner",
                "description": "For Schedule C business owners",
                "complexity": "complex",
                "estimated_time": "45-60 minutes",
            },
            "rental_property": {
                "name": "Rental Property Owner",
                "description": "For Schedule E rental income",
                "complexity": "moderate",
                "estimated_time": "30-45 minutes",
            },
            "investment_income": {
                "name": "Investment Income",
                "description": "For stocks, dividends, capital gains",
                "complexity": "moderate",
                "estimated_time": "20-30 minutes",
            },
            "retirement": {
                "name": "Retirement Income",
                "description": "For retirees with pension, SS, RMDs",
                "complexity": "moderate",
                "estimated_time": "25-35 minutes",
            },
            "first_time_filer": {
                "name": "First-Time Filer",
                "description": "Simplified organizer for new filers",
                "complexity": "basic",
                "estimated_time": "10-15 minutes",
            },
            "multi_state": {
                "name": "Multi-State Filer",
                "description": "For income in multiple states",
                "complexity": "complex",
                "estimated_time": "40-50 minutes",
            },
            "high_net_worth": {
                "name": "High Net Worth",
                "description": "Comprehensive organizer for complex returns",
                "complexity": "very_complex",
                "estimated_time": "60+ minutes",
            },
        }
        return info.get(template, {"name": template, "complexity": "unknown"})
    
    # =========================================================================
    # INTERNAL HELPERS
    # =========================================================================
    
    def _send_organizer_email(
        self,
        organizer: TaxOrganizer,
        email: str,
        portal_link: str = None,
        custom_message: str = None
    ):
        """Send organizer email to client."""
        # Template: templates/emails/organizer_send.html
        subject = f"Your {organizer.year} Tax Organizer is Ready"
        
        template_vars = {
            "year": organizer.year,
            "deadline": organizer.deadline_date,
            "portal_link": portal_link,
            "custom_message": custom_message,
        }
        
        if self.email_service:
            self.email_service.send_template(
                to=email,
                subject=subject,
                template="organizer_send",
                variables=template_vars
            )
    
    def _send_reminder_email(
        self,
        organizer: TaxOrganizer,
        custom_message: str = None
    ):
        """Send reminder email."""
        email = self._get_client_email(organizer.client_id)
        days_left = organizer.days_until_deadline
        
        # Choose urgency level
        if days_left is not None and days_left <= 3:
            template = "organizer_reminder_urgent"
            subject = f"URGENT: Your {organizer.year} Tax Organizer - {days_left} Days Left"
        else:
            template = "organizer_reminder"
            subject = f"Reminder: Please Complete Your {organizer.year} Tax Organizer"
        
        template_vars = {
            "year": organizer.year,
            "deadline": organizer.deadline_date,
            "days_left": days_left,
            "portal_link": organizer.portal_link,
            "progress": organizer.progress_percentage,
            "custom_message": custom_message,
        }
        
        if self.email_service:
            self.email_service.send_template(
                to=email,
                subject=subject,
                template=template,
                variables=template_vars
            )
    
    def _escalate_organizer(self, organizer: TaxOrganizer):
        """Escalate organizer to admin after max reminders."""
        # Notify admin
        # Create task for manual follow-up
        pass
    
    def _on_organizer_completed(self, organizer: TaxOrganizer):
        """Handle post-completion actions."""
        # Send thank you email
        # Update client status
        # Create tax return record if needed
        pass
    
    def _get_client_email(self, client_id: int) -> str:
        """Get client email from database."""
        # Implementation depends on Core Engine integration
        return ""
    
    # =========================================================================
    # DATABASE OPERATIONS (Stubs - implemented with actual DB)
    # =========================================================================
    
    def _save_organizer(self, organizer: TaxOrganizer) -> int:
        """Save new organizer to database."""
        # INSERT INTO tax_organizers ...
        return 0
    
    def _update_organizer(self, organizer: TaxOrganizer):
        """Update organizer in database."""
        # UPDATE tax_organizers SET ... WHERE id = ...
        pass
    
    def _load_organizer(self, organizer_id: int) -> Optional[TaxOrganizer]:
        """Load organizer from database."""
        # SELECT * FROM tax_organizers WHERE id = ...
        return None
    
    def _load_client_organizers(
        self,
        client_id: int,
        year: int = None,
        status: OrganizerStatus = None
    ) -> List[TaxOrganizer]:
        """Load all organizers for a client."""
        # SELECT * FROM tax_organizers WHERE client_id = ...
        return []
    
    def _load_overdue_organizers(self) -> List[TaxOrganizer]:
        """Load all overdue organizers."""
        # SELECT * FROM tax_organizers 
        # WHERE deadline_date < NOW() AND status != 'completed'
        return []
    
    def _get_due_reminders(self) -> List[TaxOrganizer]:
        """Get organizers due for reminder."""
        # SELECT * FROM tax_organizers
        # WHERE next_reminder_date <= NOW() AND status NOT IN ('completed', 'not_started')
        return []
    
    def _get_organizer_stats(self, year: int) -> Dict[str, int]:
        """Get organizer statistics for year."""
        # SELECT status, COUNT(*) FROM tax_organizers WHERE year = ... GROUP BY status
        return {}
    
    def _calculate_avg_completion_time(self, year: int = None) -> float:
        """Calculate average completion time."""
        # SELECT AVG(EXTRACT(DAY FROM completed_date - sent_date))
        # FROM tax_organizers WHERE status = 'completed'
        return 0.0
