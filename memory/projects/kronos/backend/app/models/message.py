"""Message model - Email and communication tracking"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Boolean, Text, JSON
from sqlalchemy.sql import func
import enum

from app.db.session import Base


class MessageChannel(str, enum.Enum):
    """Message channel types"""
    EMAIL = "email"
    SMS = "sms"
    WEB = "web"
    PHONE = "phone"


class MessageCategory(str, enum.Enum):
    """AI-categorized message types"""
    PROSPECTIVE = "prospective"  # Lead inquiries
    CLIENT = "client"  # Active client communication
    OFFICE = "office"  # Internal/admin
    SPAM = "spam"
    OTHER = "other"


class MessageStatus(str, enum.Enum):
    """Message read status"""
    UNREAD = "unread"
    READ = "read"
    ARCHIVED = "archived"
    DELETED = "deleted"


class Message(Base):
    """Message model - all communications"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Message details
    from_address = Column(String, nullable=False, index=True)
    to_address = Column(String, nullable=False, index=True)
    channel = Column(SQLEnum(MessageChannel), default=MessageChannel.EMAIL, nullable=False)
    
    # Content
    subject = Column(String)
    body = Column(Text)
    html_body = Column(Text)  # For email HTML content
    
    # Threading
    thread_id = Column(String, index=True)  # Group related messages
    in_reply_to = Column(String)  # Email message ID for threading
    
    # Status and categorization
    status = Column(SQLEnum(MessageStatus), default=MessageStatus.UNREAD, nullable=False, index=True)
    category = Column(SQLEnum(MessageCategory), default=MessageCategory.OTHER, index=True)
    
    # AI analysis
    sentiment_score = Column(Integer)  # -1 (negative) to 1 (positive)
    priority_score = Column(Integer)  # 1-5, AI-determined urgency
    ai_summary = Column(Text)  # Auto-generated summary
    
    # Associations
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=True)
    
    # Attachments (stored separately in files table)
    has_attachments = Column(Boolean, default=False)
    attachment_ids = Column(JSON, default=list)
    
    # Metadata
    metadata = Column(JSON, default=dict)  # Email headers, etc.
    
    # Timestamps
    sent_at = Column(DateTime(timezone=True), nullable=False)
    received_at = Column(DateTime(timezone=True), server_default=func.now())
    read_at = Column(DateTime(timezone=True))
    
    def __repr__(self):
        return f"<Message from={self.from_address} subject={self.subject[:30]}>"
