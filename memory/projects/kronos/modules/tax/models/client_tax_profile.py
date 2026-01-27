"""
Client Tax Profile Model
Kronos Tax Module - Extended client profile for tax-specific data
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional, List, Dict
from enum import Enum


class TaxSituation(Enum):
    """Client tax situation types."""
    W2_EMPLOYEE = "w2_employee"
    SELF_EMPLOYED = "self_employed"
    BUSINESS_OWNER = "business_owner"
    RETIRED = "retired"
    INVESTOR = "investor"
    RENTAL_OWNER = "rental_owner"
    HIGH_NET_WORTH = "high_net_worth"
    MULTI_STATE = "multi_state"
    EXPAT = "expat"
    FIRST_TIME = "first_time"


class FilingFrequency(Enum):
    """How often client files."""
    ANNUAL = "annual"
    QUARTERLY = "quarterly"  # Estimated payments
    MONTHLY = "monthly"      # Payroll


class PreferredContact(Enum):
    """Client communication preference."""
    EMAIL = "email"
    PHONE = "phone"
    SMS = "sms"
    PORTAL = "portal"


@dataclass
class ClientTaxProfile:
    """
    Extended client profile for tax-specific information.
    
    This extends the core Client model with tax-related data.
    """
    id: Optional[int] = None
    client_id: int = 0  # FK to core clients table
    
    # Tax situation
    tax_situation: TaxSituation = TaxSituation.W2_EMPLOYEE
    filing_frequency: FilingFrequency = FilingFrequency.ANNUAL
    
    # Filing status (IRS filing status)
    irs_filing_status: str = "single"  # single, married_joint, married_separate, head_of_household
    
    # Dependents
    has_dependents: bool = False
    dependent_count: int = 0
    
    # Income sources
    has_w2_income: bool = True
    has_1099_income: bool = False
    has_business_income: bool = False
    has_rental_income: bool = False
    has_investment_income: bool = False
    has_retirement_income: bool = False
    
    # Special situations
    has_foreign_accounts: bool = False
    has_cryptocurrency: bool = False
    is_self_employed: bool = False
    owns_rental_property: bool = False
    has_stock_options: bool = False
    
    # Multi-state
    states_filed: List[str] = field(default_factory=list)  # State abbreviations
    primary_state: Optional[str] = None
    
    # Preferences
    preferred_contact: PreferredContact = PreferredContact.EMAIL
    prefers_refund_direct_deposit: bool = True
    prefers_extension: bool = False
    
    # Banking (for direct deposit - encrypted)
    has_banking_on_file: bool = False
    
    # History
    client_since_year: Optional[int] = None
    years_filed: List[int] = field(default_factory=list)
    consecutive_years: int = 0
    
    # Pricing
    standard_fee: Optional[float] = None
    fee_tier: str = "standard"  # basic, standard, complex, premium
    
    # Important dates
    birthday: Optional[date] = None  # For retirement planning
    spouse_birthday: Optional[date] = None
    
    # Notes
    special_instructions: Optional[str] = None
    tax_notes: Optional[str] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    @property
    def complexity_score(self) -> int:
        """Calculate return complexity (1-10 scale)."""
        score = 1
        
        # Income complexity
        if self.has_1099_income:
            score += 1
        if self.has_business_income:
            score += 2
        if self.has_rental_income:
            score += 2
        if self.has_investment_income:
            score += 1
        
        # Special situations
        if self.has_foreign_accounts:
            score += 2
        if self.has_cryptocurrency:
            score += 1
        if self.has_stock_options:
            score += 1
        
        # Multi-state
        if len(self.states_filed) > 1:
            score += len(self.states_filed) - 1
        
        return min(score, 10)
    
    @property
    def recommended_template(self) -> str:
        """Suggest the best organizer template."""
        if self.tax_situation == TaxSituation.HIGH_NET_WORTH:
            return "high_net_worth"
        if self.has_business_income or self.is_self_employed:
            return "small_business"
        if self.has_rental_income:
            return "rental_property"
        if self.tax_situation == TaxSituation.RETIRED:
            return "retirement"
        if self.has_1099_income:
            return "self_employed"
        if len(self.states_filed) > 1:
            return "multi_state"
        if self.tax_situation == TaxSituation.FIRST_TIME:
            return "first_time_filer"
        return "w2_employee"
    
    @property
    def is_high_value(self) -> bool:
        """Check if client is high-value based on fee tier."""
        return self.fee_tier in ["complex", "premium"]
    
    @property
    def retention_priority(self) -> str:
        """Calculate retention priority."""
        if self.is_high_value:
            return "high"
        if self.consecutive_years >= 5:
            return "high"
        if self.consecutive_years >= 3:
            return "medium"
        return "standard"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "client_id": self.client_id,
            "tax_situation": self.tax_situation.value,
            "filing_frequency": self.filing_frequency.value,
            "irs_filing_status": self.irs_filing_status,
            "has_dependents": self.has_dependents,
            "dependent_count": self.dependent_count,
            "has_w2_income": self.has_w2_income,
            "has_1099_income": self.has_1099_income,
            "has_business_income": self.has_business_income,
            "has_rental_income": self.has_rental_income,
            "has_investment_income": self.has_investment_income,
            "has_retirement_income": self.has_retirement_income,
            "has_foreign_accounts": self.has_foreign_accounts,
            "has_cryptocurrency": self.has_cryptocurrency,
            "is_self_employed": self.is_self_employed,
            "owns_rental_property": self.owns_rental_property,
            "states_filed": self.states_filed,
            "primary_state": self.primary_state,
            "preferred_contact": self.preferred_contact.value,
            "client_since_year": self.client_since_year,
            "years_filed": self.years_filed,
            "consecutive_years": self.consecutive_years,
            "fee_tier": self.fee_tier,
            "complexity_score": self.complexity_score,
            "recommended_template": self.recommended_template,
            "retention_priority": self.retention_priority,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ClientTaxProfile":
        """Create ClientTaxProfile from dictionary."""
        return cls(
            id=data.get("id"),
            client_id=data.get("client_id", 0),
            tax_situation=TaxSituation(data.get("tax_situation", "w2_employee")),
            filing_frequency=FilingFrequency(data.get("filing_frequency", "annual")),
            irs_filing_status=data.get("irs_filing_status", "single"),
            has_dependents=data.get("has_dependents", False),
            dependent_count=data.get("dependent_count", 0),
            has_w2_income=data.get("has_w2_income", True),
            has_1099_income=data.get("has_1099_income", False),
            has_business_income=data.get("has_business_income", False),
            has_rental_income=data.get("has_rental_income", False),
            has_investment_income=data.get("has_investment_income", False),
            has_retirement_income=data.get("has_retirement_income", False),
            has_foreign_accounts=data.get("has_foreign_accounts", False),
            has_cryptocurrency=data.get("has_cryptocurrency", False),
            is_self_employed=data.get("is_self_employed", False),
            owns_rental_property=data.get("owns_rental_property", False),
            states_filed=data.get("states_filed", []),
            primary_state=data.get("primary_state"),
            preferred_contact=PreferredContact(data.get("preferred_contact", "email")),
            client_since_year=data.get("client_since_year"),
            years_filed=data.get("years_filed", []),
            consecutive_years=data.get("consecutive_years", 0),
            fee_tier=data.get("fee_tier", "standard"),
        )
