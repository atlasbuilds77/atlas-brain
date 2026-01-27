"""Lead schemas - Request/Response models"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional, List, Dict, Any
from app.models.lead import LeadStatus, LeadSource


class LeadBase(BaseModel):
    """Base lead schema"""
    name: str = Field(..., min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    company: Optional[str] = Field(None, max_length=255)
    source: LeadSource = LeadSource.OTHER
    notes: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)


class LeadCreate(LeadBase):
    """Schema for creating a lead"""
    pass


class LeadUpdate(BaseModel):
    """Schema for updating a lead"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    company: Optional[str] = None
    status: Optional[LeadStatus] = None
    source: Optional[LeadSource] = None
    assigned_to: Optional[int] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None


class LeadInDB(LeadBase):
    """Schema for lead in database"""
    id: int
    user_id: Optional[int] = None
    status: LeadStatus
    lead_score: float
    assigned_to: Optional[int] = None
    created_at: datetime
    contacted_at: Optional[datetime] = None
    converted_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class Lead(LeadInDB):
    """Public lead schema (response)"""
    pass


class LeadScore(BaseModel):
    """Lead scoring response"""
    lead_id: int
    score: float = Field(..., ge=0, le=100)
    factors: Dict[str, Any] = Field(default_factory=dict)
    recommendation: str


class LeadList(BaseModel):
    """Paginated lead list response"""
    items: List[Lead]
    total: int
    page: int
    page_size: int
    pages: int
