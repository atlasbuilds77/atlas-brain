"""
Tax Document Model
Kronos Tax Module - Document classification and tracking
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional, List
from enum import Enum


class DocumentType(Enum):
    """Tax document types."""
    # Income documents
    W2 = "w2"
    W2_G = "w2_g"                    # Gambling winnings
    FORM_1099_NEC = "1099_nec"       # Non-employee compensation
    FORM_1099_MISC = "1099_misc"     # Miscellaneous income
    FORM_1099_INT = "1099_int"       # Interest income
    FORM_1099_DIV = "1099_div"       # Dividends
    FORM_1099_B = "1099_b"           # Broker transactions
    FORM_1099_R = "1099_r"           # Retirement distributions
    FORM_1099_G = "1099_g"           # Government payments
    FORM_1099_S = "1099_s"           # Real estate proceeds
    FORM_1099_K = "1099_k"           # Payment card transactions
    K1 = "k1"                        # Partnership/S-corp income
    SSA_1099 = "ssa_1099"            # Social security benefits
    
    # Deduction documents
    FORM_1098 = "1098"               # Mortgage interest
    FORM_1098_E = "1098_e"           # Student loan interest
    FORM_1098_T = "1098_t"           # Tuition statement
    PROPERTY_TAX = "property_tax"
    CHARITABLE_RECEIPT = "charitable"
    MEDICAL_RECEIPT = "medical"
    BUSINESS_EXPENSE = "business_expense"
    
    # Identity documents
    DRIVERS_LICENSE = "drivers_license"
    SOCIAL_SECURITY_CARD = "ssn_card"
    PASSPORT = "passport"
    
    # Other
    PRIOR_YEAR_RETURN = "prior_return"
    ESTIMATED_PAYMENTS = "estimated_payments"
    BANK_STATEMENT = "bank_statement"
    OTHER = "other"


class DocumentStatus(Enum):
    """Document processing status."""
    REQUESTED = "requested"
    UPLOADED = "uploaded"
    RECEIVED = "received"
    VERIFIED = "verified"
    PROCESSED = "processed"
    REJECTED = "rejected"


class SensitivityLevel(Enum):
    """Document sensitivity classification."""
    PUBLIC = "public"           # Non-sensitive
    INTERNAL = "internal"       # Internal use
    CONFIDENTIAL = "confidential"  # Contains financial data
    HIGHLY_CONFIDENTIAL = "highly_confidential"  # Contains SSN, etc.


@dataclass
class TaxDocument:
    """
    Tax document data model.
    
    Represents a document related to tax preparation.
    """
    id: Optional[int] = None
    client_id: int = 0
    return_id: Optional[int] = None  # FK to tax_returns
    organizer_id: Optional[int] = None  # FK to tax_organizers
    
    # Document classification
    document_type: DocumentType = DocumentType.OTHER
    status: DocumentStatus = DocumentStatus.REQUESTED
    sensitivity: SensitivityLevel = SensitivityLevel.CONFIDENTIAL
    
    # File information
    file_id: Optional[int] = None  # FK to core files table
    filename: Optional[str] = None
    file_path: Optional[str] = None  # Encrypted storage path
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    
    # Tax year
    tax_year: int = 0
    
    # Metadata
    description: Optional[str] = None
    issuer: Optional[str] = None  # Who issued the document (employer, bank, etc.)
    amount: Optional[float] = None  # Key amount from document
    
    # Security
    encrypted: bool = True
    encryption_key_id: Optional[str] = None
    checksum: Optional[str] = None
    
    # Dates
    document_date: Optional[date] = None  # Date on the document
    received_date: Optional[datetime] = None
    processed_date: Optional[datetime] = None
    retention_until: Optional[date] = None
    
    # Processing
    verified_by: Optional[int] = None  # User ID
    verification_notes: Optional[str] = None
    ocr_extracted: bool = False
    extracted_data: Optional[dict] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Set default retention period."""
        if self.retention_until is None and self.tax_year:
            # 3-year retention from end of tax year
            self.retention_until = date(self.tax_year + 4, 4, 15)
        
        # Auto-classify sensitivity based on document type
        if self.document_type in [DocumentType.DRIVERS_LICENSE, 
                                   DocumentType.SOCIAL_SECURITY_CARD,
                                   DocumentType.PASSPORT]:
            self.sensitivity = SensitivityLevel.HIGHLY_CONFIDENTIAL
    
    @property
    def is_income_document(self) -> bool:
        """Check if document is an income form."""
        income_types = [
            DocumentType.W2, DocumentType.W2_G,
            DocumentType.FORM_1099_NEC, DocumentType.FORM_1099_MISC,
            DocumentType.FORM_1099_INT, DocumentType.FORM_1099_DIV,
            DocumentType.FORM_1099_B, DocumentType.FORM_1099_R,
            DocumentType.FORM_1099_G, DocumentType.FORM_1099_S,
            DocumentType.FORM_1099_K, DocumentType.K1,
            DocumentType.SSA_1099,
        ]
        return self.document_type in income_types
    
    @property
    def is_identity_document(self) -> bool:
        """Check if document is an identity document."""
        identity_types = [
            DocumentType.DRIVERS_LICENSE,
            DocumentType.SOCIAL_SECURITY_CARD,
            DocumentType.PASSPORT,
        ]
        return self.document_type in identity_types
    
    @property
    def requires_encryption(self) -> bool:
        """Check if document must be encrypted."""
        return self.sensitivity in [
            SensitivityLevel.CONFIDENTIAL,
            SensitivityLevel.HIGHLY_CONFIDENTIAL
        ]
    
    @property
    def days_until_expiration(self) -> Optional[int]:
        """Days until retention period expires."""
        if self.retention_until is None:
            return None
        delta = self.retention_until - date.today()
        return delta.days
    
    def mark_received(self):
        """Mark document as received."""
        self.status = DocumentStatus.RECEIVED
        self.received_date = datetime.now()
        self.updated_at = datetime.now()
    
    def mark_verified(self, user_id: int, notes: str = None):
        """Mark document as verified."""
        self.status = DocumentStatus.VERIFIED
        self.verified_by = user_id
        self.verification_notes = notes
        self.updated_at = datetime.now()
    
    def mark_processed(self):
        """Mark document as processed."""
        self.status = DocumentStatus.PROCESSED
        self.processed_date = datetime.now()
        self.updated_at = datetime.now()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "client_id": self.client_id,
            "return_id": self.return_id,
            "organizer_id": self.organizer_id,
            "document_type": self.document_type.value,
            "status": self.status.value,
            "sensitivity": self.sensitivity.value,
            "file_id": self.file_id,
            "filename": self.filename,
            "tax_year": self.tax_year,
            "description": self.description,
            "issuer": self.issuer,
            "amount": self.amount,
            "encrypted": self.encrypted,
            "document_date": self.document_date.isoformat() if self.document_date else None,
            "received_date": self.received_date.isoformat() if self.received_date else None,
            "processed_date": self.processed_date.isoformat() if self.processed_date else None,
            "retention_until": self.retention_until.isoformat() if self.retention_until else None,
            "is_income_document": self.is_income_document,
            "requires_encryption": self.requires_encryption,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "TaxDocument":
        """Create TaxDocument from dictionary."""
        return cls(
            id=data.get("id"),
            client_id=data.get("client_id", 0),
            return_id=data.get("return_id"),
            organizer_id=data.get("organizer_id"),
            document_type=DocumentType(data.get("document_type", "other")),
            status=DocumentStatus(data.get("status", "requested")),
            sensitivity=SensitivityLevel(data.get("sensitivity", "confidential")),
            file_id=data.get("file_id"),
            filename=data.get("filename"),
            file_path=data.get("file_path"),
            tax_year=data.get("tax_year", 0),
            description=data.get("description"),
            issuer=data.get("issuer"),
            amount=data.get("amount"),
            encrypted=data.get("encrypted", True),
        )


@dataclass
class DocumentChecklist:
    """Checklist of required documents for a return."""
    client_id: int
    tax_year: int
    required_documents: List[DocumentType] = field(default_factory=list)
    received_documents: List[DocumentType] = field(default_factory=list)
    
    @property
    def missing_documents(self) -> List[DocumentType]:
        """Get list of missing documents."""
        return [d for d in self.required_documents if d not in self.received_documents]
    
    @property
    def completion_percentage(self) -> float:
        """Calculate checklist completion."""
        if not self.required_documents:
            return 100.0
        return (len(self.received_documents) / len(self.required_documents)) * 100
    
    @property
    def is_complete(self) -> bool:
        """Check if all required documents received."""
        return len(self.missing_documents) == 0
    
    def to_dict(self) -> dict:
        return {
            "client_id": self.client_id,
            "tax_year": self.tax_year,
            "required": [d.value for d in self.required_documents],
            "received": [d.value for d in self.received_documents],
            "missing": [d.value for d in self.missing_documents],
            "completion_percentage": self.completion_percentage,
            "is_complete": self.is_complete,
        }
