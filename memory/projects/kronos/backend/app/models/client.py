"""Client model - Active client management"""

from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Enum as SQLEnum, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.db.session import Base


class ClientStatus(str, enum.Enum):
    """Client status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    CHURNED = "churned"
    ONBOARDING = "onboarding"


class Client(Base):
    """Client model - converted leads / active clients"""
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=True)  # Track conversion source
    
    # Status
    status = Column(SQLEnum(ClientStatus), default=ClientStatus.ONBOARDING, nullable=False, index=True)
    
    # Business metrics
    lifetime_value = Column(Float, default=0.0)
    retention_risk_score = Column(Float, default=0.0)  # 0-1, AI-predicted churn risk
    
    # Communication tracking
    last_interaction = Column(DateTime(timezone=True))
    next_followup = Column(DateTime(timezone=True))
    preferred_contact_method = Column(String)  # email, phone, sms
    
    # Metadata
    custom_fields = Column(JSON, default=dict)  # Industry-specific data
    tags = Column(JSON, default=list)
    
    # Timestamps
    client_since = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="clients")
    files = relationship("File", back_populates="client", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="client", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Client {self.user_id} - {self.status}>"
