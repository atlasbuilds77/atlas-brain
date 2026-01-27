"""File model - Document and file storage tracking"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, BigInteger, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.session import Base


class File(Base):
    """File model - uploaded documents and files"""
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # File details
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    content_type = Column(String)
    size_bytes = Column(BigInteger)
    
    # Storage
    storage_path = Column(String, nullable=False)  # S3 key or local path
    storage_bucket = Column(String)  # S3 bucket name
    
    # Associations
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)  # If from email
    
    # Categorization
    category = Column(String, index=True)  # tax_return, invoice, contract, etc.
    year = Column(Integer, index=True)  # For tax documents
    tags = Column(JSON, default=list)
    
    # Security
    encrypted = Column(Boolean, default=True)
    encryption_key_id = Column(String)  # Reference to encryption key
    
    # Compliance
    retention_until = Column(DateTime(timezone=True))  # Auto-delete after this date
    is_sensitive = Column(Boolean, default=False)  # PII, financial data
    
    # Access tracking
    download_count = Column(Integer, default=0)
    last_downloaded_at = Column(DateTime(timezone=True))
    
    # Metadata
    metadata = Column(JSON, default=dict)  # Custom fields
    
    # Timestamps
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    client = relationship("Client", back_populates="files")
    
    def __repr__(self):
        return f"<File {self.filename}>"
