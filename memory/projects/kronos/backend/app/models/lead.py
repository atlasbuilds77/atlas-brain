"""Lead model - Lead management and tracking"""

from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Enum as SQLEnum, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.db.session import Base


class LeadStatus(str, enum.Enum):
    """Lead status options"""
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    CONVERTED = "converted"
    DEAD = "dead"


class LeadSource(str, enum.Enum):
    """Lead source tracking"""
    WEBSITE = "website"
    REFERRAL = "referral"
    SOCIAL = "social"
    EMAIL = "email"
    PHONE = "phone"
    OTHER = "other"


class Lead(Base):
    """Lead model - potential clients"""
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Links to user if they sign up
    
    # Basic info
    name = Column(String, nullable=False)
    email = Column(String, index=True)
    phone = Column(String)
    company = Column(String)
    
    # Lead tracking
    status = Column(SQLEnum(LeadStatus), default=LeadStatus.NEW, nullable=False, index=True)
    source = Column(SQLEnum(LeadSource), default=LeadSource.OTHER, nullable=False)
    lead_score = Column(Float, default=0.0)  # AI-calculated score
    
    # Assignment and tracking
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Notes and metadata
    notes = Column(Text)
    tags = Column(JSON, default=list)  # ["tax", "small-business", etc.]
    custom_fields = Column(JSON, default=dict)  # Industry-specific data
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    contacted_at = Column(DateTime(timezone=True))
    converted_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="leads")
    
    def __repr__(self):
        return f"<Lead {self.name} - {self.status}>"
