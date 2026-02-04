"""User model - Authentication and user management"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.db.session import Base


class UserRole(str, enum.Enum):
    """User roles"""
    ADMIN = "admin"
    CLIENT = "client"
    LEAD = "lead"


class User(Base):
    """User model - core authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Discord OAuth
    discord_id = Column(String, unique=True, nullable=True)
    discord_username = Column(String, nullable=True)
    discord_refresh_token = Column(String, nullable=True)
    discord_verified = Column(Boolean, default=False)
    
    # Authentication
    webhook_key = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=True)
    password_hash = Column(String, nullable=True)
    
    # Account status
    has_nebula_role = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    
    # Stripe (legacy - kept for backwards compatibility)
    stripe_customer_id = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True)
    subscription_status = Column(String, nullable=True)
    subscription_ends_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.discord_username or self.email}>"
