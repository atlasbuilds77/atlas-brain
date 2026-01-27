"""
File Endpoints
/api/files/upload, /api/files/{id}/download
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File as FastAPIFile
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from typing import Optional, List
import structlog
from datetime import datetime, timedelta

from app.db.session import get_db
from app.models.file import File
from app.schemas.file import (
    FileUpload, FileUpdate, File as FileSchema,
    FileList, FileDownloadURL
)
from app.core.security import get_current_user_id
from app.services.storage_service import StorageService

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.get("", response_model=FileList)
async def list_files(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    client_id: Optional[int] = None,
    category: Optional[str] = None,
    year: Optional[int] = None,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    List all files (paginated)
    
    - Supports filtering by client, category, year
    - Returns paginated results
    """
    # Build query
    query = select(File)
    
    if client_id:
        query = query.where(File.client_id == client_id)
    
    if category:
        query = query.where(File.category == category)
    
    if year:
        query = query.where(File.year == year)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Add pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    query = query.order_by(File.uploaded_at.desc())
    
    # Execute query
    result = await db.execute(query)
    files = result.scalars().all()
    
    return FileList(
        items=files,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size
    )


@router.post("/upload", response_model=FileSchema, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    client_id: Optional[int] = Query(None),
    category: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    is_sensitive: bool = Query(False),
    retention_years: Optional[int] = Query(None),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a file
    
    - Uploads file to S3-compatible storage
    - Encrypts sensitive files
    - Sets retention policy
    """
    try:
        # Read file content
        content = await file.read()
        
        # Upload to storage
        storage_service = StorageService()
        storage_result = await storage_service.upload_file(
            content=content,
            filename=file.filename,
            content_type=file.content_type,
            encrypt=is_sensitive
        )
        
        # Calculate retention date
        retention_until = None
        if retention_years:
            retention_until = datetime.utcnow() + timedelta(days=365 * retention_years)
        
        # Create file record
        new_file = File(
            filename=storage_result["filename"],
            original_filename=file.filename,
            content_type=file.content_type,
            size_bytes=len(content),
            storage_path=storage_result["path"],
            storage_bucket=storage_result["bucket"],
            client_id=client_id,
            user_id=user_id,
            category=category,
            year=year,
            encrypted=storage_result["encrypted"],
            encryption_key_id=storage_result.get("encryption_key_id"),
            retention_until=retention_until,
            is_sensitive=is_sensitive
        )
        
        db.add(new_file)
        await db.commit()
        await db.refresh(new_file)
        
        logger.info("File uploaded", file_id=new_file.id, filename=file.filename)
        
        return new_file
        
    except Exception as e:
        logger.error("File upload failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}"
        )


@router.get("/{file_id}", response_model=FileSchema)
async def get_file(
    file_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get file metadata by ID"""
    result = await db.execute(
        select(File).where(File.id == file_id)
    )
    file = result.scalar_one_or_none()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    return file


@router.get("/{file_id}/download", response_model=FileDownloadURL)
async def get_download_url(
    file_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Get pre-signed download URL
    
    - Generates temporary download link
    - Expires in 1 hour
    - Updates download tracking
    """
    result = await db.execute(
        select(File).where(File.id == file_id)
    )
    file = result.scalar_one_or_none()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Generate pre-signed URL
    storage_service = StorageService()
    download_url = await storage_service.get_download_url(
        storage_path=file.storage_path,
        bucket=file.storage_bucket,
        expires_in=3600  # 1 hour
    )
    
    # Update download tracking
    file.download_count += 1
    file.last_downloaded_at = datetime.utcnow()
    await db.commit()
    
    logger.info("Download URL generated", file_id=file_id)
    
    return FileDownloadURL(
        file_id=file.id,
        filename=file.original_filename,
        download_url=download_url,
        expires_in=3600
    )


@router.put("/{file_id}", response_model=FileSchema)
async def update_file(
    file_id: int,
    file_data: FileUpdate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Update file metadata"""
    result = await db.execute(
        select(File).where(File.id == file_id)
    )
    file = result.scalar_one_or_none()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Update fields
    update_data = file_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(file, field, value)
    
    await db.commit()
    await db.refresh(file)
    
    logger.info("File updated", file_id=file_id)
    
    return file


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Delete file (both record and storage)"""
    result = await db.execute(
        select(File).where(File.id == file_id)
    )
    file = result.scalar_one_or_none()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Delete from storage
    try:
        storage_service = StorageService()
        await storage_service.delete_file(
            storage_path=file.storage_path,
            bucket=file.storage_bucket
        )
    except Exception as e:
        logger.warning("Failed to delete file from storage", file_id=file_id, error=str(e))
    
    # Delete record
    await db.execute(delete(File).where(File.id == file_id))
    await db.commit()
    
    logger.info("File deleted", file_id=file_id)
