"""
Tax Return Model
Kronos Tax Module - Data model for tax returns
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional, List
from enum import Enum


class FilingStatus(Enum):
    """Tax return filing statuses."""
    NOT_STARTED = "not_started"
    ORGANIZER_SENT = "organizer_sent"
    DOCUMENTS_PENDING = "documents_pending"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    READY_TO_FILE = "ready_to_file"
    FILED = "filed"
    EXTENDED = "extended"
    AMENDED = "amended"


class FilingType(Enum):
    """Types of tax returns."""
    PERSONAL = "personal"
    BUSINESS = "business"
    PARTNERSHIP = "partnership"
    S_CORP = "s_corp"
    C_CORP = "c_corp"
    TRUST = "trust"
    ESTATE = "estate"
    NONPROFIT = "nonprofit"


@dataclass
class TaxReturn:
    """
    Tax Return data model.
    
    Represents a single tax return for a client/year combination.
    """
    id: Optional[int] = None
    client_id: int = 0
    year: int = 0
    
    # Filing details
    status: FilingStatus = FilingStatus.NOT_STARTED
    filing_type: FilingType = FilingType.PERSONAL
    
    # Key dates
    filed_date: Optional[date] = None
    extension_date: Optional[date] = None
    deadline: Optional[date] = None
    
    # Assignment
    assigned_to: Optional[int] = None  # User ID of preparer
    reviewer_id: Optional[int] = None  # User ID of reviewer
    
    # Financial
    refund_amount: Optional[float] = None
    amount_due: Optional[float] = None
    fee_charged: Optional[float] = None
    
    # Flags
    is_complex: bool = False
    needs_extension: bool = False
    has_issues: bool = False
    
    # Related records
    organizer_id: Optional[int] = None
    document_ids: List[int] = field(default_factory=list)
    
    # Notes
    preparer_notes: Optional[str] = None
    client_notes: Optional[str] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Set default deadline based on filing type."""
        if self.deadline is None and self.year:
            if self.filing_type in [FilingType.BUSINESS, FilingType.PARTNERSHIP, 
                                     FilingType.S_CORP]:
                # Business returns due March 15
                self.deadline = date(self.year + 1, 3, 15)
            else:
                # Personal returns due April 15
                self.deadline = date(self.year + 1, 4, 15)
    
    @property
    def is_overdue(self) -> bool:
        """Check if return is past deadline and not filed."""
        if self.status in [FilingStatus.FILED, FilingStatus.EXTENDED]:
            return False
        if self.deadline is None:
            return False
        return date.today() > self.deadline
    
    @property
    def days_until_deadline(self) -> Optional[int]:
        """Days remaining until deadline."""
        if self.deadline is None:
            return None
        if self.status in [FilingStatus.FILED, FilingStatus.EXTENDED]:
            return None
        delta = self.deadline - date.today()
        return delta.days
    
    @property
    def is_complete(self) -> bool:
        """Check if return is filed or extended."""
        return self.status in [FilingStatus.FILED, FilingStatus.EXTENDED]
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "client_id": self.client_id,
            "year": self.year,
            "status": self.status.value,
            "filing_type": self.filing_type.value,
            "filed_date": self.filed_date.isoformat() if self.filed_date else None,
            "extension_date": self.extension_date.isoformat() if self.extension_date else None,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "assigned_to": self.assigned_to,
            "reviewer_id": self.reviewer_id,
            "refund_amount": self.refund_amount,
            "amount_due": self.amount_due,
            "fee_charged": self.fee_charged,
            "is_complex": self.is_complex,
            "needs_extension": self.needs_extension,
            "has_issues": self.has_issues,
            "organizer_id": self.organizer_id,
            "document_ids": self.document_ids,
            "preparer_notes": self.preparer_notes,
            "is_overdue": self.is_overdue,
            "days_until_deadline": self.days_until_deadline,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "TaxReturn":
        """Create TaxReturn from dictionary."""
        return cls(
            id=data.get("id"),
            client_id=data.get("client_id", 0),
            year=data.get("year", 0),
            status=FilingStatus(data.get("status", "not_started")),
            filing_type=FilingType(data.get("filing_type", "personal")),
            filed_date=date.fromisoformat(data["filed_date"]) if data.get("filed_date") else None,
            extension_date=date.fromisoformat(data["extension_date"]) if data.get("extension_date") else None,
            deadline=date.fromisoformat(data["deadline"]) if data.get("deadline") else None,
            assigned_to=data.get("assigned_to"),
            reviewer_id=data.get("reviewer_id"),
            refund_amount=data.get("refund_amount"),
            amount_due=data.get("amount_due"),
            fee_charged=data.get("fee_charged"),
            is_complex=data.get("is_complex", False),
            needs_extension=data.get("needs_extension", False),
            has_issues=data.get("has_issues", False),
            organizer_id=data.get("organizer_id"),
            document_ids=data.get("document_ids", []),
            preparer_notes=data.get("preparer_notes"),
            client_notes=data.get("client_notes"),
        )


@dataclass
class TaxReturnSummary:
    """Summary statistics for tax returns."""
    total_returns: int = 0
    filed: int = 0
    extended: int = 0
    in_progress: int = 0
    not_started: int = 0
    overdue: int = 0
    total_refunds: float = 0.0
    total_due: float = 0.0
    total_fees: float = 0.0
    
    @property
    def completion_rate(self) -> float:
        """Percentage of returns completed."""
        if self.total_returns == 0:
            return 0.0
        return (self.filed + self.extended) / self.total_returns * 100
    
    def to_dict(self) -> dict:
        return {
            "total_returns": self.total_returns,
            "filed": self.filed,
            "extended": self.extended,
            "in_progress": self.in_progress,
            "not_started": self.not_started,
            "overdue": self.overdue,
            "completion_rate": self.completion_rate,
            "total_refunds": self.total_refunds,
            "total_due": self.total_due,
            "total_fees": self.total_fees,
        }
