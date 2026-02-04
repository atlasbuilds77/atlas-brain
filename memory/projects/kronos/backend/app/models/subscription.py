"""Subscription model - Multi-product subscription management"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.db.session import Base


class SubscriptionStatus(str, enum.Enum):
    """Subscription status types"""
    ACTIVE = "active"
    CANCELED = "canceled"
    PAST_DUE = "past_due"
    NONE = "none"


class ProductType(str, enum.Enum):
    """Product types"""
    AUTOMATION = "automation"
    NEBULA = "nebula"


class Subscription(Base):
    """Subscription model - supports multiple products per user"""
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_type = Column(SQLEnum(ProductType), nullable=False)
    stripe_subscription_id = Column(String(255), unique=True, nullable=True)
    status = Column(SQLEnum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.NONE)
    current_period_end = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")
    
    def __repr__(self):
        return f"<Subscription user_id={self.user_id} product={self.product_type} status={self.status}>"
    
    @property
    def is_active(self) -> bool:
        """Check if subscription is currently active"""
        return self.status == SubscriptionStatus.ACTIVE
