"""Client schemas - Request/Response models"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List, Dict, Any
from app.models.client import ClientStatus


class ClientBase(BaseModel):
    """Base client schema"""
    status: ClientStatus = ClientStatus.ONBOARDING
    preferred_contact_method: Optional[str] = None
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)


class ClientCreate(ClientBase):
    """Schema for creating a client"""
    user_id: int
    lead_id: Optional[int] = None


class ClientUpdate(BaseModel):
    """Schema for updating a client"""
    status: Optional[ClientStatus] = None
    lifetime_value: Optional[float] = Field(None, ge=0)
    next_followup: Optional[datetime] = None
    preferred_contact_method: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


class ClientInDB(ClientBase):
    """Schema for client in database"""
    id: int
    user_id: int
    lead_id: Optional[int] = None
    lifetime_value: float
    retention_risk_score: float
    last_interaction: Optional[datetime] = None
    next_followup: Optional[datetime] = None
    client_since: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class Client(ClientInDB):
    """Public client schema (response)"""
    pass


class ClientRisk(BaseModel):
    """Client retention risk analysis"""
    client_id: int
    risk_score: float = Field(..., ge=0, le=1)
    risk_level: str  # low, medium, high
    factors: Dict[str, Any] = Field(default_factory=dict)
    recommendations: List[str]


class ClientList(BaseModel):
    """Paginated client list response"""
    items: List[Client]
    total: int
    page: int
    page_size: int
    pages: int
