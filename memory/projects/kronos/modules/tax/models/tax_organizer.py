"""
Tax Organizer Model
Kronos Tax Module - Data model for tax organizers
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class OrganizerStatus(Enum):
    """Tax organizer statuses."""
    NOT_STARTED = "not_started"
    SENT = "sent"
    DELIVERED = "delivered"
    OPENED = "opened"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    EXPIRED = "expired"


class OrganizerTemplate(Enum):
    """Available organizer templates."""
    W2_EMPLOYEE = "w2_employee"
    SELF_EMPLOYED = "self_employed"
    SMALL_BUSINESS = "small_business"
    RENTAL_PROPERTY = "rental_property"
    INVESTMENT_INCOME = "investment_income"
    RETIREMENT = "retirement"
    FIRST_TIME_FILER = "first_time_filer"
    MULTI_STATE = "multi_state"
    EXPAT = "expat"
    HIGH_NET_WORTH = "high_net_worth"


@dataclass
class OrganizerSection:
    """A section within a tax organizer."""
    id: str
    name: str
    description: str
    required: bool = True
    completed: bool = False
    fields: List[Dict[str, Any]] = field(default_factory=list)
    documents_required: List[str] = field(default_factory=list)
    documents_uploaded: List[int] = field(default_factory=list)  # File IDs


@dataclass
class TaxOrganizer:
    """
    Tax Organizer data model.
    
    Represents a tax organizer sent to collect client information
    and documents for tax preparation.
    """
    id: Optional[int] = None
    client_id: int = 0
    year: int = 0
    
    # Template & status
    template: OrganizerTemplate = OrganizerTemplate.W2_EMPLOYEE
    status: OrganizerStatus = OrganizerStatus.NOT_STARTED
    
    # Tracking dates
    created_date: datetime = field(default_factory=datetime.now)
    sent_date: Optional[datetime] = None
    delivered_date: Optional[datetime] = None
    opened_date: Optional[datetime] = None
    started_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    
    # Deadline & reminders
    deadline_date: Optional[date] = None
    reminder_count: int = 0
    last_reminder_date: Optional[datetime] = None
    next_reminder_date: Optional[datetime] = None
    
    # Progress tracking
    total_sections: int = 0
    completed_sections: int = 0
    sections: List[OrganizerSection] = field(default_factory=list)
    
    # Delivery method
    delivery_method: str = "email"  # email, portal, both
    delivery_email: Optional[str] = None
    portal_link: Optional[str] = None
    secure_access_code: Optional[str] = None
    
    # Associated records
    return_id: Optional[int] = None
    document_ids: List[int] = field(default_factory=list)
    
    # Notes
    client_notes: Optional[str] = None
    internal_notes: Optional[str] = None
    
    # Timestamps
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Set default deadline if not provided."""
        if self.deadline_date is None and self.year:
            # Default deadline: March 15 of filing year
            self.deadline_date = date(self.year + 1, 3, 15)
    
    @property
    def progress_percentage(self) -> float:
        """Calculate completion percentage."""
        if self.total_sections == 0:
            return 0.0
        return (self.completed_sections / self.total_sections) * 100
    
    @property
    def is_overdue(self) -> bool:
        """Check if organizer is past deadline and incomplete."""
        if self.status == OrganizerStatus.COMPLETED:
            return False
        if self.deadline_date is None:
            return False
        return date.today() > self.deadline_date
    
    @property
    def days_until_deadline(self) -> Optional[int]:
        """Days remaining until deadline."""
        if self.deadline_date is None:
            return None
        if self.status == OrganizerStatus.COMPLETED:
            return None
        delta = self.deadline_date - date.today()
        return delta.days
    
    @property
    def needs_reminder(self) -> bool:
        """Check if a reminder should be sent."""
        if self.status in [OrganizerStatus.NOT_STARTED, OrganizerStatus.COMPLETED]:
            return False
        if self.next_reminder_date is None:
            return False
        return datetime.now() >= self.next_reminder_date
    
    @property
    def days_since_sent(self) -> Optional[int]:
        """Days since organizer was sent."""
        if self.sent_date is None:
            return None
        delta = datetime.now() - self.sent_date
        return delta.days
    
    @property
    def response_time_days(self) -> Optional[int]:
        """Days between sent and completed."""
        if self.sent_date is None or self.completed_date is None:
            return None
        delta = self.completed_date - self.sent_date
        return delta.days
    
    def mark_sent(self, delivery_method: str = "email", 
                  email: str = None, portal_link: str = None):
        """Mark organizer as sent."""
        self.status = OrganizerStatus.SENT
        self.sent_date = datetime.now()
        self.delivery_method = delivery_method
        self.delivery_email = email
        self.portal_link = portal_link
        self.updated_at = datetime.now()
    
    def mark_opened(self):
        """Mark organizer as opened by client."""
        self.status = OrganizerStatus.OPENED
        self.opened_date = datetime.now()
        self.updated_at = datetime.now()
    
    def mark_in_progress(self):
        """Mark organizer as in progress."""
        self.status = OrganizerStatus.IN_PROGRESS
        if self.started_date is None:
            self.started_date = datetime.now()
        self.updated_at = datetime.now()
    
    def mark_completed(self):
        """Mark organizer as completed."""
        self.status = OrganizerStatus.COMPLETED
        self.completed_date = datetime.now()
        self.completed_sections = self.total_sections
        self.updated_at = datetime.now()
    
    def record_reminder(self):
        """Record that a reminder was sent."""
        self.reminder_count += 1
        self.last_reminder_date = datetime.now()
        self.updated_at = datetime.now()
    
    def update_progress(self, completed_sections: int):
        """Update section completion progress."""
        self.completed_sections = completed_sections
        if completed_sections > 0 and self.status == OrganizerStatus.OPENED:
            self.mark_in_progress()
        if completed_sections >= self.total_sections:
            self.mark_completed()
        self.updated_at = datetime.now()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "client_id": self.client_id,
            "year": self.year,
            "template": self.template.value,
            "status": self.status.value,
            "created_date": self.created_date.isoformat(),
            "sent_date": self.sent_date.isoformat() if self.sent_date else None,
            "opened_date": self.opened_date.isoformat() if self.opened_date else None,
            "completed_date": self.completed_date.isoformat() if self.completed_date else None,
            "deadline_date": self.deadline_date.isoformat() if self.deadline_date else None,
            "reminder_count": self.reminder_count,
            "progress_percentage": self.progress_percentage,
            "total_sections": self.total_sections,
            "completed_sections": self.completed_sections,
            "delivery_method": self.delivery_method,
            "portal_link": self.portal_link,
            "is_overdue": self.is_overdue,
            "days_until_deadline": self.days_until_deadline,
            "days_since_sent": self.days_since_sent,
            "updated_at": self.updated_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "TaxOrganizer":
        """Create TaxOrganizer from dictionary."""
        return cls(
            id=data.get("id"),
            client_id=data.get("client_id", 0),
            year=data.get("year", 0),
            template=OrganizerTemplate(data.get("template", "w2_employee")),
            status=OrganizerStatus(data.get("status", "not_started")),
            deadline_date=date.fromisoformat(data["deadline_date"]) if data.get("deadline_date") else None,
            reminder_count=data.get("reminder_count", 0),
            total_sections=data.get("total_sections", 0),
            completed_sections=data.get("completed_sections", 0),
            delivery_method=data.get("delivery_method", "email"),
            portal_link=data.get("portal_link"),
        )


@dataclass
class OrganizerDashboard:
    """Dashboard summary for organizer statuses."""
    total: int = 0
    not_started: int = 0
    sent: int = 0
    opened: int = 0
    in_progress: int = 0
    completed: int = 0
    overdue: int = 0
    
    @property
    def completion_rate(self) -> float:
        """Percentage of organizers completed."""
        if self.total == 0:
            return 0.0
        return (self.completed / self.total) * 100
    
    @property
    def response_rate(self) -> float:
        """Percentage that have been opened or completed."""
        if self.total == 0:
            return 0.0
        responded = self.opened + self.in_progress + self.completed
        return (responded / self.total) * 100
    
    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "not_started": self.not_started,
            "sent": self.sent,
            "opened": self.opened,
            "in_progress": self.in_progress,
            "completed": self.completed,
            "overdue": self.overdue,
            "completion_rate": self.completion_rate,
            "response_rate": self.response_rate,
        }
