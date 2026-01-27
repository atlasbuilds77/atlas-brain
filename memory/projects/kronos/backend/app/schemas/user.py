"""User schemas - Request/Response models"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional
from app.models.user import UserRole


# Base schemas
class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=255)
    role: UserRole = UserRole.LEAD


class UserCreate(UserBase):
    """Schema for creating a user"""
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserInDB(UserBase):
    """Schema for user in database"""
    id: int
    created_at: datetime
    last_active: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class User(UserInDB):
    """Public user schema (response)"""
    pass


# Token schemas
class Token(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class TokenPayload(BaseModel):
    """JWT token payload"""
    sub: int
    role: str
    exp: datetime
    iat: datetime
    type: str


class RefreshToken(BaseModel):
    """Refresh token request"""
    refresh_token: str
