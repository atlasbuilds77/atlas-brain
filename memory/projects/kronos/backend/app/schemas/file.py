"""File schemas - Request/Response models"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List, Dict, Any


class FileBase(BaseModel):
    """Base file schema"""
    filename: str = Field(..., max_length=255)
    category: Optional[str] = None
    year: Optional[int] = None
    tags: List[str] = Field(default_factory=list)
    is_sensitive: bool = False


class FileUpload(BaseModel):
    """File upload request"""
    client_id: Optional[int] = None
    category: Optional[str] = None
    year: Optional[int] = None
    tags: List[str] = Field(default_factory=list)
    is_sensitive: bool = False
    retention_years: Optional[int] = None


class FileUpdate(BaseModel):
    """Schema for updating file metadata"""
    filename: Optional[str] = Field(None, max_length=255)
    category: Optional[str] = None
    year: Optional[int] = None
    tags: Optional[List[str]] = None
    is_sensitive: Optional[bool] = None


class FileInDB(FileBase):
    """Schema for file in database"""
    id: int
    original_filename: str
    content_type: Optional[str] = None
    size_bytes: Optional[int] = None
    storage_path: str
    storage_bucket: Optional[str] = None
    client_id: Optional[int] = None
    user_id: Optional[int] = None
    message_id: Optional[int] = None
    encrypted: bool
    encryption_key_id: Optional[str] = None
    retention_until: Optional[datetime] = None
    download_count: int
    last_downloaded_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    uploaded_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class File(FileInDB):
    """Public file schema (response)"""
    pass


class FileDownloadURL(BaseModel):
    """Pre-signed download URL"""
    file_id: int
    filename: str
    download_url: str
    expires_in: int  # seconds


class FileList(BaseModel):
    """Paginated file list response"""
    items: List[File]
    total: int
    page: int
    page_size: int
    pages: int
