"""Message schemas - Request/Response models"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional, List, Dict, Any
from app.models.message import MessageChannel, MessageCategory, MessageStatus


class MessageBase(BaseModel):
    """Base message schema"""
    from_address: str = Field(..., max_length=255)
    to_address: str = Field(..., max_length=255)
    channel: MessageChannel = MessageChannel.EMAIL
    subject: Optional[str] = Field(None, max_length=500)
    body: Optional[str] = None
    html_body: Optional[str] = None


class MessageCreate(MessageBase):
    """Schema for creating a message"""
    thread_id: Optional[str] = None
    in_reply_to: Optional[str] = None
    user_id: Optional[int] = None
    client_id: Optional[int] = None
    lead_id: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    sent_at: datetime = Field(default_factory=datetime.utcnow)


class MessageUpdate(BaseModel):
    """Schema for updating a message"""
    status: Optional[MessageStatus] = None
    category: Optional[MessageCategory] = None


class MessageInDB(MessageBase):
    """Schema for message in database"""
    id: int
    thread_id: Optional[str] = None
    in_reply_to: Optional[str] = None
    status: MessageStatus
    category: MessageCategory
    sentiment_score: Optional[int] = None
    priority_score: Optional[int] = None
    ai_summary: Optional[str] = None
    user_id: Optional[int] = None
    client_id: Optional[int] = None
    lead_id: Optional[int] = None
    has_attachments: bool
    attachment_ids: List[int] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    sent_at: datetime
    received_at: datetime
    read_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class Message(MessageInDB):
    """Public message schema (response)"""
    pass


class MessageCategorize(BaseModel):
    """Message categorization response"""
    message_id: int
    category: MessageCategory
    confidence: float = Field(..., ge=0, le=1)
    sentiment_score: Optional[int] = None
    priority_score: Optional[int] = None
    summary: Optional[str] = None


class MessageList(BaseModel):
    """Paginated message list response"""
    items: List[Message]
    total: int
    page: int
    page_size: int
    pages: int
